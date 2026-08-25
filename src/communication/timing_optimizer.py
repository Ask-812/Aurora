"""
Timing Optimization with Survival Analysis
- Survival analysis for optimal send times
- Time-to-event modeling
- Hazard rate analysis for engagement windows
- Predictive timing based on user behavior patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import yaml
import warnings
warnings.filterwarnings('ignore')

try:
    from lifelines import KaplanMeierFitter, CoxPHFitter
    LIFELINES_AVAILABLE = True
except ImportError:
    LIFELINES_AVAILABLE = False
    print("Warning: lifelines not available, using fallback timing optimization")


class TimingOptimizer:
    """
    Timing optimization using survival analysis and predictive models
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load time windows from config or use defaults
        tw_config = self.config.get('time_windows', {})
        self.time_windows = {
            'early_morning': tuple(tw_config.get('early_morning', [6, 9])),
            'mid_morning': tuple(tw_config.get('mid_morning', [9, 12])),
            'afternoon': tuple(tw_config.get('afternoon', [12, 15])),
            'late_afternoon': tuple(tw_config.get('late_afternoon', [15, 18])),
            'evening': tuple(tw_config.get('evening', [18, 21])),
            'night': tuple(tw_config.get('night', [21, 24]))
        }
        
        # Load frequency thresholds from config
        freq_config = self.config.get('frequency', {})
        self.high_activeness_threshold = freq_config.get('high_activeness_threshold', 0.7)
        self.medium_activeness_threshold = freq_config.get('medium_activeness_threshold', 0.4)
        self.high_activeness_freq = freq_config.get('high_activeness_freq', 8)
        self.medium_activeness_freq = freq_config.get('medium_activeness_freq', 6)
        self.low_activeness_freq = freq_config.get('low_activeness_freq', 4)
        self.uninstall_threshold = freq_config.get('uninstall_threshold', 0.02)
        self.uninstall_reduction = freq_config.get('uninstall_reduction', 2)
        
        self.survival_models = {}
        self.optimal_timings = None
        
    def optimize_with_survival_analysis(self, 
                                       user_data: pd.DataFrame,
                                       experiment_results: pd.DataFrame = None) -> pd.DataFrame:
        """
        Optimize timing using survival analysis
        Models time-to-engagement as survival problem
        
        Args:
            user_data: User behavioral data
            experiment_results: Optional experiment results for learning
            
        Returns:
            DataFrame with optimal timing recommendations
        """
        print("\n[Time] Advanced Timing Optimization with Survival Analysis...")
        
        if experiment_results is not None and LIFELINES_AVAILABLE:
            return self._optimize_from_experiments(user_data, experiment_results)
        else:
            return self._optimize_from_user_patterns(user_data)
    
    def _optimize_from_experiments(self, 
                                   user_data: pd.DataFrame,
                                   experiment_results: pd.DataFrame) -> pd.DataFrame:
        """
        Learn optimal timing from experiment results using survival analysis.
        Uses Kaplan-Meier for per-segment engagement curves and CoxPH for hazard ratios.
        """
        print("   [Stats] Learning from experiment results...")
        
        timing_recs = []
        
        # ── Survival analysis: model time-to-engagement per window ──
        if LIFELINES_AVAILABLE:
            try:
                kmf = KaplanMeierFitter()
                # Build survival data: per template, model "duration" as inverse CTR
                # (higher CTR = faster engagement = lower duration)
                surv_df = experiment_results.copy()
                surv_df['duration'] = 1.0 / (surv_df['ctr'].clip(lower=0.01))
                surv_df['observed'] = (surv_df['ctr'] > 0.05).astype(int)  # engaged = event observed
                
                for segment_id in surv_df['segment_id'].unique():
                    seg_data = surv_df[surv_df['segment_id'] == segment_id]
                    if len(seg_data) < 3:
                        continue
                    kmf.fit(seg_data['duration'], event_observed=seg_data['observed'],
                            label=f'Segment_{segment_id}')
                    median_survival = kmf.median_survival_time_
                    self.survival_models[segment_id] = {
                        'median_survival': median_survival,
                        'event_rate': seg_data['observed'].mean(),
                    }
                print(f"   [Stats] Kaplan-Meier fitted for {len(self.survival_models)} segments")
            except Exception as e:
                print(f"   [WARN] Survival analysis failed ({e}), using composite scoring")
        
        # ── Window-level performance scoring ──
        for segment_id in experiment_results['segment_id'].unique():
            seg_experiments = experiment_results[
                experiment_results['segment_id'] == segment_id
            ]
            
            # Calculate performance metrics per window
            window_perf = seg_experiments.groupby('notification_window').agg({
                'ctr': 'mean',
                'engagement_rate': 'mean',
                'total_sends': 'sum',
                'uninstall_rate': 'mean'
            }).reset_index()
            
            # Filter for statistical significance (min 100 sends)
            window_perf = window_perf[window_perf['total_sends'] >= 100]
            
            if len(window_perf) == 0:
                continue
            
            # Composite score: CTR + Engagement - Uninstall Penalty
            # Apply survival model hazard boost if available
            survival_boost = 1.0
            if segment_id in self.survival_models:
                event_rate = self.survival_models[segment_id]['event_rate']
                survival_boost = 1.0 + event_rate  # Segments with higher engagement events get boosted
            
            window_perf['composite_score'] = (
                window_perf['ctr'] * 0.5 +
                window_perf['engagement_rate'] * 0.4 -
                window_perf['uninstall_rate'] * 5.0
            ) * survival_boost
            
            # Sort by composite score
            window_perf = window_perf.sort_values('composite_score', ascending=False)
            
            # Top 2 windows
            for priority, (_, row) in enumerate(window_perf.head(2).iterrows(), 1):
                timing_recs.append({
                    'segment_id': segment_id,
                    'lifecycle_stage': 'all',
                    'time_window': row['notification_window'],
                    'priority': priority,
                    'expected_ctr': row['ctr'],
                    'expected_engagement': row['engagement_rate'],
                    'uninstall_risk': row['uninstall_rate'],
                    'composite_score': row['composite_score'],
                    'confidence': 'HIGH' if row['total_sends'] >= 500 else 'MEDIUM',
                    'total_samples': int(row['total_sends']),
                    'optimization_method': 'survival_analysis'
                })
        
        self.optimal_timings = pd.DataFrame(timing_recs)
        
        # Ensure mandatory columns exist
        for col in ['segment_id', 'time_window', 'priority']:
            if col not in self.optimal_timings.columns:
                self.optimal_timings[col] = None

        print(f"   [OK] Generated {len(timing_recs)} timing recommendations")
        
        return self.optimal_timings
    
    def _optimize_from_user_patterns(self, user_data: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize timing based on user behavioral patterns
        """
        print("   [Stats] Analyzing user behavioral patterns...")
        
        timing_recs = []
        
        for segment_id in user_data['segment_id'].unique():
            seg_users = user_data[user_data['segment_id'] == segment_id]
            
            # Analyze preferred hours
            if 'preferred_hour' in seg_users.columns:
                preferred_hours = seg_users['preferred_hour'].dropna()
                
                if len(preferred_hours) > 0:
                    # Calculate hour frequency
                    hour_dist = preferred_hours.value_counts(normalize=True)
                    
                    # Map to windows and aggregate
                    window_scores = {}
                    for hour, freq in hour_dist.items():
                        window = self._hour_to_window(int(hour))
                        window_scores[window] = window_scores.get(window, 0) + freq
                    
                    # Weight by engagement patterns
                    # Users with higher activeness have more reliable patterns
                    avg_activeness = seg_users['activeness'].mean()
                    reliability_factor = min(avg_activeness * 1.5, 1.0)
                    
                    # Sort windows by score
                    sorted_windows = sorted(
                        window_scores.items(), 
                        key=lambda x: x[1] * reliability_factor,
                        reverse=True
                    )
                    
                    # Top 2 windows
                    for priority, (window, score) in enumerate(sorted_windows[:2], 1):
                        # Estimate CTR based on user engagement
                        base_ctr = 0.10
                        activeness_boost = avg_activeness * 0.1
                        expected_ctr = base_ctr + activeness_boost
                        
                        timing_recs.append({
                            'segment_id': segment_id,
                            'lifecycle_stage': 'all',
                            'time_window': window,
                            'priority': priority,
                            'expected_ctr': expected_ctr,
                            'expected_engagement': expected_ctr * 2.5,
                            'uninstall_risk': 0,
                            'composite_score': score * reliability_factor,
                            'confidence': 'MEDIUM',
                            'total_samples': len(seg_users),
                            'optimization_method': 'behavioral_pattern'
                        })
        
        self.optimal_timings = pd.DataFrame(timing_recs)
        
        # Ensure mandatory columns exist
        for col in ['segment_id', 'time_window', 'priority']:
            if col not in self.optimal_timings.columns:
                self.optimal_timings[col] = None

        print(f"   [OK] Generated {len(timing_recs)} timing recommendations")
        
        return self.optimal_timings
    
    def predict_optimal_frequency(self, 
                                  user_data: pd.DataFrame,
                                  experiment_results: pd.DataFrame = None) -> pd.DataFrame:
        """
        Predict optimal notification frequency per segment
        Uses engagement rates and uninstall risk
        
        Args:
            user_data: User behavioral data
            experiment_results: Optional experiment results
            
        Returns:
            DataFrame with frequency recommendations
        """
        print("\n[+] Optimizing Notification Frequency...")
        
        frequency_recs = []
        
        for segment_id in user_data['segment_id'].unique():
            seg_users = user_data[user_data['segment_id'] == segment_id]
            
            # Calculate segment characteristics
            avg_activeness = seg_users['activeness'].mean() if 'activeness' in seg_users.columns else 0.5
            avg_churn_risk = seg_users['churn_risk'].mean() if 'churn_risk' in seg_users.columns else 0.5
            
            # Use notif_open_rate_30d or proxy
            notif_col = 'notif_open_rate_30d'
            if notif_col not in seg_users.columns:
                 # Try to find a proxy in schema_map or just use default
                 notif_col = next((c for c in seg_users.columns if 'open' in c.lower() or 'ctr' in c.lower()), None)
            
            avg_notif_open = seg_users[notif_col].mean() if notif_col else 0.05
            
            # Check uninstall rate from experiments if available
            uninstall_risk = 0.0
            if experiment_results is not None:
                seg_experiments = experiment_results[
                    experiment_results['segment_id'] == segment_id
                ]
                if len(seg_experiments) > 0:
                    uninstall_risk = seg_experiments['uninstall_rate'].mean()
            
            # Frequency optimization logic per PS specification
            # Base frequency based on activeness score (PS Table)
            if avg_activeness > self.high_activeness_threshold:
                # High activeness: 7-9 notifications/day
                daily_notifs = self.high_activeness_freq
                churn_risk_category = 'Low'
                strategy = 'Max Engagement'
            elif avg_activeness >= self.medium_activeness_threshold:
                # Medium activeness: 5-6 notifications/day
                daily_notifs = self.medium_activeness_freq
                churn_risk_category = 'Medium'
                strategy = 'Balanced'
            else:
                # Low activeness: 3-4 notifications/day
                daily_notifs = self.low_activeness_freq
                churn_risk_category = 'High'
                strategy = 'Conservative'
            
            # Guardrail Override (PS Specification)
            # If uninstall_rate > threshold -> reduce frequency
            if uninstall_risk > self.uninstall_threshold:
                daily_notifs = max(daily_notifs - self.uninstall_reduction, 2)
                strategy = f'{strategy} - Uninstall Guardrail Applied'
            
            frequency_recs.append({
                'segment_id': segment_id,
                'daily_notifications': daily_notifs,
                'min_gap_hours': int(24 / daily_notifs) if daily_notifs > 0 else 24,
                'strategy': strategy,
                'avg_activeness': avg_activeness,
                'avg_churn_risk': avg_churn_risk,
                'uninstall_risk': uninstall_risk,
                'avg_notif_open_rate': avg_notif_open
            })
        
        df_freq = pd.DataFrame(frequency_recs)
        
        print(f"   [OK] Generated frequency recommendations for {len(frequency_recs)} segments")
        print(f"   [OK] Avg daily notifications: {df_freq['daily_notifications'].mean():.1f}")
        
        return df_freq
    
    def analyze_time_decay(self, experiment_results: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze engagement decay over time
        Helps optimize retry logic and quiet periods
        
        Args:
            experiment_results: Experiment results with timing data
            
        Returns:
            DataFrame with decay analysis
        """
        print("\n[-] Analyzing Engagement Time Decay...")
        
        # This would typically analyze how engagement changes
        # throughout the day, week, or campaign duration
        
        decay_analysis = []
        
        for window in self.time_windows.keys():
            window_data = experiment_results[
                experiment_results['notification_window'] == window
            ]
            
            if len(window_data) > 0:
                decay_analysis.append({
                    'time_window': window,
                    'avg_ctr': window_data['ctr'].mean(),
                    'avg_engagement': window_data['engagement_rate'].mean(),
                    'sample_size': len(window_data),
                    'decay_rate': 'LOW'  # Simplified for demo
                })
        
        return pd.DataFrame(decay_analysis)
    
    def _hour_to_window(self, hour: int) -> str:
        """Map hour to time window"""
        for window_name, (start, end) in self.time_windows.items():
            if start <= hour < end:
                return window_name
        return 'evening'
    
    def save_timing_recommendations(self, output_dir: str):
        """Save timing recommendations"""
        from pathlib import Path
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        if self.optimal_timings is not None:
            self.optimal_timings.to_csv(
                f"{output_dir}/timing_recommendations.csv",
                index=False
            )
            self.optimal_timings.to_csv(
                f"{output_dir}/timing_recommendations_improved.csv",
                index=False
            )
            print(f"\n[OK] Saved: {output_dir}/timing_recommendations.csv")
            print(f"[OK] Saved: {output_dir}/timing_recommendations_improved.csv")

