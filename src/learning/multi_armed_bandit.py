"""
Multi-Armed Bandit Learning Engine
- Thompson Sampling for template selection
- Contextual Bandits for personalization
- UCB (Upper Confidence Bound) algorithm
- Bayesian optimization for frequency tuning
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
import yaml
import warnings
warnings.filterwarnings('ignore')


class MultiArmedBanditEngine:
    """
    Intelligent learning using Multi-Armed Bandit algorithms
    """
    
    def __init__(self, exploration_factor: float = 1.0, config_path: str = 'config/config.yaml'):
        self.exploration_factor = exploration_factor
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        perf_config = self.config.get('performance', {})
        self.good_ctr_threshold = perf_config.get('good_ctr', 0.15)
        self.bad_ctr_threshold = perf_config.get('bad_ctr', 0.05)
        
        # Bandit state for each template
        self.template_bandits = {}  # {template_id: {'alpha': int, 'beta': int}}
        
        # Contextual features for each segment
        self.segment_contexts = {}
        
        # Learning history
        self.learning_history = []
    
    def initialize_bandits(self, templates: pd.DataFrame):
        """
        Initialize Thompson Sampling bandits for each template
        Uses Beta distribution: Beta(alpha=successes+1, beta=failures+1)
        
        Args:
            templates: DataFrame with template information
        """
        print("\n🎰 Initializing Multi-Armed Bandit System...")
        
        for template_id in templates['template_id'].unique():
            # Start with uniform prior: Beta(1, 1)
            self.template_bandits[template_id] = {
                'alpha': 1,  # Success count + 1
                'beta': 1,   # Failure count + 1
                'total_sends': 0,
                'total_clicks': 0,
                'total_engagements': 0,
                'estimated_ctr': 0.5,  # Prior mean
                'confidence_interval': (0.0, 1.0)
            }
        
        print(f"   [OK] Initialized {len(self.template_bandits)} bandit arms")
    
    def update_from_experiments(self, experiment_results: pd.DataFrame):
        """
        Update bandit parameters from experiment results
        
        Args:
            experiment_results: Results with CTR and engagement data
        """
        print("\n🔄 Updating Bandit State from Experiments...")
        
        updates_count = 0
        
        for _, row in experiment_results.iterrows():
            template_id = row['template_id']
            
            if template_id not in self.template_bandits:
                continue
            
            # Calculate successes (clicks) and failures (sends - clicks)
            sends = row['total_sends']
            clicks = row['total_opens']  # Opens as proxy for clicks
            failures = sends - clicks
            
            # Update Beta parameters
            self.template_bandits[template_id]['alpha'] += clicks
            self.template_bandits[template_id]['beta'] += failures
            self.template_bandits[template_id]['total_sends'] += sends
            self.template_bandits[template_id]['total_clicks'] += clicks
            self.template_bandits[template_id]['total_engagements'] += row['total_engagements']
            
            # Update estimated CTR (posterior mean)
            alpha = self.template_bandits[template_id]['alpha']
            beta = self.template_bandits[template_id]['beta']
            self.template_bandits[template_id]['estimated_ctr'] = alpha / (alpha + beta)
            
            # Calculate 95% credible interval
            ci_lower = stats.beta.ppf(0.025, alpha, beta)
            ci_upper = stats.beta.ppf(0.975, alpha, beta)
            self.template_bandits[template_id]['confidence_interval'] = (ci_lower, ci_upper)
            
            updates_count += 1
        
        print(f"   [OK] Updated {updates_count} bandit arms")
        
        # Display top performers
        self._display_top_performers(top_n=5)
    
    def thompson_sampling_select(self, template_ids: List[str], 
                                 n_samples: int = 1) -> List[str]:
        """
        Select templates using Thompson Sampling
        Samples from Beta posterior distribution for each arm
        
        Args:
            template_ids: List of candidate template IDs
            n_samples: Number of templates to select
            
        Returns:
            List of selected template IDs
        """
        samples = {}
        
        for template_id in template_ids:
            if template_id not in self.template_bandits:
                # Unknown template: assign high uncertainty
                samples[template_id] = np.random.beta(1, 1)
            else:
                alpha = self.template_bandits[template_id]['alpha']
                beta = self.template_bandits[template_id]['beta']
                
                # Sample from Beta posterior
                samples[template_id] = np.random.beta(alpha, beta)
        
        # Select top n_samples
        sorted_templates = sorted(samples.items(), key=lambda x: x[1], reverse=True)
        selected = [t[0] for t in sorted_templates[:n_samples]]
        
        return selected
    
    def ucb_select(self, template_ids: List[str], 
                   n_samples: int = 1,
                   confidence: float = 2.0) -> List[str]:
        """
        Select templates using Upper Confidence Bound (UCB)
        UCB = mean + confidence * sqrt(ln(total_plays) / plays_this_arm)
        
        Args:
            template_ids: List of candidate template IDs
            n_samples: Number of templates to select
            confidence: Confidence parameter (higher = more exploration)
            
        Returns:
            List of selected template IDs
        """
        total_plays = sum(
            self.template_bandits[tid]['total_sends'] 
            for tid in template_ids 
            if tid in self.template_bandits
        )
        
        if total_plays == 0:
            total_plays = 1
        
        ucb_scores = {}
        
        for template_id in template_ids:
            if template_id not in self.template_bandits:
                # Unknown: assign high score for exploration
                ucb_scores[template_id] = float('inf')
            else:
                bandit = self.template_bandits[template_id]
                plays = max(bandit['total_sends'], 1)
                mean_reward = bandit['estimated_ctr']
                
                exploration_bonus = confidence * np.sqrt(np.log(total_plays) / plays)
                ucb_scores[template_id] = mean_reward + exploration_bonus
        
        # Select top n_samples
        sorted_templates = sorted(ucb_scores.items(), key=lambda x: x[1], reverse=True)
        selected = [t[0] for t in sorted_templates[:n_samples]]
        
        return selected
    
    def get_template_rankings(self, method: str = 'thompson') -> pd.DataFrame:
        """
        Get ranked templates by expected performance
        
        Args:
            method: 'thompson' (posterior mean) or 'ucb'
            
        Returns:
            DataFrame with rankings
        """
        rankings = []
        
        for template_id, bandit in self.template_bandits.items():
            rankings.append({
                'template_id': template_id,
                'estimated_ctr': bandit['estimated_ctr'],
                'ci_lower': bandit['confidence_interval'][0],
                'ci_upper': bandit['confidence_interval'][1],
                'total_sends': bandit['total_sends'],
                'total_clicks': bandit['total_clicks'],
                'alpha': bandit['alpha'],
                'beta': bandit['beta'],
                'confidence_width': bandit['confidence_interval'][1] - bandit['confidence_interval'][0]
            })
        
        df = pd.DataFrame(rankings)
        df = df.sort_values('estimated_ctr', ascending=False)
        
        return df
    
    def identify_winners_losers(self, confidence_threshold: float = 0.95) -> Dict:
        """
        Identify winning and losing templates with statistical confidence
        
        Args:
            confidence_threshold: Confidence level for classification
            
        Returns:
            Dict with 'winners', 'losers', 'uncertain'
        """
        rankings = self.get_template_rankings()
        
        # Statistical thresholds from config
        good_threshold = self.good_ctr_threshold
        bad_threshold = self.bad_ctr_threshold
        
        winners = []
        losers = []
        uncertain = []
        
        for _, row in rankings.iterrows():
            ci_lower = row['ci_lower']
            ci_upper = row['ci_upper']
            estimated_ctr = row['estimated_ctr']
            
            # Winner: Lower bound of CI > good_threshold
            if ci_lower > good_threshold:
                winners.append(row['template_id'])
            
            # Loser: Upper bound of CI < bad_threshold
            elif ci_upper < bad_threshold:
                losers.append(row['template_id'])
            
            # Uncertain: need more data
            else:
                uncertain.append(row['template_id'])
        
        return {
            'winners': winners,
            'losers': losers,
            'uncertain': uncertain
        }
    
    def optimize_exploration_exploitation(self, phase: str = 'learning') -> float:
        """
        Dynamically adjust exploration factor based on learning phase
        
        Args:
            phase: 'exploration', 'learning', or 'exploitation'
            
        Returns:
            Optimal exploration factor
        """
        if phase == 'exploration':
            # High exploration at start
            return 2.5
        elif phase == 'learning':
            # Balanced
            return 1.5
        elif phase == 'exploitation':
            # Low exploration, exploit known winners
            return 0.5
        else:
            return 1.0
    
    def _display_top_performers(self, top_n: int = 5):
        """Display top performing templates"""
        rankings = self.get_template_rankings()
        
        print(f"\n   [Stats] Top {top_n} Templates (by Estimated CTR):")
        
        for i, (_, row) in enumerate(rankings.head(top_n).iterrows(), 1):
            print(f"      {i}. {row['template_id']}: "
                  f"CTR={row['estimated_ctr']:.3f} "
                  f"(95% CI: [{row['ci_lower']:.3f}, {row['ci_upper']:.3f}]) "
                  f"| Sends={int(row['total_sends'])}")
    
    def generate_learning_report(self) -> pd.DataFrame:
        """
        Generate comprehensive learning report
        
        Returns:
            DataFrame with learning insights
        """
        classification = self.identify_winners_losers()
        rankings = self.get_template_rankings()
        
        report = []
        
        for _, row in rankings.iterrows():
            template_id = row['template_id']
            
            # Classify
            if template_id in classification['winners']:
                status = 'WINNER'
                action = 'PROMOTE'
            elif template_id in classification['losers']:
                status = 'LOSER'
                action = 'SUPPRESS'
            else:
                status = 'UNCERTAIN'
                action = 'CONTINUE_TESTING'
            
            report.append({
                'template_id': template_id,
                'status': status,
                'recommended_action': action,
                'estimated_ctr': row['estimated_ctr'],
                'confidence_interval': f"[{row['ci_lower']:.3f}, {row['ci_upper']:.3f}]",
                'total_sends': row['total_sends'],
                'confidence_width': row['confidence_width'],
                'exploration_priority': 'HIGH' if row['confidence_width'] > 0.3 else 'LOW'
            })
        
        return pd.DataFrame(report)
    
    def save_bandit_state(self, output_dir: str):
        """Save bandit state for persistence"""
        import json
        from pathlib import Path
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        state = {}
        for template_id, bandit in self.template_bandits.items():
            state[template_id] = {
                'alpha': int(bandit['alpha']),
                'beta': int(bandit['beta']),
                'total_sends': int(bandit['total_sends']),
                'total_clicks': int(bandit['total_clicks']),
                'total_engagements': int(bandit['total_engagements']),
                'estimated_ctr': float(bandit['estimated_ctr']),
                'ci_lower': float(bandit['confidence_interval'][0]),
                'ci_upper': float(bandit['confidence_interval'][1])
            }
        
        with open(f"{output_dir}/bandit_state.json", 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"\n✅ Saved bandit state: {output_dir}/bandit_state.json")

