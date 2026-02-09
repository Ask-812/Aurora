"""
Timing Optimizer - Optimizes notification timing windows
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import yaml


class TimingOptimizer:
    """Optimizes notification timing for each segment"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.time_windows = self.config['time_windows']
        self.timing_recs = None
    
    def optimize_timing_iteration0(self, user_data: pd.DataFrame, 
                                   segments: pd.DataFrame = None) -> pd.DataFrame:
        """
        Initial timing optimization based on user preferred_hour
        
        Args:
            user_data: User data with preferred_hour and segment_id
            segments: Segment assignments (optional, if not already in user_data)
            
        Returns:
            pd.DataFrame: Timing recommendations
        """
        print("\n⏰ Optimizing notification timing (Iteration 0)...")
        
        # Check if segment_id already in user_data
        if 'segment_id' not in user_data.columns and segments is not None:
            df = user_data.merge(segments[['user_id', 'segment_id', 'segment_name']], 
                                on='user_id', how='left')
        else:
            df = user_data.copy()
        
        timing_recs = []
        
        for seg_id in df['segment_id'].unique():
            seg_data = df[df['segment_id'] == seg_id]
            seg_name = seg_data['segment_name'].iloc[0]
            
            # Calculate preferred hours distribution
            if 'preferred_hour' in seg_data.columns:
                preferred_hours = seg_data['preferred_hour'].dropna()
                
                if len(preferred_hours) > 0:
                    # Find most common hours
                    hour_counts = preferred_hours.value_counts()
                    
                    # Map to windows and rank
                    window_scores = {}
                    for hour, count in hour_counts.items():
                        window = self._hour_to_window(int(hour))
                        window_scores[window] = window_scores.get(window, 0) + count
                    
                    # Sort by score
                    sorted_windows = sorted(window_scores.items(), 
                                          key=lambda x: x[1], reverse=True)
                    
                    # Take top 2 windows
                    for priority, (window, score) in enumerate(sorted_windows[:2], 1):
                        timing_recs.append({
                            'segment_id': seg_id,
                            'segment_name': seg_name,
                            'lifecycle_stage': 'all',
                            'time_window': window,
                            'priority': priority,
                            'expected_ctr': 0.12 if priority == 1 else 0.08,  # Initial estimates
                            'rationale': f"Based on {int(score)} users preferring this window"
                        })
                else:
                    # Default windows if no data
                    timing_recs.extend(self._default_windows(seg_id, seg_name))
            else:
                # Default windows if column missing
                timing_recs.extend(self._default_windows(seg_id, seg_name))
        
        self.timing_recs = pd.DataFrame(timing_recs)
        
        print(f"   ✓ Generated {len(timing_recs)} timing recommendations")
        print(f"   ✓ Covering {df['segment_id'].nunique()} segments")
        
        return self.timing_recs
    
    def optimize_timing_iteration1(self, experiment_results: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize timing based on experiment results
        
        Args:
            experiment_results: Results with CTR by segment × window
            
        Returns:
            pd.DataFrame: Updated timing recommendations
        """
        print("\n⏰ Optimizing notification timing (Iteration 1 - Learning)...")
        
        # Analyze performance by segment × window
        window_performance = experiment_results.groupby(
            ['segment_id', 'notification_window']
        ).agg({
            'ctr': 'mean',
            'engagement_rate': 'mean',
            'total_sends': 'sum'
        }).reset_index()
        
        # Filter for statistical significance
        window_performance = window_performance[
            window_performance['total_sends'] >= 100
        ]
        
        timing_recs = []
        
        for seg_id in window_performance['segment_id'].unique():
            seg_data = window_performance[window_performance['segment_id'] == seg_id]
            
            # Sort by CTR
            seg_data = seg_data.sort_values('ctr', ascending=False)
            
            # Take top 2 windows
            for priority, (_, row) in enumerate(seg_data.head(2).iterrows(), 1):
                timing_recs.append({
                    'segment_id': row['segment_id'],
                    'segment_name': f"Segment {row['segment_id']}",
                    'lifecycle_stage': 'all',
                    'time_window': row['notification_window'],
                    'priority': priority,
                    'expected_ctr': row['ctr'],
                    'rationale': f"Learned from {int(row['total_sends'])} sends with {row['ctr']:.1%} CTR"
                })
        
        self.timing_recs = pd.DataFrame(timing_recs)
        
        print(f"   ✓ Updated {len(timing_recs)} timing recommendations based on data")
        
        return self.timing_recs
    
    def _hour_to_window(self, hour: int) -> str:
        """Map hour to time window"""
        for window_name, (start, end) in self.time_windows.items():
            if start <= hour < end:
                return window_name
        return 'evening'  # Default
    
    def _default_windows(self, seg_id: int, seg_name: str) -> List[Dict]:
        """Generate default timing windows"""
        return [
            {
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'all',
                'time_window': 'evening',
                'priority': 1,
                'expected_ctr': 0.12,
                'rationale': 'Default: Evening is typically high engagement'
            },
            {
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'all',
                'time_window': 'early_morning',
                'priority': 2,
                'expected_ctr': 0.08,
                'rationale': 'Default: Morning commute time'
            }
        ]
    
    def save_timing(self, output_dir: str):
        """Save timing recommendations to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.timing_recs.to_csv(output_path / 'timing_recommendations.csv', index=False)
        
        print(f"✓ Timing recommendations saved to {output_dir}/timing_recommendations.csv")
