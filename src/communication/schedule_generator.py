"""
Schedule Generator - Creates user-wise notification schedules
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import random
import yaml


class ScheduleGenerator:
    """Generates user-wise notification schedules"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        random.seed(self.config.get('segmentation', {}).get('random_state', 42))
        self.schedules = None
    
    def generate_schedules(self, user_data: pd.DataFrame, segments: pd.DataFrame = None,
                          templates: pd.DataFrame = None, timing_recs: pd.DataFrame = None,
                          segment_goals: pd.DataFrame = None, frequency_recs: pd.DataFrame = None,
                          max_users: int = 100) -> pd.DataFrame:
        """
        Generate notification schedules for users
        
        Args:
            user_data: User data with behavioral features
            segments: Segment assignments (optional if already in user_data)
            templates: Message templates
            timing_recs: Timing recommendations
            segment_goals: Goal definitions
            max_users: Maximum users to generate schedules for (for demo)
            
        Returns:
            pd.DataFrame: User notification schedules
        """
        print(f"\n[Schedule] Generating notification schedules for {min(max_users, len(user_data))} users...")
        
        # Check if segment info already in user_data
        if 'segment_id' not in user_data.columns and segments is not None:
            df = user_data.merge(segments[['user_id', 'segment_id', 'segment_name', 'activeness', 'churn_risk']], 
                                on='user_id', how='left')
        else:
            df = user_data.copy()
        
        # Limit to max_users for demo
        df = df.head(max_users)
        
        schedules = []
        
        for _, user in df.iterrows():
            # Calculate frequency
            frequency = self._calculate_frequency(user, frequency_recs)
            
            # Generate schedule for next 7 days
            for day in range(7):
                user_signup_days = user.get('days_since_signup')
                if user_signup_days is None:
                     # Heuristic: look for other date-related columns or just use 0
                     user_signup_days = 0
                
                lifecycle_day = f"D{int(user_signup_days) + day}"
                
                # Get goal for this day
                goal = self._get_goal_for_day(user, day, segment_goals)
                
                # Get templates for this segment/lifecycle/goal
                # Note: Templates are now bilingual (same row has both en/hi columns)
                available_templates = templates[
                    (templates['segment_id'] == user['segment_id']) &
                    (templates['lifecycle_stage'] == user['lifecycle_stage']) &
                    (templates['goal'] == goal)
                ]
                
                if available_templates.empty:
                    # Fallback to any templates for this segment
                    available_templates = templates[
                        templates['segment_id'] == user['segment_id']
                    ]
                
                if available_templates.empty:
                    continue
                
                # Select templates based on frequency (up to 9 per PS)
                num_notifs = min(frequency, 9)
                need_replace = num_notifs > len(available_templates)
                selected = available_templates.sample(n=num_notifs, replace=need_replace)
                
                # Get timing windows
                timing = timing_recs[timing_recs['segment_id'] == user['segment_id']]
                
                # Build schedule row
                schedule_row = {
                    'user_id': user['user_id'],
                    'segment_id': user['segment_id'],
                    'segment_name': user.get('segment_name', f"Segment {user['segment_id']}"),
                    'lifecycle_stage': user['lifecycle_stage'],
                    'lifecycle_day': lifecycle_day,
                    'day_offset': day,
                    'goal': goal,
                    'journey_stage': self._get_journey_stage(user['lifecycle_stage'], day),
                    'daily_frequency': frequency
                }
                
                # Add notifications
                for i, (_, template) in enumerate(selected.iterrows()):
                    # Select time window
                    if not timing.empty:
                        window_row = timing.iloc[i % len(timing)]
                        window = window_row['time_window']
                    else:
                        window = 'evening'
                    
                    # Generate time within window
                    time = self._generate_time(window)
                    
                    schedule_row[f'notif_{i+1}_template_id'] = template['template_id']
                    schedule_row[f'notif_{i+1}_time'] = time
                    schedule_row[f'notif_{i+1}_channel'] = 'push'
                
                schedules.append(schedule_row)
        
        self.schedules = pd.DataFrame(schedules)
        
        print(f"   [OK] Generated {len(schedules)} schedule entries")
        print(f"   [OK] Covering {df['user_id'].nunique()} users x 7 days")
        
        return self.schedules
    
    def _calculate_frequency(self, user: pd.Series, frequency_recs: pd.DataFrame = None) -> int:
        """Calculate notification frequency for user"""
        # Prefer segment-level frequency recommendations when provided
        if frequency_recs is not None and 'segment_id' in user:
            match = frequency_recs[frequency_recs['segment_id'] == user['segment_id']]
            if not match.empty:
                return int(match['daily_notifications'].iloc[0])
        
        # Fallback: PS table based on activeness using config thresholds
        freq_config = self.config.get('frequency', {})
        high_thresh = freq_config.get('high_activeness_threshold', 0.7)
        med_thresh = freq_config.get('medium_activeness_threshold', 0.4)
        high_freq = freq_config.get('high_activeness_freq', 8)
        med_freq = freq_config.get('medium_activeness_freq', 6)
        low_freq = freq_config.get('low_activeness_freq', 4)

        activeness = user.get('activeness', 0.5)
        if activeness > high_thresh:
            return high_freq
        if activeness >= med_thresh:
            return med_freq
        return low_freq
    
    def _get_goal_for_day(self, user: pd.Series, day: int, 
                         segment_goals: pd.DataFrame) -> str:
        """Get goal for specific day"""
        lifecycle = user.get('lifecycle_stage', 'trial')
        seg_id = user['segment_id']
        
        # Get goals for this segment and lifecycle
        goals = segment_goals[
            (segment_goals['segment_id'] == seg_id) &
            (segment_goals['lifecycle_stage'] == lifecycle)
        ]
        
        if goals.empty:
            return 'activation'
        
        # Map day to goal
        if lifecycle == 'trial':
            if day == 0:
                return 'activation'
            elif day <= 2:
                return 'habit_formation'
            elif day <= 5:
                return 'feature_discovery'
            else:
                return 'conversion_readiness'
        elif lifecycle == 'paid':
            return 'retention'
        elif lifecycle == 'churned':
            return 're_engagement'
        else:
            return 'activation'
    
    def _generate_time(self, window: str) -> str:
        """Generate random time within window"""
        window_ranges = {
            'early_morning': (6, 9),
            'mid_morning': (9, 12),
            'afternoon': (12, 15),
            'late_afternoon': (15, 18),
            'evening': (18, 21),
            'night': (21, 24)
        }
        
        start, end = window_ranges.get(window, (18, 21))
        hour = random.randint(start, end - 1)
        minute = random.choice([0, 15, 30, 45])
        
        return f"{hour:02d}:{minute:02d}"

    def _get_journey_stage(self, lifecycle: str, day: int) -> str:
        """Map lifecycle + day to a numbered journey stage."""
        if lifecycle == 'trial':
            stages = [
                (0, '1_activation'),
                (2, '2_habit_formation'),
                (5, '3_feature_discovery'),
                (7, '4_conversion_readiness'),
            ]
        elif lifecycle == 'paid':
            stages = [
                (0, '5_early_retention'),
                (7, '6_deep_engagement'),
                (14, '7_loyalty_building'),
                (21, '8_advocacy'),
            ]
        elif lifecycle == 'churned':
            stages = [(0, '9_win_back'), (3, '10_re_activation')]
        else:  # inactive
            stages = [(0, '11_gentle_nudge'), (3, '12_last_chance')]
        for threshold, name in reversed(stages):
            if day >= threshold:
                return name
        return stages[0][1]
    
    def save_schedules(self, output_dir: str):
        """Save schedules to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.schedules.to_csv(output_path / 'user_notification_schedule.csv', index=False)
        
        print(f"[OK] Schedules saved to {output_dir}/user_notification_schedule.csv")

