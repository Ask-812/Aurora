"""
Template Generator - Creates personalized, bilingual message templates

Per PS requirement: Each template row has BOTH languages in separate columns:
- message_title_en, message_title_hi
- message_body_en, message_body_hi  
- cta_text_en, cta_text_hi

Hindi columns use Hinglish (natural for SpeakX's Tier 2/3 India audience).
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import random


class TemplateGenerator:
    """Generates personalized message templates with bilingual content"""
    
    def __init__(self, knowledge_bank: Dict, themes: pd.DataFrame):
        self.kb = knowledge_bank
        self.themes = themes
        self.templates = None
    
    def generate_templates(self, segment_goals: pd.DataFrame) -> pd.DataFrame:
        """
        Generate 5 message templates for each segment × lifecycle × goal × theme
        
        Each template row contains BOTH English and Hindi (Hinglish) in separate columns.
        
        Args:
            segment_goals: DataFrame with segment goals
            
        Returns:
            pd.DataFrame: Message templates with bilingual columns
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
                    # Generate bilingual content (title, body, CTA)
                    title_en, title_hi = self._generate_title(theme, variant)
                    body_en, body_hi = self._generate_body(seg_name, lifecycle, goal, theme, variant)
                    cta_en, cta_hi = self._generate_cta(goal, theme, variant)
                    
                    # Determine tone
                    tone = self._select_tone(lifecycle, theme)
                    
                    # Determine feature reference
                    feature = self._select_feature(goal, theme)
                    
                    # Single row with both languages
                    templates.append({
                        'template_id': f'TPL_{template_id:04d}',
                        'segment_id': seg_id,
                        'segment_name': seg_name,
                        'lifecycle_stage': lifecycle,
                        'goal': goal,
                        'theme': theme,
                        'variant': variant + 1,
                        'message_title_en': title_en,
                        'message_title_hi': title_hi,
                        'message_body_en': body_en,
                        'message_body_hi': body_hi,
                        'cta_text_en': cta_en,
                        'cta_text_hi': cta_hi,
                        'tone': tone,
                        'hook': theme,
                        'feature_reference': feature
                    })
                    
                    template_id += 1
        
        self.templates = pd.DataFrame(templates)
        
        print(f"   [OK] Generated {len(templates)} bilingual templates")
        print(f"   [OK] Each template has English + Hinglish columns")
        
        return self.templates
    
    def _generate_title(self, theme: str, variant: int) -> Tuple[str, str]:
        """Generate notification title in English and Hinglish"""
        
        titles = {
            'accomplishment': [
                ("🎯 Keep the momentum!", "🎯 Momentum banaye rakho!"),
                ("🏆 You're doing great!", "🏆 Bahut badiya chal raha hai!"),
                ("⭐ Keep up the progress!", "⭐ Progress jaari rakho!"),
                ("🔥 You're on fire!", "🔥 Aag laga di tumne!"),
                ("💪 Keep crushing it!", "💪 Aise hi karo!")
            ],
            'loss_avoidance': [
                ("⚠️ Don't lose your streak!", "⚠️ Apna streak mat todo!"),
                ("🔔 Streak at risk!", "🔔 Streak khatrey mein hai!"),
                ("⏰ Time is running out!", "⏰ Time khatam ho raha hai!"),
                ("❗ Your progress is at risk!", "❗ Progress khatrey mein!"),
                ("🚨 Act now!", "🚨 Abhi action lo!")
            ],
            'social_influence': [
                ("👥 See what others are doing!", "👥 Dekho baaki kya kar rahe!"),
                ("🏅 Leaderboard update!", "🏅 Leaderboard update!"),
                ("📊 You vs others", "📊 Tum vs Baaki log"),
                ("🌟 Join top learners!", "🌟 Top learners mein shamil ho!"),
                ("👋 Your friends are practicing!", "👋 Dost practice kar rahe!")
            ],
            'unpredictability': [
                ("🎁 Surprise waiting!", "🎁 Surprise wait kar raha!"),
                ("✨ Something new for you!", "✨ Tumhare liye kuch naya!"),
                ("🎲 Mystery reward!", "🎲 Mystery reward!"),
                ("🔓 Unlock something special!", "🔓 Special cheez unlock karo!"),
                ("🎉 Discover today's bonus!", "🎉 Aaj ka bonus dekho!")
            ],
            'empowerment': [
                ("🎮 Your choice, your pace!", "🎮 Tumhari choice, tumhari speed!"),
                ("⚡ Take control!", "⚡ Control lo!"),
                ("🛠️ Customize your learning!", "🛠️ Apna learning customize karo!"),
                ("🎯 Practice what you want!", "🎯 Jo chaaho practice karo!"),
                ("💡 Learn your way!", "💡 Apne tarike se seekho!")
            ],
            'ownership': [
                ("👑 Your achievements!", "👑 Tumhari achievements!"),
                ("💎 Your coins are waiting!", "💎 Tumhare coins wait kar rahe!"),
                ("🏠 Check your progress!", "🏠 Apna progress dekho!"),
                ("📈 Your stats update!", "📈 Tumhare stats ka update!"),
                ("🎖️ Your badges!", "🎖️ Tumhare badges!")
            ],
            'epic_meaning': [
                ("🚀 Join the movement!", "🚀 Movement mein shamil ho!"),
                ("🌍 Be part of something big!", "🌍 Kuch bada karo!"),
                ("💫 Transform your future!", "💫 Future transform karo!"),
                ("🎓 Your journey to fluency!", "🎓 Fluency ka safar!"),
                ("✨ Make a difference!", "✨ Fark daalo!")
            ],
            'scarcity': [
                ("⏳ Limited time!", "⏳ Limited time!"),
                ("🔥 Offer ends soon!", "🔥 Offer jaldi khatam!"),
                ("⚡ Last chance today!", "⚡ Aaj ka last chance!"),
                ("🎯 Don't miss out!", "🎯 Miss mat karo!"),
                ("⏰ Today only!", "⏰ Sirf aaj!")
            ]
        }
        
        theme_titles = titles.get(theme, titles['accomplishment'])
        return theme_titles[variant % len(theme_titles)]
    
    def _generate_body(self, seg_name: str, lifecycle: str, goal: str, 
                       theme: str, variant: int) -> Tuple[str, str]:
        """Generate notification body in English and Hinglish"""
        
        bodies = {
            'accomplishment': [
                ("You've completed {exercises_completed_7d} exercises this week. Just 3 more for your badge!",
                 "Is hafte {exercises_completed_7d} exercises complete! Sirf 3 aur karo badge ke liye!"),
                ("Day {streak_current} of your streak! Complete today's exercise to keep going.",
                 "Streak ka din {streak_current}! Aaj ka exercise karo streak continue karne ke liye."),
                ("{exercises_completed_7d} exercises done—you're making amazing progress!",
                 "{exercises_completed_7d} exercises ho gaye—amazing progress ho raha hai!"),
                ("You've earned {coins_balance} coins! Complete another exercise to earn more.",
                 "Tumne {coins_balance} coins kamaye! Ek aur exercise karo aur coins badao."),
                ("Your {streak_current}-day streak is impressive! Maintain it with today's practice.",
                 "Tumhara {streak_current}-day streak amazing hai! Aaj practice karke maintain karo.")
            ],
            'loss_avoidance': [
                ("Your streak will break in {hours_left} hours! Complete one exercise to save it.",
                 "Tumhara streak {hours_left} ghante mein toot jayega! Ek exercise karo bachane ke liye."),
                ("Don't lose your {streak_current}-day streak! A quick practice session will save it.",
                 "Apna {streak_current}-day streak mat khoo! Ek chhoti practice se bach jayega."),
                ("Your hard-earned progress is at risk. Complete today's exercise to protect it.",
                 "Tumhari mehnat khatrey mein hai. Aaj ka exercise karo protect karne ke liye."),
                ("Only {hours_left} hours left! Don't let your streak break.",
                 "Sirf {hours_left} ghante bache! Streak tootne mat do."),
                ("Your {coins_balance} coins will expire soon! Use them before it's too late.",
                 "Tumhare {coins_balance} coins expire hone wale! Jaldi use karo.")
            ],
            'social_influence': [
                ("{peer_name} from {location} just completed 5 exercises. Can you match that?",
                 "{peer_name} {location} se 5 exercises kar chuke. Tum bhi kar sakte ho?"),
                ("Join {active_users}+ users practicing right now!",
                 "{active_users}+ users abhi practice kar rahe—tum bhi join karo!"),
                ("{peer_name} completed {peer_exercises} exercises today. Beat their score!",
                 "{peer_name} ne aaj {peer_exercises} exercises kiye. Unhe beat karo!"),
                ("You're #{rank} on the leaderboard. One exercise could push you higher!",
                 "Tum leaderboard par #{rank} ho. Ek exercise se aur upar jao!"),
                ("{active_users} learners are online now—don't get left behind!",
                 "{active_users} learners abhi online—peeche mat raho!")
            ],
            'unpredictability': [
                ("A new speaking exercise has been unlocked just for you. Try it now!",
                 "Ek naya speaking exercise sirf tumhare liye unlock hua. Abhi try karo!"),
                ("The AI tutor has a surprise lesson today. See what's waiting!",
                 "AI tutor ka aaj surprise lesson hai. Dekho kya wait kar raha!"),
                ("Complete your next exercise to unlock a mystery reward!",
                 "Next exercise complete karo aur mystery reward unlock karo!"),
                ("Your speaking score might surprise you today. Find out!",
                 "Tumhara speaking score aaj surprise kar sakta hai. Dekho!"),
                ("New practice scenarios just added! Explore them now.",
                 "Naye practice scenarios add hue! Abhi explore karo.")
            ],
            'empowerment': [
                ("Choose your practice topic for today—we have 20+ options!",
                 "Aaj ka topic tum choose karo—20+ options hai!"),
                ("Practice at your own pace. No pressure, just progress.",
                 "Apni speed se practice karo. Pressure nahi, sirf progress."),
                ("Customize your learning path. Pick what interests you most!",
                 "Apna learning path customize karo. Jo pasand ho wo choose karo!"),
                ("You control your progress. Start when you're ready.",
                 "Progress tumhare haath mein hai. Jab ready ho tab start karo."),
                ("Pick any exercise that interests you—it's your choice!",
                 "Koi bhi exercise choose karo—tumhari marzi!")
            ],
            'ownership': [
                ("Your {coins_balance} coins are ready to use! See what you can unlock.",
                 "Tumhare {coins_balance} coins ready hai! Dekho kya unlock kar sakte ho."),
                ("You've built a {streak_current}-day streak! That's YOUR achievement.",
                 "Tumne {streak_current}-day streak banaya! Ye TUMHARI achievement hai."),
                ("Your progress dashboard has updates. Check out YOUR stats!",
                 "Tumhare progress dashboard mein updates. APNE stats dekho!"),
                ("You've earned {coins_balance} coins—use them to unlock premium content!",
                 "Tumne {coins_balance} coins kamaye—premium content unlock karo!"),
                ("Your learning journey has been impressive. Keep building YOUR story!",
                 "Tumhara learning journey impressive raha. APNI kahani banao!")
            ],
            'epic_meaning': [
                ("Join 1M+ Indians who are becoming confident English speakers!",
                 "10 lakh+ Indians join karo jo confident English speakers ban rahe!"),
                ("Be part of the English learning revolution in India!",
                 "India ki English learning revolution ka hissa bano!"),
                ("Transform your career with better communication skills. Start today!",
                 "Apna career transform karo better communication se. Aaj start karo!"),
                ("Join thousands who improved their English this month!",
                 "Hazaron logon ke saath judo jinhone is mahine English improve ki!"),
                ("Your journey to English fluency starts with one exercise today.",
                 "English fluency ka safar aaj ek exercise se shuru karo.")
            ],
            'scarcity': [
                ("Only 3 hours left to complete today's goal. Don't wait!",
                 "Aaj ka goal complete karne ke liye sirf 3 ghante bache. Jaldi karo!"),
                ("Limited time offer: Double coins on your next exercise!",
                 "Limited time offer: Next exercise par double coins!"),
                ("Today's special exercise expires in 2 hours. Try it now!",
                 "Aaj ka special exercise 2 ghante mein expire. Abhi try karo!"),
                ("Last chance to maintain your streak today. Act now!",
                 "Aaj streak maintain karne ka last chance. Abhi action lo!"),
                ("This practice opportunity expires at midnight. Don't miss it!",
                 "Ye practice opportunity midnight ko expire. Miss mat karo!")
            ]
        }
        
        theme_bodies = bodies.get(theme, bodies['accomplishment'])
        return theme_bodies[variant % len(theme_bodies)]
    
    def _generate_cta(self, goal: str, theme: str, variant: int) -> Tuple[str, str]:
        """Generate CTA button text in English and Hinglish"""
        
        ctas = {
            'accomplishment': [
                ("Continue Learning", "Learning Continue Karo"),
                ("Practice Now", "Abhi Practice Karo"),
                ("Keep Going", "Aage Badho"),
                ("Complete Exercise", "Exercise Complete Karo"),
                ("Earn More Coins", "Aur Coins Kamao")
            ],
            'loss_avoidance': [
                ("Save My Streak", "Mera Streak Bachao"),
                ("Practice Now", "Abhi Practice Karo"),
                ("Don't Lose It", "Kho Mat"),
                ("Protect Progress", "Progress Protect Karo"),
                ("Act Now", "Abhi Karo")
            ],
            'social_influence': [
                ("Join Now", "Abhi Join Karo"),
                ("Beat Them", "Unhe Harao"),
                ("See Leaderboard", "Leaderboard Dekho"),
                ("Compete Now", "Abhi Compete Karo"),
                ("Climb Higher", "Upar Jao")
            ],
            'unpredictability': [
                ("Discover Now", "Abhi Discover Karo"),
                ("See Surprise", "Surprise Dekho"),
                ("Unlock It", "Unlock Karo"),
                ("Try It", "Try Karo"),
                ("Find Out", "Pata Karo")
            ],
            'empowerment': [
                ("Choose Topic", "Topic Choose Karo"),
                ("Start My Way", "Apne Tarike Se Start"),
                ("Customize", "Customize Karo"),
                ("Pick Exercise", "Exercise Choose Karo"),
                ("My Choice", "Meri Choice")
            ],
            'ownership': [
                ("View My Stats", "Mere Stats Dekho"),
                ("Use My Coins", "Mere Coins Use Karo"),
                ("See Progress", "Progress Dekho"),
                ("My Dashboard", "Mera Dashboard"),
                ("Check Rewards", "Rewards Check Karo")
            ],
            'epic_meaning': [
                ("Join Movement", "Movement Join Karo"),
                ("Start Journey", "Safar Shuru Karo"),
                ("Transform Now", "Abhi Transform Karo"),
                ("Be Part Of It", "Iska Hissa Bano"),
                ("Begin Today", "Aaj Shuru Karo")
            ],
            'scarcity': [
                ("Grab Now", "Abhi Pakdo"),
                ("Don't Wait", "Wait Mat Karo"),
                ("Hurry Up", "Jaldi Karo"),
                ("Claim Offer", "Offer Claim Karo"),
                ("Last Chance", "Last Chance")
            ]
        }
        
        theme_ctas = ctas.get(theme, ctas['accomplishment'])
        return theme_ctas[variant % len(theme_ctas)]
    
    def _generate_content(self, seg_name: str, lifecycle: str, goal: str, 
                         theme: str, variant: int) -> str:
        """Generate template content based on parameters (legacy support)"""
        _, body_en = self._generate_body(seg_name, lifecycle, goal, theme, variant)
        return body_en
    
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

