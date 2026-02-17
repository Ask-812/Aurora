"""
Data validation utilities
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class DataValidator:
    """Validates input data schemas and quality"""
    
    REQUIRED_USER_COLUMNS = [
        'user_id', 'lifecycle_stage', 'days_since_signup',
        'sessions_last_7d', 'exercises_completed_7d'
    ]
    
    OPTIONAL_USER_COLUMNS = [
        'age_band_region', 'streak_current', 'coins_balance',
        'feature_ai_tutor_used', 'feature_leaderboard_viewed',
        'preferred_hour', 'notif_open_rate_30d', 'motivation_score'
    ]
    
    VALID_LIFECYCLE_STAGES = ['trial', 'paid', 'churned', 'inactive']
    
    @staticmethod
    def validate_user_data(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate user data CSV
        
        Returns:
            dict: Validation results with 'valid' flag and 'errors' list
        """
        errors = []
        warnings = []
        
        # Check required columns
        missing_cols = set(DataValidator.REQUIRED_USER_COLUMNS) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for duplicates
        if df['user_id'].duplicated().any():
            duplicates = df[df['user_id'].duplicated()]['user_id'].tolist()
            errors.append(f"Duplicate user_ids found: {duplicates[:5]}...")
        
        # Validate lifecycle stages
        invalid_stages = df[~df['lifecycle_stage'].isin(DataValidator.VALID_LIFECYCLE_STAGES)]
        if len(invalid_stages) > 0:
            errors.append(f"Invalid lifecycle stages found: {invalid_stages['lifecycle_stage'].unique()}")
        
        # Validate numeric ranges
        if 'preferred_hour' in df.columns:
            invalid_hours = df[(df['preferred_hour'] < 0) | (df['preferred_hour'] > 23)]
            if len(invalid_hours) > 0:
                errors.append(f"Invalid preferred_hour values (must be 0-23): {len(invalid_hours)} rows")
        
        if 'notif_open_rate_30d' in df.columns:
            invalid_rates = df[(df['notif_open_rate_30d'] < 0) | (df['notif_open_rate_30d'] > 1)]
            if len(invalid_rates) > 0:
                errors.append(f"Invalid notif_open_rate_30d values (must be 0-1): {len(invalid_rates)} rows")
        
        # Check for missing data
        for col in DataValidator.REQUIRED_USER_COLUMNS:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                warnings.append(f"Column '{col}' has {missing_count} missing values ({missing_count/len(df)*100:.1f}%)")
        
        # Check for outliers
        if 'sessions_last_7d' in df.columns:
            high_sessions = df[df['sessions_last_7d'] > 50]
            if len(high_sessions) > 0:
                warnings.append(f"{len(high_sessions)} users have >50 sessions/week (possible bots or data errors)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_users': len(df),
            'columns': list(df.columns)
        }
    
    @staticmethod
    def validate_experiment_results(df: pd.DataFrame) -> Dict[str, Any]:
        """Validate experiment results CSV"""
        errors = []
        warnings = []
        
        required_cols = [
            'template_id', 'segment_id', 'lifecycle_stage', 'goal', 'theme',
            'notification_window', 'total_sends', 'total_opens', 'total_engagements',
            'ctr', 'engagement_rate', 'uninstall_rate'
        ]
        
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate metrics
        if (df['ctr'] < 0).any() or (df['ctr'] > 1).any():
            errors.append("CTR values must be between 0 and 1")
        
        if (df['engagement_rate'] < 0).any() or (df['engagement_rate'] > 1).any():
            errors.append("Engagement rate values must be between 0 and 1")
        
        # Check for statistical significance
        low_sends = df[df['total_sends'] < 100]
        if len(low_sends) > 0:
            warnings.append(f"{len(low_sends)} templates have <100 sends (may lack statistical significance)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_templates': len(df)
        }
    
    @staticmethod
    def clean_user_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and handle missing data in user DataFrame"""
        df = df.copy()
        
        # Handle missing numeric values with median
        numeric_cols = ['sessions_last_7d', 'exercises_completed_7d', 'streak_current', 
                       'coins_balance', 'notif_open_rate_30d', 'motivation_score']
        
        for col in numeric_cols:
            if col in df.columns and df[col].isna().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
        
        # Handle missing boolean values with False (conservative)
        bool_cols = ['feature_ai_tutor_used', 'feature_leaderboard_viewed']
        for col in bool_cols:
            if col in df.columns and df[col].isna().any():
                df[col].fillna(False, inplace=True)
        
        # Handle missing categorical with mode
        if 'lifecycle_stage' in df.columns and df['lifecycle_stage'].isna().any():
            mode_val = df['lifecycle_stage'].mode()[0]
            df['lifecycle_stage'].fillna(mode_val, inplace=True)
        
        # Handle missing preferred_hour with 19 (evening, common time)
        if 'preferred_hour' in df.columns and df['preferred_hour'].isna().any():
            df['preferred_hour'].fillna(19, inplace=True)
        
        # Cap outliers
        if 'sessions_last_7d' in df.columns:
            df.loc[df['sessions_last_7d'] > 50, 'sessions_last_7d'] = 50
        
        if 'exercises_completed_7d' in df.columns:
            df.loc[df['exercises_completed_7d'] > 100, 'exercises_completed_7d'] = 100
        
        return df

