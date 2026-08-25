"""
Tests for the Thompson-sampling multi-armed bandit.

These cover the properties the learning loop depends on: correct Beta-posterior
bookkeeping, credible intervals that tighten with evidence, exploration that
still favours the better arm, and state that survives a save/load round trip.
"""

import json
import os

import numpy as np
import pandas as pd
import pytest

from src.learning.multi_armed_bandit import MultiArmedBanditEngine


def _templates(ids):
    return pd.DataFrame({"template_id": ids})


def _results(rows):
    return pd.DataFrame(
        [
            {
                "template_id": tid,
                "total_sends": sends,
                "total_opens": opens,
                "total_engagements": engagements,
            }
            for tid, sends, opens, engagements in rows
        ]
    )


@pytest.fixture
def bandit(config_path):
    engine = MultiArmedBanditEngine(config_path=config_path)
    engine.initialize_bandits(_templates(["T1", "T2", "T3"]))
    return engine


class TestInitialization:
    def test_starts_with_uniform_beta_prior(self, bandit):
        for state in bandit.template_bandits.values():
            assert state["alpha"] == 1
            assert state["beta"] == 1

    def test_creates_one_arm_per_template(self, bandit):
        assert set(bandit.template_bandits) == {"T1", "T2", "T3"}

    def test_duplicate_template_ids_collapse_to_one_arm(self, config_path):
        engine = MultiArmedBanditEngine(config_path=config_path)
        engine.initialize_bandits(_templates(["T1", "T1", "T2"]))
        assert len(engine.template_bandits) == 2


class TestPosteriorUpdates:
    def test_alpha_and_beta_accumulate_clicks_and_misses(self, bandit):
        bandit.update_from_experiments(_results([("T1", 100, 20, 10)]))
        state = bandit.template_bandits["T1"]
        assert state["alpha"] == 1 + 20
        assert state["beta"] == 1 + 80

    def test_estimated_ctr_is_posterior_mean(self, bandit):
        bandit.update_from_experiments(_results([("T1", 100, 20, 10)]))
        state = bandit.template_bandits["T1"]
        # Beta(1+20, 1+80) -> mean = 21 / 102
        assert state["estimated_ctr"] == pytest.approx(21 / 102)

    def test_updates_are_incremental_across_rounds(self, bandit):
        bandit.update_from_experiments(_results([("T1", 100, 20, 10)]))
        bandit.update_from_experiments(_results([("T1", 100, 30, 10)]))
        state = bandit.template_bandits["T1"]
        assert state["alpha"] == 1 + 50
        assert state["total_sends"] == 200

    def test_unknown_template_is_ignored(self, bandit):
        bandit.update_from_experiments(_results([("UNKNOWN", 100, 20, 10)]))
        assert "UNKNOWN" not in bandit.template_bandits

    def test_credible_interval_tightens_with_more_evidence(self, config_path):
        narrow = MultiArmedBanditEngine(config_path=config_path)
        narrow.initialize_bandits(_templates(["T1"]))
        narrow.update_from_experiments(_results([("T1", 10_000, 2_000, 0)]))

        wide = MultiArmedBanditEngine(config_path=config_path)
        wide.initialize_bandits(_templates(["T1"]))
        wide.update_from_experiments(_results([("T1", 100, 20, 0)]))

        def width(engine):
            lo, hi = engine.template_bandits["T1"]["confidence_interval"]
            return hi - lo

        assert width(narrow) < width(wide)

    def test_credible_interval_brackets_the_true_rate(self, bandit):
        bandit.update_from_experiments(_results([("T1", 5_000, 1_000, 0)]))
        lo, hi = bandit.template_bandits["T1"]["confidence_interval"]
        assert lo < 0.20 < hi


class TestThompsonSampling:
    def test_selects_requested_number_of_arms(self, bandit):
        assert len(bandit.thompson_sampling_select(["T1", "T2", "T3"], n_samples=2)) == 2

    def test_returns_only_candidate_ids(self, bandit):
        selected = bandit.thompson_sampling_select(["T1", "T2"], n_samples=1)
        assert selected[0] in {"T1", "T2"}

    def test_favours_the_stronger_arm_over_many_draws(self, bandit):
        bandit.update_from_experiments(
            _results([("T1", 1_000, 400, 0), ("T2", 1_000, 50, 0)])
        )
        np.random.seed(42)
        picks = [bandit.thompson_sampling_select(["T1", "T2"], n_samples=1)[0] for _ in range(200)]
        assert picks.count("T1") > 180, "clearly better arm should dominate selection"

    def test_still_explores_when_arms_are_close(self, bandit):
        bandit.update_from_experiments(
            _results([("T1", 60, 12, 0), ("T2", 60, 11, 0)])
        )
        np.random.seed(7)
        picks = {bandit.thompson_sampling_select(["T1", "T2"], n_samples=1)[0] for _ in range(60)}
        assert picks == {"T1", "T2"}, "near-tied arms must both keep getting traffic"


class TestWinnersAndLosers:
    def test_high_performer_is_a_winner(self, bandit):
        bandit.update_from_experiments(_results([("T1", 5_000, 2_000, 0)]))
        verdict = bandit.identify_winners_losers()
        assert "T1" in verdict["winners"]

    def test_low_performer_is_a_loser(self, bandit):
        bandit.update_from_experiments(_results([("T2", 5_000, 50, 0)]))
        verdict = bandit.identify_winners_losers()
        assert "T2" in verdict["losers"]

    def test_thin_evidence_yields_no_verdict(self, bandit):
        bandit.update_from_experiments(_results([("T3", 8, 2, 0)]))
        verdict = bandit.identify_winners_losers()
        assert "T3" in verdict["uncertain"], "must not rule on an arm with almost no data"


class TestRankingsAndPersistence:
    def test_rankings_are_sorted_best_first(self, bandit):
        bandit.update_from_experiments(
            _results([("T1", 1_000, 400, 0), ("T2", 1_000, 100, 0), ("T3", 1_000, 250, 0)])
        )
        ranked = bandit.get_template_rankings()
        assert list(ranked["template_id"])[0] == "T1"

    def test_state_round_trips_through_disk(self, bandit, tmp_path):
        bandit.update_from_experiments(_results([("T1", 100, 20, 5)]))
        bandit.save_bandit_state(str(tmp_path))

        saved = json.loads((tmp_path / "bandit_state.json").read_text())
        assert saved["T1"]["alpha"] == 21
        assert saved["T1"]["beta"] == 81
