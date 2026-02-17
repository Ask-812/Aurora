"""
Delta Reporter - Documents learning improvements with causal reasoning
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List


class DeltaReporter:
    """Documents and reports learning deltas"""
    
    def __init__(self):
        self.delta_report = None
    
    def generate_delta_report(self, changes_log: List[Dict],
                             iteration0_stats: Dict,
                             iteration1_stats: Dict) -> pd.DataFrame:
        """
        Generate comprehensive delta report
        
        Args:
            changes_log: List of changes from learning engine
            iteration0_stats: Statistics from Iteration 0
            iteration1_stats: Statistics from Iteration 1
            
        Returns:
            pd.DataFrame: Delta report
        """
        print("\n[+] Generating delta report...")
        
        # Convert changes log to DataFrame
        if changes_log:
            self.delta_report = pd.DataFrame(changes_log)
        else:
            self.delta_report = pd.DataFrame(columns=[
                'entity_type', 'entity_id', 'change_type', 'metric_trigger',
                'before_value', 'after_value', 'explanation'
            ])
        
        # Add summary metrics
        summary = self._calculate_summary_delta(iteration0_stats, iteration1_stats)
        
        print(f"   [OK] Documented {len(changes_log)} changes")
        print(f"\n   [Stats] Summary Improvements:")
        for metric, value in summary.items():
            if 'improvement' in metric or 'reduction' in metric:
                print(f"      • {metric}: {value:+.2%}" if isinstance(value, float) else f"      • {metric}: {value}")
        
        return self.delta_report
    
    def _calculate_summary_delta(self, iter0: Dict, iter1: Dict) -> Dict:
        """Calculate summary improvements"""
        summary = {}
        
        # CTR improvement
        if 'avg_ctr' in iter0 and 'avg_ctr' in iter1:
            summary['ctr_improvement'] = iter1['avg_ctr'] - iter0['avg_ctr']
        
        # Engagement improvement
        if 'avg_engagement' in iter0 and 'avg_engagement' in iter1:
            summary['engagement_improvement'] = iter1['avg_engagement'] - iter0['avg_engagement']
        
        # Uninstall rate reduction
        if 'avg_uninstall_rate' in iter0 and 'avg_uninstall_rate' in iter1:
            summary['uninstall_rate_reduction'] = iter0['avg_uninstall_rate'] - iter1['avg_uninstall_rate']
        
        # Template count change
        if 'total_templates' in iter0 and 'total_templates' in iter1:
            summary['templates_change'] = iter1['total_templates'] - iter0['total_templates']
        
        # Good templates increase
        if 'good_count' in iter0 and 'good_count' in iter1:
            summary['good_templates_increase'] = iter1['good_count'] - iter0['good_count']
        
        return summary
    
    def save_delta_report(self, output_dir: str):
        """Save delta report to CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.delta_report.to_csv(output_path / 'learning_delta_report.csv', index=False)
        
        print(f"\n[OK] Delta report saved to {output_dir}/learning_delta_report.csv")
    
    def print_detailed_summary(self, iteration0_stats: Dict, iteration1_stats: Dict):
        """Print detailed comparison"""
        print("\n" + "=" * 80)
        print("ITERATION 0 vs ITERATION 1 - DETAILED COMPARISON")
        print("=" * 80)
        
        print("\n[Stats] ITERATION 0 (Before Learning):")
        print(f"   Total Templates: {iteration0_stats.get('total_templates', 'N/A')}")
        print(f"   GOOD Templates: {iteration0_stats.get('good_count', 'N/A')}")
        print(f"   BAD Templates: {iteration0_stats.get('bad_count', 'N/A')}")
        print(f"   Average CTR: {iteration0_stats.get('avg_ctr', 0):.2%}")
        print(f"   Average Engagement: {iteration0_stats.get('avg_engagement', 0):.2%}")
        print(f"   Average Uninstall Rate: {iteration0_stats.get('avg_uninstall_rate', 0):.2%}")
        
        print("\n[Stats] ITERATION 1 (After Learning):")
        print(f"   Total Templates: {iteration1_stats.get('total_templates', 'N/A')}")
        print(f"   GOOD Templates: {iteration1_stats.get('good_count', 'N/A')}")
        print(f"   BAD Templates: {iteration1_stats.get('bad_count', 'N/A')}")
        print(f"   Average CTR: {iteration1_stats.get('avg_ctr', 0):.2%}")
        print(f"   Average Engagement: {iteration1_stats.get('avg_engagement', 0):.2%}")
        print(f"   Average Uninstall Rate: {iteration1_stats.get('avg_uninstall_rate', 0):.2%}")
        
        print("\n[+] IMPROVEMENTS:")
        ctr_delta = iteration1_stats.get('avg_ctr', 0) - iteration0_stats.get('avg_ctr', 0)
        eng_delta = iteration1_stats.get('avg_engagement', 0) - iteration0_stats.get('avg_engagement', 0)
        uninstall_delta = iteration0_stats.get('avg_uninstall_rate', 0) - iteration1_stats.get('avg_uninstall_rate', 0)
        
        print(f"   CTR: {iteration0_stats.get('avg_ctr', 0):.2%} → {iteration1_stats.get('avg_ctr', 0):.2%} ({ctr_delta:+.2%})")
        print(f"   Engagement: {iteration0_stats.get('avg_engagement', 0):.2%} → {iteration1_stats.get('avg_engagement', 0):.2%} ({eng_delta:+.2%})")
        print(f"   Uninstall Rate: {iteration0_stats.get('avg_uninstall_rate', 0):.2%} → {iteration1_stats.get('avg_uninstall_rate', 0):.2%} ({uninstall_delta:+.2%})")
        
        template_delta = iteration1_stats.get('total_templates', 0) - iteration0_stats.get('total_templates', 0)
        print(f"   Templates: {iteration0_stats.get('total_templates', 0)} → {iteration1_stats.get('total_templates', 0)} ({template_delta:+d})")
        
        print("\n" + "=" * 80)

