"""
Segmentation Engine with ML-Powered Insights
- RFM Analysis
- Hierarchical Clustering with Optimal K
- LLM-Powered Domain-Aware Segment Naming
- Behavioral Cohort Analysis
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from typing import Dict, List, Tuple
import yaml
import warnings
warnings.filterwarnings('ignore')

# LLM utilities for dynamic naming
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.llm_utils import call_llm_with_retry, parse_json_response


class SegmentationEngine:
    """
    ML-powered segmentation using multiple techniques:
    1. RFM (Recency, Frequency, Monetary) Analysis
    2. Hierarchical Clustering with Optimal K Selection
    3. LLM-Powered Domain-Aware Segment Naming
    """

    def __init__(self, config_path: str = 'config/config.yaml', kb_data: Dict = None, schema_map: Dict = None):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        seg_config = self.config.get('segmentation', {})
        self.min_clusters = seg_config.get('min_clusters', 6)
        self.max_clusters = seg_config.get('max_clusters', 12)
        self.random_state = seg_config.get('random_state', 42)

        self.scaler = StandardScaler()
        self.best_model = None
        self.best_k = None
        self.segment_profiles = None
        self.rfm_scores = None

        # Schema mapping for dynamic data handling
        self.schema_map = schema_map or {}

        # KB data for domain-aware naming
        self.kb_data = kb_data or {}
        self.domain = self.kb_data.get('detected_domain', 'generic')
        self.features = []
        fgm = self.kb_data.get('feature_goal_map', {})
        for f in fgm.get('features', []):
            self.features.append(f.get('feature_name', ''))

    def create_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create segments using advanced ML techniques"""
        print("\n[*] ML-Powered Segmentation...")
        print(f"   Users: {len(df)} | Features: {df.shape[1]}")

        df = df.copy()

        # Step 1: RFM Analysis
        print("\n   [Stats] Step 1: RFM Analysis")
        df = self._calculate_rfm_scores(df)

        # Step 2: Feature Engineering for Clustering
        print("   [Tool] Step 2: Feature Engineering")
        df, feature_matrix = self._engineer_clustering_features(df)

        # Step 3: Optimal K Selection
        print("   [Find] Step 3: Optimal Cluster Count Selection")
        optimal_k = self._find_optimal_k(feature_matrix)
        print(f"      [OK] Optimal K: {optimal_k}")

        # Step 4: Hierarchical Clustering
        print("   [Tree] Step 4: Hierarchical Clustering")
        df = self._hierarchical_clustering(df, feature_matrix, optimal_k)

        # Step 5: Segment Profiling
        print("   [List] Step 5: Segment Profiling")
        self.segment_profiles = self._create_profiles(df)

        # Step 6: LLM-Powered Segment Naming
        print("   [Tag]  Step 6: LLM-Powered Domain-Aware Naming")
        df = self._name_segments_llm(df)

        # Update profiles with names
        for _, row in self.segment_profiles.iterrows():
            seg_id = row['segment_id']
            name = df[df['segment_id'] == seg_id]['segment_name'].iloc[0]
            self.segment_profiles.loc[
                self.segment_profiles['segment_id'] == seg_id, 'segment_name'
            ] = name

        # Display results
        self._display_segment_analysis(df)

        return df

    def _calculate_rfm_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RFM scores adapted for domain context dynamically"""
        
        # 1. Recency
        # Use first retention metric or first numeric column as proxy for recency if 'days_since_signup' missing
        recency_col = 'days_since_signup'
        if recency_col not in df.columns:
            ret_metrics = list(self.schema_map.get('retention_metrics') or [])
            if ret_metrics and ret_metrics[0] in df.columns:
                recency_col = ret_metrics[0]
            else:
                # Add dummy recency if totally missing
                df['rfm_recency_proxy'] = 30 
                recency_col = 'rfm_recency_proxy'
                
        df['rfm_recency'] = df[recency_col].apply(
            lambda x: 5 if x <= 7 else (4 if x <= 14 else (3 if x <= 30 else (2 if x <= 60 else 1)))
        )

        # 2. Frequency
        freq_col = 'sessions_last_7d'
        if freq_col not in df.columns:
            act_metrics = list(self.schema_map.get('activeness_metrics') or [])
            if act_metrics and act_metrics[0] in df.columns:
                freq_col = act_metrics[0]
            else:
                df['rfm_freq_proxy'] = 1
                freq_col = 'rfm_freq_proxy'

        # Use rank if qcut fails due to too many duplicates or small data
        try:
            df['rfm_frequency'] = pd.qcut(
                df[freq_col], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop'
            )
        except ValueError:
            # Fallback to rank-based binning
            df['rfm_frequency'] = pd.qcut(
                df[freq_col].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]
            )

        # 3. Monetary / Engagement Value
        # Combine value metrics if available
        val_metrics = list(self.schema_map.get('value_metrics') or [])
        if val_metrics:
            df['engagement_value'] = df[val_metrics].sum(axis=1)
        else:
            # Fallback to edtech formula if those columns happen to exist, else 0
            df['engagement_value'] = (
                (df['exercises_completed_7d'] if 'exercises_completed_7d' in df.columns else 0) * 2 +
                (df['sessions_last_7d'] if 'sessions_last_7d' in df.columns else 0) +
                (df['streak_current'] if 'streak_current' in df.columns else 0) * 0.5
            )

        try:
            df['rfm_monetary'] = pd.qcut(
                df['engagement_value'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop'
            )
        except ValueError:
            df['rfm_monetary'] = pd.qcut(
                df['engagement_value'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]
            )

        df['rfm_score'] = (
            df['rfm_recency'].astype(float) * 0.3 +
            df['rfm_frequency'].astype(float) * 0.4 +
            df['rfm_monetary'].astype(float) * 0.3
        )

        df['rfm_segment'] = df['rfm_score'].apply(self._rfm_segment_label)

        self.rfm_scores = df[['user_id', 'rfm_recency', 'rfm_frequency',
                              'rfm_monetary', 'rfm_score', 'rfm_segment']].copy()

        print(f"      [OK] RFM Distribution:")
        print(df['rfm_segment'].value_counts().to_string())

        return df

    def _rfm_segment_label(self, score: float) -> str:
        """Map RFM score to segment label"""
        if score >= 4.5:
            return "Champions"
        elif score >= 4.0:
            return "Loyal"
        elif score >= 3.5:
            return "Potential Loyalist"
        elif score >= 3.0:
            return "Promising"
        elif score >= 2.5:
            return "Needs Attention"
        elif score >= 2.0:
            return "At Risk"
        else:
            return "Lost"

    def _engineer_clustering_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        """Engineer comprehensive features for clustering dynamically"""
        
        # Proxies for intensity and consistency — use schema_map for dynamic column names
        ret_metrics = list(self.schema_map.get('retention_metrics') or [])
        act_metrics = list(self.schema_map.get('activeness_metrics') or [])
        
        recency_col = next((c for c in ['days_since_signup'] + ret_metrics if c in df.columns), None)
        freq_col = next((c for c in ['sessions_last_7d'] + act_metrics if c in df.columns), None)
        
        if recency_col and freq_col:
            # Use second activeness metric (or freq itself) for intensity
            intensity_col = act_metrics[1] if len(act_metrics) > 1 and act_metrics[1] in df.columns else freq_col
            df['engagement_intensity'] = (
                df[freq_col].astype(float) * df[intensity_col].astype(float)
            ) / (df[recency_col].astype(float) + 1)
        else:
            df['engagement_intensity'] = 0.0

        if recency_col and 'streak_current' in df.columns:
            df['streak_consistency'] = df['streak_current'].astype(float) / (df[recency_col].astype(float) + 1)
        elif recency_col:
            df['streak_consistency'] = 0.0
        else:
            df['streak_consistency'] = 0.0
        
        df['notification_engagement'] = df['notif_open_rate_30d'] if 'notif_open_rate_30d' in df.columns else 0.5

        # Feature diversity from feature flags
        feat_cols = list(self.schema_map.get('feature_flags') or [])
        if feat_cols:
            existing_feat_cols = [c for c in feat_cols if c in df.columns]
            df['feature_diversity'] = df[existing_feat_cols].astype(float).mean(axis=1) if existing_feat_cols else 0.0
        else:
            df['feature_diversity'] = 0.0

        df['activity_pattern'] = df.apply(
            lambda row: 'morning' if row.get('preferred_hour', 12) < 12
            else ('afternoon' if row.get('preferred_hour', 12) < 18 else 'evening'),
            axis=1
        )

        clustering_features = [
            'activeness', 'gamification_propensity', 'social_propensity',
            'churn_risk', 'rfm_score', 'engagement_intensity',
            'streak_consistency', 'notification_engagement',
            'feature_diversity', 'motivation_score'
        ]

        # Filter to only existing columns
        clustering_features = [c for c in clustering_features if c in df.columns]
        
        if not clustering_features:
            # Fallback to all numeric columns if no core features found
            clustering_features = df.select_dtypes(include=[np.number]).columns.tolist()
            # Exclude IDs
            clustering_features = [c for c in clustering_features if 'id' not in c.lower()]

        for col in clustering_features:
            df[col] = df[col].fillna(df[col].median())

        X = df[clustering_features].values
        X_scaled = self.scaler.fit_transform(X)

        return df, X_scaled

    def _find_optimal_k(self, X: np.ndarray) -> int:
        """Find optimal K using silhouette, Davies-Bouldin, and elbow"""
        silhouette_scores = []
        davies_bouldin_scores = []
        inertias = []

        k_range = range(self.min_clusters, min(self.max_clusters, len(X) - 1) + 1)
        
        if len(k_range) == 0:
            # Fallback for very small data
            return min(len(X) - 1, 2) if len(X) > 2 else 1

        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = kmeans.fit_predict(X)
            silhouette_scores.append(silhouette_score(X, labels))
            davies_bouldin_scores.append(davies_bouldin_score(X, labels))
            inertias.append(kmeans.inertia_)

        best_silhouette_k = k_range[np.argmax(silhouette_scores)]
        best_db_k = k_range[np.argmin(davies_bouldin_scores)]
        elbow_k = self._find_elbow(k_range, inertias)

        print(f"      [Stats] Silhouette optimal K: {best_silhouette_k} (score: {max(silhouette_scores):.3f})")
        print(f"      [Stats] Davies-Bouldin optimal K: {best_db_k} (score: {min(davies_bouldin_scores):.3f})")
        print(f"      [Stats] Elbow optimal K: {elbow_k}")

        return best_silhouette_k

    def _find_elbow(self, k_range: range, inertias: List[float]) -> int:
        """Find elbow point using distance from line method"""
        k_array = np.array(list(k_range))
        inertia_array = np.array(inertias)

        k_norm = (k_array - k_array.min()) / (k_array.max() - k_array.min())
        inertia_norm = (inertia_array - inertia_array.min()) / (inertia_array.max() - inertia_array.min())

        line_vec = np.array([k_norm[-1] - k_norm[0], inertia_norm[-1] - inertia_norm[0]])
        line_vec_norm = line_vec / np.linalg.norm(line_vec)

        distances = []
        for i in range(len(k_norm)):
            point_vec = np.array([k_norm[i] - k_norm[0], inertia_norm[i] - inertia_norm[0]])
            proj = np.dot(point_vec, line_vec_norm) * line_vec_norm
            dist = np.linalg.norm(point_vec - proj)
            distances.append(dist)

        return k_range[np.argmax(distances)]

    def _hierarchical_clustering(self, df: pd.DataFrame, X: np.ndarray, k: int) -> pd.DataFrame:
        """Perform hierarchical clustering with optimal k"""
        hierarchical = AgglomerativeClustering(n_clusters=k, linkage='ward')
        df['segment_id'] = hierarchical.fit_predict(X)
        self.best_model = hierarchical
        self.best_k = k
        print(f"      [OK] Created {k} segments using hierarchical clustering")
        return df

    def _get_val(self, df, col, default=0):
        return df[col] if col in df.columns else default

    def _create_profiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive segment profiles dynamically"""
        profiles = []

        for seg_id in sorted(df['segment_id'].unique()):
            seg_data = df[df['segment_id'] == seg_id]
            seg_name = seg_data['segment_name'].iloc[0] if 'segment_name' in seg_data.columns else f"Segment {seg_id}"

            profile = {
                'segment_id': seg_id,
                'segment_name': seg_name,
                'segment_size': len(seg_data),
                'segment_percentage': len(seg_data) / len(df) * 100,
                'avg_activeness': seg_data['activeness'].mean(),
                'avg_gamification_propensity': seg_data['gamification_propensity'].mean(),
                'avg_social_propensity': seg_data['social_propensity'].mean(),
                'avg_ai_tutor_propensity': seg_data['ai_tutor_propensity'].mean(),
                'avg_leaderboard_propensity': seg_data['leaderboard_propensity'].mean(),
                'avg_churn_risk': seg_data['churn_risk'].mean(),
                'avg_rfm_score': seg_data['rfm_score'].mean(),
                'rfm_segment_mode': seg_data['rfm_segment'].mode()[0],
                'avg_sessions_7d': seg_data['sessions_last_7d'].mean() if 'sessions_last_7d' in seg_data.columns else 0,
                'avg_exercises_7d': seg_data['exercises_completed_7d'].mean() if 'exercises_completed_7d' in seg_data.columns else 0,
                'avg_streak': seg_data['streak_current'].mean() if 'streak_current' in seg_data.columns else 0,
                'avg_notif_open_rate': seg_data['notif_open_rate_30d'].mean() if 'notif_open_rate_30d' in seg_data.columns else 0,
                'avg_engagement_intensity': seg_data['engagement_intensity'].mean(),
                'avg_streak_consistency': seg_data['streak_consistency'].mean(),
                'avg_feature_diversity': seg_data['feature_diversity'].mean(),
                'pct_trial': (seg_data['lifecycle_stage'] == 'trial').sum() / len(seg_data) * 100,
                'pct_paid': (seg_data['lifecycle_stage'] == 'paid').sum() / len(seg_data) * 100,
                'pct_churned': (seg_data['lifecycle_stage'] == 'churned').sum() / len(seg_data) * 100,
                'pct_inactive': (seg_data['lifecycle_stage'] == 'inactive').sum() / len(seg_data) * 100,
            }
            profiles.append(profile)

        return pd.DataFrame(profiles)

    # ------------------------------------------------------------------ #
    #  LLM-Powered Segment Naming (domain-aware)
    # ------------------------------------------------------------------ #

    def _name_segments_llm(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign segment names using LLM based on domain + cluster profiles."""

        profiles_summary = []
        for _, p in self.segment_profiles.iterrows():
            profiles_summary.append(
                f"Cluster {int(p['segment_id'])}: "
                f"size={int(p['segment_size'])} ({p['segment_percentage']:.1f}%), "
                f"activeness={p['avg_activeness']:.2f}, "
                f"churn_risk={p['avg_churn_risk']:.2f}, "
                f"gamification={p['avg_gamification_propensity']:.2f}, "
                f"social={p['avg_social_propensity']:.2f}, "
                f"rfm={p['avg_rfm_score']:.2f}, "
                f"trial={p['pct_trial']:.0f}%, paid={p['pct_paid']:.0f}%, "
                f"churned={p['pct_churned']:.0f}%, inactive={p['pct_inactive']:.0f}%"
            )

        features_str = ", ".join(self.features) if self.features else "core features"

        system_prompt = (
            "You are a senior user segmentation analyst. "
            "Given cluster profiles and the business domain, assign short, "
            "descriptive, domain-relevant segment names. "
            "Names must reflect user behavior patterns in the specific domain. "
            "Do NOT use generic labels like 'Segment A' or education-specific labels "
            "like 'Learners' unless the domain is education."
        )

        user_prompt = (
            f"Domain: {self.domain}\n"
            f"Product features: {features_str}\n\n"
            f"Cluster profiles:\n" + "\n".join(profiles_summary) + "\n\n"
            "Return a JSON object mapping cluster IDs to short names (2-4 words each).\n"
            "Example format: {\"0\": \"High-Value Loyalists\", \"1\": \"Price-Sensitive Browsers\"}\n"
            "Return ONLY the JSON object, no explanation."
        )

        raw = call_llm_with_retry(system_prompt, user_prompt)
        names_map = parse_json_response(raw) if raw else None

        if names_map and isinstance(names_map, dict):
            # Apply LLM names
            segment_names = {}
            for seg_id_str, name in names_map.items():
                try:
                    segment_names[int(seg_id_str)] = str(name)
                except (ValueError, TypeError):
                    continue

            # Fill any missing
            for seg_id in df['segment_id'].unique():
                if seg_id not in segment_names:
                    segment_names[seg_id] = f"{self.domain.title()} Segment {seg_id}"

            df['segment_name'] = df['segment_id'].map(segment_names)
            print(f"      [OK] LLM assigned {len(segment_names)} domain-aware segment names")
            for sid, sname in sorted(segment_names.items()):
                print(f"          Cluster {sid} -> {sname}")
        else:
            # Fallback to rule-based naming
            print("      [WARN] LLM naming failed -- using rule-based fallback")
            df = self._name_segments_fallback(df)

        return df

    def _name_segments_fallback(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fallback: assign names based on dominant cluster characteristics."""
        segment_names = {}
        domain_prefix = self.domain.title() if self.domain != 'generic' else ''

        for _, profile in self.segment_profiles.iterrows():
            seg_id = profile['segment_id']
            activeness = profile['avg_activeness']
            churn_risk = profile['avg_churn_risk']
            social = profile['avg_social_propensity']
            rfm = profile['avg_rfm_score']

            if churn_risk > 0.7:
                name = "At-Risk Users"
            elif rfm >= 4.0 and activeness > 0.6:
                name = "Power Users"
            elif social > 0.6:
                name = "Social Engagers"
            elif activeness > 0.5:
                name = "Active Users"
            elif churn_risk > 0.5:
                name = "Needs Attention"
            else:
                name = f"Segment {seg_id}"

            if domain_prefix:
                name = f"{domain_prefix} {name}"
            segment_names[seg_id] = name

        df['segment_name'] = df['segment_id'].map(segment_names)
        return df

    def _display_segment_analysis(self, df: pd.DataFrame):
        """Display comprehensive segment analysis"""
        print("\n" + "=" * 80)
        print("SEGMENT ANALYSIS")
        print("=" * 80)

        for _, profile in self.segment_profiles.iterrows():
            seg_id = profile['segment_id']
            seg_name = df[df['segment_id'] == seg_id]['segment_name'].iloc[0]

            print(f"\n[*] Segment {seg_id}: {seg_name}")
            print(f"   Size: {profile['segment_size']} users ({profile['segment_percentage']:.1f}%)")
            print(f"   RFM: {profile['avg_rfm_score']:.2f} ({profile['rfm_segment_mode']})")
            print(f"   Activeness: {profile['avg_activeness']:.2f} | Churn Risk: {profile['avg_churn_risk']:.2f}")
            print(f"   Gamification: {profile['avg_gamification_propensity']:.2f} | Social: {profile['avg_social_propensity']:.2f}")
            print(f"   Lifecycle: Trial {profile['pct_trial']:.0f}% | Paid {profile['pct_paid']:.0f}% | Churned {profile['pct_churned']:.0f}%")

    def save_segments(self, df: pd.DataFrame, output_dir: str):
        """Save segment outputs"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cols = [
            'user_id', 'lifecycle_stage', 'segment_id', 'segment_name',
            'activeness', 'gamification_propensity', 'social_propensity',
            'ai_tutor_propensity', 'leaderboard_propensity', 'churn_risk',
            'rfm_score', 'rfm_segment',
            'engagement_intensity', 'streak_consistency', 'feature_diversity'
        ]
        # Only include columns that exist in the DataFrame
        cols = [c for c in cols if c in df.columns]
        segment_output = df[cols].copy()

        segment_output.to_csv(f"{output_dir}/user_segments.csv", index=False)
        print(f"\n[OK] Saved: {output_dir}/user_segments.csv")
