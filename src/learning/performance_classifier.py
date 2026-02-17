"""
Performance Classifier - Classifies template performance
"""

import pandas as pd
from pathlib import Path
from typing import Dict
import yaml


class PerformanceClassifier:
    """Classifies template performance as GOOD/NEUTRAL/BAD"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.good_ctr = self.config['performance']['good_ctr']
        self.good_engagement = self.config['performance']['good_engagement']
        self.bad_ctr = self.config['performance']['bad_ctr']
        self.bad_engagement = self.config['performance']['bad_engagement']
        self.min_sends = self.config['performance']['min_sends_significance']
    
    def classify_performance(self, experiment_results: pd.DataFrame) -> pd.DataFrame:
        """
        Classify template performance based on CTR and engagement
        
        Args:
            experiment_results: DataFrame with experiment results
            
        Returns:
            pd.DataFrame: Results with performance_status column
        """
        print("\n[Stats] Classifying template performance...")
        
        df = experiment_results.copy()
        
        # Calculate CTR and engagement if not present
        if 'ctr' not in df.columns:
            df['ctr'] = df['total_opens'] / df['total_sends']
        
        if 'engagement_rate' not in df.columns:
            df['engagement_rate'] = df['total_engagements'] / df['total_opens'].replace(0, 1)
        
        # Classify performance
        df['performance_status'] = df.apply(self._classify_row, axis=1)
        
        # Add statistical significance flag
        df['statistically_significant'] = df['total_sends'] >= self.min_sends
        
        # Summary
        status_counts = df['performance_status'].value_counts()
        print(f"   [OK] Classified {len(df)} templates:")
        print(f"      • GOOD: {status_counts.get('GOOD', 0)} ({status_counts.get('GOOD', 0)/len(df)*100:.1f}%)")
        print(f"      • NEUTRAL: {status_counts.get('NEUTRAL', 0)} ({status_counts.get('NEUTRAL', 0)/len(df)*100:.1f}%)")
        print(f"      • BAD: {status_counts.get('BAD', 0)} ({status_counts.get('BAD', 0)/len(df)*100:.1f}%)")
        
        # Statistical significance
        sig_count = df['statistically_significant'].sum()
        print(f"   [OK] {sig_count}/{len(df)} templates have statistical significance (>={self.min_sends} sends)")
        
        return df
    
    def _classify_row(self, row: pd.Series) -> str:
        """Classify a single template"""
        ctr = row['ctr']
        engagement = row['engagement_rate']
        
        # GOOD: High CTR AND high engagement
        if ctr > self.good_ctr and engagement > self.good_engagement:
            return 'GOOD'
        
        # BAD: Low CTR OR low engagement
        elif ctr < self.bad_ctr or engagement < self.bad_engagement:
            return 'BAD'
        
        # NEUTRAL: Everything else
        else:
            return 'NEUTRAL'
    
    def get_summary_stats(self, classified_results: pd.DataFrame) -> Dict:
        """Get summary statistics of classification"""
        stats = {
            'total_templates': len(classified_results),
            'good_count': (classified_results['performance_status'] == 'GOOD').sum(),
            'neutral_count': (classified_results['performance_status'] == 'NEUTRAL').sum(),
            'bad_count': (classified_results['performance_status'] == 'BAD').sum(),
            'avg_ctr': classified_results['ctr'].mean(),
            'avg_engagement': classified_results['engagement_rate'].mean(),
            'avg_uninstall_rate': classified_results.get('uninstall_rate', pd.Series([0])).mean()
        }
        
        return stats

