"""
Segmentation Engine with ML-Powered Insights
- RFM Analysis
- Hierarchical Clustering with Optimal K
- Propensity Score Modeling
- Behavioral Cohort Analysis
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import cdist
import yaml
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class SegmentationEngine:
    """
    ML-powered segmentation using multiple techniques:
    1. RFM (Recency, Frequency, Monetary) Analysis
    2. Hierarchical Clustering with Optimal K Selection
    3. Ensemble Clustering for Robustness
    4. Behavioral Pattern Recognition
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
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
    
    def create_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create segments using advanced ML techniques
        
        Args:
            df: User data with behavioral features
            
        Returns:
            pd.DataFrame: Data with segment assignments and enriched features
        """
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
        
        # Step 6: Segment Naming
        print("   [Tag]  Step 6: Intelligent Segment Naming")
        df = self._name_segments(df)
        
        # Display results
        self._display_segment_analysis(df)
        
        return df
    
    def _calculate_rfm_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RFM (Recency, Frequency, Monetary) scores
        Adapted for EdTech context: Recency, Frequency, Engagement Value
        """
        # Recency: Days since last activity (lower is better)
        # Use days_since_signup as proxy - more recent users are "fresher"
        df['rfm_recency'] = df['days_since_signup'].apply(
            lambda x: 5 if x <= 7 else (4 if x <= 14 else (3 if x <= 30 else (2 if x <= 60 else 1)))
        )
        
        # Frequency: Session count (higher is better)
        df['rfm_frequency'] = pd.qcut(
            df['sessions_last_7d'], 
            q=5, 
            labels=[1, 2, 3, 4, 5],
            duplicates='drop'
        )
        
        # Monetary/Value: Exercises completed + engagement (higher is better)
        df['engagement_value'] = (
            df['exercises_completed_7d'] * 2 +  # Core action
            df['sessions_last_7d'] +             # Engagement
            df['streak_current'] * 0.5 +         # Habit formation
            df['coins_balance'] * 0.01          # Progress
        )
        
        df['rfm_monetary'] = pd.qcut(
            df['engagement_value'], 
            q=5, 
            labels=[1, 2, 3, 4, 5],
            duplicates='drop'
        )
        
        # Overall RFM Score
        df['rfm_score'] = (
            df['rfm_recency'].astype(float) * 0.3 +
            df['rfm_frequency'].astype(float) * 0.4 +
            df['rfm_monetary'].astype(float) * 0.3
        )
        
        # RFM Segment
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
        """
        Engineer comprehensive features for clustering
        """
        # Behavioral features
        df['engagement_intensity'] = (
            df['sessions_last_7d'] * df['exercises_completed_7d']
        ) / (df['days_since_signup'] + 1)
        
        df['streak_consistency'] = df['streak_current'] / (df['days_since_signup'] + 1)
        
        df['notification_engagement'] = df['notif_open_rate_30d']
        
        # Feature usage intensity
        df['feature_diversity'] = (
            df['feature_ai_tutor_used'].astype(int) +
            df['feature_leaderboard_viewed'].astype(int)
        ) / 2.0
        
        # Activity pattern
        df['activity_pattern'] = df.apply(
            lambda row: 'morning' if row['preferred_hour'] < 12 
            else ('afternoon' if row['preferred_hour'] < 18 else 'evening'),
            axis=1
        )
        
        # Select features for clustering
        clustering_features = [
            'activeness',
            'gamification_propensity',
            'social_propensity',
            'churn_risk',
            'rfm_score',
            'engagement_intensity',
            'streak_consistency',
            'notification_engagement',
            'feature_diversity',
            'motivation_score'
        ]
        
        # Handle missing values
        for col in clustering_features:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        X = df[clustering_features].values
        
        # Standardize
        X_scaled = self.scaler.fit_transform(X)
        
        return df, X_scaled
    
    def _find_optimal_k(self, X: np.ndarray, method: str = 'silhouette') -> int:
        """
        Find optimal number of clusters using multiple methods
        - Silhouette Score
        - Davies-Bouldin Index
        - Elbow Method
        """
        silhouette_scores = []
        davies_bouldin_scores = []
        inertias = []
        
        k_range = range(self.min_clusters, self.max_clusters + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = kmeans.fit_predict(X)
            
            silhouette_scores.append(silhouette_score(X, labels))
            davies_bouldin_scores.append(davies_bouldin_score(X, labels))
            inertias.append(kmeans.inertia_)
        
        # Silhouette: higher is better
        best_silhouette_k = k_range[np.argmax(silhouette_scores)]
        
        # Davies-Bouldin: lower is better
        best_db_k = k_range[np.argmin(davies_bouldin_scores)]
        
        # Elbow method: find elbow point
        elbow_k = self._find_elbow(k_range, inertias)
        
        print(f"      [Stats] Silhouette optimal K: {best_silhouette_k} (score: {max(silhouette_scores):.3f})")
        print(f"      [Stats] Davies-Bouldin optimal K: {best_db_k} (score: {min(davies_bouldin_scores):.3f})")
        print(f"      [Stats] Elbow optimal K: {elbow_k}")
        
        # Use silhouette as primary metric
        return best_silhouette_k
    
    def _find_elbow(self, k_range: range, inertias: List[float]) -> int:
        """Find elbow point using distance from line method"""
        k_array = np.array(list(k_range))
        inertia_array = np.array(inertias)
        
        # Normalize
        k_norm = (k_array - k_array.min()) / (k_array.max() - k_array.min())
        inertia_norm = (inertia_array - inertia_array.min()) / (inertia_array.max() - inertia_array.min())
        
        # Calculate distance from line connecting first and last points
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
        """
        Perform hierarchical clustering with optimal k
        """
        # Use Ward linkage for balanced clusters
        hierarchical = AgglomerativeClustering(
            n_clusters=k,
            linkage='ward'
        )
        
        df['segment_id'] = hierarchical.fit_predict(X)
        self.best_model = hierarchical
        self.best_k = k
        
        print(f"      [OK] Created {k} segments using hierarchical clustering")
        
        return df
    
    def _create_profiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create comprehensive segment profiles with advanced metrics
        """
        profiles = []
        
        for seg_id in sorted(df['segment_id'].unique()):
            seg_data = df[df['segment_id'] == seg_id]
            seg_name = seg_data['segment_name'].iloc[0] if 'segment_name' in seg_data.columns else f"Segment {seg_id}"
            
            profile = {
                'segment_id': seg_id,
                'segment_name': seg_name,
                'segment_size': len(seg_data),
                'segment_percentage': len(seg_data) / len(df) * 100,
                
                # Core metrics
                'avg_activeness': seg_data['activeness'].mean(),
                'avg_gamification_propensity': seg_data['gamification_propensity'].mean(),
                'avg_social_propensity': seg_data['social_propensity'].mean(),
                'avg_churn_risk': seg_data['churn_risk'].mean(),
                
                # RFM
                'avg_rfm_score': seg_data['rfm_score'].mean(),
                'rfm_segment_mode': seg_data['rfm_segment'].mode()[0],
                
                # Engagement
                'avg_sessions_7d': seg_data['sessions_last_7d'].mean(),
                'avg_exercises_7d': seg_data['exercises_completed_7d'].mean(),
                'avg_streak': seg_data['streak_current'].mean(),
                'avg_notif_open_rate': seg_data['notif_open_rate_30d'].mean(),
                
                # Advanced metrics
                'avg_engagement_intensity': seg_data['engagement_intensity'].mean(),
                'avg_streak_consistency': seg_data['streak_consistency'].mean(),
                'avg_feature_diversity': seg_data['feature_diversity'].mean(),
                
                # Lifecycle distribution
                'pct_trial': (seg_data['lifecycle_stage'] == 'trial').sum() / len(seg_data) * 100,
                'pct_paid': (seg_data['lifecycle_stage'] == 'paid').sum() / len(seg_data) * 100,
                'pct_churned': (seg_data['lifecycle_stage'] == 'churned').sum() / len(seg_data) * 100,
                'pct_inactive': (seg_data['lifecycle_stage'] == 'inactive').sum() / len(seg_data) * 100,
            }
            
            profiles.append(profile)
        
        return pd.DataFrame(profiles)
    
    def _name_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign meaningful names based on multi-dimensional characteristics
        """
        segment_names = {}
        
        for _, profile in self.segment_profiles.iterrows():
            seg_id = profile['segment_id']
            
            # Extract key characteristics
            activeness = profile['avg_activeness']
            gamification = profile['avg_gamification_propensity']
            social = profile['avg_social_propensity']
            churn_risk = profile['avg_churn_risk']
            rfm = profile['avg_rfm_score']
            engagement_intensity = profile['avg_engagement_intensity']
            
            # Multi-dimensional naming logic
            if rfm >= 4.5 and activeness > 0.7:
                name = "Power Users (Champions)"
            elif rfm >= 4.0 and gamification > 0.7:
                name = "Achievement Hunters"
            elif social > 0.7 and activeness > 0.5:
                name = "Social Learners"
            elif churn_risk > 0.7:
                name = "At-Risk Users"
            elif activeness < 0.3 and churn_risk > 0.5:
                name = "Dormant Users"
            elif engagement_intensity > 0.5 and gamification > 0.6:
                name = "Consistent Achievers"
            elif activeness > 0.5 and gamification < 0.4:
                name = "Casual Learners"
            elif rfm >= 3.5 and rfm < 4.0:
                name = "Emerging Engagers"
            elif social < 0.3 and activeness > 0.4:
                name = "Independent Learners"
            elif churn_risk > 0.5 and churn_risk <= 0.7:
                name = "Needs Attention"
            else:
                name = f"Balanced Learners {seg_id}"
            
            segment_names[seg_id] = name
        
        df['segment_name'] = df['segment_id'].map(segment_names)
        
        return df
    
    def _display_segment_analysis(self, df: pd.DataFrame):
        """Display comprehensive segment analysis"""
        print("\n" + "═" * 80)
        print("SEGMENT ANALYSIS")
        print("═" * 80)
        
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
        from pathlib import Path
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save user segments
        segment_output = df[[
            'user_id', 'segment_id', 'segment_name',
            'activeness', 'gamification_propensity', 'social_propensity', 'churn_risk',
            'rfm_score', 'rfm_segment',
            'engagement_intensity', 'streak_consistency', 'feature_diversity'
        ]].copy()
        
        segment_output.to_csv(f"{output_dir}/user_segments.csv", index=False)
        print(f"\n✅ Saved: {output_dir}/user_segments.csv")

