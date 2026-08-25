"""
Experiment Results Generator — Synthesizes realistic experiment data
from Iteration 0 outputs for demo and testing.

Generates experiment_results_sample.csv that is fully compatible with
the templates, segments, themes, and timing produced by iteration0.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


def generate_experiment_results(
    output_dir: str = "data/output",
    sample_dir: str = "data/sample",
    samples_per_template: int = 1,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic experiment results from iteration0 outputs.

    Reads templates, timing, and themes CSVs produced by iteration0 and
    creates a realistic experiment_results_sample.csv that iteration1
    can consume directly.

    Args:
        output_dir: Directory containing iteration0 outputs.
        sample_dir: Directory to save generated experiment results.
        samples_per_template: How many experiment rows per template.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with synthetic experiment results.
    """
    rng = np.random.RandomState(seed)

    # Load iteration0 outputs
    templates = pd.read_csv(f"{output_dir}/message_templates.csv")
    timing = pd.read_csv(f"{output_dir}/timing_recommendations.csv")

    # Get unique time windows from timing recommendations
    time_windows = timing["time_window"].unique().tolist()
    if not time_windows:
        time_windows = ["evening", "mid_morning"]

    # Sample a representative subset of templates (one per segment × lifecycle × goal × theme)
    group_cols = ["segment_id", "lifecycle_stage", "goal", "theme"]
    available = [c for c in group_cols if c in templates.columns]
    if available:
        sampled = templates.groupby(available).first().reset_index()
    else:
        sampled = templates.head(50)

    rows = []
    for _, tpl in sampled.iterrows():
        for _ in range(samples_per_template):
            # Assign a random time window
            window = rng.choice(time_windows)

            # Assign quality tier so learning engine sees clear winners/losers
            tier = rng.choice(['GOOD', 'NEUTRAL', 'BAD'], p=[0.20, 0.40, 0.40])
            if tier == 'GOOD':
                base_ctr = rng.uniform(0.15, 0.30)
                engagement_rate = rng.uniform(0.40, 0.70)
                uninstall_rate = rng.uniform(0.001, 0.015)
            elif tier == 'NEUTRAL':
                base_ctr = rng.uniform(0.05, 0.15)
                engagement_rate = rng.uniform(0.20, 0.40)
                uninstall_rate = rng.uniform(0.005, 0.025)
            else:  # BAD
                base_ctr = rng.uniform(0.01, 0.05)
                engagement_rate = rng.uniform(0.05, 0.20)
                uninstall_rate = rng.uniform(0.02, 0.06)

            # Theme modifier (some themes naturally perform better)
            theme_mod = {
                'accomplishment': 1.10, 'social_influence': 1.08,
                'epic_meaning': 1.05, 'ownership': 1.02,
                'empowerment': 1.0, 'scarcity': 0.95,
                'loss_avoidance': 0.92, 'unpredictability': 0.90,
            }.get(str(tpl.get('theme', '')).lower(), 1.0)
            base_ctr *= theme_mod
            engagement_rate *= theme_mod

            # Window modifier
            window_mod = {
                'evening': 1.12, 'mid_morning': 1.08, 'afternoon': 1.0,
                'late_afternoon': 0.95, 'early_morning': 0.88, 'night': 0.82,
            }.get(window, 1.0)
            base_ctr *= window_mod

            total_sends = int(rng.choice([200, 300, 500, 800, 1000]))
            total_opens = int(total_sends * base_ctr)
            total_engagements = int(total_opens * engagement_rate)
            ctr = total_opens / total_sends if total_sends else 0

            # Performance status per PS thresholds
            if ctr > 0.15 and engagement_rate > 0.40:
                performance_status = 'GOOD'
            elif ctr < 0.05 or engagement_rate < 0.20:
                performance_status = 'BAD'
            else:
                performance_status = 'NEUTRAL'

            rows.append({
                "template_id": tpl["template_id"],
                "segment_id": tpl["segment_id"],
                "lifecycle_stage": tpl["lifecycle_stage"],
                "goal": tpl.get("goal", "activation"),
                "theme": tpl.get("theme", "accomplishment"),
                "notification_window": window,
                "total_sends": total_sends,
                "total_opens": total_opens,
                "total_engagements": total_engagements,
                "ctr": round(ctr, 4),
                "engagement_rate": round(engagement_rate, 4),
                "uninstall_rate": round(uninstall_rate, 4),
                "performance_status": performance_status,
            })

    df = pd.DataFrame(rows)

    # Save
    Path(sample_dir).mkdir(parents=True, exist_ok=True)
    out_path = f"{sample_dir}/experiment_results_sample.csv"
    df.to_csv(out_path, index=False)
    print(f"   [OK] Generated {len(df)} synthetic experiment rows -> {out_path}")

    return df
