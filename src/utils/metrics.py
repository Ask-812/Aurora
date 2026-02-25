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
        """
        Calculate activeness score (0-1)
        
        Formula: 0.3*sessions + 0.3*exercises + 0.2*notif_open + 0.2*has_streak
        """
        sessions_norm = MetricsCalculator.normalize(df['sessions_last_7d'])
        exercises_norm = MetricsCalculator.normalize(df['exercises_completed_7d'])
        
        notif_open = df.get('notif_open_rate_30d', pd.Series([0.5] * len(df)))
        has_streak = (df.get('streak_current', pd.Series([0] * len(df))) > 0).astype(float)
        
        activeness = (
            0.3 * sessions_norm +
            0.3 * exercises_norm +
            0.2 * notif_open +
            0.2 * has_streak
        )
        
        return activeness
    
    @staticmethod
    def calculate_gamification_propensity(df: pd.DataFrame) -> pd.Series:
        """
        Calculate gamification propensity score (0-1)
        
        Formula: 0.4*streak + 0.3*coins + 0.3*avg_feature_usage
        Uses any feature_*_used columns dynamically
        """
        streak_norm = MetricsCalculator.normalize(df.get('streak_current', pd.Series([0] * len(df))))
        coins_norm = MetricsCalculator.normalize(df.get('coins_balance', pd.Series([0] * len(df))))
        
        # Find all feature_*_used columns dynamically
        feature_cols = [c for c in df.columns if c.startswith('feature_') and c.endswith('_used')]
        if feature_cols:
            feature_usage = df[feature_cols].astype(float).mean(axis=1)
        else:
            feature_usage = pd.Series([0.0] * len(df), index=df.index)
        
        gamification = (
            0.4 * streak_norm +
            0.3 * coins_norm +
            0.3 * feature_usage
        )
        
        return gamification
    
    @staticmethod
    def calculate_social_propensity(df: pd.DataFrame) -> pd.Series:
        """
        Calculate social propensity score (0-1)
        
        Formula: 0.5*social_features + 0.5*sessions
        Detects leaderboard/social features dynamically
        """
        # Find social-related feature columns dynamically
        social_feature_cols = [c for c in df.columns if c.startswith('feature_') and 
                               any(kw in c.lower() for kw in ['leaderboard', 'social', 'share'])]
        if social_feature_cols:
            social_features = df[social_feature_cols].astype(float).mean(axis=1)
        else:
            social_features = pd.Series([0.0] * len(df), index=df.index)
        
        sessions_norm = MetricsCalculator.normalize(df['sessions_last_7d'])
        
        social = (
            0.5 * social_features +
            0.5 * sessions_norm
        )
        
        return social
    
    @staticmethod
    def calculate_ai_tutor_propensity(df: pd.DataFrame) -> pd.Series:
        """
        Calculate AI tutor propensity score (0-1)
        
        Users with high AI tutor usage + high conversation engagement
        Formula: 0.6*ai_tutor_features + 0.2*exercises + 0.2*activeness
        """
        # Find AI tutor related feature columns dynamically
        ai_tutor_cols = [c for c in df.columns if c.startswith('feature_') and 
                         any(kw in c.lower() for kw in ['ai_tutor', 'tutor', 'conversation', 'ai'])]
        if ai_tutor_cols:
            ai_tutor_features = df[ai_tutor_cols].astype(float).mean(axis=1)
        else:
            ai_tutor_features = pd.Series([0.0] * len(df), index=df.index)
        
        exercises_norm = MetricsCalculator.normalize(df['exercises_completed_7d'])
        activeness = MetricsCalculator.calculate_activeness(df)
        
        ai_tutor_propensity = (
            0.6 * ai_tutor_features +
            0.2 * exercises_norm +
            0.2 * activeness
        )
        
        return ai_tutor_propensity
    
    @staticmethod
    def calculate_leaderboard_propensity(df: pd.DataFrame) -> pd.Series:
        """
        Calculate leaderboard propensity score (0-1)
        
        Users who are competitive and engage with leaderboards
        Formula: 0.5*leaderboard_features + 0.3*streak + 0.2*gamification
        """
        # Find leaderboard related feature columns dynamically
        leaderboard_cols = [c for c in df.columns if c.startswith('feature_') and 
                            any(kw in c.lower() for kw in ['leaderboard', 'rank', 'compete', 'score'])]
        if leaderboard_cols:
            leaderboard_features = df[leaderboard_cols].astype(float).mean(axis=1)
        else:
            leaderboard_features = pd.Series([0.0] * len(df), index=df.index)
        
        streak_norm = MetricsCalculator.normalize(df.get('streak_current', pd.Series([0] * len(df))))
        gamification = MetricsCalculator.calculate_gamification_propensity(df)
        
        leaderboard_propensity = (
            0.5 * leaderboard_features +
            0.3 * streak_norm +
            0.2 * gamification
        )
        
        return leaderboard_propensity
    
    @staticmethod
    def calculate_churn_risk(df: pd.DataFrame) -> pd.Series:
        """
        Calculate churn risk score (0-1, higher = more risk)
        
        Formula: 0.4*(1-sessions) + 0.3*(1-notif_open) + 0.3*no_streak
        """
        sessions_norm = MetricsCalculator.normalize(df['sessions_last_7d'])
        notif_open = df.get('notif_open_rate_30d', pd.Series([0.5] * len(df)))
        no_streak = (df.get('streak_current', pd.Series([0] * len(df))) == 0).astype(float)
        
        churn_risk = (
            0.4 * (1 - sessions_norm) +
            0.3 * (1 - notif_open) +
            0.3 * no_streak
        )
        
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

