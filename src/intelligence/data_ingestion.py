"""
Data Ingestion Engine - Validates and prepares user data
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from ..utils.validation import DataValidator
from ..utils.metrics import MetricsCalculator
from ..llm_utils import call_llm_with_retry, parse_json_response


class DataIngestionEngine:
    """Handles user data ingestion, validation, and feature engineering"""
    
    def __init__(self, knowledge_bank: Dict = None):
        self.validator = DataValidator()
        self.metrics_calc = MetricsCalculator()
        self.user_data = None
        self.knowledge_bank = knowledge_bank
        self.schema_map = {}
        self.feature_columns = [] # Will be populated after schema mapping
    
    def load_and_validate(self, csv_path: str) -> pd.DataFrame:
        """
        Load user data CSV and validate with dynamic schema discovery
        """
        print(f"\n[Stats] Loading user data from {csv_path}...")
        
        file_path = Path(csv_path)
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        print(f"   Loaded {len(df)} users")

        # Step 1: Discover Schema via LLM
        self.schema_map = self._map_schema_llm(df)
        
        # Step 2: Auto-fill and normalize using the map
        df = self._ensure_required_columns_dynamic(df)
        df = self._preprocess_for_validation_dynamic(df)

        # Step 3: Validate
        print("\n[Find] Validating data quality...")
        validation_result = self.validator.validate_user_data(df)
        
        if not validation_result['valid']:
            print("\n[ERROR] Validation failed:")
            for error in validation_result['errors']:
                print(f"   - {error}")
            raise ValueError("Data validation failed")
        
        if validation_result['warnings']:
            print("\n[WARN] Warnings:")
            for warning in validation_result['warnings']:
                print(f"   - {warning}")
        
        # Step 4: Clean
        print("\n[Clean] Cleaning data...")
        df = self.validator.clean_user_data(df, schema_map=self.schema_map)
        
        print("[OK] Data ingestion complete")
        self.user_data = df
        return df

    def _map_schema_llm(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Use LLM to identify the role of each column in the dataset."""
        print("\n[Brain] Analyzing dataset schema via LLM...")
        
        headers = list(df.columns)
        sample_rows = df.head(5).to_dict(orient='records')
        
        domain = self.knowledge_bank.get('domain', 'unknown') if self.knowledge_bank else 'unknown'
        kb_context = ""
        if self.knowledge_bank and 'feature_goal_map' in self.knowledge_bank:
            features = [f.get('feature_id') for f in self.knowledge_bank['feature_goal_map'].get('features', [])]
            kb_context = f"Known product features: {', '.join(features)}"

        system_prompt = """You are an Elite Data Strategist and Schema Architect. Your mission is to perform Semantic Intent Mapping -- transitioning raw dataset headers into structured behavioral roles regardless of the business domain.

BEHAVIORAL INTENT FRAMEWORK (Chain-of-Thought):
Before mapping, execute this internal logic sequence:
1. Linguistic Scan: Does the header name suggest a discrete action (Activeness), a state/attribute (Status), or a cumulative outcome (Value)?
2. Structural Inference: Based on the sample data, determine if the column is a Binary Flag (0/1), a continuous Intensity (Activity frequency), or a unique Identifier.
3. Domain Pivot: Mentally translate headers into EdTech, Fintech, or E-commerce equivalents to test role fit.
   Example: 'Daily Orders' in Foodtech = Activeness. 'Total Spend' in Fintech = Value. 'Login Streak' in EdTech = Retention.

SELF-VERIFICATION & VALIDATION (Chain-of-Verification):
Before finalizing, cross-check against these constraints:
- Type Integrity: Ensure Boolean/Status flags go to feature_flags and Numeric counts go to metrics.
- Redundancy Check: Adhere to MECE principle (Mutually Exclusive, Collectively Exhaustive) where possible.

ROLE DEFINITIONS:
- user_id: The unique identifier for a user.
- lifecycle_stage: The user's current status (trial, paid, churned, inactive).
- activeness_metrics: Columns representing frequency of app opens, sessions, or core actions.
- value_metrics: Columns representing monetary value, loyalty points, or depth of usage.
- retention_metrics: Columns representing streaks, tenure, or recentness.
- feature_flags: Columns indicating if a specific feature was used (usually boolean or flags).

Return ONLY a strictly valid JSON object. No prose.
Schema: {"user_id": "string", "lifecycle_stage": "string", "activeness_metrics": ["list"], "value_metrics": ["list"], "retention_metrics": ["list"], "feature_flags": ["list"]}"""

        user_prompt = f"""
Domain: {domain}
{kb_context}

Dataset Headers: {headers}
Sample Data (5 rows): {sample_rows}

Map these columns to my internal roles.
"""
        
        response = call_llm_with_retry(system_prompt, user_prompt)
        mapping = parse_json_response(response)
        
        # Validation of mapping
        if not mapping or 'user_id' not in mapping:
            print("   [Warn] LLM schema mapping failed. Falling back to default heuristics.")
            return self._fallback_schema_mapping(headers)

        # Normalize scalar fields — LLM sometimes returns ['user_id'] instead of 'user_id'
        for key in ['user_id', 'lifecycle_stage']:
            val = mapping.get(key)
            if isinstance(val, list):
                mapping[key] = val[0] if val else None
        # Ensure list fields are always lists
        for key in ['activeness_metrics', 'value_metrics', 'retention_metrics', 'feature_flags']:
            val = mapping.get(key)
            if val is None:
                mapping[key] = []
            elif isinstance(val, str):
                mapping[key] = [val]

        print(f"   [OK] Identified roles: ID={mapping.get('user_id')}, Features={len(mapping.get('feature_flags', []))}")
        
        # Update feature_columns based on mapping
        self.feature_columns = mapping.get('feature_flags', [])
        return mapping

    def _fallback_schema_mapping(self, headers: List[str]) -> Dict[str, Any]:
        """Rule-based fallback if LLM fails."""
        mapping = {
            'user_id': headers[0],
            'lifecycle_stage': 'lifecycle_stage' if 'lifecycle_stage' in headers else None,
            'activeness_metrics': [h for h in headers if 'session' in h.lower() or 'open' in h.lower()],
            'value_metrics': [h for h in headers if 'coins' in h.lower() or 'order' in h.lower()],
            'retention_metrics': [h for h in headers if 'streak' in h.lower() or 'signup' in h.lower()],
            'feature_flags': [h for h in headers if h.startswith('feature_')]
        }
        self.feature_columns = mapping['feature_flags']
        return mapping

    def _ensure_required_columns_dynamic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map raw columns to standard internal names and fill missing."""
        df = df.copy()
        m = self.schema_map
        
        # Helper: get scalar value from mapping (LLM may return list or string)
        def _scalar(val):
            if isinstance(val, list):
                return val[0] if val else None
            return val
        
        # Rename essential columns to internal standard names for the rest of the pipeline
        rename_map = {}
        uid = _scalar(m.get('user_id'))
        if uid and uid in df.columns and uid != 'user_id':
            rename_map[uid] = 'user_id'
        lcs = _scalar(m.get('lifecycle_stage'))
        if lcs and lcs in df.columns and lcs != 'lifecycle_stage':
            rename_map[lcs] = 'lifecycle_stage'
            
        if rename_map:
            df = df.rename(columns=rename_map)

        # For non-id columns, we keep their original names but track their roles via schema_map
        # Ensure 'user_id' exists
        if 'user_id' not in df.columns:
            df['user_id'] = [f"U{idx + 1:05d}" for idx in range(len(df))]
            
        # Ensure 'lifecycle_stage' exists with a default
        if 'lifecycle_stage' not in df.columns:
            df['lifecycle_stage'] = 'trial'

        return df

    def _preprocess_for_validation_dynamic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize using dynamic mapping."""
        df = df.copy()
        
        # Normalize lifecycle
        df['lifecycle_stage'] = df['lifecycle_stage'].astype(str).str.lower().str.strip()
        invalid_mask = ~df['lifecycle_stage'].isin(self.validator.VALID_LIFECYCLE_STAGES)
        if invalid_mask.any():
            df.loc[invalid_mask, 'lifecycle_stage'] = 'trial'

        # Coerce all metrics to numeric
        all_metric_cols = (
            list(self.schema_map.get('activeness_metrics') or []) +
            list(self.schema_map.get('value_metrics') or []) +
            list(self.schema_map.get('retention_metrics') or [])
        )
        for col in all_metric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Coerce boolean fields
        feat_cols = list(self.schema_map.get('feature_flags') or [])
        for col in feat_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower().isin(['1', 'true', 'yes', 'y', '1.0'])

        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer behavioral features for segmentation using the dynamic schema mapping
        """
        print("\n[Tool] Engineering features via dynamic schema...")
        
        df = df.copy()
        
        # Calculate behavioral scores using the mapping
        df['activeness'] = self.metrics_calc.calculate_activeness_dynamic(df, self.schema_map)
        df['gamification_propensity'] = self.metrics_calc.calculate_gamification_propensity_dynamic(df, self.schema_map)
        df['social_propensity'] = self.metrics_calc.calculate_social_propensity_dynamic(df, self.schema_map)
        df['ai_tutor_propensity'] = self.metrics_calc.calculate_ai_tutor_propensity_dynamic(df, self.schema_map)
        df['leaderboard_propensity'] = self.metrics_calc.calculate_leaderboard_propensity_dynamic(df, self.schema_map)
        df['churn_risk'] = self.metrics_calc.calculate_churn_risk_dynamic(df, self.schema_map)
        
        print(f"   [OK] Activeness score (mean: {df['activeness'].mean():.2f})")
        print(f"   [OK] Churn risk (mean: {df['churn_risk'].mean():.2f})")
        
        self.user_data = df
        return df
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics of user data dynamically"""
        stats = {
            'total_users': len(df),
            'lifecycle_distribution': df['lifecycle_stage'].value_counts().to_dict(),
            'avg_activeness': df['activeness'].mean() if 'activeness' in df.columns else 0,
            'avg_churn_risk': df['churn_risk'].mean() if 'churn_risk' in df.columns else 0
        }
        return stats

