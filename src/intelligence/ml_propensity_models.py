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
from typing import Dict, List, Set, Tuple
import yaml
import warnings
warnings.filterwarnings('ignore')


class PropensityModelEngine:
    """
    Machine Learning models for user propensity prediction
    """

    # Maps each engineered feature to the schema roles its formula consumes.
    # Used to detect when a feature is a rescaled view of the model target.
    _DERIVED_FEATURE_SOURCES = {
        'activeness': ('activeness_metrics',),
        'gamification_propensity': ('value_metrics', 'feature_flags'),
        'social_propensity': ('feature_flags',),
        'ai_tutor_propensity': ('feature_flags',),
        'leaderboard_propensity': ('feature_flags', 'retention_metrics'),
        'churn_risk': ('activeness_metrics', 'retention_metrics'),
    }

    _SCHEMA_ROLES = ('activeness_metrics', 'value_metrics', 'retention_metrics', 'feature_flags')
    
    def __init__(self, random_state: int = 42, config_path: str = 'config/config.yaml', schema_map: Dict = None):
        self.random_state = random_state
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        perf_config = self.config.get('performance', {})
        self.churn_risk_threshold = perf_config.get('churn_risk_threshold', 0.7)

        # A forward-looking target column, when the dataset provides one. It must never
        # appear in any feature matrix: for the engagement model it *is* the label, and
        # for the churn model it is information from after the prediction point.
        ml_config = self.config.get('ml', {})
        self.forecast_target_column = ml_config.get('forecast_target_column', 'engagement_next_7d')
        
        # Schema mapping for dynamic features
        self.schema_map = schema_map or {}
        
        # Models
        self.churn_model = None
        self.engagement_model = None
        self.conversion_model = None
        
        # Feature importance
        self.feature_importance = {}
        
        # Model performance
        self.model_metrics = {}

    def _derived_features_using(self, target_source_cols: List[str]) -> Set[str]:
        """
        Return engineered features that are computed from the same raw columns as the
        model target, and therefore leak it.

        Example: when the target is sum(value_metrics) = coins_balance, the feature
        gamification_propensity is a normalised blend of value_metrics + feature_flags,
        so it carries a rescaled copy of the target and must be dropped.
        """
        if not target_source_cols:
            return set()

        targets = set(target_source_cols)
        tainted_roles = {
            role for role in self._SCHEMA_ROLES
            if targets & set(self.schema_map.get(role) or [])
        }
        if not tainted_roles:
            return set()

        return {
            feature for feature, roles in self._DERIVED_FEATURE_SOURCES.items()
            if tainted_roles & set(roles)
        }
    
    def train_churn_model(self, df: pd.DataFrame) -> Tuple[xgb.XGBClassifier, Dict]:
        """
        Train churn prediction model using XGBoost
        
        Args:
            df: User data with features
            
        Returns:
            Trained model and metrics
        """
        print("\n[*] Training Churn Prediction Model (XGBoost)...")
        
        # Define churn target from actual behavioral data (lifecycle_stage)
        # Avoids circular logic of predicting the derived churn_risk from its own inputs
        if 'lifecycle_stage' in df.columns:
            df['churn_target'] = df['lifecycle_stage'].apply(
                lambda x: 1 if str(x).lower() in ['churned', 'inactive'] else 0
            ).astype(int)
        else:
            # Fallback: use churn_risk threshold (less ideal but functional)
            df['churn_target'] = (df['churn_risk'] > self.churn_risk_threshold).astype(int)
        
        # Ensure we have at least 2 classes for stratify
        stratify_val = df['churn_target'] if len(df['churn_target'].unique()) > 1 else None

        # Dynamic features for training
        base_features = [
            'activeness',
            'gamification_propensity',
            'social_propensity',
            'ai_tutor_propensity',
            'leaderboard_propensity'
        ]
        
        # Add mapped metrics
        mapped_features = []
        for role in ['activeness_metrics', 'retention_metrics', 'value_metrics', 'feature_flags']:
            mapped_features.extend(list(self.schema_map.get(role) or []))
            
        feature_cols = sorted({f for f in (base_features + mapped_features) if f in df.columns})
        
        if not feature_cols:
            # Absolute fallback
            feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [c for c in feature_cols if 'id' not in c.lower() and c != 'churn_target']

        # The forecast column describes the week *after* the prediction point, so using
        # it to predict churn would be time-travel leakage.
        forecast_col = self.forecast_target_column
        if forecast_col and forecast_col in feature_cols:
            feature_cols.remove(forecast_col)
            print(f"   [Guard] Excluded forward-looking column from churn features: {forecast_col}")

        print(f"   [Tool] Using {len(feature_cols)} dynamic features for churn prediction")
        
        # Handle missing values
        for col in feature_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        # Add interaction features for richer signal
        if 'activeness' in df.columns and 'gamification_propensity' in df.columns:
            df['active_x_gamification'] = df['activeness'] * df['gamification_propensity']
            feature_cols.append('active_x_gamification')
        if 'activeness' in df.columns and 'social_propensity' in df.columns:
            df['active_x_social'] = df['activeness'] * df['social_propensity']
            feature_cols.append('active_x_social')
        if 'churn_risk' in df.columns and 'activeness' in df.columns:
            df['churn_x_active'] = df['churn_risk'] * df['activeness']
            feature_cols.append('churn_x_active')
        # Engagement diversity (std dev across propensity scores)
        propensity_cols = [c for c in ['gamification_propensity', 'social_propensity',
                                        'ai_tutor_propensity', 'leaderboard_propensity'] if c in df.columns]
        if len(propensity_cols) >= 2:
            df['engagement_diversity'] = df[propensity_cols].std(axis=1)
            feature_cols.append('engagement_diversity')

        # Sorted, not set-ordered: Python randomises str hashing per process, so an
        # unsorted set would reorder the feature matrix between runs and make results
        # irreproducible even with a fixed seed.
        feature_cols = sorted(set(feature_cols))

        X = df[feature_cols]
        y = df['churn_target']
        
        # Handle class imbalance
        neg_count = (y == 0).sum()
        pos_count = (y == 1).sum()
        spw = neg_count / pos_count if pos_count > 0 else 1.0

        # Train-test split (handle small data)
        test_size = 0.2 if len(df) >= 10 else 0.5
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=stratify_val
        )
        
        # Train XGBoost with class-imbalance correction
        self.churn_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            scale_pos_weight=spw,
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
        try:
            auc_score = roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0.5
        except:
            auc_score = 0.5
            
        # Cross-validation (handle small data / imbalanced classes)
        try:
            from sklearn.model_selection import StratifiedKFold
            n_minority = min(y.value_counts())
            cv_folds = min(5, n_minority) if n_minority >= 2 else 2
            skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
            cv_scores = cross_val_score(
                self.churn_model, X, y, cv=skf, scoring='roc_auc'
            )
            # Replace any NaN with test AUC
            cv_scores = np.where(np.isnan(cv_scores), auc_score, cv_scores)
        except Exception:
            cv_scores = np.array([auc_score])
        
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
        print(f"   [OK] Cross-Val AUC: {cv_scores.mean():.4f} (+/-{cv_scores.std():.4f})")
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
        # Use value metrics or activeness metrics as proxy
        val_metrics = list(self.schema_map.get('value_metrics') or [])
        act_metrics = list(self.schema_map.get('activeness_metrics') or [])
        # target_source_cols records exactly which raw columns built the target, so that
        # they (and any composite derived from them) can be excluded from the features.
        target_source_cols: List[str] = []
        forecast_col = self.forecast_target_column
        if forecast_col and forecast_col in df.columns:
            # Preferred: a genuine forward-looking target. Predicting it from this
            # week's behaviour is real forecasting rather than same-period inference.
            df['engagement_target'] = pd.to_numeric(df[forecast_col], errors='coerce').fillna(0)
            target_source_cols = [forecast_col]
            print(f"   [Target] Forecasting '{forecast_col}' (forward-looking)")
        elif val_metrics:
            existing_val = [c for c in val_metrics if c in df.columns]
            df['engagement_target'] = df[existing_val].sum(axis=1) if existing_val else 0
            target_source_cols = existing_val
        elif act_metrics:
            existing_act = [c for c in act_metrics if c in df.columns]
            df['engagement_target'] = df[existing_act].sum(axis=1) if existing_act else 0
            target_source_cols = existing_act
        else:
            df['engagement_target'] = (
                (df['sessions_last_7d'] if 'sessions_last_7d' in df.columns else 0) * 0.3 +
                (df['notif_open_rate_30d'] if 'notif_open_rate_30d' in df.columns else 0) * 100 * 0.3
            )
            target_source_cols = [c for c in ['sessions_last_7d', 'notif_open_rate_30d'] if c in df.columns]

        # Leakage guard: drop any engineered feature whose own definition consumes a
        # target source column. Without this the model simply rediscovers a rescaled
        # copy of the target (e.g. gamification_propensity normalises value_metrics,
        # which is also the target) and reports an inflated R2.
        leaky_features = self._derived_features_using(target_source_cols)

        # Dynamic features
        feature_cols = [f for f in [
            'days_since_signup', 'streak_current', 'activeness',
            'gamification_propensity', 'social_propensity', 'churn_risk'
        ] if f in df.columns]

        # Include the mapped behavioural metrics as well. The churn model already uses
        # these; withholding them from the forecaster left real signal on the table.
        for role in ('activeness_metrics', 'retention_metrics', 'value_metrics', 'feature_flags'):
            feature_cols.extend([f for f in list(self.schema_map.get(role) or []) if f in df.columns])
        feature_cols = sorted(set(feature_cols))

        excluded = sorted({c for c in feature_cols if c in target_source_cols or c in leaky_features})
        feature_cols = [c for c in feature_cols if c not in excluded]
        if excluded:
            print(f"   [Guard] Excluded {len(excluded)} leakage-prone feature(s): {', '.join(excluded)}")

        if not feature_cols:
             feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
             feature_cols = [c for c in feature_cols if 'id' not in c.lower() and c != 'engagement_target']
             feature_cols = [c for c in feature_cols
                             if c not in target_source_cols and c not in leaky_features]

        X = df[feature_cols]
        y = df['engagement_target']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )

        # A forward-looking engagement target is a count of future actions. When it
        # really is a non-negative integer, a Poisson objective matches the noise
        # structure far better than squared error, which assumes constant variance.
        is_count_target = bool(
            (y >= 0).all() and np.allclose(y, np.round(y), equal_nan=False)
        )
        objective = 'poisson' if is_count_target else 'regression'
        if is_count_target:
            print("   [Model] Count target detected -> Poisson objective")

        self.engagement_model = lgb.LGBMRegressor(
            objective=objective,
            n_estimators=400,
            max_depth=5,
            learning_rate=0.05,
            num_leaves=31,
            min_child_samples=20,
            subsample=0.9,
            subsample_freq=1,
            colsample_bytree=0.9,
            random_state=self.random_state,
            verbose=-1
        )
        
        self.engagement_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            callbacks=[lgb.early_stopping(stopping_rounds=30, verbose=False)]
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
        print(f"   [OK] R2 Score: {r2:.4f}")
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
            # We must use the SAME features as training
            churn_features = self.churn_model.feature_names_in_ if hasattr(self.churn_model, 'feature_names_in_') else []
            
            if churn_features is None or len(churn_features) == 0:
                 # Fallback if names not saved
                 churn_features = [c for c in df.columns if c in ['activeness', 'gamification_propensity', 'social_propensity', 'churn_risk']]

            for col in churn_features:
                if col in df.columns:
                    df[col] = df[col].fillna(df[col].median())
            
            X_churn = df[churn_features]
            df['ml_churn_propensity'] = self.churn_model.predict_proba(X_churn)[:, 1]
        
        # Engagement propensity
        if self.engagement_model:
            engagement_features = self.engagement_model.feature_name_ if hasattr(self.engagement_model, 'feature_name_') else []
            
            if engagement_features is None or len(engagement_features) == 0:
                 engagement_features = [c for c in df.columns if c in ['activeness', 'gamification_propensity', 'social_propensity', 'churn_risk']]

            for col in engagement_features:
                if col in df.columns:
                    if df[col].dtype == 'bool':
                        df[col] = df[col].astype(int)
                    else:
                        df[col] = df[col].fillna(df[col].median())
            
            X_engagement = df[engagement_features]
            df['ml_engagement_propensity'] = self.engagement_model.predict(X_engagement)
            
            # Normalize to 0-1
            if df['ml_engagement_propensity'].max() != df['ml_engagement_propensity'].min():
                df['ml_engagement_propensity'] = (
                    (df['ml_engagement_propensity'] - df['ml_engagement_propensity'].min()) /
                    (df['ml_engagement_propensity'].max() - df['ml_engagement_propensity'].min())
                )
            else:
                df['ml_engagement_propensity'] = 0.5
        
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

