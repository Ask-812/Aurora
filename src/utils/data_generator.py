"""
Ground-truth synthetic user data generator.

Why this exists
---------------
The dataset originally bundled with this project (`data/sample/user_data_sample.csv`)
draws `lifecycle_stage` independently of the behavioural columns. No relationship
exists between features and labels, so no model can score above chance on it. That
makes it useless for answering the question "is the ML layer actually correct?".

This module generates a benchmark where the answer is knowable, because the data
generating process (DGP) is written down here explicitly.

The DGP
-------
Each user has two latent traits that are never written to the CSV:

    engagement ~ Beta(2, 2)     how much the user likes the product
    diligence  ~ Beta(2, 2)     how consistently they return

Every observable is drawn conditionally on those latents plus noise:

    sessions_last_7d        ~ Poisson(0.5 + 14 * engagement)
    exercises_completed_7d  ~ Poisson(sessions * (0.4 + 1.6 * engagement))
    streak_current          ~ Poisson(1 + 18 * diligence)         capped at 30
    coins_balance           ~ 45 * cumulative_activity + Normal noise
    notif_open_rate_30d     ~ Beta shaped around (0.05 + 0.55 * engagement)
    feature_*_used          ~ Bernoulli(f(engagement, diligence))

Churn is then sampled — not computed — from a logistic model on the same latents:

    P(churn) = sigmoid(2.2 - 4.4 * engagement - 1.6 * diligence + 0.9 * recency_z)

Because churn is *sampled*, the Bayes-optimal AUC is bounded well below 1.0. A model
that scores ~0.80-0.88 here has genuinely learned the process; a model that scores
~1.0 is leaking, and a model that scores ~0.5 is broken.

The forecast target
-------------------
`engagement_next_7d` is drawn for the *following* week from the same latents, and is
suppressed to zero for users who churn. It is a forward-looking quantity: it is never
an input to any feature, so predicting it is a real forecasting task rather than the
circular one the original target created.

Deliberately unmapped column name
---------------------------------
The heuristic schema mapper in `src/intelligence/data_ingestion.py` claims columns
containing "session" or "open" as activeness metrics, "coins"/"order" as value
metrics, and "streak"/"signup" as retention metrics. The name `engagement_next_7d`
matches none of those patterns, so the target can never be silently absorbed into the
feature set.
"""

from __future__ import annotations

import argparse
from typing import Optional

import numpy as np
import pandas as pd


AGE_BANDS = ["18-20_Tier1", "20-30_Tier1", "20-30_Tier2", "30-40_Tier2", "30-40_Tier3"]

# Coefficients of the churn logit. Exposed so tests can assert the direction of each
# effect rather than hardcoding magic numbers in two places.
CHURN_INTERCEPT = 2.2
CHURN_ENGAGEMENT_COEF = -4.4
CHURN_DILIGENCE_COEF = -1.6
CHURN_RECENCY_COEF = 0.9


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def generate_user_data(n_users: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generate a user behaviour dataset with a known, learnable structure.

    Args:
        n_users: Number of users to generate.
        seed: RNG seed; the same seed always produces the same frame.

    Returns:
        DataFrame matching the schema of `data/sample/user_data_sample.csv`, plus a
        forward-looking `engagement_next_7d` column.
    """
    rng = np.random.default_rng(seed)

    # ---- latent traits (never emitted) ----------------------------------------
    engagement = rng.beta(2.0, 2.0, n_users)
    diligence = rng.beta(2.0, 2.0, n_users)

    # ---- tenure and recency ---------------------------------------------------
    days_since_signup = rng.integers(1, 400, n_users)
    # Engaged users have been seen more recently.
    days_since_last_active = rng.poisson(1 + 12 * (1 - engagement)).clip(0, 60)
    recency_z = (days_since_last_active - days_since_last_active.mean()) / (
        days_since_last_active.std() or 1.0
    )

    # ---- observable behaviour, all conditioned on the latents ------------------
    sessions = rng.poisson(0.5 + 14 * engagement).clip(0, 60)
    exercises = rng.poisson(sessions * (0.4 + 1.6 * engagement)).clip(0, 200)
    streak = rng.poisson(1 + 18 * diligence).clip(0, 30)

    cumulative_activity = sessions * (0.6 + 0.8 * diligence) * np.sqrt(
        np.maximum(days_since_signup, 1) / 30.0
    )
    coins = np.maximum(0, 45 * cumulative_activity + rng.normal(0, 60, n_users)).round()

    open_centre = np.clip(0.05 + 0.55 * engagement, 0.01, 0.95)
    concentration = 12.0
    notif_open_rate = rng.beta(open_centre * concentration,
                               (1 - open_centre) * concentration)

    ai_tutor = rng.random(n_users) < (0.10 + 0.65 * engagement)
    leaderboard = rng.random(n_users) < (0.10 + 0.55 * diligence)

    motivation = np.clip(0.25 * rng.random(n_users) + 0.75 * engagement, 0, 1)
    preferred_hour = rng.integers(6, 23, n_users)

    # ---- churn is SAMPLED from a logistic model, not derived -------------------
    churn_logit = (
        CHURN_INTERCEPT
        + CHURN_ENGAGEMENT_COEF * engagement
        + CHURN_DILIGENCE_COEF * diligence
        + CHURN_RECENCY_COEF * recency_z
    )
    churn_prob = _sigmoid(churn_logit)
    churned = rng.random(n_users) < churn_prob

    # Non-churned users split into trial/paid by engagement; churned users split
    # into churned/inactive by how long they have been gone.
    paid = (~churned) & (rng.random(n_users) < (0.15 + 0.6 * engagement))
    lifecycle = np.where(
        churned,
        np.where(days_since_last_active > 14, "inactive", "churned"),
        np.where(paid, "paid", "trial"),
    )

    # ---- forward-looking forecast target --------------------------------------
    next_week = rng.poisson(0.5 + 14 * engagement * (0.6 + 0.4 * diligence))
    engagement_next_7d = np.where(churned, 0, next_week).astype(int)

    return pd.DataFrame(
        {
            "user_id": [f"U{i:04d}" for i in range(n_users)],
            "lifecycle_stage": lifecycle,
            "days_since_signup": days_since_signup,
            "age_band_region": rng.choice(AGE_BANDS, n_users),
            "sessions_last_7d": sessions,
            "exercises_completed_7d": exercises,
            "streak_current": streak,
            "coins_balance": coins.astype(int),
            "feature_ai_tutor_used": ai_tutor,
            "feature_leaderboard_viewed": leaderboard,
            "preferred_hour": preferred_hour,
            "notif_open_rate_30d": notif_open_rate,
            "motivation_score": motivation,
            "engagement_next_7d": engagement_next_7d,
        }
    )


def bayes_optimal_churn_auc(n_users: int = 20000, seed: int = 7) -> float:
    """
    Estimate the ceiling any churn model could reach on this DGP.

    Because churn is sampled from `churn_prob`, even a model handed the true
    probability cannot separate the classes perfectly. Scoring the labels with the
    true probability gives the achievable upper bound, which is what makes a real
    model's AUC interpretable.
    """
    from sklearn.metrics import roc_auc_score

    rng = np.random.default_rng(seed)
    engagement = rng.beta(2.0, 2.0, n_users)
    diligence = rng.beta(2.0, 2.0, n_users)
    days_since_last_active = rng.poisson(1 + 12 * (1 - engagement)).clip(0, 60)
    recency_z = (days_since_last_active - days_since_last_active.mean()) / (
        days_since_last_active.std() or 1.0
    )
    churn_prob = _sigmoid(
        CHURN_INTERCEPT
        + CHURN_ENGAGEMENT_COEF * engagement
        + CHURN_DILIGENCE_COEF * diligence
        + CHURN_RECENCY_COEF * recency_z
    )
    churned = rng.random(n_users) < churn_prob
    return float(roc_auc_score(churned, churn_prob))


def bayes_optimal_engagement_r2(n_users: int = 20000, seed: int = 11) -> float:
    """
    Estimate the ceiling any engagement forecaster could reach on this DGP.

    `engagement_next_7d` is a Poisson draw, so most of its variance is irreducible
    counting noise that no model can explain. An oracle that knew both latent traits
    exactly would still only reach this R², which is what makes the model's score
    interpretable: 0.27 against a ceiling of ~0.35 is a good model on a noisy target,
    not a broken one.
    """
    rng = np.random.default_rng(seed)
    engagement = rng.beta(2.0, 2.0, n_users)
    diligence = rng.beta(2.0, 2.0, n_users)
    days_since_last_active = rng.poisson(1 + 12 * (1 - engagement)).clip(0, 60)
    recency_z = (days_since_last_active - days_since_last_active.mean()) / (
        days_since_last_active.std() or 1.0
    )

    churn_prob = _sigmoid(
        CHURN_INTERCEPT
        + CHURN_ENGAGEMENT_COEF * engagement
        + CHURN_DILIGENCE_COEF * diligence
        + CHURN_RECENCY_COEF * recency_z
    )
    churned = rng.random(n_users) < churn_prob

    lam = 0.5 + 14 * engagement * (0.6 + 0.4 * diligence)
    observed = np.where(churned, 0, rng.poisson(lam))

    # Oracle prediction: knows the latents, but not the sampled churn coin flip.
    oracle = (1 - churn_prob) * lam

    ss_res = float(((observed - oracle) ** 2).sum())
    ss_tot = float(((observed - observed.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot


def main(argv: Optional[list] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--n-users", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/sample/user_data_benchmark.csv")
    args = parser.parse_args(argv)

    df = generate_user_data(n_users=args.n_users, seed=args.seed)
    df.to_csv(args.output, index=False)

    churn_rate = df["lifecycle_stage"].isin(["churned", "inactive"]).mean()
    print(f"[OK] Wrote {len(df)} users -> {args.output}")
    print(f"     churn rate: {churn_rate:.1%}")
    print(f"     Bayes-optimal churn AUC for this DGP: {bayes_optimal_churn_auc():.3f}")
    print(f"     Bayes-optimal engagement R2 for this DGP: {bayes_optimal_engagement_r2():.3f}")


if __name__ == "__main__":
    main()
