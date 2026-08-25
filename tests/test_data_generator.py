"""
Tests for the ground-truth data generator and the guarantees it provides.

These tests are what let the benchmark numbers be trusted. They assert that the
generated data really does contain the structure the module claims, that the
structure is learnable, and — most importantly — that the original sample data
genuinely has no signal, so its near-chance scores are a property of the data
rather than a bug in the pipeline.
"""

import numpy as np
import pandas as pd
import pytest

from src.intelligence.data_ingestion import DataIngestionEngine
from src.intelligence.ml_propensity_models import PropensityModelEngine
from src.utils.data_generator import (
    bayes_optimal_churn_auc,
    bayes_optimal_engagement_r2,
    generate_user_data,
)


EXPECTED_COLUMNS = {
    "user_id",
    "lifecycle_stage",
    "days_since_signup",
    "age_band_region",
    "sessions_last_7d",
    "exercises_completed_7d",
    "streak_current",
    "coins_balance",
    "feature_ai_tutor_used",
    "feature_leaderboard_viewed",
    "preferred_hour",
    "notif_open_rate_30d",
    "motivation_score",
    "engagement_next_7d",
}


@pytest.fixture(scope="module")
def benchmark_df():
    return generate_user_data(n_users=1500, seed=42)


class TestSchemaAndDeterminism:
    def test_emits_the_expected_columns(self, benchmark_df):
        assert set(benchmark_df.columns) == EXPECTED_COLUMNS

    def test_latent_traits_are_never_emitted(self, benchmark_df):
        for hidden in ("engagement", "diligence", "churn_prob", "churn_logit"):
            assert hidden not in benchmark_df.columns

    def test_same_seed_reproduces_the_frame(self):
        a = generate_user_data(n_users=200, seed=7)
        b = generate_user_data(n_users=200, seed=7)
        pd.testing.assert_frame_equal(a, b)

    def test_different_seeds_differ(self):
        a = generate_user_data(n_users=200, seed=1)
        b = generate_user_data(n_users=200, seed=2)
        assert not a["lifecycle_stage"].equals(b["lifecycle_stage"])

    def test_respects_requested_size(self):
        assert len(generate_user_data(n_users=321, seed=3)) == 321

    def test_all_lifecycle_values_are_valid(self, benchmark_df):
        assert set(benchmark_df["lifecycle_stage"]) <= {"trial", "paid", "churned", "inactive"}

    def test_counts_are_non_negative(self, benchmark_df):
        for col in ("sessions_last_7d", "exercises_completed_7d", "streak_current",
                    "coins_balance", "engagement_next_7d"):
            assert (benchmark_df[col] >= 0).all(), col

    def test_rates_are_bounded(self, benchmark_df):
        assert benchmark_df["notif_open_rate_30d"].between(0, 1).all()
        assert benchmark_df["motivation_score"].between(0, 1).all()


class TestPlantedStructure:
    def test_churn_rate_is_realistic(self, benchmark_df):
        rate = benchmark_df["lifecycle_stage"].isin(["churned", "inactive"]).mean()
        assert 0.15 < rate < 0.60, f"implausible churn rate {rate:.2%}"

    def test_churned_users_are_less_active(self, benchmark_df):
        churned = benchmark_df["lifecycle_stage"].isin(["churned", "inactive"])
        assert (
            benchmark_df.loc[churned, "sessions_last_7d"].mean()
            < benchmark_df.loc[~churned, "sessions_last_7d"].mean()
        )

    def test_sessions_and_open_rate_move_together(self, benchmark_df):
        corr = benchmark_df["sessions_last_7d"].corr(benchmark_df["notif_open_rate_30d"])
        assert corr > 0.25, f"latent engagement should link these, got r={corr:.3f}"

    def test_churned_users_have_zero_future_engagement(self, benchmark_df):
        churned = benchmark_df["lifecycle_stage"].isin(["churned", "inactive"])
        assert (benchmark_df.loc[churned, "engagement_next_7d"] == 0).all()

    def test_future_engagement_is_not_a_copy_of_current(self, benchmark_df):
        """It must be a fresh draw, otherwise forecasting it would be trivial."""
        active = benchmark_df[~benchmark_df["lifecycle_stage"].isin(["churned", "inactive"])]
        corr = active["sessions_last_7d"].corr(active["engagement_next_7d"])
        assert 0.2 < corr < 0.95, f"expected related-but-distinct, got r={corr:.3f}"


class TestOracleCeilings:
    def test_churn_ceiling_is_below_perfect(self):
        """Sampled labels mean even an oracle cannot reach AUC 1.0."""
        assert 0.70 < bayes_optimal_churn_auc(n_users=8000) < 0.95

    def test_engagement_ceiling_is_below_one(self):
        assert 0.2 < bayes_optimal_engagement_r2(n_users=8000) < 0.90

    def test_ceilings_are_deterministic(self):
        assert bayes_optimal_churn_auc(n_users=4000, seed=5) == pytest.approx(
            bayes_optimal_churn_auc(n_users=4000, seed=5)
        )


class TestPipelineRecoversTheSignal:
    """End-to-end: the real ingestion + model path must learn the planted structure."""

    @pytest.fixture(scope="class")
    def trained(self, tmp_path_factory):
        path = tmp_path_factory.mktemp("bench") / "benchmark.csv"
        generate_user_data(n_users=1500, seed=42).to_csv(path, index=False)

        ingestion = DataIngestionEngine()
        df = ingestion.load_and_validate(str(path))
        df = ingestion.engineer_features(df)

        models = PropensityModelEngine(random_state=42, schema_map=ingestion.schema_map)
        _, churn = models.train_churn_model(df)
        _, engagement = models.train_engagement_model(df)
        return models, churn, engagement

    def test_churn_model_beats_chance_by_a_wide_margin(self, trained):
        _, churn, _ = trained
        assert churn["auc_test"] > 0.72, (
            f"pipeline failed to recover planted churn signal (AUC={churn['auc_test']:.3f})"
        )

    def test_churn_model_does_not_exceed_the_oracle(self, trained):
        """A score above the sampled-label ceiling would mean leakage."""
        _, churn, _ = trained
        assert churn["auc_test"] < 0.95, (
            f"AUC={churn['auc_test']:.3f} implausibly high for sampled labels - suspect leakage"
        )

    def test_engagement_model_explains_real_variance(self, trained):
        _, _, engagement = trained
        assert engagement["r2_score"] > 0.15, (
            f"pipeline failed to recover planted engagement signal (R2={engagement['r2_score']:.3f})"
        )

    def test_forecast_target_never_enters_the_features(self, trained):
        """engagement_next_7d is the label, and is future info for the churn model."""
        models, _, _ = trained
        assert "engagement_next_7d" not in list(models.engagement_model.feature_name_)
        assert "engagement_next_7d" not in list(models.churn_model.feature_names_in_)


class TestOriginalSampleHasNoSignal:
    """
    Pins the claim the README makes about the bundled sample. If someone later swaps
    that file for one with real signal, this test fails loudly and the README stops
    being wrong silently.
    """

    def test_sample_labels_are_independent_of_behaviour(self):
        df = pd.read_csv("data/sample/user_data_sample.csv")
        churned = df["lifecycle_stage"].isin(["churned", "inactive"]).astype(int)
        corr = abs(np.corrcoef(df["sessions_last_7d"], churned)[0, 1])
        assert corr < 0.10, (
            f"sample data now shows behaviour-churn correlation r={corr:.3f}; "
            "the README's 'no signal by construction' claim needs updating"
        )
