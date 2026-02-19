"""
Template Generator - Creates personalized, bilingual message templates
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import random


class TemplateGenerator:
    """Generates personalized message templates"""
    
    def __init__(self, knowledge_bank: Dict, themes: pd.DataFrame):
        self.kb = knowledge_bank
        self.themes = themes
        self.templates = None
        
        # Hindi translations for common terms
        self.translations = {
            'exercise': 'अभ्यास',
            'streak': 'स्ट्रीक',
            'coins': 'सिक्के',
            'complete': 'पूरा करें',
            'today': 'आज',
            'practice': 'अभ्यास करें',
            'learn': 'सीखें',
            'speaking': 'बोलना',
            'English': 'अंग्रेजी',
            'day': 'दिन',
            'keep going': 'जारी रखें',
            'don\'t lose': 'मत खोएं',
            'join': 'शामिल हों',
            'unlock': 'अनलॉक करें',
            'your': 'आपका',
            'you': 'आप'
        }
    
    def generate_templates(self, segment_goals: pd.DataFrame) -> pd.DataFrame:
        """
        Generate 5 message templates for each segment × lifecycle × goal × theme
        
        Args:
            segment_goals: DataFrame with segment goals
            
        Returns:
            pd.DataFrame: Message templates
        """
        print("\n[Edit]  Generating message templates...")
        
        templates = []
        template_id = 1
        
        # Group by segment, lifecycle, goal
        for (seg_id, lifecycle, goal), group in segment_goals.groupby(
            ['segment_id', 'lifecycle_stage', 'primary_goal']
        ):
            seg_name = group['segment_name'].iloc[0]
            
            # Get themes for this segment × lifecycle
            theme_row = self.themes[
                (self.themes['segment_id'] == seg_id) &
                (self.themes['lifecycle_stage'] == lifecycle)
            ]
            
            if theme_row.empty:
                continue
            
            primary_theme = theme_row['primary_theme'].iloc[0]
            secondary_theme = None
            if 'secondary_theme' in theme_row.columns:
                secondary_theme = theme_row['secondary_theme'].iloc[0]

            theme_values = [primary_theme]
            if pd.notna(secondary_theme) and secondary_theme != primary_theme:
                theme_values.append(secondary_theme)

            # Generate 5 variants per theme
            for theme in theme_values:
                for variant in range(5):
                    # Generate English template
                    content_en = self._generate_content(
                        seg_name, lifecycle, goal, theme, variant
                    )
                    
                    # Translate to Hindi
                    content_hi = self._translate_to_hindi(content_en)
                    
                    # Determine tone
                    tone = self._select_tone(lifecycle, theme)
                    
                    # Determine feature reference
                    feature = self._select_feature(goal, theme)
                    
                    # English template
                    templates.append({
                        'template_id': f'T{template_id:04d}',
                        'segment_id': seg_id,
                        'segment_name': seg_name,
                        'lifecycle_stage': lifecycle,
                        'goal': goal,
                        'theme': theme,
                        'language': 'en',
                        'content': content_en,
                        'tone': tone,
                        'hook': theme,
                        'feature_reference': feature
                    })
                    
                    # Hindi template
                    templates.append({
                        'template_id': f'T{template_id:04d}_hi',
                        'segment_id': seg_id,
                        'segment_name': seg_name,
                        'lifecycle_stage': lifecycle,
                        'goal': goal,
                        'theme': theme,
                        'language': 'hi',
                        'content': content_hi,
                        'tone': tone,
                        'hook': theme,
                        'feature_reference': feature
                    })
                    
                    template_id += 1
        
        self.templates = pd.DataFrame(templates)
        
        print(f"   [OK] Generated {len(templates)} templates ({len(templates)//2} English + {len(templates)//2} Hindi)")
        print(f"   [OK] Covering {template_id-1} unique message variants")
        
        return self.templates
    
    def _generate_content(self, seg_name: str, lifecycle: str, goal: str, 
                         theme: str, variant: int) -> str:
        """Generate template content based on parameters"""
        
        # Template patterns by theme
        patterns = {
            'accomplishment': [
                "You've completed {exercises_completed_7d} exercises this week—keep going!",
                "Day {streak_current} of your streak! Complete today's exercise.",
                "{exercises_completed_7d} exercises done—you're making progress!",
                "You've earned {coins_balance} coins! Complete another exercise.",
                "Your {streak_current}-day streak is impressive—maintain it today!"
            ],
            'loss_avoidance': [
                "Your streak will break in {hours_left} hours—complete one exercise!",
                "Don't lose your {streak_current}-day streak! Practice now.",
                "Your progress is at risk—complete today's exercise.",
                "Only {hours_left} hours to maintain your streak!",
                "Don't let your {coins_balance} coins go to waste—practice today!"
            ],
            'social_influence': [
                "{peer_name} from {location} is ahead—can you catch up?",
                "Join {active_users} users practicing today!",
                "{peer_name} completed {peer_exercises} exercises—beat that!",
                "You're #{rank} on the leaderboard—climb higher!",
                "{active_users} learners are online now—join them!"
            ],
            'unpredictability': [
                "Discover a new speaking exercise today!",
                "Try the AI tutor—see how it helps!",
                "Unlock a surprise reward after your next exercise!",
                "What's your speaking score today? Find out!",
                "Explore new practice scenarios—start now!"
            ],
            'empowerment': [
                "Choose your practice topic today!",
                "Practice at your own pace—start when ready.",
                "Customize your learning path—explore options.",
                "You control your progress—practice now!",
                "Pick any exercise that interests you today!"
            ],
            'ownership': [
                "Your {coins_balance} coins—use them wisely!",
                "You've built a {streak_current}-day streak—it's yours!",
                "Your progress, your achievement—keep building!",
                "You own {coins_balance} coins—earn more today!",
                "Your learning journey—make it count today!"
            ],
            'epic_meaning': [
                "Join 1M+ Indians becoming confident speakers!",
                "Be part of the English learning revolution!",
                "Transform your career—practice speaking today!",
                "Join thousands improving their English daily!",
                "Your journey to fluency starts today!"
            ],
            'scarcity': [
                "Only 3 hours left to complete today's goal!",
                "Limited time offer—practice now!",
                "Today's special exercise expires soon!",
                "Last chance to maintain your streak today!",
                "Don't miss today's practice opportunity!"
            ]
        }
        
        # Get pattern for theme
        theme_patterns = patterns.get(theme, patterns['accomplishment'])
        pattern = theme_patterns[variant % len(theme_patterns)]
        
        return pattern
    
    def _translate_to_hindi(self, english_text: str) -> str:
        """Simple translation to Hindi"""
        hindi_text = english_text
        
        # Replace common terms
        for en, hi in self.translations.items():
            hindi_text = hindi_text.replace(en, hi)
        
        # If no translation happened, provide a generic Hindi message
        if hindi_text == english_text:
            hindi_text = f"आज {english_text}"
        
        return hindi_text
    
    def _select_tone(self, lifecycle: str, theme: str) -> str:
        """Select appropriate tone"""
        tone_map = {
            'trial': {
                'accomplishment': 'encouraging',
                'loss_avoidance': 'urgent',
                'social_influence': 'motivational',
                'unpredictability': 'inviting',
                'empowerment': 'supportive',
                'ownership': 'celebratory',
                'epic_meaning': 'aspirational',
                'scarcity': 'urgent'
            },
            'paid': {
                'accomplishment': 'celebratory',
                'loss_avoidance': 'friendly',
                'social_influence': 'motivational',
                'unpredictability': 'inviting',
                'empowerment': 'supportive',
                'ownership': 'celebratory',
                'epic_meaning': 'aspirational',
                'scarcity': 'friendly'
            },
            'churned': {
                'accomplishment': 'encouraging',
                'loss_avoidance': 'urgent',
                'social_influence': 'motivational',
                'unpredictability': 'curious',
                'empowerment': 'supportive',
                'ownership': 'friendly',
                'epic_meaning': 'aspirational',
                'scarcity': 'urgent'
            },
            'inactive': {
                'accomplishment': 'encouraging',
                'loss_avoidance': 'friendly',
                'social_influence': 'inviting',
                'unpredictability': 'curious',
                'empowerment': 'supportive',
                'ownership': 'friendly',
                'epic_meaning': 'aspirational',
                'scarcity': 'friendly'
            }
        }
        
        return tone_map.get(lifecycle, {}).get(theme, 'friendly')
    
    def _select_feature(self, goal: str, theme: str) -> str:
        """Select relevant feature reference"""
        feature_map = {
            'activation': 'exercises',
            'habit_formation': 'streak',
            'feature_discovery': 'ai_tutor',
            'conversion_readiness': 'exercises',
            'retention': 'exercises',
            'expansion': 'leaderboard',
            'advocacy': 'exercises',
            're_engagement': 'exercises'
        }
        
        return feature_map.get(goal, 'exercises')
    
    def save_templates(self, output_dir: str):
        """Save templates to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.templates.to_csv(output_path / 'message_templates.csv', index=False)
        
        print(f"[OK] Templates saved to {output_dir}/message_templates.csv")

