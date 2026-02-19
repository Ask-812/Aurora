"""
ML-Powered Propensity Models
- Churn Prediction (XGBoost)
- Engagement Propensity (LightGBM)
- Conversion Likelihood
- LTV Estimation
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, Tuple
import yaml
import warnings
warnings.filterwarnings('ignore')


class PropensityModelEngine:
    """
    Machine Learning models for user propensity prediction
    """
    
    def __init__(self, random_state: int = 42, config_path: str = 'config/config.yaml'):
        self.random_state = random_state
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        perf_config = self.config.get('performance', {})
        self.churn_risk_threshold = perf_config.get('churn_risk_threshold', 0.7)
        
        # Models
        self.churn_model = None
        self.engagement_model = None
        self.conversion_model = None
        
        # Feature importance
        self.feature_importance = {}
        
        # Model performance
        self.model_metrics = {}
    
    def train_churn_model(self, df: pd.DataFrame) -> Tuple[xgb.XGBClassifier, Dict]:
        """
        Train churn prediction model using XGBoost
        
        Args:
            df: User data with features
            
        Returns:
            Trained model and metrics
        """
        print("\n[*] Training Churn Prediction Model (XGBoost)...")
        
        # Define churn target using config threshold
        df['churn_target'] = (df['churn_risk'] > self.churn_risk_threshold).astype(int)
        
        # Features for training
        feature_cols = [
            'sessions_last_7d',
            'exercises_completed_7d',
            'streak_current',
            'notif_open_rate_30d',
            'days_since_signup',
            'activeness',
            'gamification_propensity',
            'social_propensity',
            'motivation_score'
        ]
        
        # Handle missing values
        for col in feature_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        X = df[feature_cols]
        y = df['churn_target']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )
        
        # Train XGBoost
        self.churn_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.random_state,
            eval_metric='logloss'
        )
        
        self.churn_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Predictions
        y_pred_proba = self.churn_model.predict_proba(X_test)[:, 1]
        
        # Metrics
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.churn_model, X, y, cv=5, scoring='roc_auc'
        )
        
        metrics = {
            'model_type': 'XGBoost Classifier',
            'auc_test': auc_score,
            'auc_cv_mean': cv_scores.mean(),
            'auc_cv_std': cv_scores.std(),
            'n_features': len(feature_cols),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        self.model_metrics['churn'] = metrics
        
        # Feature importance
        self.feature_importance['churn'] = dict(zip(
            feature_cols,
            self.churn_model.feature_importances_
        ))
        
        print(f"   [OK] AUC Score: {auc_score:.4f}")
        print(f"   [OK] Cross-Val AUC: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        print(f"   [OK] Top Features: {self._get_top_features('churn', 3)}")
        
        return self.churn_model, metrics
    
    def train_engagement_model(self, df: pd.DataFrame) -> Tuple[lgb.LGBMRegressor, Dict]:
        """
        Train engagement propensity model using LightGBM
        Predicts future engagement score
        
        Args:
            df: User data with features
            
        Returns:
            Trained model and metrics
        """
        print("\n[*] Training Engagement Propensity Model (LightGBM)...")
        
        # Target: future engagement (combined metric)
        df['engagement_target'] = (
            df['sessions_last_7d'] * 0.3 +
            df['exercises_completed_7d'] * 0.4 +
            df['notif_open_rate_30d'] * 100 * 0.3
        )
        
        # Features
        feature_cols = [
            'days_since_signup',
            'streak_current',
            'coins_balance',
            'activeness',
            'gamification_propensity',
            'social_propensity',
            'motivation_score',
            'churn_risk',
            'feature_ai_tutor_used',
            'feature_leaderboard_viewed'
        ]
        
        # Handle missing values
        for col in feature_cols:
            if col in df.columns:
                if df[col].dtype == 'bool':
                    df[col] = df[col].astype(int)
                else:
                    df[col] = df[col].fillna(df[col].median())
        
        X = df[feature_cols]
        y = df['engagement_target']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )
        
        # Train LightGBM
        self.engagement_model = lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            num_leaves=31,
            random_state=self.random_state,
            verbose=-1
        )
        
        self.engagement_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)]
        )
        
        # Predictions
        y_pred = self.engagement_model.predict(X_test)
        
        # Metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'model_type': 'LightGBM Regressor',
            'rmse': rmse,
            'r2_score': r2,
            'n_features': len(feature_cols),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        self.model_metrics['engagement'] = metrics
        
        # Feature importance
        self.feature_importance['engagement'] = dict(zip(
            feature_cols,
            self.engagement_model.feature_importances_
        ))
        
        print(f"   [OK] RMSE: {rmse:.4f}")
        print(f"   [OK] R² Score: {r2:.4f}")
        print(f"   [OK] Top Features: {self._get_top_features('engagement', 3)}")
        
        return self.engagement_model, metrics
    
    def predict_user_propensities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate propensity scores for all users
        
        Args:
            df: User data
            
        Returns:
            DataFrame with propensity scores
        """
        print("\n[Stats] Generating Propensity Scores...")
        
        df = df.copy()
        
        # Churn propensity
        if self.churn_model:
            churn_features = [
                'sessions_last_7d', 'exercises_completed_7d', 'streak_current',
                'notif_open_rate_30d', 'days_since_signup', 'activeness',
                'gamification_propensity', 'social_propensity', 'motivation_score'
            ]
            
            for col in churn_features:
                if col in df.columns:
                    df[col] = df[col].fillna(df[col].median())
            
            X_churn = df[churn_features]
            df['ml_churn_propensity'] = self.churn_model.predict_proba(X_churn)[:, 1]
        
        # Engagement propensity
        if self.engagement_model:
            engagement_features = [
                'days_since_signup', 'streak_current', 'coins_balance',
                'activeness', 'gamification_propensity', 'social_propensity',
                'motivation_score', 'churn_risk',
                'feature_ai_tutor_used', 'feature_leaderboard_viewed'
            ]
            
            for col in engagement_features:
                if col in df.columns:
                    if df[col].dtype == 'bool':
                        df[col] = df[col].astype(int)
                    else:
                        df[col] = df[col].fillna(df[col].median())
            
            X_engagement = df[engagement_features]
            df['ml_engagement_propensity'] = self.engagement_model.predict(X_engagement)
            
            # Normalize to 0-1
            df['ml_engagement_propensity'] = (
                (df['ml_engagement_propensity'] - df['ml_engagement_propensity'].min()) /
                (df['ml_engagement_propensity'].max() - df['ml_engagement_propensity'].min())
            )
        
        print(f"   [OK] Generated propensity scores for {len(df)} users")
        print(f"   [OK] Avg Churn Propensity: {df['ml_churn_propensity'].mean():.3f}")
        print(f"   [OK] Avg Engagement Propensity: {df['ml_engagement_propensity'].mean():.3f}")
        
        return df
    
    def _get_top_features(self, model_name: str, top_n: int = 3) -> str:
        """Get top N important features"""
        if model_name not in self.feature_importance:
            return "N/A"
        
        importance = self.feature_importance[model_name]
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return ", ".join([f[0] for f in sorted_features[:top_n]])
    
    def get_model_summary(self) -> pd.DataFrame:
        """Get summary of all trained models"""
        summary = []
        
        for model_name, metrics in self.model_metrics.items():
            summary.append({
                'model': model_name,
                **metrics
            })
        
        return pd.DataFrame(summary)
    
    def save_models(self, output_dir: str):
        """Save trained models"""
        import pickle
        from pathlib import Path
        
        Path(f"{output_dir}/models").mkdir(parents=True, exist_ok=True)
        
        if self.churn_model:
            with open(f"{output_dir}/models/churn_model.pkl", 'wb') as f:
                pickle.dump(self.churn_model, f)
            print(f"   [OK] Saved: {output_dir}/models/churn_model.pkl")
        
        if self.engagement_model:
            with open(f"{output_dir}/models/engagement_model.pkl", 'wb') as f:
                pickle.dump(self.engagement_model, f)
            print(f"   [OK] Saved: {output_dir}/models/engagement_model.pkl")
        
        # Save metrics
        summary = self.get_model_summary()
        summary.to_csv(f"{output_dir}/ml_model_performance.csv", index=False)
        print(f"   [OK] Saved: {output_dir}/ml_model_performance.csv")

