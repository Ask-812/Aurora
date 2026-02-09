"""
Goal Builder - Defines goals and journeys for each segment
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List


class GoalBuilder:
    """Builds goal hierarchies and user journeys"""
    
    def __init__(self):
        self.segment_goals = None
    
    def build_goals(self, segment_profiles: pd.DataFrame) -> pd.DataFrame:
        """
        Build goals for each segment × lifecycle stage combination
        
        Args:
            segment_profiles: DataFrame with segment characteristics
            
        Returns:
            pd.DataFrame: Segment goals mapping
        """
        print("\n🎯 Building goals and journeys...")
        
        goals = []
        
        for _, segment in segment_profiles.iterrows():
            seg_id = segment['segment_id']
            seg_name = segment['segment_name']
            
            # Trial goals (D0-D7)
            goals.extend(self._build_trial_goals(seg_id, seg_name, segment))
            
            # Paid goals (D8-D30)
            goals.extend(self._build_paid_goals(seg_id, seg_name, segment))
            
            # Churned goals
            goals.extend(self._build_churned_goals(seg_id, seg_name, segment))
            
            # Inactive goals
            goals.extend(self._build_inactive_goals(seg_id, seg_name, segment))
        
        self.segment_goals = pd.DataFrame(goals)
        
        print(f"   ✓ Created {len(goals)} goal definitions")
        print(f"   ✓ Covering {len(segment_profiles)} segments × 4 lifecycle stages")
        
        return self.segment_goals
    
    def _build_trial_goals(self, seg_id: int, seg_name: str, segment: pd.Series) -> List[Dict]:
        """Build goals for trial period (D0-D7)"""
        goals = []
        
        # D0: Activation
        goals.append({
            'segment_id': seg_id,
            'segment_name': seg_name,
            'lifecycle_stage': 'trial',
            'lifecycle_day': 'D0',
            'primary_goal': 'activation',
            'sub_goals': 'onboarding_complete,first_exercise',
            'success_metric': 'exercises_completed >= 1',
            'priority': 'critical'
        })
        
        # D1-D2: Habit Formation
        for day in [1, 2]:
            goals.append({
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'trial',
                'lifecycle_day': f'D{day}',
                'primary_goal': 'habit_formation',
                'sub_goals': 'daily_exercise,streak_building',
                'success_metric': f'streak_current >= {day+1}',
                'priority': 'high'
            })
        
        # D3-D5: Feature Discovery
        for day in [3, 4, 5]:
            feature = 'ai_tutor' if segment['avg_gamification_propensity'] < 0.5 else 'coins_rewards'
            goals.append({
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'trial',
                'lifecycle_day': f'D{day}',
                'primary_goal': 'feature_discovery',
                'sub_goals': f'{feature}_usage,exploration',
                'success_metric': f'feature_{feature}_used = True',
                'priority': 'medium'
            })
        
        # D6-D7: Conversion Readiness
        for day in [6, 7]:
            goals.append({
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'trial',
                'lifecycle_day': f'D{day}',
                'primary_goal': 'conversion_readiness',
                'sub_goals': 'consistent_usage,value_realization',
                'success_metric': 'sessions_last_7d >= 5',
                'priority': 'critical'
            })
        
        return goals
    
    def _build_paid_goals(self, seg_id: int, seg_name: str, segment: pd.Series) -> List[Dict]:
        """Build goals for paid period (D8-D30)"""
        goals = []
        
        # D8-D14: Retention
        goals.append({
            'segment_id': seg_id,
            'segment_name': seg_name,
            'lifecycle_stage': 'paid',
            'lifecycle_day': 'D8-D14',
            'primary_goal': 'retention',
            'sub_goals': 'continued_engagement,habit_maintenance',
            'success_metric': 'exercises_completed >= 1',
            'priority': 'critical'
        })
        
        # D15-D21: Expansion
        goals.append({
            'segment_id': seg_id,
            'segment_name': seg_name,
            'lifecycle_stage': 'paid',
            'lifecycle_day': 'D15-D21',
            'primary_goal': 'expansion',
            'sub_goals': 'feature_exploration,advanced_usage',
            'success_metric': 'features_used >= 2',
            'priority': 'medium'
        })
        
        # D22-D30: Advocacy
        goals.append({
            'segment_id': seg_id,
            'segment_name': seg_name,
            'lifecycle_stage': 'paid',
            'lifecycle_day': 'D22-D30',
            'primary_goal': 'advocacy',
            'sub_goals': 'high_engagement,potential_referral',
            'success_metric': 'sessions_last_7d >= 7',
            'priority': 'low'
        })
        
        return goals
    
    def _build_churned_goals(self, seg_id: int, seg_name: str, segment: pd.Series) -> List[Dict]:
        """Build goals for churned users"""
        return [{
            'segment_id': seg_id,
            'segment_name': seg_name,
            'lifecycle_stage': 'churned',
            'lifecycle_day': 'any',
            'primary_goal': 're_engagement',
            'sub_goals': 'win_back,value_reminder',
            'success_metric': 'sessions_last_7d >= 1',
            'priority': 'high'
        }]
    
    def _build_inactive_goals(self, seg_id: int, seg_name: str, segment: pd.Series) -> List[Dict]:
        """Build goals for inactive users"""
        return [{
            'segment_id': seg_id,
            'segment_name': seg_name,
            'lifecycle_stage': 'inactive',
            'lifecycle_day': 'any',
            'primary_goal': 'activation',
            'sub_goals': 'first_engagement,value_discovery',
            'success_metric': 'exercises_completed >= 1',
            'priority': 'medium'
        }]
    
    def save_goals(self, output_dir: str):
        """Save segment goals to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.segment_goals.to_csv(output_path / 'segment_goals.csv', index=False)
        
        print(f"✓ Goals saved to {output_dir}/segment_goals.csv")
