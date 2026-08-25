"""
Goal Builder - Defines goals and journeys for each segment
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List


class GoalBuilder:
    """Builds goal hierarchies and user journeys"""
    
    def __init__(self, kb_data: dict = None):
        self.segment_goals = None
        self.kb_data = kb_data or {}
        self.domain = self.kb_data.get('detected_domain', 'generic')
        
        # Extract feature names from KB for domain-aware goals
        fgm = self.kb_data.get('feature_goal_map', {})
        features = fgm.get('features', [])
        self.feature_names = [f.get('feature_name', 'core_feature') for f in features] if features else ['core_feature']
        self.feature_goals = {f.get('feature_name', 'core_feature'): f.get('goal', 'engagement') for f in features} if features else {}
    
    def build_goals(self, segment_profiles: pd.DataFrame) -> pd.DataFrame:
        """
        Build goals for each segment × lifecycle stage combination
        
        Args:
            segment_profiles: DataFrame with segment characteristics
            
        Returns:
            pd.DataFrame: Segment goals mapping
        """
        print("\n[*] Building goals and journeys...")
        
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
        
        print(f"   [OK] Created {len(goals)} goal definitions")
        print(f"   [OK] Covering {len(segment_profiles)} segments x 4 lifecycle stages")
        
        return self.segment_goals
    
    def _build_trial_goals(self, seg_id: int, seg_name: str, segment: pd.Series) -> List[Dict]:
        """Build goals for trial period (D0-D7) — domain-aware via KB features"""
        goals = []
        primary_feature = self.feature_names[0] if self.feature_names else 'core_feature'
        secondary_feature = self.feature_names[1] if len(self.feature_names) > 1 else primary_feature
        
        # D0: Activation
        goals.append({
            'segment_id': seg_id,
            'segment_name': seg_name,
            'lifecycle_stage': 'trial',
            'lifecycle_day': 'D0',
            'primary_goal': 'activation',
            'sub_goals': f'onboarding_complete,first_{primary_feature}_usage',
            'success_metric': 'primary_action_completed >= 1',
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
                'sub_goals': f'daily_{primary_feature}_usage,streak_building',
                'success_metric': f'engagement_streak >= {day+1}',
                'priority': 'high'
            })
        
        # D3-D5: Feature Discovery — pick feature based on segment profile
        for day in [3, 4, 5]:
            feature = secondary_feature if segment.get('avg_gamification_propensity', 0.5) < 0.5 else primary_feature
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
        """Build goals for paid period (D8-D30) — day-on-day progression"""
        goals = []
        primary_feature = self.feature_names[0] if self.feature_names else 'core_feature'
        secondary_feature = self.feature_names[1] if len(self.feature_names) > 1 else primary_feature

        # D8-D10: Early Retention — solidify post-conversion habit
        for day in [8, 9, 10]:
            goals.append({
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'paid',
                'lifecycle_day': f'D{day}',
                'primary_goal': 'retention',
                'sub_goals': f'continued_{primary_feature}_engagement,habit_maintenance',
                'success_metric': f'engagement_streak >= {day - 7}',
                'priority': 'critical'
            })

        # D11-D14: Deepening — explore more features
        for day in [11, 12, 13, 14]:
            goals.append({
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'paid',
                'lifecycle_day': f'D{day}',
                'primary_goal': 'deepening',
                'sub_goals': f'{secondary_feature}_usage,feature_exploration',
                'success_metric': 'features_used >= 2',
                'priority': 'high'
            })

        # D15-D21: Expansion — advanced usage and social hooks
        for day in range(15, 22):
            goals.append({
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'paid',
                'lifecycle_day': f'D{day}',
                'primary_goal': 'expansion',
                'sub_goals': 'advanced_usage,social_sharing',
                'success_metric': 'weekly_active_days >= 5',
                'priority': 'medium'
            })

        # D22-D30: Advocacy — turn power users into promoters
        for day in range(22, 31):
            goals.append({
                'segment_id': seg_id,
                'segment_name': seg_name,
                'lifecycle_stage': 'paid',
                'lifecycle_day': f'D{day}',
                'primary_goal': 'advocacy',
                'sub_goals': 'high_engagement,referral_potential',
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
            'success_metric': 'primary_action_completed >= 1',
            'priority': 'medium'
        }]
    
    def save_goals(self, output_dir: str):
        """Save segment goals to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.segment_goals.to_csv(output_path / 'segment_goals.csv', index=False)
        
        print(f"[OK] Goals saved to {output_dir}/segment_goals.csv")

