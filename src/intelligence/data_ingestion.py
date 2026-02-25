"""
Data Ingestion Engine - Validates and prepares user data
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from ..utils.validation import DataValidator
from ..utils.metrics import MetricsCalculator


class DataIngestionEngine:
    """Handles user data ingestion, validation, and feature engineering"""
    
    def __init__(self, knowledge_bank: Dict = None):
        self.validator = DataValidator()
        self.metrics_calc = MetricsCalculator()
        self.user_data = None
        self.knowledge_bank = knowledge_bank
        self.feature_columns = self._extract_feature_columns_from_kb()
    
    def load_and_validate(self, csv_path: str) -> pd.DataFrame:
        """
        Load user data CSV and validate
        
        Args:
            csv_path: Path to user data CSV
            
        Returns:
            pd.DataFrame: Validated and cleaned user data
        """
        print(f"\n[Stats] Loading user data from {csv_path}...")
        
        # Load CSV/XLSX
        file_path = Path(csv_path)
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        print(f"   Loaded {len(df)} users")
        
        # Auto-fill missing required columns and normalize values
        df = self._ensure_required_columns(df)
        df = self._preprocess_for_validation(df)

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

    def _extract_feature_columns_from_kb(self) -> List[str]:
        """Extract feature column names from Knowledge Bank."""
        feature_cols = []
        if self.knowledge_bank and 'feature_goal_map' in self.knowledge_bank:
            features = self.knowledge_bank['feature_goal_map'].get('features', [])
            for feat in features:
                fid = feat.get('feature_id', '')
                if fid:
                    feature_cols.append(f'feature_{fid}_used')
        # Fallback defaults if KB not available
        if not feature_cols:
            feature_cols = ['feature_ai_tutor_used', 'feature_leaderboard_viewed']
        return feature_cols

    def _ensure_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure required columns exist with safe defaults for demo runs."""
        df = df.copy()

        # Standard behavioral defaults
        defaults = {
            'user_id': None,
            'lifecycle_stage': 'trial',
            'days_since_signup': 7,
            'age_band_region': 'unknown',
            'sessions_last_7d': 0,
            'exercises_completed_7d': 0,
            'streak_current': 0,
            'coins_balance': 0,
            'preferred_hour': 19,
            'notif_open_rate_30d': 0.10,
            'motivation_score': 0.50
        }
        # Add feature columns from KB
        for fc in self.feature_columns:
            defaults[fc] = False

        # All columns we expect (required + standard + KB features)
        expected_cols = (
            set(self.validator.REQUIRED_USER_COLUMNS) |
            set(self.validator.STANDARD_COLUMNS) |
            set(self.feature_columns)
        )

        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            print("\n[Warn] Auto-filling missing columns...")
            for col in sorted(missing_cols):
                if col == 'user_id':
                    df[col] = [f"U{idx + 1:05d}" for idx in range(len(df))]
                else:
                    df[col] = defaults.get(col)
                print(f"   • Added '{col}' with default values")

        return df

    def _preprocess_for_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize common fields so validation does not fail on formatting."""
        df = df.copy()

        # Normalize lifecycle stage
        if 'lifecycle_stage' in df.columns:
            df['lifecycle_stage'] = df['lifecycle_stage'].astype(str).str.lower().str.strip()
            invalid_mask = ~df['lifecycle_stage'].isin(self.validator.VALID_LIFECYCLE_STAGES)
            if invalid_mask.any():
                df.loc[invalid_mask, 'lifecycle_stage'] = 'trial'
                print(f"   [Warn] Normalized {invalid_mask.sum()} invalid lifecycle_stage values to 'trial'")

        # Coerce numeric fields
        numeric_cols = [
            'days_since_signup', 'sessions_last_7d', 'exercises_completed_7d',
            'streak_current', 'coins_balance', 'preferred_hour',
            'notif_open_rate_30d', 'motivation_score'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Clamp preferred_hour to 0-23
        if 'preferred_hour' in df.columns:
            df['preferred_hour'] = df['preferred_hour'].clip(0, 23)

        # Clamp notif_open_rate_30d to 0-1
        if 'notif_open_rate_30d' in df.columns:
            df['notif_open_rate_30d'] = df['notif_open_rate_30d'].clip(0, 1)

        # Coerce boolean fields (feature columns from KB)
        for col in self.feature_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower().isin(['1', 'true', 'yes', 'y'])

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
        df['ai_tutor_propensity'] = self.metrics_calc.calculate_ai_tutor_propensity(df)
        df['leaderboard_propensity'] = self.metrics_calc.calculate_leaderboard_propensity(df)
        df['churn_risk'] = self.metrics_calc.calculate_churn_risk(df)
        
        print(f"   [OK] Activeness score (mean: {df['activeness'].mean():.2f})")
        print(f"   [OK] Gamification propensity (mean: {df['gamification_propensity'].mean():.2f})")
        print(f"   [OK] Social propensity (mean: {df['social_propensity'].mean():.2f})")
        print(f"   [OK] AI tutor propensity (mean: {df['ai_tutor_propensity'].mean():.2f})")
        print(f"   [OK] Leaderboard propensity (mean: {df['leaderboard_propensity'].mean():.2f})")
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

