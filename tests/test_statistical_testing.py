"""
Tests for the dual Bayesian + frequentist A/B testing framework.

The system only promotes a template when both schools of inference agree, so
these tests pin down each one independently and then the combined verdict.
"""

import numpy as np
import pytest

from src.learning.statistical_testing import StatisticalTestingFramework


@pytest.fixture
def stats_framework():
    return StatisticalTestingFramework(alpha=0.05, power=0.8)


class TestBayesianABTest:
    def test_detects_a_clearly_better_treatment(self, stats_framework):
        result = stats_framework.bayesian_ab_test(
            control_successes=100, control_trials=1_000,
            treatment_successes=200, treatment_trials=1_000,
        )
        assert result["prob_treatment_better"] > 0.99
        assert result["decision"] == "TREATMENT WINS"

    def test_detects_a_clearly_worse_treatment(self, stats_framework):
        result = stats_framework.bayesian_ab_test(
            control_successes=200, control_trials=1_000,
            treatment_successes=100, treatment_trials=1_000,
        )
        assert result["prob_treatment_better"] < 0.01
        assert result["decision"] == "CONTROL WINS"

    def test_identical_arms_are_inconclusive(self, stats_framework):
        result = stats_framework.bayesian_ab_test(
            control_successes=100, control_trials=1_000,
            treatment_successes=100, treatment_trials=1_000,
        )
        assert result["decision"] == "INCONCLUSIVE"
        assert result["prob_treatment_better"] == pytest.approx(0.5, abs=0.15)

    def test_small_samples_stay_inconclusive(self, stats_framework):
        """A 2x lift on 10 trials is not enough evidence to call."""
        result = stats_framework.bayesian_ab_test(
            control_successes=1, control_trials=10,
            treatment_successes=2, treatment_trials=10,
        )
        assert result["decision"] == "INCONCLUSIVE"

    def test_observed_rates_are_reported_verbatim(self, stats_framework):
        result = stats_framework.bayesian_ab_test(
            control_successes=150, control_trials=1_000,
            treatment_successes=250, treatment_trials=1_000,
        )
        assert result["control_rate"] == pytest.approx(0.15)
        assert result["treatment_rate"] == pytest.approx(0.25)

    def test_credible_interval_brackets_observed_rate(self, stats_framework):
        result = stats_framework.bayesian_ab_test(
            control_successes=150, control_trials=1_000,
            treatment_successes=250, treatment_trials=1_000,
        )
        lo, hi = result["treatment_ci"]
        assert lo < 0.25 < hi

    def test_credible_interval_narrows_with_sample_size(self, stats_framework):
        small = stats_framework.bayesian_ab_test(100, 200, 100, 200)
        large = stats_framework.bayesian_ab_test(5_000, 10_000, 5_000, 10_000)

        def width(r):
            lo, hi = r["treatment_ci"]
            return hi - lo

        assert width(large) < width(small)

    def test_expected_improvement_has_the_right_sign(self, stats_framework):
        better = stats_framework.bayesian_ab_test(100, 1_000, 200, 1_000)
        worse = stats_framework.bayesian_ab_test(200, 1_000, 100, 1_000)
        assert better["expected_improvement"] > 0
        assert worse["expected_improvement"] < 0


class TestFrequentistABTest:
    def test_large_true_effect_is_significant(self, stats_framework):
        result = stats_framework.frequentist_ab_test(
            control_successes=100, control_trials=1_000,
            treatment_successes=200, treatment_trials=1_000,
        )
        assert result["p_value"] < 0.05
        assert bool(result["is_significant"]) is True

    def test_no_effect_is_not_significant(self, stats_framework):
        result = stats_framework.frequentist_ab_test(
            control_successes=100, control_trials=1_000,
            treatment_successes=102, treatment_trials=1_000,
        )
        assert result["p_value"] > 0.05
        assert bool(result["is_significant"]) is False

    def test_cohens_h_is_zero_for_equal_rates(self, stats_framework):
        assert stats_framework._cohens_h(0.2, 0.2) == pytest.approx(0.0, abs=1e-12)

    def test_cohens_h_grows_with_separation(self, stats_framework):
        small = abs(stats_framework._cohens_h(0.20, 0.22))
        large = abs(stats_framework._cohens_h(0.20, 0.60))
        assert large > small

    def test_cohens_h_matches_closed_form(self, stats_framework):
        expected = 2 * np.arcsin(np.sqrt(0.5)) - 2 * np.arcsin(np.sqrt(0.1))
        assert abs(stats_framework._cohens_h(0.5, 0.1)) == pytest.approx(abs(expected), rel=1e-6)


class TestSampleSizeCalculation:
    def test_smaller_effects_need_bigger_samples(self, stats_framework):
        subtle = stats_framework.calculate_sample_size(baseline_rate=0.10, min_detectable_effect=0.01)
        obvious = stats_framework.calculate_sample_size(baseline_rate=0.10, min_detectable_effect=0.10)
        assert subtle > obvious

    def test_returns_a_positive_integer(self, stats_framework):
        n = stats_framework.calculate_sample_size(baseline_rate=0.10, min_detectable_effect=0.02)
        assert n > 0
        assert n == int(n)


class TestAgreementBetweenMethods:
    def test_both_methods_agree_on_a_strong_effect(self, stats_framework):
        bayes = stats_framework.bayesian_ab_test(100, 1_000, 200, 1_000)
        freq = stats_framework.frequentist_ab_test(100, 1_000, 200, 1_000)
        assert bayes["prob_treatment_better"] > 0.95
        assert bool(freq["is_significant"]) is True

    def test_both_methods_agree_on_a_null_effect(self, stats_framework):
        bayes = stats_framework.bayesian_ab_test(100, 1_000, 101, 1_000)
        freq = stats_framework.frequentist_ab_test(100, 1_000, 101, 1_000)
        assert bayes["decision"] == "INCONCLUSIVE"
        assert bool(freq["is_significant"]) is False
