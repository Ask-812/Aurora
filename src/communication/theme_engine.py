"""
Theme Engine - Maps Octalysis themes to segments
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List


class ThemeEngine:
    """Maps behavioral themes to user segments"""
    
    def __init__(self, tone_hook_matrix: Dict):
        self.tone_hook_matrix = tone_hook_matrix
        self.themes = None
    
    def generate_themes(self, segment_profiles: pd.DataFrame) -> pd.DataFrame:
        """
        Generate communication themes for each segment × lifecycle combination
        
        Args:
            segment_profiles: DataFrame with segment characteristics
            
        Returns:
            pd.DataFrame: Theme mappings
        """
        print("\n[Theme] Generating communication themes...")
        
        themes = []
        lifecycle_stages = ['trial', 'paid', 'churned', 'inactive']
        
        for _, segment in segment_profiles.iterrows():
            seg_id = segment['segment_id']
            seg_name = segment['segment_name']
            
            for lifecycle in lifecycle_stages:
                primary, secondary = self._select_themes(segment, lifecycle)
                rationale = self._generate_rationale(segment, primary, secondary)
                
                themes.append({
                    'segment_id': seg_id,
                    'segment_name': seg_name,
                    'lifecycle_stage': lifecycle,
                    'primary_theme': primary,
                    'secondary_theme': secondary,
                    'theme_rationale': rationale
                })
        
        self.themes = pd.DataFrame(themes)
        
        print(f"   [OK] Generated {len(themes)} theme mappings")
        print(f"   [OK] Covering {len(segment_profiles)} segments × {len(lifecycle_stages)} lifecycle stages")
        
        return self.themes
    
    def _select_themes(self, segment: pd.Series, lifecycle: str) -> tuple:
        """Select primary and secondary themes based on segment characteristics"""
        
        # Extract segment characteristics
        activeness = segment['avg_activeness']
        gamification = segment['avg_gamification_propensity']
        social = segment['avg_social_propensity']
        churn_risk = segment['avg_churn_risk']
        
        # Theme selection logic
        if churn_risk > 0.7:
            # High churn risk → Loss avoidance
            primary = 'loss_avoidance'
            secondary = 'scarcity' if lifecycle == 'trial' else 'social_influence'
        
        elif gamification > 0.7:
            # High gamification → Accomplishment
            primary = 'accomplishment'
            secondary = 'ownership' if lifecycle == 'paid' else 'epic_meaning'
        
        elif social > 0.7:
            # High social → Social influence
            primary = 'social_influence'
            secondary = 'accomplishment'
        
        elif activeness < 0.3:
            # Low activeness → Unpredictability (discovery)
            primary = 'unpredictability'
            secondary = 'empowerment'
        
        elif activeness > 0.6 and gamification < 0.4:
            # Active but not gamified → Empowerment
            primary = 'empowerment'
            secondary = 'accomplishment'
        
        else:
            # Balanced users
            if lifecycle == 'trial':
                primary = 'unpredictability'
                secondary = 'accomplishment'
            elif lifecycle == 'paid':
                primary = 'accomplishment'
                secondary = 'ownership'
            elif lifecycle == 'churned':
                primary = 'loss_avoidance'
                secondary = 'unpredictability'
            else:  # inactive
                primary = 'unpredictability'
                secondary = 'epic_meaning'
        
        return primary, secondary
    
    def _generate_rationale(self, segment: pd.Series, primary: str, secondary: str) -> str:
        """Generate explanation for theme selection"""
        
        seg_name = segment['segment_name']
        activeness = segment['avg_activeness']
        gamification = segment['avg_gamification_propensity']
        social = segment['avg_social_propensity']
        churn_risk = segment['avg_churn_risk']
        
        rationale_parts = []
        
        # Primary theme rationale
        if primary == 'accomplishment':
            rationale_parts.append(f"High gamification propensity ({gamification:.2f}) indicates strong response to achievement")
        elif primary == 'social_influence':
            rationale_parts.append(f"High social propensity ({social:.2f}) indicates competitive motivation")
        elif primary == 'loss_avoidance':
            rationale_parts.append(f"High churn risk ({churn_risk:.2f}) requires urgency and retention focus")
        elif primary == 'unpredictability':
            rationale_parts.append(f"Low activeness ({activeness:.2f}) needs discovery and exploration")
        elif primary == 'empowerment':
            rationale_parts.append(f"Active ({activeness:.2f}) but low gamification ({gamification:.2f}) prefers autonomy")
        
        # Secondary theme rationale
        rationale_parts.append(f"Secondary theme '{secondary}' provides complementary motivation")
        
        return "; ".join(rationale_parts)
    
    def save_themes(self, output_dir: str):
        """Save themes to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.themes.to_csv(output_path / 'communication_themes.csv', index=False)
        
        print(f"[OK] Themes saved to {output_dir}/communication_themes.csv")

