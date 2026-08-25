"""
Regression tests for the ML propensity layer.

The point of these tests is to separate two things that the sample dataset
conflates:

1. Does the pipeline *avoid* leaking the target into the features?
2. Does the pipeline *recover* a relationship when one genuinely exists?

The bundled synthetic sample has no learnable signal, so a good score there
would indicate a bug. These tests therefore build their own datasets with a
known ground truth.
"""

import numpy as np
import pandas as pd
import pytest

from src.intelligence.ml_propensity_models import PropensityModelEngine


SCHEMA_MAP = {
    "user_id": "user_id",
    "lifecycle_stage": "lifecycle_stage",
    "activeness_metrics": ["sessions_last_7d"],
    "value_metrics": ["coins_balance"],
    "retention_metrics": ["streak_current"],
    "feature_flags": ["feature_ai_tutor_used", "feature_leaderboard_viewed"],
}


def _engine(config_path):
    return PropensityModelEngine(random_state=42, config_path=config_path, schema_map=SCHEMA_MAP)


def _frame(n=400, seed=0, signal=False):
    """Build a synthetic frame; when signal=True the target is a function of the features."""
    rng = np.random.default_rng(seed)

    sessions = rng.integers(0, 20, n).astype(float)
    streak = rng.integers(0, 30, n).astype(float)
    days_since_signup = rng.integers(1, 365, n).astype(float)
    ai_tutor = rng.integers(0, 2, n).astype(float)
    leaderboard = rng.integers(0, 2, n).astype(float)

    if signal:
        # coins_balance is a deterministic-plus-noise function of behaviour.
        coins = 30 * sessions + 12 * streak + 90 * ai_tutor + rng.normal(0, 8, n)
    else:
        coins = rng.integers(0, 1000, n).astype(float)

    df = pd.DataFrame(
        {
            "user_id": [f"U{i:04d}" for i in range(n)],
            "lifecycle_stage": rng.choice(["trial", "paid", "churned", "inactive"], n),
            "sessions_last_7d": sessions,
            "streak_current": streak,
            "days_since_signup": days_since_signup,
            "coins_balance": coins,
            "feature_ai_tutor_used": ai_tutor,
            "feature_leaderboard_viewed": leaderboard,
            "notif_open_rate_30d": rng.random(n),
        }
    )

    # Mirror the derived columns that data_ingestion.engineer_features would add.
    def _norm(s):
        span = s.max() - s.min()
        return (s - s.min()) / span if span else pd.Series(np.zeros(len(s)), index=s.index)

    df["activeness"] = _norm(df["sessions_last_7d"])
    # Derived from value_metrics + feature_flags -> leaks a coins_balance target.
    df["gamification_propensity"] = (
        _norm(df["coins_balance"]) + df["feature_ai_tutor_used"] + df["feature_leaderboard_viewed"]
    ) / 3
    df["social_propensity"] = df["feature_leaderboard_viewed"]
    df["churn_risk"] = 0.6 * (1 - df["activeness"]) + 0.4 * (1 - _norm(df["streak_current"]))
    return df


class TestLeakageGuard:
    def test_flags_feature_derived_from_target_columns(self, config_path):
        engine = _engine(config_path)
        leaky = engine._derived_features_using(["coins_balance"])
        assert "gamification_propensity" in leaky, (
            "gamification_propensity normalises value_metrics, which is the engagement "
            "target, so it must be flagged as leaky"
        )

    def test_does_not_flag_unrelated_features(self, config_path):
        engine = _engine(config_path)
        leaky = engine._derived_features_using(["coins_balance"])
        assert "social_propensity" not in leaky
        assert "activeness" not in leaky

    def test_activeness_target_taints_activeness_derived_features(self, config_path):
        engine = _engine(config_path)
        leaky = engine._derived_features_using(["sessions_last_7d"])
        assert "activeness" in leaky
        assert "churn_risk" in leaky

    def test_empty_target_sources_flags_nothing(self, config_path):
        engine = _engine(config_path)
        assert engine._derived_features_using([]) == set()

    def test_leaky_feature_excluded_from_trained_model(self, config_path):
        engine = _engine(config_path)
        engine.train_engagement_model(_frame(signal=True))
        trained_on = list(engine.engagement_model.feature_name_)
        assert "gamification_propensity" not in trained_on
        assert "coins_balance" not in trained_on


class TestEngagementModel:
    def test_recovers_a_real_relationship(self, config_path):
        """With leakage removed, a genuine signal must still be learnable."""
        engine = _engine(config_path)
        _, metrics = engine.train_engagement_model(_frame(signal=True))
        assert metrics["r2_score"] > 0.75, (
            f"expected the model to recover a planted signal, got R2={metrics['r2_score']:.3f}"
        )

    def test_reports_no_signal_on_random_target(self, config_path):
        """Random targets must not produce a high score once leakage is gone."""
        engine = _engine(config_path)
        _, metrics = engine.train_engagement_model(_frame(signal=False))
        assert metrics["r2_score"] < 0.3, (
            f"random target scored R2={metrics['r2_score']:.3f}; leakage may have returned"
        )

    def test_metrics_payload_shape(self, config_path):
        engine = _engine(config_path)
        _, metrics = engine.train_engagement_model(_frame(signal=True))
        for key in ("model_type", "rmse", "r2_score", "n_features", "train_size", "test_size"):
            assert key in metrics
        assert metrics["train_size"] + metrics["test_size"] == 400


class TestChurnModel:
    def test_trains_and_reports_auc(self, config_path):
        engine = _engine(config_path)
        _, metrics = engine.train_churn_model(_frame(signal=True))
        assert 0.0 <= metrics["auc_test"] <= 1.0
        assert metrics["n_features"] > 0

    def test_churn_target_derived_from_lifecycle_stage(self, config_path):
        engine = _engine(config_path)
        df = _frame(signal=True)
        engine.train_churn_model(df)
        expected = df["lifecycle_stage"].isin(["churned", "inactive"]).astype(int)
        assert (df["churn_target"] == expected).all()

    def test_predictions_are_probabilities(self, config_path):
        engine = _engine(config_path)
        df = _frame(signal=True)
        engine.train_churn_model(df)
        engine.train_engagement_model(df)
        scored = engine.predict_user_propensities(df)
        assert scored["ml_churn_propensity"].between(0, 1).all()
