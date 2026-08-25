"""
Theme Engine — LLM-Powered Octalysis 8 Core Drives Mapping

Dynamically assigns primary and secondary Octalysis drives to each
segment × lifecycle combination using LLM analysis of segment profiles,
domain, and KB-extracted hooks.

The 8 Octalysis Core Drives:
  1. Epic Meaning & Calling
  2. Development & Accomplishment
  3. Empowerment of Creativity & Feedback
  4. Ownership & Possession
  5. Social Influence & Relatedness
  6. Scarcity & Impatience
  7. Unpredictability & Curiosity
  8. Loss & Avoidance
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.llm_utils import call_llm_with_retry, parse_json_response


OCTALYSIS_DRIVES = [
    'epic_meaning',
    'accomplishment',
    'empowerment',
    'ownership',
    'social_influence',
    'scarcity',
    'unpredictability',
    'loss_avoidance',
]


class ThemeEngine:
    """Maps behavioral themes to user segments using LLM + Octalysis 8 Core Drives."""

    def __init__(self, tone_hook_matrix: Dict, kb_data: Dict = None):
        self.tone_hook_matrix = tone_hook_matrix
        self.themes = None
        self.kb_data = kb_data or {}
        self.domain = self.kb_data.get('detected_domain', 'generic')

        # Extract KB hooks for context
        hooks = self.tone_hook_matrix.get('octalysis_hooks', {})
        self.kb_hooks_summary = {}
        for drive, info in hooks.items():
            if isinstance(info, dict) and 'hooks' in info:
                self.kb_hooks_summary[drive] = [h.get('trigger', '') for h in info['hooks'][:3]]

    def generate_themes(self, segment_profiles: pd.DataFrame) -> pd.DataFrame:
        """Generate communication themes for each segment × lifecycle using LLM."""
        print("\n[Theme] LLM-Powered Octalysis Theme Mapping...")

        lifecycle_stages = ['trial', 'paid', 'churned', 'inactive']

        # Try LLM-powered theme assignment
        themes = self._assign_themes_llm(segment_profiles, lifecycle_stages)

        if not themes:
            print("   [WARN] LLM theme assignment failed -- using rule-based fallback")
            themes = self._assign_themes_fallback(segment_profiles, lifecycle_stages)

        self.themes = pd.DataFrame(themes)

        print(f"   [OK] Generated {len(themes)} theme mappings")
        print(f"   [OK] Covering {len(segment_profiles)} segments x {len(lifecycle_stages)} lifecycle stages")

        # Display theme assignments
        self._display_themes()

        return self.themes

    def _assign_themes_llm(self, segment_profiles: pd.DataFrame,
                           lifecycle_stages: List[str]) -> List[Dict]:
        """Assign themes using LLM analysis."""

        # Build segment summaries
        segments_desc = []
        for _, p in segment_profiles.iterrows():
            segments_desc.append(
                f"Segment {int(p['segment_id'])} '{p['segment_name']}': "
                f"size={int(p['segment_size'])}, activeness={p['avg_activeness']:.2f}, "
                f"churn_risk={p['avg_churn_risk']:.2f}, "
                f"gamification={p['avg_gamification_propensity']:.2f}, "
                f"social={p['avg_social_propensity']:.2f}, "
                f"rfm={p['avg_rfm_score']:.2f}"
            )

        hooks_ctx = ""
        if self.kb_hooks_summary:
            hooks_ctx = "\nKB-extracted behavioral hooks:\n"
            for drive, triggers in self.kb_hooks_summary.items():
                hooks_ctx += f"  {drive}: {', '.join(triggers)}\n"

        system_prompt = (
            "You are a World-Class Behavioral Strategist and Octalysis Specialist. "
            "Your objective is to architect a Psychological Engagement Blueprint by matching user behavioral data "
            "to the motivational drives of the Octalysis Framework.\n\n"
            "THINKING FRAMEWORK - MOTIVATIONAL TRIANGULATION:\n"
            "Execute this 3-step cognitive process for every segment x lifecycle combination:\n"
            "1. BEHAVIORAL VECTOR ANALYSIS: Decipher raw stats. If Churn Risk > 0.7 but Social Propensity is high, "
            "user is fading but values community.\n"
            "2. DOMAIN CONTEXTUALIZATION (The Industry Pivot): Translate abstract Core Drives into industry-specific value. "
            "Example (Fintech): Accomplishment = Wealth Milestone. Example (Homestays): Scarcity = Exclusive Access.\n"
            "3. LIFECYCLE FRICTION MAPPING: Trial = Aha Moment (Unpredictability); Churned = Sunk Cost Recovery (Loss Avoidance).\n\n"
            "The 8 Octalysis Core Drives are:\n"
            "1. epic_meaning - purpose, calling, being part of something bigger\n"
            "2. accomplishment - progress, mastery, achievement\n"
            "3. empowerment - creativity, choice, feedback\n"
            "4. ownership - possession, collection, earning\n"
            "5. social_influence - competition, mentorship, social proof\n"
            "6. scarcity - limited time, exclusivity, urgency\n"
            "7. unpredictability - curiosity, surprise, mystery\n"
            "8. loss_avoidance - fear of losing progress, FOMO\n\n"
            "SEGREGATION STRATEGY: Ensure each segment receives a Distinct Motivation Signature.\n"
            "Lower-tier users with zero streak: Give epic_meaning or unpredictability to lower friction, NOT accomplishment.\n\n"
            "OUTPUT: Return ONLY a valid JSON array. Each object must include segment_id, lifecycle, primary_drive, secondary_drive, and rationale."
        )

        user_prompt = (
            f"Domain: {self.domain}\n"
            f"Lifecycle stages: {', '.join(lifecycle_stages)}\n\n"
            f"Segments:\n" + "\n".join(segments_desc) + "\n"
            f"{hooks_ctx}\n"
            "For each segment × lifecycle combination, assign a primary_drive and secondary_drive "
            "(must be from the 8 drives listed above) and a brief rationale.\n\n"
            "Return a JSON array like:\n"
            '[{"segment_id": 0, "lifecycle": "trial", "primary_drive": "accomplishment", '
            '"secondary_drive": "unpredictability", "rationale": "New users need achievement milestones"}]\n\n'
            "Return ALL combinations. Return ONLY the JSON array."
        )

        raw = call_llm_with_retry(system_prompt, user_prompt)
        parsed = parse_json_response(raw) if raw else None

        if not parsed or not isinstance(parsed, list):
            return []

        # Build themes from LLM output
        themes = []
        seg_names = dict(zip(
            segment_profiles['segment_id'].astype(int),
            segment_profiles['segment_name']
        ))

        for entry in parsed:
            try:
                seg_id = int(entry.get('segment_id', -1))
                lifecycle = entry.get('lifecycle', '')
                primary = entry.get('primary_drive', 'accomplishment')
                secondary = entry.get('secondary_drive', 'unpredictability')
                rationale = entry.get('rationale', '')

                # Validate drives
                if primary not in OCTALYSIS_DRIVES:
                    primary = 'accomplishment'
                if secondary not in OCTALYSIS_DRIVES:
                    secondary = 'unpredictability'

                themes.append({
                    'segment_id': seg_id,
                    'segment_name': seg_names.get(seg_id, f'Segment {seg_id}'),
                    'lifecycle_stage': lifecycle,
                    'primary_theme': primary,
                    'secondary_theme': secondary,
                    'theme_rationale': rationale,
                })
            except (ValueError, TypeError):
                continue

        # Fill any missing combinations
        existing = {(t['segment_id'], t['lifecycle_stage']) for t in themes}
        for _, p in segment_profiles.iterrows():
            for lc in lifecycle_stages:
                key = (int(p['segment_id']), lc)
                if key not in existing:
                    primary, secondary = self._default_theme(p, lc)
                    themes.append({
                        'segment_id': int(p['segment_id']),
                        'segment_name': p['segment_name'],
                        'lifecycle_stage': lc,
                        'primary_theme': primary,
                        'secondary_theme': secondary,
                        'theme_rationale': 'Default assignment (LLM missed this combo)',
                    })

        return themes if themes else []

    def _assign_themes_fallback(self, segment_profiles: pd.DataFrame,
                                lifecycle_stages: List[str]) -> List[Dict]:
        """Fallback rule-based theme assignment."""
        themes = []
        for _, segment in segment_profiles.iterrows():
            for lifecycle in lifecycle_stages:
                primary, secondary = self._default_theme(segment, lifecycle)
                rationale = self._generate_rationale(segment, primary, secondary)
                themes.append({
                    'segment_id': segment['segment_id'],
                    'segment_name': segment['segment_name'],
                    'lifecycle_stage': lifecycle,
                    'primary_theme': primary,
                    'secondary_theme': secondary,
                    'theme_rationale': rationale,
                })
        return themes

    def _default_theme(self, segment, lifecycle: str) -> tuple:
        """Rule-based default theme selection."""
        churn = segment['avg_churn_risk']
        gamification = segment['avg_gamification_propensity']
        social = segment['avg_social_propensity']
        activeness = segment['avg_activeness']

        if churn > 0.7:
            return ('loss_avoidance', 'scarcity')
        elif gamification > 0.6:
            return ('accomplishment', 'ownership')
        elif social > 0.6:
            return ('social_influence', 'accomplishment')
        elif activeness < 0.3:
            return ('unpredictability', 'epic_meaning')
        elif lifecycle == 'churned':
            return ('loss_avoidance', 'unpredictability')
        elif lifecycle == 'trial':
            return ('accomplishment', 'unpredictability')
        elif lifecycle == 'paid':
            return ('accomplishment', 'ownership')
        else:
            return ('unpredictability', 'empowerment')

    def _generate_rationale(self, segment, primary: str, secondary: str) -> str:
        """Generate explanation for theme selection."""
        parts = []
        if primary == 'accomplishment':
            parts.append(f"Gamification={segment['avg_gamification_propensity']:.2f} → achievement drive")
        elif primary == 'social_influence':
            parts.append(f"Social={segment['avg_social_propensity']:.2f} → competitive motivation")
        elif primary == 'loss_avoidance':
            parts.append(f"Churn={segment['avg_churn_risk']:.2f} → retention urgency")
        elif primary == 'unpredictability':
            parts.append(f"Activeness={segment['avg_activeness']:.2f} → needs discovery triggers")
        parts.append(f"Secondary '{secondary}' for complementary motivation")
        return "; ".join(parts)

    def _display_themes(self):
        """Display theme assignments in terminal."""
        if self.themes is None or self.themes.empty:
            return

        print("\n   +" + "-" * 69 + "+")
        print("   |  OCTALYSIS THEME ASSIGNMENTS                                       |")
        print("   +" + "-" * 69 + "+")

        for seg_id in sorted(self.themes['segment_id'].unique()):
            seg_themes = self.themes[self.themes['segment_id'] == seg_id]
            seg_name = seg_themes['segment_name'].iloc[0]
            print(f"   |  Segment {seg_id}: {seg_name}")
            for _, row in seg_themes.iterrows():
                lc = row['lifecycle_stage']
                p = row['primary_theme']
                s = row['secondary_theme']
                print(f"   |    {lc:10s} -> primary: {p:20s} secondary: {s}")
            print(f"   |")
        print("   +" + "-" * 69 + "+")

    def save_themes(self, output_dir: str):
        """Save themes to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        self.themes.to_csv(output_path / 'communication_themes.csv', index=False)
        print(f"[OK] Themes saved to {output_dir}/communication_themes.csv")
