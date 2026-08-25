"""
Template Generator — LLM-Powered Bilingual Message Templates

Generates exactly 5 templates per Segment × Lifecycle × Goal × Theme
using LLM calls for domain-customized bilingual content.

Each template row has BOTH languages in separate columns:
  - message_title_en, message_title_hi
  - message_body_en, message_body_hi
  - cta_text_en, cta_text_hi

Hindi columns use Hinglish (default secondary language).
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
import random

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.llm_utils import call_llm_with_retry, parse_json_response


class TemplateGenerator:
    """Generates personalized message templates with LLM-powered bilingual content."""

    def __init__(self, knowledge_bank: Dict, themes: pd.DataFrame):
        self.kb = knowledge_bank
        self.themes = themes
        self.templates = None

        # Extract domain and features
        self.domain = knowledge_bank.get('detected_domain', 'generic')
        self.feature_names = self._extract_feature_names()
        self.north_star = knowledge_bank.get('north_star', {})
        self.allowed_tones = knowledge_bank.get('tone_hook_matrix', {}).get('allowed_tones', [])
        self.hooks = knowledge_bank.get('tone_hook_matrix', {}).get('octalysis_hooks', {})

    def _extract_feature_names(self) -> List[str]:
        """Extract feature names from the knowledge bank."""
        features = []
        fgm = self.kb.get('feature_goal_map', {})
        for f in fgm.get('features', []):
            features.append(f.get('feature_name', 'Core Feature'))
        if not features:
            features = ['Core Feature']
        return features

    def generate_templates(self, segment_goals: pd.DataFrame) -> pd.DataFrame:
        """Generate exactly 5 message templates per segment × lifecycle × goal × theme.

        Uses LLM for domain-customized bilingual content with fallback.
        """
        print("\n[Edit] LLM-Powered Template Generation...")

        templates = []
        template_id = 1

        # Group by segment + lifecycle + goal
        groups = segment_goals.groupby(['segment_id', 'lifecycle_stage', 'primary_goal'])

        total_groups = 0
        llm_success = 0
        fallback_used = 0

        for (seg_id, lifecycle, goal), group in groups:
            seg_name = group['segment_name'].iloc[0]

            # Get themes for this segment × lifecycle
            theme_row = self.themes[
                (self.themes['segment_id'] == seg_id) &
                (self.themes['lifecycle_stage'] == lifecycle)
            ]

            if theme_row.empty:
                continue

            primary_theme = theme_row['primary_theme'].iloc[0]
            secondary_theme = theme_row['secondary_theme'].iloc[0] if 'secondary_theme' in theme_row.columns else None

            theme_values = [primary_theme]
            if pd.notna(secondary_theme) and secondary_theme != primary_theme:
                theme_values.append(secondary_theme)

            for theme in theme_values:
                total_groups += 1

                # Try LLM generation
                llm_templates = self._generate_5_templates_llm(
                    seg_name, lifecycle, goal, theme
                )

                if llm_templates and len(llm_templates) >= 5:
                    llm_success += 1
                    for i, t in enumerate(llm_templates[:5]):
                        templates.append({
                            'template_id': f'TPL_{template_id:04d}',
                            'segment_id': seg_id,
                            'segment_name': seg_name,
                            'lifecycle_stage': lifecycle,
                            'goal': goal,
                            'theme': theme,
                            'variant': i + 1,
                            'message_title_en': t.get('title_en', ''),
                            'message_title_hi': t.get('title_hi', ''),
                            'message_body_en': t.get('body_en', ''),
                            'message_body_hi': t.get('body_hi', ''),
                            'cta_text_en': t.get('cta_en', ''),
                            'cta_text_hi': t.get('cta_hi', ''),
                            'tone': t.get('tone', 'friendly'),
                            'hook': theme,
                            'feature_reference': t.get('feature_reference', self.feature_names[0]),
                        })
                        template_id += 1
                else:
                    # Fallback: generate 5 simple templates
                    fallback_used += 1
                    for variant in range(5):
                        title_en, title_hi = self._fallback_title(theme, variant)
                        body_en, body_hi = self._fallback_body(seg_name, lifecycle, goal, theme, variant)
                        cta_en, cta_hi = self._fallback_cta(theme, variant)

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
                            'tone': 'friendly',
                            'hook': theme,
                            'feature_reference': self.feature_names[variant % len(self.feature_names)],
                        })
                        template_id += 1

        self.templates = pd.DataFrame(templates)

        print(f"   [OK] Generated {len(templates)} bilingual templates")
        print(f"   [OK] LLM-generated: {llm_success}/{total_groups} groups | Fallback: {fallback_used}/{total_groups} groups")
        print(f"   [OK] Each template has English + Hinglish columns")

        # Display top templates
        self._display_top_templates()

        return self.templates

    def _generate_5_templates_llm(self, seg_name: str, lifecycle: str,
                                   goal: str, theme: str) -> List[Dict]:
        """Generate exactly 5 bilingual templates via LLM."""

        features_str = ", ".join(self.feature_names[:5])
        tones_str = ", ".join(self.allowed_tones[:5]) if self.allowed_tones else "friendly, encouraging"
        nsm = self.north_star.get('north_star_metric', 'engagement')

        system_prompt = (
            f"You are an Elite Behavioral Copywriter and Cultural Linguist for a {self.domain} product. "
            f"The company's North Star Metric is '{nsm}'.\n\n"
            f"THE PERSONIFICATION FRAMEWORK (User-Centric Thinking):\n"
            f"Before writing, inhabit the Target User:\n"
            f"1. Embody the State: Feel the user's situation ({lifecycle} lifecycle in {self.domain}).\n"
            f"2. Identify the Friction: What is the between-the-lines pain point?\n"
            f"3. Filter the Jargon: 100% RULE: Never use words like Octalysis, Retention, Drive, or Metric.\n\n"
            f"INVISIBLE PSYCHOLOGY (Between-the-Lines Encoding):\n"
            f"Encode the '{theme}' drive into grammar and tone:\n"
            f"- Loss Avoidance: Tense, urgent. Encode the pain of losing progress.\n"
            f"- Social Influence: Peer-pulse language. Encode community warmth.\n"
            f"- Accomplishment: Celebratory. Encode pride of mastery.\n"
            f"- Epic Meaning: High-vision. Encode purpose.\n\n"
            f"LINGUISTIC PRECISION:\n"
            f"- English: Premium, benefit-first.\n"
            f"- Hinglish: Natural Urban-Hindi (Roman script). Avoid robot-translations.\n\n"
            f"Allowed tones: {tones_str}. "
            f"Keep titles under 50 chars, bodies under 150 chars, CTAs under 25 chars. "
            f"Reference real product features."
        )

        user_prompt = (
            f"Segment: {seg_name}\n"
            f"Lifecycle: {lifecycle}\n"
            f"Goal: {goal}\n"
            f"Octalysis Drive: {theme}\n"
            f"Product features: {features_str}\n\n"
            f"Generate exactly 5 notification templates as a JSON array:\n"
            f"[{{\n"
            f'  "title_en": "...", "title_hi": "...",\n'
            f'  "body_en": "...", "body_hi": "...",\n'
            f'  "cta_en": "...", "cta_hi": "...",\n'
            f'  "tone": "...", "feature_reference": "..."\n'
            f"}}]\n\n"
            f"Return ONLY the JSON array with exactly 5 items."
        )

        raw = call_llm_with_retry(system_prompt, user_prompt)
        parsed = parse_json_response(raw) if raw else None

        if parsed and isinstance(parsed, list) and len(parsed) >= 5:
            return parsed[:5]
        return None

    # ------------------------------------------------------------------ #
    #  Fallback templates (minimal, domain-aware)
    # ------------------------------------------------------------------ #

    def _fallback_title(self, theme: str, variant: int) -> Tuple[str, str]:
        """Minimal fallback titles per Octalysis drive."""
        titles = {
            'accomplishment': [
                ("🎯 Keep going!", "🎯 Aage badho!"),
                ("🏆 Great progress!", "🏆 Badiya progress!"),
                ("⭐ You're on track!", "⭐ Sahi track pe ho!"),
                ("🔥 Keep it up!", "🔥 Aise hi karo!"),
                ("💪 Almost there!", "💪 Bas thoda aur!"),
            ],
            'loss_avoidance': [
                ("⚠️ Don't miss out!", "⚠️ Miss mat karo!"),
                ("🔔 Time is running out!", "🔔 Time khatam ho raha!"),
                ("⏰ Act before it's late!", "⏰ Der se pehle karo!"),
                ("❗ Your progress is at risk!", "❗ Progress khatrey mein!"),
                ("🚨 Last chance!", "🚨 Aakhri mauka!"),
            ],
            'social_influence': [
                ("👥 See what's trending!", "👥 Dekho kya trend hai!"),
                ("🏅 Compare with others!", "🏅 Auron se compare karo!"),
                ("📊 You vs the community", "📊 Tum vs community"),
                ("🌟 Join top users!", "🌟 Top users mein shamil ho!"),
                ("👋 Others are active!", "👋 Baaki active hain!"),
            ],
            'unpredictability': [
                ("🎁 Surprise for you!", "🎁 Tumhare liye surprise!"),
                ("✨ Something new!", "✨ Kuch naya hai!"),
                ("🎲 Discover today!", "🎲 Aaj discover karo!"),
                ("🔓 Unlock something!", "🔓 Kuch unlock karo!"),
                ("🎉 Check this out!", "🎉 Ye dekho!"),
            ],
            'empowerment': [
                ("🎮 Your choice!", "🎮 Tumhari choice!"),
                ("⚡ Take control!", "⚡ Control lo!"),
                ("🛠️ Customize it!", "🛠️ Customize karo!"),
                ("🎯 Your way!", "🎯 Apne tarike se!"),
                ("💡 You decide!", "💡 Tum decide karo!"),
            ],
            'ownership': [
                ("👑 Your rewards!", "👑 Tumhare rewards!"),
                ("💎 Check your progress!", "💎 Progress dekho!"),
                ("🏠 Your dashboard!", "🏠 Tumhara dashboard!"),
                ("📈 Your stats!", "📈 Tumhare stats!"),
                ("🎖️ You earned this!", "🎖️ Ye tumne kamaya!"),
            ],
            'epic_meaning': [
                ("🚀 Be part of it!", "🚀 Iska hissa bano!"),
                ("🌍 Make an impact!", "🌍 Impact daalo!"),
                ("💫 Transform today!", "💫 Aaj transform karo!"),
                ("🎓 Your journey!", "🎓 Tumhara safar!"),
                ("✨ Something bigger!", "✨ Kuch bada karo!"),
            ],
            'scarcity': [
                ("⏳ Limited time!", "⏳ Simit samay!"),
                ("🔥 Ending soon!", "🔥 Jaldi khatam!"),
                ("⚡ Today only!", "⚡ Sirf aaj!"),
                ("🎯 Don't wait!", "🎯 Wait mat karo!"),
                ("⏰ Hurry!", "⏰ Jaldi karo!"),
            ],
        }
        items = titles.get(theme, titles['accomplishment'])
        return items[variant % len(items)]

    def _fallback_body(self, seg_name: str, lifecycle: str, goal: str,
                       theme: str, variant: int) -> Tuple[str, str]:
        """Minimal fallback bodies."""
        feature = self.feature_names[variant % len(self.feature_names)]
        domain = self.domain

        bodies = [
            (f"Explore {feature} and take the next step in your {domain} journey!",
             f"{feature} explore karo aur apne {domain} journey mein aage badho!"),
            (f"Your {feature} experience is waiting. Check it out now!",
             f"Tumhara {feature} experience wait kar raha. Abhi dekho!"),
            (f"Make the most of {feature} today. You're doing great!",
             f"Aaj {feature} ka best use karo. Bahut accha chal raha!"),
            (f"Don't miss what's new in {feature}. Open and see!",
             f"{feature} mein naya kya hai miss mat karo. Khol ke dekho!"),
            (f"Your {domain} progress is impressive. Keep using {feature}!",
             f"Tumhara {domain} progress impressive hai. {feature} use karte raho!"),
        ]
        return bodies[variant % len(bodies)]

    def _fallback_cta(self, theme: str, variant: int) -> Tuple[str, str]:
        """Minimal fallback CTAs."""
        ctas = [
            ("Open Now", "Abhi Kholo"),
            ("Check It Out", "Dekho"),
            ("Get Started", "Shuru Karo"),
            ("Explore", "Explore Karo"),
            ("Try Now", "Abhi Try Karo"),
        ]
        return ctas[variant % len(ctas)]

    def _display_top_templates(self):
        """Display top templates in terminal for verification."""
        if self.templates is None or self.templates.empty:
            return

        print("\n   +" + "-" * 70 + "+")
        print("   |  TOP GENERATED TEMPLATES (Sample)                                    |")
        print("   +" + "-" * 70 + "+")

        # Show one template per segment (first variant only)
        shown = set()
        count = 0
        for _, t in self.templates.iterrows():
            seg_key = t['segment_id']
            if seg_key in shown or count >= 6:
                continue
            shown.add(seg_key)
            count += 1

            print(f"   |")
            print(f"   |  [{t['template_id']}] Segment: {t['segment_name']} | {t['lifecycle_stage']} | {t['theme']}")
            print(f"   |  EN: {t['message_title_en']}")
            print(f"   |      {t['message_body_en'][:80]}...")
            print(f"   |  HI: {t['message_title_hi']}")
            print(f"   |      {t['message_body_hi'][:80]}...")
            print(f"   |  CTA: {t['cta_text_en']} / {t['cta_text_hi']}")

        print(f"   |")
        print("   +" + "-" * 70 + "+")

    def save_templates(self, output_dir: str):
        """Save templates to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        self.templates.to_csv(output_path / 'message_templates.csv', index=False)
        print(f"[OK] Templates saved to {output_dir}/message_templates.csv")
