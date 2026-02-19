"""
Learning Engine - Applies learning from experiment results
"""

import pandas as pd
from typing import Dict, List, Tuple
import yaml


class LearningEngine:
    """Applies learning actions based on experiment results"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.changes_log = []
    
    def learn_and_improve(self, templates: pd.DataFrame, timing_recs: pd.DataFrame,
                         themes: pd.DataFrame, experiment_results: pd.DataFrame) -> Tuple:
        """
        Apply learning from experiment results
        
        Args:
            templates: Current templates
            timing_recs: Current timing recommendations
            themes: Current themes
            experiment_results: Classified experiment results
            
        Returns:
            tuple: (improved_templates, improved_timing, improved_themes, changes_log)
        """
        print("\n[AI] Learning from experiment results...")
        
        self.changes_log = []
        
        # 1. Template Learning
        improved_templates = self._learn_templates(templates, experiment_results)
        
        # 2. Timing Learning
        improved_timing = self._learn_timing(timing_recs, experiment_results)
        
        # 3. Theme Learning
        improved_themes = self._learn_themes(themes, experiment_results)
        
        # 4. Frequency Learning
        frequency_changes = self._learn_frequency(experiment_results)
        
        print(f"\n   [OK] Applied {len(self.changes_log)} learning actions")
        
        return improved_templates, improved_timing, improved_themes, self.changes_log
    
    def _learn_templates(self, templates: pd.DataFrame, 
                        experiment_results: pd.DataFrame) -> pd.DataFrame:
        """Learn which templates to suppress/promote"""
        print("   📝 Learning template performance...")
        
        templates_improved = templates.copy()
        
        # Add weight column if not present
        if 'weight' not in templates_improved.columns:
            templates_improved['weight'] = 1.0
        
        # Get BAD templates
        bad_templates = experiment_results[
            experiment_results['performance_status'] == 'BAD'
        ]['template_id'].unique()
        
        # Suppress BAD templates
        for template_id in bad_templates:
            if template_id in templates_improved['template_id'].values:
                # Get metrics
                metrics = experiment_results[
                    experiment_results['template_id'] == template_id
                ].iloc[0]
                
                # Log change
                self.changes_log.append({
                    'entity_type': 'template',
                    'entity_id': template_id,
                    'change_type': 'suppression',
                    'metric_trigger': f"ctr={metrics['ctr']:.3f}, engagement={metrics['engagement_rate']:.3f}",
                    'before_value': 'active',
                    'after_value': 'suppressed',
                    'explanation': f"CTR of {metrics['ctr']:.1%} (threshold: 5%) and/or engagement of {metrics['engagement_rate']:.1%} (threshold: 20%) below acceptable levels. Suppressed to improve overall performance."
                })
                
                # Remove template
                templates_improved = templates_improved[
                    templates_improved['template_id'] != template_id
                ]
        
        # Get GOOD templates
        good_templates = experiment_results[
            experiment_results['performance_status'] == 'GOOD'
        ]['template_id'].unique()
        
        # Promote GOOD templates
        for template_id in good_templates:
            if template_id in templates_improved['template_id'].values:
                # Get metrics
                metrics = experiment_results[
                    experiment_results['template_id'] == template_id
                ].iloc[0]
                
                # Log change
                self.changes_log.append({
                    'entity_type': 'template',
                    'entity_id': template_id,
                    'change_type': 'promotion',
                    'metric_trigger': f"ctr={metrics['ctr']:.3f}, engagement={metrics['engagement_rate']:.3f}",
                    'before_value': 'weight=1.0',
                    'after_value': 'weight=3.0',
                    'explanation': f"CTR of {metrics['ctr']:.1%} (>15%) and engagement of {metrics['engagement_rate']:.1%} (>40%) indicate strong performance. Increased weight to 3.0 for higher usage probability."
                })
                
                # Increase weight
                templates_improved.loc[
                    templates_improved['template_id'] == template_id, 'weight'
                ] = 3.0
        
        print(f"      • Suppressed {len(bad_templates)} BAD templates")
        print(f"      • Promoted {len(good_templates)} GOOD templates")
        
        return templates_improved
    
    def _learn_timing(self, timing_recs: pd.DataFrame,
                     experiment_results: pd.DataFrame) -> pd.DataFrame:
        """Learn optimal timing windows"""
        print("   [Time] Learning timing patterns...")
        
        # Analyze window performance by segment
        window_perf = experiment_results.groupby(
            ['segment_id', 'notification_window']
        ).agg({
            'ctr': 'mean',
            'total_sends': 'sum'
        }).reset_index()
        
        # Filter for significance
        window_perf = window_perf[window_perf['total_sends'] >= 100]
        
        timing_improved = []
        changes_count = 0
        
        for seg_id in window_perf['segment_id'].unique():
            seg_data = window_perf[window_perf['segment_id'] == seg_id]
            
            # Find worst performing window
            worst = seg_data.loc[seg_data['ctr'].idxmin()]

            bad_ctr_threshold = self.config['performance'].get('bad_ctr', 0.05)
            if worst['ctr'] < bad_ctr_threshold:
                # Log suppression
                self.changes_log.append({
                    'entity_type': 'timing',
                    'entity_id': f"segment_{seg_id}",
                    'change_type': 'window_suppression',
                    'metric_trigger': f"{worst['notification_window']}_ctr={worst['ctr']:.3f}",
                    'before_value': worst['notification_window'],
                    'after_value': 'suppressed',
                    'explanation': f"Window '{worst['notification_window']}' had {worst['ctr']:.1%} CTR (threshold: {bad_ctr_threshold:.0%}) for segment {seg_id}. Suppressed to reallocate sends to better-performing windows."
                })
                changes_count += 1
                
                # Remove this window
                seg_data = seg_data[seg_data['notification_window'] != worst['notification_window']]
            
            # Keep top 2 windows
            for priority, (_, row) in enumerate(seg_data.nlargest(2, 'ctr').iterrows(), 1):
                timing_improved.append({
                    'segment_id': row['segment_id'],
                    'segment_name': f"Segment {row['segment_id']}",
                    'lifecycle_stage': 'all',
                    'time_window': row['notification_window'],
                    'priority': priority,
                    'expected_ctr': row['ctr'],
                    'rationale': f"Learned: {row['ctr']:.1%} CTR from {int(row['total_sends'])} sends"
                })
        
        print(f"      • Optimized timing for {len(window_perf['segment_id'].unique())} segments")
        print(f"      • Suppressed {changes_count} underperforming windows")
        
        return pd.DataFrame(timing_improved) if timing_improved else timing_recs
    
    def _learn_themes(self, themes: pd.DataFrame,
                     experiment_results: pd.DataFrame) -> pd.DataFrame:
        """Learn which themes perform best"""
        print("   [Theme] Learning theme effectiveness...")
        
        # Analyze theme performance
        theme_perf = experiment_results.groupby(
            ['segment_id', 'theme']
        ).agg({
            'ctr': 'mean',
            'engagement_rate': 'mean'
        }).reset_index()
        
        themes_improved = themes.copy()
        changes_count = 0
        
        for seg_id in theme_perf['segment_id'].unique():
            seg_themes = theme_perf[theme_perf['segment_id'] == seg_id]
            
            if len(seg_themes) > 1:
                # Find best theme
                best_theme = seg_themes.loc[seg_themes['ctr'].idxmax()]
                current_theme = themes[themes['segment_id'] == seg_id]['primary_theme'].iloc[0]
                
                if best_theme['theme'] != current_theme and best_theme['ctr'] > 0.12:
                    # Log change
                    self.changes_log.append({
                        'entity_type': 'theme',
                        'entity_id': f"segment_{seg_id}",
                        'change_type': 'primary_theme_update',
                        'metric_trigger': f"{best_theme['theme']}_ctr={best_theme['ctr']:.3f}",
                        'before_value': current_theme,
                        'after_value': best_theme['theme'],
                        'explanation': f"Theme '{best_theme['theme']}' achieved {best_theme['ctr']:.1%} CTR vs '{current_theme}' for segment {seg_id}. Updated primary theme to improve resonance."
                    })
                    
                    # Update theme
                    themes_improved.loc[
                        themes_improved['segment_id'] == seg_id, 'primary_theme'
                    ] = best_theme['theme']
                    changes_count += 1
        
        print(f"      • Updated themes for {changes_count} segments")
        
        return themes_improved
    
    def _learn_frequency(self, experiment_results: pd.DataFrame) -> List[Dict]:
        """Learn frequency adjustments based on uninstall rate"""
        print("   [Stats] Learning frequency adjustments...")
        
        if 'uninstall_rate' not in experiment_results.columns:
            print("      ⚠️  No uninstall_rate data available")
            return []
        
        # Analyze uninstall rate by segment
        uninstall_by_segment = experiment_results.groupby('segment_id')['uninstall_rate'].mean()
        
        frequency_changes = []
        
        for seg_id, uninstall_rate in uninstall_by_segment.items():
            if uninstall_rate > 0.02:  # 2% threshold
                # Log change
                self.changes_log.append({
                    'entity_type': 'frequency',
                    'entity_id': f"segment_{seg_id}",
                    'change_type': 'frequency_reduction',
                    'metric_trigger': f"uninstall_rate={uninstall_rate:.3f}",
                    'before_value': 'baseline',
                    'after_value': 'reduced_by_2',
                    'explanation': f"Segment {seg_id} had {uninstall_rate:.1%} uninstall rate (threshold: 2%). Reduced notification frequency by 2/day to prevent churn."
                })
                
                frequency_changes.append({
                    'segment_id': seg_id,
                    'adjustment': -2,
                    'reason': f"High uninstall rate: {uninstall_rate:.1%}"
                })
        
        print(f"      • Reduced frequency for {len(frequency_changes)} segments")
        
        return frequency_changes

