"""
NLP-Based Template Optimization
- TF-IDF and semantic similarity analysis
- Sentiment scoring
- Topic modeling for theme effectiveness
- Message pattern analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class NLPTemplateOptimizer:
    """
    Advanced NLP analysis for template optimization
    """
    
    def __init__(self):
        self.vectorizer = None
        self.template_vectors = None
        self.sentiment_lexicon = self._build_sentiment_lexicon()
        self.engagement_keywords = self._build_engagement_keywords()
        
    def _build_sentiment_lexicon(self) -> Dict[str, float]:
        """Build sentiment lexicon for template analysis"""
        # Positive sentiment words
        positive = {
            'congratulations': 1.0, 'great': 0.8, 'awesome': 0.9,
            'amazing': 0.9, 'excellent': 0.9, 'fantastic': 0.9,
            'perfect': 0.8, 'successful': 0.7, 'achievement': 0.7,
            'progress': 0.6, 'improve': 0.6, 'win': 0.8,
            'reward': 0.7, 'unlock': 0.6, 'earn': 0.5,
            'celebrate': 0.8, 'proud': 0.7, 'ahead': 0.6
        }
        
        # Negative sentiment words
        negative = {
            'lose': -0.8, 'miss': -0.6, 'break': -0.7,
            'risk': -0.5, 'behind': -0.6, 'falling': -0.7,
            'waste': -0.8, 'expire': -0.6, 'fail': -0.9,
            'don\'t': -0.3, 'only': -0.2, 'last': -0.3
        }
        
        # Action/urgency words (neutral but important)
        action = {
            'now': 0.4, 'today': 0.4, 'complete': 0.5,
            'join': 0.5, 'practice': 0.4, 'continue': 0.4,
            'start': 0.5, 'maintain': 0.3, 'keep': 0.3
        }
        
        return {**positive, **negative, **action}
    
    def _build_engagement_keywords(self) -> Dict[str, float]:
        """Build engagement-driving keywords with weights"""
        return {
            # Gamification
            'streak': 0.8, 'coins': 0.7, 'reward': 0.8,
            'unlock': 0.7, 'level': 0.7, 'badge': 0.6,
            
            # Social proof
            'users': 0.7, 'rank': 0.8, 'leaderboard': 0.8,
            'ahead': 0.7, 'beat': 0.7, 'compete': 0.6,
            
            # Urgency
            'today': 0.6, 'now': 0.7, 'hours': 0.6,
            'last': 0.5, 'only': 0.6, 'final': 0.7,
            
            # Progress
            'completed': 0.6, 'progress': 0.7, 'day': 0.5,
            'exercises': 0.6, 'practice': 0.5,
            
            # Personalization
            'your': 0.4, 'you': 0.3
        }
    
    def analyze_templates(self, 
                         templates: pd.DataFrame,
                         experiment_results: pd.DataFrame = None) -> pd.DataFrame:
        """
        Perform comprehensive NLP analysis on templates
        
        Args:
            templates: DataFrame with template content
            experiment_results: Optional performance data
            
        Returns:
            DataFrame with NLP features and scores
        """
        print("\n📝 NLP Template Analysis...")
        
        templates = templates.copy()
        
        # Create combined content column for analysis (use English columns)
        # Support both old 'content' column and new bilingual columns
        if 'content' not in templates.columns:
            # New schema: combine title + body + CTA
            templates['content'] = (
                templates.get('message_title_en', '').fillna('') + ' ' +
                templates.get('message_body_en', '').fillna('') + ' ' +
                templates.get('cta_text_en', '').fillna('')
            ).str.strip()
        
        # Basic text features
        templates['word_count'] = templates['content'].apply(self._count_words)
        templates['char_count'] = templates['content'].apply(len)
        templates['avg_word_length'] = templates['content'].apply(self._avg_word_length)
        
        # Sentiment analysis
        templates['sentiment_score'] = templates['content'].apply(self._calculate_sentiment)
        templates['positive_ratio'] = templates['content'].apply(self._positive_ratio)
        templates['negative_ratio'] = templates['content'].apply(self._negative_ratio)
        
        # Engagement features
        templates['engagement_score'] = templates['content'].apply(self._calculate_engagement_score)
        templates['urgency_score'] = templates['content'].apply(self._calculate_urgency_score)
        templates['personalization_score'] = templates['content'].apply(self._calculate_personalization_score)
        
        # Pattern analysis
        templates['has_emoji'] = templates['content'].apply(self._has_emoji)
        templates['has_numbers'] = templates['content'].apply(self._has_numbers)
        templates['has_question'] = templates['content'].apply(lambda x: '?' in x)
        templates['has_exclamation'] = templates['content'].apply(lambda x: '!' in x)
        
        # TF-IDF analysis
        if SKLEARN_AVAILABLE:
            templates = self._add_tfidf_features(templates)
        
        # If experiment results available, analyze performance correlation
        if experiment_results is not None:
            templates = self._analyze_performance_correlation(templates, experiment_results)
        
        print(f"   [OK] Analyzed {len(templates)} templates")
        print(f"   [OK] Avg sentiment: {templates['sentiment_score'].mean():.3f}")
        print(f"   [OK] Avg engagement score: {templates['engagement_score'].mean():.3f}")
        
        return templates
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def _avg_word_length(self, text: str) -> float:
        """Calculate average word length"""
        words = text.split()
        if len(words) == 0:
            return 0
        return sum(len(word) for word in words) / len(words)
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        scores = [
            self.sentiment_lexicon.get(word, 0)
            for word in words
        ]
        
        if len(scores) == 0:
            return 0.0
        
        return sum(scores) / len(words)
    
    def _positive_ratio(self, text: str) -> float:
        """Calculate ratio of positive words"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = sum(
            1 for word in words
            if self.sentiment_lexicon.get(word, 0) > 0
        )
        
        return positive_count / len(words) if words else 0
    
    def _negative_ratio(self, text: str) -> float:
        """Calculate ratio of negative words"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        negative_count = sum(
            1 for word in words
            if self.sentiment_lexicon.get(word, 0) < 0
        )
        
        return negative_count / len(words) if words else 0
    
    def _calculate_engagement_score(self, text: str) -> float:
        """Calculate engagement potential score"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        scores = [
            self.engagement_keywords.get(word, 0)
            for word in words
        ]
        
        if len(scores) == 0:
            return 0.0
        
        return sum(scores) / len(words)
    
    def _calculate_urgency_score(self, text: str) -> float:
        """Calculate urgency score"""
        urgency_words = ['now', 'today', 'hours', 'last', 'only', 'final', 'don\'t lose']
        text_lower = text.lower()
        
        count = sum(1 for word in urgency_words if word in text_lower)
        
        # Bonus for specific patterns
        if 'will break' in text_lower or 'will lose' in text_lower:
            count += 2
        
        return min(count / 3.0, 1.0)  # Normalize to 0-1
    
    def _calculate_personalization_score(self, text: str) -> float:
        """Calculate personalization score"""
        personal_pronouns = ['your', 'you', 'you\'ve', 'you\'re']
        text_lower = text.lower()
        words = text_lower.split()
        
        count = sum(1 for word in words if word in personal_pronouns)
        
        return min(count / len(words) * 10, 1.0)  # Normalize
    
    def _has_emoji(self, text: str) -> bool:
        """Check if text contains emoji"""
        # Simple emoji detection (Unicode ranges)
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
            "\U0001F680-\U0001F6FF"  # Transport & Map
            "\U0001F1E0-\U0001F1FF"  # Flags
            "]+", flags=re.UNICODE
        )
        return bool(emoji_pattern.search(text))
    
    def _has_numbers(self, text: str) -> bool:
        """Check if text contains numbers"""
        return bool(re.search(r'\d', text))
    
    def _add_tfidf_features(self, templates: pd.DataFrame) -> pd.DataFrame:
        """Add TF-IDF based features"""
        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        try:
            self.template_vectors = self.vectorizer.fit_transform(
                templates['content'].fillna('')
            )
            
            # Calculate average TF-IDF score
            templates['avg_tfidf_score'] = np.array(
                self.template_vectors.mean(axis=1)
            ).flatten()
            
        except Exception as e:
            print(f"   ⚠️  TF-IDF analysis failed: {e}")
            templates['avg_tfidf_score'] = 0.0
        
        return templates
    
    def _analyze_performance_correlation(self,
                                        templates: pd.DataFrame,
                                        experiment_results: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze correlation between NLP features and performance
        """
        # Merge with performance data
        merged = templates.merge(
            experiment_results[['template_id', 'ctr', 'engagement_rate']],
            on='template_id',
            how='left'
        )
        
        # Calculate correlations
        nlp_features = [
            'word_count', 'sentiment_score', 'engagement_score',
            'urgency_score', 'personalization_score'
        ]
        
        correlations = {}
        for feature in nlp_features:
            if feature in merged.columns:
                corr = merged[[feature, 'ctr']].corr().iloc[0, 1]
                correlations[feature] = corr if not np.isnan(corr) else 0
        
        print(f"\n   [Stats] Feature-Performance Correlations:")
        for feature, corr in sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True):
            print(f"      {feature}: {corr:.3f}")
        
        return templates
    
    def find_similar_templates(self,
                              template_id: str,
                              templates: pd.DataFrame,
                              top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Find similar templates using cosine similarity
        
        Args:
            template_id: Reference template ID
            templates: DataFrame with all templates
            top_n: Number of similar templates to return
            
        Returns:
            List of (template_id, similarity_score) tuples
        """
        if self.template_vectors is None:
            return []
        
        # Find index of reference template
        try:
            idx = templates[templates['template_id'] == template_id].index[0]
        except IndexError:
            return []
        
        # Calculate similarities
        similarities = cosine_similarity(
            self.template_vectors[idx:idx+1],
            self.template_vectors
        )[0]
        
        # Get top N (excluding self)
        similar_indices = np.argsort(similarities)[::-1][1:top_n+1]
        
        results = [
            (templates.iloc[i]['template_id'], similarities[i])
            for i in similar_indices
        ]
        
        return results
    
    def generate_optimization_recommendations(self,
                                            templates: pd.DataFrame,
                                            experiment_results: pd.DataFrame) -> pd.DataFrame:
        """
        Generate actionable recommendations for template optimization
        
        Args:
            templates: Analyzed templates
            experiment_results: Performance data
            
        Returns:
            DataFrame with recommendations
        """
        print("\n💡 Generating Optimization Recommendations...")
        
        # Merge with performance
        merged = templates.merge(
            experiment_results[['template_id', 'ctr', 'engagement_rate', 'performance_status']],
            on='template_id',
            how='left'
        )
        
        recommendations = []
        
        for _, row in merged.iterrows():
            recs = []
            
            # Word count recommendations
            if row['word_count'] > 20:
                recs.append("Shorten message (< 15 words)")
            elif row['word_count'] < 8:
                recs.append("Add more context")
            
            # Sentiment recommendations
            if row['sentiment_score'] < 0:
                recs.append("Increase positive sentiment")
            
            # Engagement recommendations
            if row['engagement_score'] < 0.1:
                recs.append("Add engagement keywords (streak, coins, etc.)")
            
            # Personalization
            if row['personalization_score'] < 0.1:
                recs.append("Add personalization (your, you)")
            
            # Urgency
            if row['urgency_score'] < 0.2 and row.get('performance_status') == 'BAD':
                recs.append("Add urgency elements")
            
            recommendations.append({
                'template_id': row['template_id'],
                'current_ctr': row.get('ctr', 0),
                'recommendations': '; '.join(recs) if recs else 'Template is well-optimized',
                'priority': 'HIGH' if row.get('performance_status') == 'BAD' else 'LOW'
            })
        
        df_recs = pd.DataFrame(recommendations)
        
        print(f"   [OK] Generated recommendations for {len(df_recs)} templates")
        
        return df_recs

