"""
Data Ingestion Engine - Validates and prepares user data
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any
from ..utils.validation import DataValidator
from ..utils.metrics import MetricsCalculator


class DataIngestionEngine:
    """Handles user data ingestion, validation, and feature engineering"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.metrics_calc = MetricsCalculator()
        self.user_data = None
    
    def load_and_validate(self, csv_path: str) -> pd.DataFrame:
        """
        Load user data CSV and validate
        
        Args:
            csv_path: Path to user data CSV
            
        Returns:
            pd.DataFrame: Validated and cleaned user data
        """
        print(f"\n[Stats] Loading user data from {csv_path}...")
        
        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"   Loaded {len(df)} users")
        
        # Validate
        print("\n[Find] Validating data...")
        validation_result = self.validator.validate_user_data(df)
        
        if not validation_result['valid']:
            print("\n❌ Validation failed:")
            for error in validation_result['errors']:
                print(f"   • {error}")
            raise ValueError("Data validation failed")
        
        # Show warnings
        if validation_result['warnings']:
            print("\n⚠️  Warnings:")
            for warning in validation_result['warnings']:
                print(f"   • {warning}")
        
        # Clean data
        print("\n🧹 Cleaning data...")
        df = self.validator.clean_user_data(df)
        
        print("[OK] Data validation and cleaning complete")
        
        self.user_data = df
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer behavioral features for segmentation
        
        Args:
            df: User data DataFrame
            
        Returns:
            pd.DataFrame: Data with engineered features
        """
        print("\n[Tool] Engineering features...")
        
        df = df.copy()
        
        # Calculate behavioral scores
        df['activeness'] = self.metrics_calc.calculate_activeness(df)
        df['gamification_propensity'] = self.metrics_calc.calculate_gamification_propensity(df)
        df['social_propensity'] = self.metrics_calc.calculate_social_propensity(df)
        df['churn_risk'] = self.metrics_calc.calculate_churn_risk(df)
        
        print(f"   [OK] Activeness score (mean: {df['activeness'].mean():.2f})")
        print(f"   [OK] Gamification propensity (mean: {df['gamification_propensity'].mean():.2f})")
        print(f"   [OK] Social propensity (mean: {df['social_propensity'].mean():.2f})")
        print(f"   [OK] Churn risk (mean: {df['churn_risk'].mean():.2f})")
        
        self.user_data = df
        return df
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics of user data"""
        stats = {
            'total_users': len(df),
            'lifecycle_distribution': df['lifecycle_stage'].value_counts().to_dict(),
            'avg_sessions': df['sessions_last_7d'].mean(),
            'avg_exercises': df['exercises_completed_7d'].mean(),
            'avg_activeness': df['activeness'].mean() if 'activeness' in df.columns else None,
            'avg_churn_risk': df['churn_risk'].mean() if 'churn_risk' in df.columns else None
        }
        return stats

