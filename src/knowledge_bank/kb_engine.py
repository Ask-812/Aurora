"""
Knowledge Bank Engine - Extracts company intelligence from documents

This engine is domain-agnostic and adaptively extracts intelligence from
various knowledge bank formats (PDFs, docs, structured/unstructured text).
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml


class KnowledgeBankEngine:
    """Extracts and structures company knowledge from text documents"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        self.north_star = None
        self.feature_goal_map = None
        self.tone_hook_matrix = None
        self.detected_domain = None
        
        # Load config for tones and other configurable values
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.config = {}
        
        # Get communication config with defaults
        comm_config = self.config.get('communication', {})
        self.allowed_tones = comm_config.get('allowed_tones', [
            'encouraging', 'friendly', 'aspirational', 'urgent',
            'celebratory', 'motivational', 'supportive'
        ])
        self.forbidden_tones = comm_config.get('forbidden_tones', [
            'aggressive', 'desperate', 'salesy', 'guilt-tripping',
            'condescending', 'pushy'
        ])
        self.tone_by_lifecycle = comm_config.get('tone_by_lifecycle', {
            'trial': ['encouraging', 'friendly', 'aspirational', 'supportive'],
            'paid': ['celebratory', 'friendly', 'aspirational', 'motivational'],
            'churned': ['friendly', 'urgent', 'aspirational', 'curious'],
            'inactive': ['curious', 'friendly', 'inviting']
        })
    
    def process_knowledge_bank(self, kb_text: str) -> Dict[str, Any]:
        """
        Process knowledge bank text and extract all intelligence
        
        Args:
            kb_text: Raw text from company knowledge base
            
        Returns:
            dict: Structured knowledge bank data
        """
        # First detect domain for context-aware extraction
        self.detected_domain = self._detect_domain(kb_text)
        
        self.north_star = self._extract_north_star(kb_text)
        self.feature_goal_map = self._extract_feature_goal_map(kb_text)
        self.tone_hook_matrix = self._extract_tone_hook_matrix(kb_text)
        
        return {
            'north_star': self.north_star,
            'feature_goal_map': self.feature_goal_map,
            'tone_hook_matrix': self.tone_hook_matrix,
            'detected_domain': self.detected_domain
        }
    
    def _detect_domain(self, text: str) -> str:
        """
        Detect the domain/industry from KB text for context-aware extraction.
        Returns: 'edtech', 'fintech', 'entertainment', 'ecommerce', 'health', 'social', or 'generic'
        """
        text_lower = text.lower()
        
        # Domain indicators with weighted scoring
        domain_indicators = {
            'edtech': ['learn', 'education', 'course', 'lesson', 'practice', 'exercise', 'quiz', 'tutor', 'student', 'teacher', 'skill'],
            'fintech': ['payment', 'transaction', 'wallet', 'money', 'bank', 'finance', 'loan', 'credit', 'invest', 'transfer'],
            'entertainment': ['watch', 'stream', 'video', 'movie', 'show', 'content', 'music', 'play', 'episode', 'series'],
            'ecommerce': ['shop', 'buy', 'cart', 'order', 'product', 'delivery', 'price', 'sale', 'discount', 'checkout'],
            'health': ['health', 'fitness', 'workout', 'exercise', 'diet', 'wellness', 'medical', 'doctor', 'patient', 'prescription'],
            'social': ['friend', 'follow', 'post', 'share', 'comment', 'like', 'message', 'connect', 'network', 'community']
        }
        
        scores = {}
        for domain, keywords in domain_indicators.items():
            scores[domain] = sum(1 for kw in keywords if kw in text_lower)
        
        best_domain = max(scores, key=scores.get)
        return best_domain if scores[best_domain] >= 2 else 'generic'
    
    def _extract_north_star(self, text: str) -> Dict[str, Any]:
        """Extract North Star metric from KB using pattern matching"""
        
        metric_name = None
        
        # Look for explicit "Key Metrics" or "North Star" sections
        key_metrics_match = re.search(r"(?:key metrics?|north star)[\s\S]{0,500}?([A-Z][^.\n]{10,80}(?:retention|conversion|engagement|revenue|growth|active users))", text, re.IGNORECASE)
        
        if key_metrics_match:
            # Clean up the extracted metric name
            candidate = key_metrics_match.group(1).strip()
            # Remove common prefixes/artifacts
            candidate = re.sub(r'^[*•\-\d\.\s]+', '', candidate)
            candidate = re.sub(r'\s+', ' ', candidate)
            if len(candidate) > 10 and len(candidate) < 100:
                metric_name = candidate
        
        # Try additional targeted patterns
        if not metric_name:
            patterns = [
                r"north star(?:\s+metric)?(?:\s+is)?:\s*([A-Z][^.\n]{10,80})",
                r"primary metric:\s*([A-Z][^.\n]{10,80})",
                r"goal:\s*\*?\*?([^*\n]{10,80}(?:retention|conversion|engagement))\*?\*?",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    candidate = match.group(1).strip()
                    candidate = re.sub(r'^[*•\-\s]+', '', candidate)
                    if len(candidate) > 10 and len(candidate) < 100:
                        metric_name = candidate
                        break
        
        # If still not found, infer from domain
        if not metric_name or len(metric_name) < 10:
            # Check for domain indicators and common metrics
            text_lower = text.lower()
            if 'retention' in text_lower and ('monthly' in text_lower or 'week' in text_lower):
                metric_name = "Monthly Active Retention"
            elif any(word in text_lower for word in ['daily engagement', 'habit formation']):
                metric_name = "Daily Active Engaged Users"
            elif any(word in text_lower for word in ['learn', 'education', 'practice', 'exercise']):
                metric_name = "Weekly Active Learners"
            elif any(word in text_lower for word in ['transaction', 'payment', 'wallet']):
                metric_name = "Transaction Volume"
            elif any(word in text_lower for word in ['watch', 'stream', 'content', 'video']):
                metric_name = "Content Engagement Hours"
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
        # Look in the metrics section for the specific metric
        metrics_section = re.search(r"(?:key metrics?)([\s\S]{0,800}?)(?:\n#{1,3}\s|\Z)", text, re.IGNORECASE)
        
        if metrics_section:
            section = metrics_section.group(1)
            # Try to find the metric and its definition
            metric_pattern = rf"{re.escape(metric[:20])}[^\n]*?\n\s*[*•\-]?\s*([A-Z][^.\n]{{20,150}})"
            match = re.search(metric_pattern, section, re.IGNORECASE)
            if match:
                defn = match.group(1).strip('* \t')
                if len(defn) > 20:
                    return defn
        
        # Fallback based on metric type
        if 'retention' in metric.lower():
            return "Percentage of users who remain active and engaged over time"
        elif 'conversion' in metric.lower():
            return "Rate at which trial users convert to paying customers"
        elif 'engagement' in metric.lower():
            return "Users who actively interact with core features daily"
        else:
            return "Primary success metric measuring product-market fit"
    
    def _extract_rationale(self, text: str, metric: str) -> str:
        """Extract why the metric matters"""
        # Look for goals or value propositions
        goal_match = re.search(r"goal:?\s*\*?\*?([^*\n]{15,100})\*?\*?", text, re.IGNORECASE)
        if goal_match:
            return f"Drives {goal_match.group(1).strip().lower()}"
        
        # Fallback based on metric type
        if 'retention' in metric.lower():
            return "Indicates product stickiness and long-term value creation"
        elif 'conversion' in metric.lower():
            return "Validates product-market fit and monetization effectiveness"
        elif 'engagement' in metric.lower():
            return "Measures active usage and habit formation, leading to retention"
        elif 'revenue' in metric.lower():
            return "Direct indicator of business sustainability and growth"
        else:
            return "Core indicator of product success and user satisfaction"
    
    def _extract_key_drivers(self, text: str) -> List[str]:
        """Extract key drivers from text"""
        drivers = []
        
        # Look specifically for Key Metrics or metrics section
        metrics_section = re.search(r"(?:key metrics?|metrics?|kpis?)[\s:]*\n([\s\S]{0,500}?)(?:\n#{1,3}\s|\n\*\*[A-Z]|\Z)", text, re.IGNORECASE)
        
        if metrics_section:
            section_text = metrics_section.group(1)
            
            # Extract bullet points or numbered items from metrics section
            driver_patterns = [
                r"[*•\-]\s+\*?\*?([^*\n]{15,}?)(?:\*?\*?\s*$|\*?\*?\n)",  # Bullet with bold handling
                r"^\d+\.\s+([^.\n]{15,})$"  # Numbered items
            ]
            
            for pattern in driver_patterns:
                matches = re.findall(pattern, section_text, re.MULTILINE)
                for match in matches:
                    cleaned = match.strip().strip('*').strip()
                    if len(cleaned) > 15 and len(cleaned) < 100:
                        drivers.append(cleaned)
        
        # If no drivers found in metrics section, look for goals
        if not drivers:
            goal_match = re.search(r"goal:?\s*\*?\*?([^*\n]{15,})\*?\*?", text, re.IGNORECASE)
            if goal_match:
                drivers.append(goal_match.group(1).strip())
        
        # Fallback to generic drivers
        if not drivers:
            text_lower = text.lower()
            if 'retention' in text_lower:
                drivers.append("User retention and engagement")
            if 'conversion' in text_lower:
                drivers.append("Trial to paid conversion")
            if 'engagement' in text_lower:
                drivers.append("Daily active engagement")
                
        # Final fallback
        if not drivers:
            drivers = ["User engagement", "Feature adoption", "Retention"]
        
        # Remove duplicates and limit
        drivers = list(dict.fromkeys(drivers))[:5]
        
        return drivers
    
    def _extract_feature_goal_map(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract feature-to-goal mappings from KB text using multiple adaptive strategies.
        Tries progressively looser patterns to ensure extraction works on various KB formats.
        """
        features = []
        feature_names = []
        
        # Strategy 1: Look for explicit features/capabilities sections
        section_patterns = [
            r"(?:features?|achieved through|capabilities|key functionality|product offerings?)[\ s:]*\n([\s\S]{0,1200}?)(?:\n#{1,3}\s|\n\*\*[A-Z]|\Z)",
            r"(?:what we offer|how it works|our solution)[\ s:]*\n([\s\S]{0,1200}?)(?:\n#{1,3}\s|\Z)",
            r"(?:product|app|platform) (?:includes?|provides?|offers?)([\s\S]{0,800}?)(?:\n#{1,3}\s|\Z)"
        ]
        
        for pattern in section_patterns:
            section_match = re.search(pattern, text, re.IGNORECASE)
            if section_match:
                section_text = section_match.group(1)
                
                # Extract bullet points or list items
                bullet_patterns = [
                    r"[*•\-]\s+([A-Z][^*\n]{5,80})",  # Standard bullets
                    r"\d+[.)\s]+([A-Z][^\n]{5,80})",    # Numbered items
                    r"\*\*([^*]{5,50})\*\*",             # Bold text
                ]
                
                for bp in bullet_patterns:
                    matches = re.findall(bp, section_text)
                    for match in matches:
                        cleaned = match.strip().strip('*').strip()
                        if 5 < len(cleaned) < 80 and cleaned not in feature_names:
                            feature_names.append(cleaned)
                
                if feature_names:
                    break
        
        # Strategy 2: Extract any capitalized phrases that look like feature names
        if not feature_names:
            # Look for noun phrases that might be features
            noun_phrase_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}(?:\s+(?:Feature|Tool|System|Module|Engine|Dashboard|Analytics|Practice|Mode))?)\b"
            matches = re.findall(noun_phrase_pattern, text)
            for match in matches:
                if 5 < len(match) < 60 and match not in feature_names:
                    feature_names.append(match)
        
        # Strategy 3: Domain-aware inference based on detected domain
        if not feature_names:
            feature_names = self._infer_features_from_domain(text)
        
        # Create feature objects
        for idx, feature_name in enumerate(feature_names[:8]):  # Limit to 8 features
            feature_id = re.sub(r'[^a-z0-9_]', '', feature_name.lower().replace(' ', '_'))
            
            features.append({
                "feature_name": feature_name.strip(),
                "feature_id": feature_id,
                "primary_goal": self._infer_goal_from_feature(feature_name, text),
                "secondary_goals": self._infer_secondary_goals(feature_name, text),
                "user_segments_most_relevant": ["all"],
                "engagement_driver_score": round(0.75 + (idx * 0.03), 2),
                "description": self._generate_feature_description(feature_name, text)
            })
        
        # Fallback if still no features
        if not features:
            features = self._get_default_features(text)
        
        return {"features": features}
    
    def _infer_features_from_domain(self, text: str) -> List[str]:
        """
        Infer likely features based on detected domain.
        Uses self.detected_domain for context-aware inference.
        """
        text_lower = text.lower()
        features = []
        domain = getattr(self, 'detected_domain', None) or 'generic'
        
        # Domain-specific feature inference
        domain_features = {
            'edtech': {
                'patterns': {
                    'ai|tutor|mentor': 'AI Tutor',
                    'leaderboard|rank|compete': 'Leaderboard',
                    'streak|daily|habit': 'Streak System',
                    'coin|reward|point': 'Rewards System',
                    'exercise|practice|quiz': 'Practice Exercises',
                    'progress|report|analytics': 'Progress Reports',
                    'gamif': 'Gamification Features'
                },
                'defaults': ['Learning Modules', 'Practice Mode', 'Progress Tracking']
            },
            'fintech': {
                'patterns': {
                    'wallet|balance': 'Digital Wallet',
                    'payment|pay': 'Payments',
                    'transfer|send': 'Money Transfer',
                    'cashback|reward': 'Cashback Rewards',
                    'bill|recharge': 'Bill Payments',
                    'invest|mutual|stock': 'Investments'
                },
                'defaults': ['Wallet', 'Payments', 'Transactions']
            },
            'entertainment': {
                'patterns': {
                    'recommend|discover': 'Recommendations',
                    'watchlist|save': 'Watchlist',
                    'download|offline': 'Downloads',
                    'profile|account': 'User Profiles',
                    'search|browse': 'Content Discovery'
                },
                'defaults': ['Content Library', 'Streaming', 'Personalization']
            },
            'ecommerce': {
                'patterns': {
                    'cart|basket': 'Shopping Cart',
                    'wishlist|save': 'Wishlist',
                    'checkout|buy': 'Checkout',
                    'track|delivery': 'Order Tracking',
                    'review|rating': 'Reviews & Ratings'
                },
                'defaults': ['Product Catalog', 'Shopping Cart', 'Order Management']
            },
            'health': {
                'patterns': {
                    'workout|exercise': 'Workouts',
                    'track|log': 'Activity Tracking',
                    'goal|target': 'Goal Setting',
                    'remind|notification': 'Health Reminders',
                    'meal|diet|nutrition': 'Nutrition Tracking'
                },
                'defaults': ['Activity Tracking', 'Health Dashboard', 'Goals']
            },
            'social': {
                'patterns': {
                    'feed|timeline': 'News Feed',
                    'message|chat': 'Messaging',
                    'profile|account': 'User Profiles',
                    'friend|connect': 'Connections',
                    'group|community': 'Communities'
                },
                'defaults': ['Feed', 'Messaging', 'Profiles']
            },
            'generic': {
                'patterns': {},
                'defaults': ['Core Feature', 'User Dashboard', 'Notifications']
            }
        }
        
        config = domain_features.get(domain, domain_features['generic'])
        
        # Try to match patterns from text
        for pattern, feature_name in config['patterns'].items():
            if re.search(pattern, text_lower):
                features.append(feature_name)
        
        # Add defaults if not enough features found
        if len(features) < 3:
            for default in config['defaults']:
                if default not in features:
                    features.append(default)
                    if len(features) >= 5:
                        break
        
        return features
    
    def _infer_goal_from_feature(self, feature_name: str, text: str) -> str:
        """
        Infer primary goal from feature name.
        Uses expanded keyword-to-goal mapping that covers multiple domains.
        """
        feature_lower = feature_name.lower()
        
        # Expanded goal mapping covering multiple domains
        goal_mapping = {
            # EdTech
            'tutor': 'skill_development',
            'learn': 'skill_development',
            'course': 'knowledge_acquisition',
            'practice': 'skill_mastery',
            'exercise': 'skill_development',
            'quiz': 'knowledge_assessment',
            'leaderboard': 'competitive_engagement',
            'streak': 'habit_formation',
            'coin': 'gamification_engagement',
            'reward': 'motivation',
            'badge': 'achievement_recognition',
            'progress': 'self_improvement',
            'report': 'performance_awareness',
            # FinTech
            'wallet': 'financial_convenience',
            'payment': 'transaction_completion',
            'transfer': 'money_movement',
            'invest': 'wealth_growth',
            'cashback': 'savings_motivation',
            'bill': 'utility_management',
            # Entertainment
            'content': 'entertainment',
            'watch': 'content_consumption',
            'stream': 'content_access',
            'recommend': 'content_discovery',
            'download': 'offline_access',
            'playlist': 'content_curation',
            # eCommerce
            'cart': 'purchase_facilitation',
            'wishlist': 'purchase_planning',
            'checkout': 'purchase_completion',
            'track': 'order_visibility',
            'review': 'social_proof',
            # Health
            'workout': 'fitness_improvement',
            'diet': 'health_management',
            'goal': 'achievement_tracking',
            'reminder': 'behavior_reinforcement',
            # Social
            'friend': 'social_connection',
            'message': 'communication',
            'feed': 'content_consumption',
            'community': 'belonging',
            # Generic
            'dashboard': 'information_access',
            'notification': 'engagement',
            'profile': 'identity_expression',
            'setting': 'personalization',
            'search': 'discovery',
            'ai': 'personalized_experience'
        }
        
        for keyword, goal in goal_mapping.items():
            if keyword in feature_lower:
                return goal
        
        return 'user_engagement'
    
    def _generate_feature_description(self, feature_name: str, text: str) -> str:
        """Generate a meaningful description for the feature based on context"""
        feature_lower = feature_name.lower()
        
        # Try to find description in text near the feature mention
        escaped_name = re.escape(feature_name[:15])
        context_match = re.search(rf"{escaped_name}[^.]*?([A-Z][^.]+\.)", text, re.IGNORECASE)
        if context_match:
            desc = context_match.group(1).strip()
            if 20 < len(desc) < 150:
                return desc
        
        # Generate based on feature type
        description_templates = {
            'tutor': 'AI-powered tutoring for personalized learning',
            'streak': 'Daily engagement tracking to build habits',
            'leaderboard': 'Competitive ranking to motivate users',
            'reward': 'Incentive system to drive engagement',
            'wallet': 'Digital wallet for seamless transactions',
            'payment': 'Quick and secure payment processing',
            'content': 'Rich content library for user engagement',
            'workout': 'Guided workout routines for fitness',
            'feed': 'Personalized content feed',
            'message': 'Real-time messaging functionality'
        }
        
        for keyword, desc in description_templates.items():
            if keyword in feature_lower:
                return desc
        
        return f"Feature enabling {feature_name.lower()} functionality"
    
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
        """
        Extract allowed tones and behavioral hooks.
        Tones come from config; Octalysis 8 Core Drives are universal behavioral 
        psychology principles (Yu-kai Chou, 2015) and are standardized.
        """
        # Generate domain-aware hook examples
        domain = getattr(self, 'detected_domain', 'generic')
        hook_examples = self._generate_hook_examples(domain)
        
        matrix = {
            "allowed_tones": self.allowed_tones,
            "forbidden_tones": self.forbidden_tones,
            "tone_by_lifecycle": self.tone_by_lifecycle,
            "detected_domain": domain,
            "octalysis_hooks": {
                "epic_meaning": {
                    "description": "Be part of something bigger",
                    "examples": hook_examples.get('epic_meaning', ["Join millions of users", "Transform your life", "Unlock your potential"]),
                    "best_for_segments": ["aspirational", "purpose_driven"]
                },
                "accomplishment": {
                    "description": "Make progress and achieve",
                    "examples": hook_examples.get('accomplishment', ["Complete your goal", "Reach the milestone", "Earn rewards"]),
                    "best_for_segments": ["achievers", "goal_oriented"]
                },
                "empowerment": {
                    "description": "Have control and experiment",
                    "examples": hook_examples.get('empowerment', ["Choose your path", "Customize your experience", "Do it your way"]),
                    "best_for_segments": ["casual", "explorers"]
                },
                "ownership": {
                    "description": "Build something valuable",
                    "examples": hook_examples.get('ownership', ["Your progress", "Your collection", "Your achievements"]),
                    "best_for_segments": ["achievers", "collectors"]
                },
                "social_influence": {
                    "description": "Others are doing it",
                    "examples": hook_examples.get('social_influence', ["Join top users", "See what others do", "Compare with friends"]),
                    "best_for_segments": ["social", "community_driven"]
                },
                "scarcity": {
                    "description": "Limited time or availability",
                    "examples": hook_examples.get('scarcity', ["Only hours left", "Last chance", "Limited offer"]),
                    "best_for_segments": ["achievers", "fomo_driven"]
                },
                "unpredictability": {
                    "description": "What will happen next",
                    "examples": hook_examples.get('unpredictability', ["Unlock surprise", "Discover something new", "See what's next"]),
                    "best_for_segments": ["explorers", "casual"]
                },
                "loss_avoidance": {
                    "description": "Don't lose what you have",
                    "examples": hook_examples.get('loss_avoidance', ["Don't lose progress", "Maintain your status", "Keep your streak"]),
                    "best_for_segments": ["achievers", "at_risk"]
                }
            },
            "hooks_by_segment": {
                "achievers": ["accomplishment", "ownership", "loss_avoidance"],
                "social_competitors": ["social_influence", "accomplishment", "scarcity"],
                "casual_learners": ["unpredictability", "empowerment", "epic_meaning"],
                "at_risk_churners": ["loss_avoidance", "scarcity", "social_influence"],
                "dormant_users": ["unpredictability", "epic_meaning", "empowerment"]
            }
        }
        
        return matrix
    
    def _generate_hook_examples(self, domain: str) -> Dict[str, List[str]]:
        """Generate domain-specific examples for Octalysis hooks"""
        
        domain_examples = {
            'edtech': {
                'epic_meaning': ["Join 1M+ learners", "Transform your skills", "Unlock your potential"],
                'accomplishment': ["Complete 10 lessons", "Reach 7-day streak", "Earn 100 coins"],
                'empowerment': ["Choose your topic", "Learn at your pace", "Customize your path"],
                'ownership': ["Your 500 coins", "Your 30-day streak", "Your certificates"],
                'social_influence': ["Beat the leaderboard", "Join top learners", "Compete with friends"],
                'scarcity': ["Only 3 hours left", "Limited seats", "Today's bonus expires"],
                'unpredictability': ["Unlock surprise reward", "Daily bonus waiting", "New content unlocked"],
                'loss_avoidance': ["Streak will break", "Don't lose progress", "Maintain your rank"]
            },
            'fintech': {
                'epic_meaning': ["Join millions saving smart", "Financial freedom awaits", "Be money smart"],
                'accomplishment': ["Saved ₹10,000", "100 transactions done", "Gold member unlocked"],
                'empowerment': ["Your money, your rules", "Invest your way", "Control your finances"],
                'ownership': ["Your savings: ₹50K", "Your cashback earned", "Your portfolio"],
                'social_influence': ["Friends using this", "Top savers this month", "Trusted by millions"],
                'scarcity': ["Offer ends tonight", "Limited cashback", "Last chance for bonus"],
                'unpredictability': ["Scratch and win", "Surprise cashback", "Lucky draw entry"],
                'loss_avoidance': ["Cashback expiring", "Don't miss savings", "Bill overdue"]
            },
            'entertainment': {
                'epic_meaning': ["Join the community", "Be part of the fandom", "Experience the best"],
                'accomplishment': ["Watched 100 hours", "Completed the series", "Top fan badge"],
                'empowerment': ["Watch anywhere", "Your playlist", "Skip the ads"],
                'ownership': ["Your watchlist", "Your favorites", "Your downloads"],
                'social_influence': ["Trending now", "Friends are watching", "Most popular"],
                'scarcity': ["Leaving soon", "Limited release", "Premium only"],
                'unpredictability': ["New releases", "Surprise drop", "What's next"],
                'loss_avoidance': ["Continue watching", "Don't miss finale", "Expires soon"]
            },
            'ecommerce': {
                'epic_meaning': ["Shop smart, save big", "Join happy shoppers", "Best deals await"],
                'accomplishment': ["100 orders placed", "Platinum member", "Top reviewer"],
                'empowerment': ["Shop your way", "Easy returns", "Your choices"],
                'ownership': ["Your wishlist", "Your rewards", "Your savings"],
                'social_influence': ["Best seller", "Highly rated", "Others bought"],
                'scarcity': ["Only 3 left", "Sale ends soon", "Flash deal"],
                'unpredictability': ["Mystery discount", "Surprise offer", "Lucky coupon"],
                'loss_avoidance': ["Price drop alert", "Cart expiring", "Almost sold out"]
            },
            'health': {
                'epic_meaning': ["Join the healthy movement", "Transform your life", "Be your best self"],
                'accomplishment': ["30-day streak", "Goal achieved", "Personal best"],
                'empowerment': ["Your fitness journey", "Your pace", "Your goals"],
                'ownership': ["Your progress", "Your records", "Your achievements"],
                'social_influence': ["Top performers", "Friends active", "Community challenge"],
                'scarcity': ["Challenge ends soon", "Limited spots", "This week only"],
                'unpredictability': ["New workout unlocked", "Bonus points", "Surprise reward"],
                'loss_avoidance': ["Streak at risk", "Don't lose progress", "Stay on track"]
            }
        }
        
        return domain_examples.get(domain, {
            'epic_meaning': ["Join millions", "Be part of something big", "Transform your experience"],
            'accomplishment': ["Complete goals", "Earn rewards", "Level up"],
            'empowerment': ["Your way", "Your choice", "Customize"],
            'ownership': ["Your progress", "Your achievements", "Your journey"],
            'social_influence': ["Others are here", "Join top users", "Trending"],
            'scarcity': ["Limited time", "Act now", "Ends soon"],
            'unpredictability': ["Surprise waiting", "Discover more", "What's next"],
            'loss_avoidance': ["Don't miss out", "Keep going", "Stay active"]
        })
    
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
        
        print(f"[OK] Knowledge Bank outputs saved to {output_dir}")

