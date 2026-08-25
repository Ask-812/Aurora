"""
Metrics calculation utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class MetricsCalculator:
    """Calculate various metrics for users and templates"""
    
    @staticmethod
    def normalize(series: pd.Series) -> pd.Series:
        """Min-max normalization to 0-1 range"""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([0.5] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val)
    
    @staticmethod
    def calculate_activeness(df: pd.DataFrame) -> pd.Series:
        """Original edtech-specific activeness."""
        sessions_norm = MetricsCalculator.normalize(df['sessions_last_7d'])
        exercises_norm = MetricsCalculator.normalize(df['exercises_completed_7d'])
        notif_open = df.get('notif_open_rate_30d', pd.Series([0.5] * len(df)))
        has_streak = (df.get('streak_current', pd.Series([0] * len(df))) > 0).astype(float)
        
        return 0.3 * sessions_norm + 0.3 * exercises_norm + 0.2 * notif_open + 0.2 * has_streak

    @staticmethod
    def calculate_activeness_dynamic(df: pd.DataFrame, schema_map: Dict[str, Any]) -> pd.Series:
        """Calculate activeness using any number of identified activity columns."""
        activity_cols = schema_map.get('activeness_metrics', []) or []
        if not activity_cols:
            return pd.Series([0.5] * len(df), index=df.index)
        
        scores = []
        for col in activity_cols:
            if col in df.columns:
                scores.append(MetricsCalculator.normalize(df[col]))
        
        if not scores:
            return pd.Series([0.5] * len(df), index=df.index)
            
        return pd.concat(scores, axis=1).mean(axis=1)
    
    @staticmethod
    def calculate_gamification_propensity(df: pd.DataFrame) -> pd.Series:
        """Original edtech gamification propensity."""
        streak_norm = MetricsCalculator.normalize(df.get('streak_current', pd.Series([0] * len(df))))
        coins_norm = MetricsCalculator.normalize(df.get('coins_balance', pd.Series([0] * len(df))))
        feature_cols = [c for c in df.columns if c.startswith('feature_') and c.endswith('_used')]
        feature_usage = df[feature_cols].astype(float).mean(axis=1) if feature_cols else 0.0
        return 0.4 * streak_norm + 0.3 * coins_norm + 0.3 * feature_usage

    @staticmethod
    def calculate_gamification_propensity_dynamic(df: pd.DataFrame, schema_map: Dict[str, Any]) -> pd.Series:
        """Propensity based on value and feature flags."""
        val_cols = schema_map.get('value_metrics', []) or []
        feat_cols = schema_map.get('feature_flags', []) or []
        
        scores = []
        for col in list(val_cols or []) + list(feat_cols or []):
            if col in df.columns:
                scores.append(MetricsCalculator.normalize(df[col].astype(float)))
        
        if not scores:
            return pd.Series([0.3] * len(df), index=df.index)
        return pd.concat(scores, axis=1).mean(axis=1)
    
    @staticmethod
    def calculate_social_propensity(df: pd.DataFrame) -> pd.Series:
        """Original social propensity."""
        social_feature_cols = [c for c in df.columns if c.startswith('feature_') and 
                               any(kw in c.lower() for kw in ['leaderboard', 'social', 'share'])]
        social_features = df[social_feature_cols].astype(float).mean(axis=1) if social_feature_cols else 0.0
        sessions_norm = MetricsCalculator.normalize(df['sessions_last_7d'])
        return 0.5 * social_features + 0.5 * sessions_norm

    @staticmethod
    def calculate_social_propensity_dynamic(df: pd.DataFrame, schema_map: Dict[str, Any]) -> pd.Series:
        """Map to features with social keywords in names or as defined in mapping."""
        feat_cols = schema_map.get('feature_flags', []) or []
        social_keywords = ['social', 'friend', 'share', 'leaderboard', 'group', 'community', 'gold']
        social_cols = [c for c in feat_cols if any(kw in c.lower() for kw in social_keywords)]
        
        if not social_cols:
            return pd.Series([0.2] * len(df), index=df.index)
            
        return df[social_cols].astype(float).mean(axis=1)
    
    @staticmethod
    def calculate_ai_tutor_propensity_dynamic(df: pd.DataFrame, schema_map: Dict[str, Any]) -> pd.Series:
        """Personalization/AI propensity."""
        feat_cols = schema_map.get('feature_flags', []) or []
        ai_keywords = ['ai', 'search', 'find', 'recommend', 'personal', 'tutor', 'gold']
        ai_cols = [c for c in feat_cols if any(kw in c.lower() for kw in ai_keywords)]
        
        if not ai_cols:
            return pd.Series([0.2] * len(df), index=df.index)
            
        return df[ai_cols].astype(float).mean(axis=1)

    @staticmethod
    def calculate_leaderboard_propensity_dynamic(df: pd.DataFrame, schema_map: Dict[str, Any]) -> pd.Series:
        """Competitiveness-based."""
        ret_cols = schema_map.get('retention_metrics', []) or []
        val_cols = schema_map.get('value_metrics', []) or []
        
        scores = []
        for col in list(ret_cols or []) + list(val_cols or []):
            if col in df.columns:
                scores.append(MetricsCalculator.normalize(df[col].astype(float)))
        
        if not scores:
            return pd.Series([0.4] * len(df), index=df.index)
        return pd.concat(scores, axis=1).mean(axis=1)
    
    @staticmethod
    def calculate_leaderboard_propensity(df: pd.DataFrame) -> pd.Series:
        """Original leaderboard propensity."""
        leaderboard_cols = [c for c in df.columns if c.startswith('feature_') and 
                            any(kw in c.lower() for kw in ['leaderboard', 'rank', 'compete', 'score'])]
        leaderboard_features = df[leaderboard_cols].astype(float).mean(axis=1) if leaderboard_cols else 0.0
        streak_norm = MetricsCalculator.normalize(df.get('streak_current', pd.Series([0] * len(df))))
        gamification = MetricsCalculator.calculate_gamification_propensity(df)
        return 0.5 * leaderboard_features + 0.3 * streak_norm + 0.2 * gamification
    
    @staticmethod
    def calculate_churn_risk(df: pd.DataFrame) -> pd.Series:
        """Original churn risk."""
        sessions_norm = MetricsCalculator.normalize(df['sessions_last_7d'])
        notif_open = df.get('notif_open_rate_30d', pd.Series([0.5] * len(df)))
        no_streak = (df['streak_current'] == 0).astype(float) if 'streak_current' in df.columns else pd.Series([0.5] * len(df), index=df.index)
        return 0.4 * (1 - sessions_norm) + 0.3 * (1 - notif_open) + 0.3 * no_streak

    @staticmethod
    def calculate_churn_risk_dynamic(df: pd.DataFrame, schema_map: Dict[str, Any]) -> pd.Series:
        """Inversely related to activeness and retention."""
        activeness = MetricsCalculator.calculate_activeness_dynamic(df, schema_map)
        ret_cols = schema_map.get('retention_metrics', []) or []
        if ret_cols:
            retention = df[ret_cols].astype(float).mean(axis=1)
            retention_norm = MetricsCalculator.normalize(retention)
        else:
            retention_norm = 0.5
            
        churn_risk = 0.6 * (1 - activeness) + 0.4 * (1 - retention_norm)
        return churn_risk
    
    @staticmethod
    def calculate_ctr(total_opens: int, total_sends: int) -> float:
        """Calculate Click-Through Rate"""
        if total_sends == 0:
            return 0.0
        return total_opens / total_sends
    
    @staticmethod
    def calculate_engagement_rate(total_engagements: int, total_opens: int) -> float:
        """Calculate Engagement Rate"""
        if total_opens == 0:
            return 0.0
        return total_engagements / total_opens
    
    @staticmethod
    def classify_performance(ctr: float, engagement_rate: float, 
                           good_ctr: float = 0.15, good_engagement: float = 0.40,
                           bad_ctr: float = 0.05, bad_engagement: float = 0.20) -> str:
        """
        Classify template performance
        
        Returns: 'GOOD', 'NEUTRAL', or 'BAD'
        """
        if ctr > good_ctr and engagement_rate > good_engagement:
            return 'GOOD'
        elif ctr < bad_ctr or engagement_rate < bad_engagement:
            return 'BAD'
        else:
            return 'NEUTRAL'

