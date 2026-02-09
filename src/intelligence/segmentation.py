"""
Segmentation Engine - Creates MECE user segments
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class SegmentationEngine:
    """Creates mutually exclusive, collectively exhaustive user segments"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.n_clusters = self.config['segmentation']['n_clusters']
        self.min_segment_size = self.config['segmentation']['min_segment_size']
        self.random_state = self.config['segmentation']['random_state']
        
        self.kmeans = None
        self.scaler = None
        self.segment_profiles = None
    
    def create_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create MECE segments using K-means clustering
        
        Args:
            df: User data with engineered features
            
        Returns:
            pd.DataFrame: Data with segment assignments
        """
        print(f"\n🎯 Creating {self.n_clusters} user segments...")
        
        df = df.copy()
        
        # Select features for clustering
        feature_cols = ['activeness', 'gamification_propensity', 
                       'social_propensity', 'churn_risk']
        
        X = df[feature_cols].values
        
        # Standardize features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10
        )
        df['segment_id'] = self.kmeans.fit_predict(X_scaled)
        
        # Name segments based on characteristics
        df = self._name_segments(df)
        
        # Validate MECE property
        self._validate_mece(df)
        
        # Create segment profiles
        self.segment_profiles = self._create_segment_profiles(df)
        
        # Display segment summary
        self._display_segment_summary(df)
        
        return df
    
    def _name_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign meaningful names to segments based on characteristics"""
        segment_names = {}
        
        for seg_id in df['segment_id'].unique():
            seg_data = df[df['segment_id'] == seg_id]
            
            # Calculate segment characteristics
            avg_activeness = seg_data['activeness'].mean()
            avg_gamification = seg_data['gamification_propensity'].mean()
            avg_social = seg_data['social_propensity'].mean()
            avg_churn_risk = seg_data['churn_risk'].mean()
            
            # Name based on dominant characteristics
            if avg_churn_risk > 0.7:
                name = "At-Risk Churners"
            elif avg_activeness > 0.7 and avg_gamification > 0.7:
                name = "Highly Active Achievers"
            elif avg_social > 0.7:
                name = "Social Competitors"
            elif avg_activeness < 0.3:
                name = "Dormant Users"
            elif avg_gamification < 0.3 and avg_activeness > 0.4:
                name = "Casual Learners"
            elif avg_gamification > 0.6 and avg_activeness > 0.5:
                name = "Consistent Achievers"
            elif avg_activeness > 0.5 and avg_social < 0.3:
                name = "Independent Learners"
            else:
                name = f"Balanced Learners"
            
            # Ensure unique names
            if name in segment_names.values():
                name = f"{name} {seg_id}"
            
            segment_names[seg_id] = name
        
        df['segment_name'] = df['segment_id'].map(segment_names)
        return df
    
    def _validate_mece(self, df: pd.DataFrame):
        """Validate Mutually Exclusive, Collectively Exhaustive property"""
        print("\n✓ Validating MECE property...")
        
        # Mutually Exclusive: Each user in exactly one segment
        user_segment_count = df.groupby('user_id')['segment_id'].nunique()
        if (user_segment_count > 1).any():
            raise ValueError("MECE violation: Some users in multiple segments")
        print("   ✓ Mutually Exclusive: Each user in exactly one segment")
        
        # Collectively Exhaustive: All users are segmented
        if df['segment_id'].isna().any():
            raise ValueError("MECE violation: Some users not segmented")
        print("   ✓ Collectively Exhaustive: All users are segmented")
        
        # Check segment sizes
        segment_sizes = df['segment_id'].value_counts(normalize=True)
        small_segments = segment_sizes[segment_sizes < self.min_segment_size]
        if len(small_segments) > 0:
            print(f"   ⚠️  Warning: {len(small_segments)} segments < {self.min_segment_size*100}% of users")
        else:
            print(f"   ✓ All segments >= {self.min_segment_size*100}% of users")
    
    def _create_segment_profiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create detailed profiles for each segment"""
        profiles = []
        
        for seg_id in sorted(df['segment_id'].unique()):
            seg_data = df[df['segment_id'] == seg_id]
            
            profile = {
                'segment_id': seg_id,
                'segment_name': seg_data['segment_name'].iloc[0],
                'size': len(seg_data),
                'percentage': len(seg_data) / len(df) * 100,
                'avg_activeness': seg_data['activeness'].mean(),
                'avg_gamification_propensity': seg_data['gamification_propensity'].mean(),
                'avg_social_propensity': seg_data['social_propensity'].mean(),
                'avg_churn_risk': seg_data['churn_risk'].mean(),
                'avg_sessions_7d': seg_data['sessions_last_7d'].mean(),
                'avg_exercises_7d': seg_data['exercises_completed_7d'].mean(),
                'lifecycle_distribution': seg_data['lifecycle_stage'].value_counts().to_dict()
            }
            
            profiles.append(profile)
        
        return pd.DataFrame(profiles)
    
    def _display_segment_summary(self, df: pd.DataFrame):
        """Display summary of created segments"""
        print("\n📊 Segment Summary:")
        print("=" * 80)
        
        for seg_id in sorted(df['segment_id'].unique()):
            seg_data = df[df['segment_id'] == seg_id]
            seg_name = seg_data['segment_name'].iloc[0]
            size = len(seg_data)
            pct = size / len(df) * 100
            
            print(f"\n{seg_name} (ID: {seg_id})")
            print(f"   Size: {size} users ({pct:.1f}%)")
            print(f"   Activeness: {seg_data['activeness'].mean():.2f}")
            print(f"   Gamification: {seg_data['gamification_propensity'].mean():.2f}")
            print(f"   Social: {seg_data['social_propensity'].mean():.2f}")
            print(f"   Churn Risk: {seg_data['churn_risk'].mean():.2f}")
    
    def save_segments(self, df: pd.DataFrame, output_dir: str):
        """Save segment data to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save user segments
        segment_cols = [
            'user_id', 'segment_id', 'segment_name',
            'activeness', 'gamification_propensity', 'social_propensity', 'churn_risk'
        ]
        df[segment_cols].to_csv(output_path / 'user_segments.csv', index=False)
        
        print(f"\n✓ Segments saved to {output_dir}/user_segments.csv")
