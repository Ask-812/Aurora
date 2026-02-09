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
        
        Formula: 0.4*streak + 0.3*coins + 0.3*feature_usage
        """
        streak_norm = MetricsCalculator.normalize(df.get('streak_current', pd.Series([0] * len(df))))
        coins_norm = MetricsCalculator.normalize(df.get('coins_balance', pd.Series([0] * len(df))))
        feature_usage = df.get('feature_ai_tutor_used', pd.Series([False] * len(df))).astype(float)
        
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
        
        Formula: 0.6*leaderboard_viewed + 0.4*sessions
        """
        leaderboard = df.get('feature_leaderboard_viewed', pd.Series([False] * len(df))).astype(float)
        sessions_norm = MetricsCalculator.normalize(df['sessions_last_7d'])
        
        social = (
            0.6 * leaderboard +
            0.4 * sessions_norm
        )
        
        return social
    
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
