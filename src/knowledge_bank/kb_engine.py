"""
Knowledge Bank Engine - Extracts company intelligence from documents
"""

import json
import re
from typing import Dict, List, Any
from pathlib import Path


class KnowledgeBankEngine:
    """Extracts and structures company knowledge from text documents"""
    
    def __init__(self):
        self.north_star = None
        self.feature_goal_map = None
        self.tone_hook_matrix = None
    
    def process_knowledge_bank(self, kb_text: str) -> Dict[str, Any]:
        """
        Process knowledge bank text and extract all intelligence
        
        Args:
            kb_text: Raw text from company knowledge base
            
        Returns:
            dict: Structured knowledge bank data
        """
        self.north_star = self._extract_north_star(kb_text)
        self.feature_goal_map = self._extract_feature_goal_map(kb_text)
        self.tone_hook_matrix = self._extract_tone_hook_matrix(kb_text)
        
        return {
            'north_star': self.north_star,
            'feature_goal_map': self.feature_goal_map,
            'tone_hook_matrix': self.tone_hook_matrix
        }
    
    def _extract_north_star(self, text: str) -> Dict[str, Any]:
        """Extract North Star metric from KB using pattern matching"""
        
        # Try to extract from text using patterns
        patterns = [
            r"north star.*?(?:is|:)\s*([^.\n]+)",
            r"key metric.*?(?:is|:)\s*([^.\n]+)",
            r"we measure success by\s*([^.\n]+)",
            r"primary metric.*?(?:is|:)\s*([^.\n]+)"
        ]
        
        metric_name = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                metric_name = match.group(1).strip()
                break
        
        # If not found in text, use default based on common patterns
        if not metric_name:
            # Check for domain indicators
            if any(word in text.lower() for word in ['learn', 'education', 'practice', 'exercise']):
                metric_name = "Daily Active Engaged Users"
            elif any(word in text.lower() for word in ['transaction', 'payment', 'wallet']):
                metric_name = "Transaction Volume"
            elif any(word in text.lower() for word in ['watch', 'stream', 'content', 'video']):
                metric_name = "Hours Watched"
            else:
                metric_name = "Daily Active Users"
        
        # Extract definition and rationale
        definition = self._extract_definition(text, metric_name)
        why_matters = self._extract_rationale(text, metric_name)
        
        north_star = {
            "north_star_metric": metric_name,
            "definition": definition,
            "why_it_matters": why_matters,
            "measurement": f"Metric tracking for {metric_name}",
            "key_drivers": self._extract_key_drivers(text)
        }
        
        return north_star
    
    def _extract_definition(self, text: str, metric: str) -> str:
        """Extract definition of the metric"""
        # Try to find definition near the metric mention
        definition_patterns = [
            rf"{re.escape(metric)}.*?(?:defined as|means|is)\s*([^.\n]+)",
            r"definition.*?:\s*([^.\n]+)"
        ]
        
        for pattern in definition_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return f"Users who actively engage with the platform"
    
    def _extract_rationale(self, text: str, metric: str) -> str:
        """Extract why the metric matters"""
        rationale_patterns = [
            r"(?:why|because|matters).*?:\s*([^.\n]+)",
            r"important because\s*([^.\n]+)"
        ]
        
        for pattern in rationale_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return "Indicates product stickiness and user value realization"
    
    def _extract_key_drivers(self, text: str) -> List[str]:
        """Extract key drivers from text"""
        drivers = []
        
        # Look for bullet points or numbered lists
        driver_patterns = [
            r"[-•]\s*([^.\n]+)",
            r"\d+\.\s*([^.\n]+)"
        ]
        
        for pattern in driver_patterns:
            matches = re.findall(pattern, text)
            drivers.extend([m.strip() for m in matches if len(m.strip()) > 10])
        
        # If no drivers found, return generic ones
        if not drivers:
            drivers = ["User engagement", "Feature adoption", "Retention"]
        
        return drivers[:5]  # Limit to top 5
    
    def _extract_feature_goal_map(self, text: str) -> Dict[str, List[Dict]]:
        """Extract feature-to-goal mappings from KB text"""
        features = []
        
        # Extract features mentioned in text
        feature_keywords = [
            'feature', 'tool', 'capability', 'functionality', 
            'module', 'component', 'service'
        ]
        
        # Look for feature mentions
        feature_pattern = r"(?:feature|tool|capability).*?:\s*([A-Z][^.\n]+)"
        feature_matches = re.findall(feature_pattern, text, re.IGNORECASE)
        
        # If no features found, try to infer from domain
        if not feature_matches:
            feature_matches = self._infer_features_from_domain(text)
        
        for idx, feature_name in enumerate(feature_matches[:5]):  # Limit to 5 features
            feature_id = feature_name.lower().replace(' ', '_').replace('&', 'and')
            
            features.append({
                "feature_name": feature_name.strip(),
                "feature_id": feature_id,
                "primary_goal": self._infer_goal_from_feature(feature_name, text),
                "secondary_goals": self._infer_secondary_goals(feature_name, text),
                "user_segments_most_relevant": ["all"],  # Will be refined by segmentation
                "engagement_driver_score": 0.70 + (idx * 0.05),  # Placeholder scoring
                "description": f"Feature for {feature_name.lower()}"
            })
        
        # If still no features, use generic ones
        if not features:
            features = self._get_default_features(text)
        
        return {"features": features}
    
    def _infer_features_from_domain(self, text: str) -> List[str]:
        """Infer likely features based on domain indicators"""
        text_lower = text.lower()
        features = []
        
        # EdTech domain
        if any(word in text_lower for word in ['learn', 'education', 'practice', 'exercise']):
            if 'ai' in text_lower or 'tutor' in text_lower:
                features.append("AI Tutor")
            if 'leaderboard' in text_lower or 'rank' in text_lower:
                features.append("Leaderboard")
            if 'streak' in text_lower:
                features.append("Streak System")
            if 'coin' in text_lower or 'reward' in text_lower:
                features.append("Rewards")
            features.append("Exercises")
        
        # FinTech domain
        elif any(word in text_lower for word in ['payment', 'transaction', 'wallet']):
            features.extend(["Wallet", "Payments", "Cashback", "Bill Pay", "Transfers"])
        
        # Entertainment domain
        elif any(word in text_lower for word in ['watch', 'stream', 'content', 'video']):
            features.extend(["Content Library", "Recommendations", "Watchlist", "Downloads", "Profiles"])
        
        # Generic features
        else:
            features.extend(["Core Feature", "Engagement Feature", "Social Feature", "Rewards", "Analytics"])
        
        return features
    
    def _infer_goal_from_feature(self, feature_name: str, text: str) -> str:
        """Infer primary goal from feature name"""
        feature_lower = feature_name.lower()
        
        goal_mapping = {
            'tutor': 'skill_development',
            'ai': 'personalized_learning',
            'leaderboard': 'competitive_engagement',
            'streak': 'habit_formation',
            'coin': 'gamification_engagement',
            'reward': 'motivation',
            'exercise': 'skill_development',
            'wallet': 'transaction_convenience',
            'payment': 'transaction_completion',
            'content': 'entertainment',
            'watch': 'content_consumption'
        }
        
        for keyword, goal in goal_mapping.items():
            if keyword in feature_lower:
                return goal
        
        return 'user_engagement'
    
    def _infer_secondary_goals(self, feature_name: str, text: str) -> List[str]:
        """Infer secondary goals"""
        return ["engagement", "retention", "satisfaction"]
    
    def _get_default_features(self, text: str) -> List[Dict]:
        """Get default features when extraction fails"""
        return [
            {
                "feature_name": "Core Feature",
                "feature_id": "core_feature",
                "primary_goal": "user_engagement",
                "secondary_goals": ["retention", "satisfaction"],
                "user_segments_most_relevant": ["all"],
                "engagement_driver_score": 0.80,
                "description": "Primary product feature"
            }
        ]
    
    def _extract_tone_hook_matrix(self, text: str) -> Dict[str, Any]:
        """Extract allowed tones and behavioral hooks"""
        matrix = {
            "allowed_tones": [
                "encouraging",
                "friendly",
                "aspirational",
                "urgent",
                "celebratory",
                "motivational",
                "supportive"
            ],
            "forbidden_tones": [
                "aggressive",
                "desperate",
                "salesy",
                "guilt-tripping",
                "condescending",
                "pushy"
            ],
            "tone_by_lifecycle": {
                "trial": ["encouraging", "friendly", "aspirational", "supportive"],
                "paid": ["celebratory", "friendly", "aspirational", "motivational"],
                "churned": ["friendly", "urgent", "aspirational", "curious"],
                "inactive": ["curious", "friendly", "inviting"]
            },
            "octalysis_hooks": {
                "epic_meaning": {
                    "description": "Be part of something bigger",
                    "examples": ["Join 1M+ Indians", "Transform your career", "Unlock your potential"],
                    "best_for_segments": ["aspirational_learners", "career_focused"]
                },
                "accomplishment": {
                    "description": "Make progress and achieve",
                    "examples": ["Complete 10 exercises", "Reach 7-day streak", "Earn 100 coins"],
                    "best_for_segments": ["achievers", "consistent_learners"]
                },
                "empowerment": {
                    "description": "Have control and experiment",
                    "examples": ["Choose your topic", "Practice at your pace", "Customize your learning"],
                    "best_for_segments": ["casual_learners", "explorers"]
                },
                "ownership": {
                    "description": "Build something valuable",
                    "examples": ["Your 500 coins", "Your 30-day streak", "Your progress"],
                    "best_for_segments": ["achievers", "collectors"]
                },
                "social_influence": {
                    "description": "Others are doing it",
                    "examples": ["Rahul is #1", "Join top learners", "Beat your friends"],
                    "best_for_segments": ["social_competitors", "community_driven"]
                },
                "scarcity": {
                    "description": "Limited time or availability",
                    "examples": ["Only 3 hours left", "Last chance today", "Limited spots"],
                    "best_for_segments": ["achievers", "fomo_driven"]
                },
                "curiosity": {
                    "description": "What will happen next",
                    "examples": ["Unlock surprise reward", "Discover new feature", "See what's next"],
                    "best_for_segments": ["explorers", "casual_learners"]
                },
                "loss_avoidance": {
                    "description": "Don't lose what you have",
                    "examples": ["Streak will break", "Don't lose progress", "Maintain your rank"],
                    "best_for_segments": ["achievers", "at_risk_churners"]
                }
            },
            "hooks_by_segment": {
                "achievers": ["accomplishment", "ownership", "loss_avoidance"],
                "social_competitors": ["social_influence", "accomplishment", "scarcity"],
                "casual_learners": ["curiosity", "empowerment", "epic_meaning"],
                "at_risk_churners": ["loss_avoidance", "scarcity", "social_influence"],
                "dormant_users": ["curiosity", "epic_meaning", "empowerment"]
            }
        }
        
        return matrix
    
    def save_outputs(self, output_dir: str):
        """Save extracted knowledge to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save north star
        with open(output_path / 'company_north_star.json', 'w', encoding='utf-8') as f:
            json.dump(self.north_star, f, indent=2, ensure_ascii=False)
        
        # Save feature goal map
        with open(output_path / 'feature_goal_map.json', 'w', encoding='utf-8') as f:
            json.dump(self.feature_goal_map, f, indent=2, ensure_ascii=False)
        
        # Save tone hook matrix
        with open(output_path / 'allowed_tone_hook_matrix.json', 'w', encoding='utf-8') as f:
            json.dump(self.tone_hook_matrix, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Knowledge Bank outputs saved to {output_dir}")
