"""
Statistical Experimentation Framework
- Bayesian A/B Testing
- Sequential analysis with early stopping
- Multi-variant testing
- Statistical significance and effect size calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class StatisticalTestingFramework:
    """
    Advanced statistical testing for experiment analysis
    """
    
    def __init__(self, alpha: float = 0.05, power: float = 0.8):
        self.alpha = alpha  # Significance level
        self.power = power  # Statistical power
        self.test_results = []
        
    def bayesian_ab_test(self, 
                        control_successes: int,
                        control_trials: int,
                        treatment_successes: int,
                        treatment_trials: int,
                        n_samples: int = 10000) -> Dict:
        """
        Bayesian A/B test using Beta-Binomial model
        
        Args:
            control_successes: Number of successes in control
            control_trials: Total trials in control
            treatment_successes: Number of successes in treatment
            treatment_trials: Total trials in treatment
            n_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary with test results
        """
        # Prior: Beta(1, 1) - uniform
        # Posterior: Beta(successes + 1, failures + 1)
        
        control_posterior = stats.beta(
            control_successes + 1,
            control_trials - control_successes + 1
        )
        
        treatment_posterior = stats.beta(
            treatment_successes + 1,
            treatment_trials - treatment_successes + 1
        )
        
        # Sample from posteriors
        control_samples = control_posterior.rvs(n_samples)
        treatment_samples = treatment_posterior.rvs(n_samples)
        
        # Probability that treatment > control
        prob_treatment_better = (treatment_samples > control_samples).mean()
        
        # Expected improvement
        expected_improvement = (treatment_samples - control_samples).mean()
        
        # Credible intervals
        control_ci = (
            control_posterior.ppf(0.025),
            control_posterior.ppf(0.975)
        )
        
        treatment_ci = (
            treatment_posterior.ppf(0.025),
            treatment_posterior.ppf(0.975)
        )
        
        # Decision
        if prob_treatment_better > 0.95:
            decision = "TREATMENT WINS"
        elif prob_treatment_better < 0.05:
            decision = "CONTROL WINS"
        else:
            decision = "INCONCLUSIVE"
        
        return {
            'prob_treatment_better': prob_treatment_better,
            'expected_improvement': expected_improvement,
            'control_rate': control_successes / control_trials,
            'treatment_rate': treatment_successes / treatment_trials,
            'control_ci': control_ci,
            'treatment_ci': treatment_ci,
            'decision': decision,
            'confidence': max(prob_treatment_better, 1 - prob_treatment_better)
        }
    
    def frequentist_ab_test(self,
                           control_successes: int,
                           control_trials: int,
                           treatment_successes: int,
                           treatment_trials: int) -> Dict:
        """
        Frequentist A/B test using two-proportion z-test
        
        Args:
            control_successes: Successes in control
            control_trials: Trials in control
            treatment_successes: Successes in treatment
            treatment_trials: Trials in treatment
            
        Returns:
            Dictionary with test results
        """
        # Rates
        p1 = control_successes / control_trials
        p2 = treatment_successes / treatment_trials
        
        # Pooled proportion
        p_pooled = (control_successes + treatment_successes) / (control_trials + treatment_trials)
        
        # Standard error
        se = np.sqrt(p_pooled * (1 - p_pooled) * (1/control_trials + 1/treatment_trials))
        
        # Z-statistic
        z = (p2 - p1) / se if se > 0 else 0
        
        # P-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        # Confidence interval for difference
        se_diff = np.sqrt(p1 * (1 - p1) / control_trials + p2 * (1 - p2) / treatment_trials)
        ci_diff = (
            (p2 - p1) - 1.96 * se_diff,
            (p2 - p1) + 1.96 * se_diff
        )
        
        # Effect size (relative improvement)
        relative_improvement = (p2 - p1) / p1 if p1 > 0 else 0
        
        # Statistical significance
        is_significant = p_value < self.alpha
        
        return {
            'control_rate': p1,
            'treatment_rate': p2,
            'absolute_difference': p2 - p1,
            'relative_improvement': relative_improvement,
            'z_statistic': z,
            'p_value': p_value,
            'is_significant': is_significant,
            'confidence_interval': ci_diff,
            'effect_size': self._cohens_h(p1, p2)
        }
    
    def _cohens_h(self, p1: float, p2: float) -> float:
        """
        Calculate Cohen's h effect size for proportions
        """
        phi1 = 2 * np.arcsin(np.sqrt(p1))
        phi2 = 2 * np.arcsin(np.sqrt(p2))
        return phi2 - phi1
    
    def sequential_test(self,
                       control_successes: int,
                       control_trials: int,
                       treatment_successes: int,
                       treatment_trials: int,
                       spending_function: str = 'obrien_fleming') -> Dict:
        """
        Sequential testing with early stopping
        Uses alpha spending functions to control Type I error
        
        Args:
            control_successes: Successes in control
            control_trials: Trials in control
            treatment_successes: Successes in treatment
            treatment_trials: Trials in treatment
            spending_function: 'obrien_fleming' or 'pocock'
            
        Returns:
            Dictionary with sequential test results
        """
        # Run standard test
        standard_result = self.frequentist_ab_test(
            control_successes, control_trials,
            treatment_successes, treatment_trials
        )
        
        # Calculate information fraction (proportion of planned sample size reached)
        # Assuming we planned for 1000 samples per arm
        planned_samples = 1000
        info_fraction = min(control_trials / planned_samples, 1.0)
        
        # Adjusted alpha based on spending function
        if spending_function == 'obrien_fleming':
            # O'Brien-Fleming: conservative early, liberal late
            adjusted_alpha = 2 * (1 - stats.norm.cdf(stats.norm.ppf(1 - self.alpha/2) / np.sqrt(info_fraction)))
        else:  # Pocock
            # Pocock: constant boundary
            adjusted_alpha = self.alpha
        
        # Decision
        can_stop_early = standard_result['p_value'] < adjusted_alpha
        
        return {
            **standard_result,
            'info_fraction': info_fraction,
            'adjusted_alpha': adjusted_alpha,
            'can_stop_early': can_stop_early,
            'recommendation': 'STOP' if can_stop_early else 'CONTINUE'
        }
    
    def multi_variant_test(self, variants: List[Dict]) -> pd.DataFrame:
        """
        Multi-variant testing with Bonferroni correction
        
        Args:
            variants: List of dicts with 'name', 'successes', 'trials'
            
        Returns:
            DataFrame with pairwise comparisons
        """
        print("\n🔬 Multi-Variant Testing...")
        
        n_variants = len(variants)
        n_comparisons = n_variants * (n_variants - 1) // 2
        
        # Bonferroni correction
        adjusted_alpha = self.alpha / n_comparisons
        
        results = []
        
        for i in range(n_variants):
            for j in range(i + 1, n_variants):
                variant_a = variants[i]
                variant_b = variants[j]
                
                test_result = self.frequentist_ab_test(
                    variant_a['successes'],
                    variant_a['trials'],
                    variant_b['successes'],
                    variant_b['trials']
                )
                
                results.append({
                    'variant_a': variant_a['name'],
                    'variant_b': variant_b['name'],
                    'rate_a': test_result['control_rate'],
                    'rate_b': test_result['treatment_rate'],
                    'difference': test_result['absolute_difference'],
                    'p_value': test_result['p_value'],
                    'adjusted_alpha': adjusted_alpha,
                    'is_significant': test_result['p_value'] < adjusted_alpha,
                    'winner': variant_a['name'] if test_result['treatment_rate'] < test_result['control_rate']
                              else (variant_b['name'] if test_result['is_significant'] else 'TIE')
                })
        
        df_results = pd.DataFrame(results)
        
        print(f"   [OK] Performed {n_comparisons} pairwise comparisons")
        print(f"   [OK] Bonferroni-adjusted α: {adjusted_alpha:.4f}")
        
        return df_results
    
    def calculate_sample_size(self,
                             baseline_rate: float,
                             min_detectable_effect: float,
                             alpha: float = None,
                             power: float = None) -> int:
        """
        Calculate required sample size for A/B test
        
        Args:
            baseline_rate: Control conversion rate
            min_detectable_effect: Minimum detectable relative improvement
            alpha: Significance level (default: self.alpha)
            power: Statistical power (default: self.power)
            
        Returns:
            Required sample size per variant
        """
        if alpha is None:
            alpha = self.alpha
        if power is None:
            power = self.power
        
        # Treatment rate
        treatment_rate = baseline_rate * (1 + min_detectable_effect)
        
        # Effect size (Cohen's h)
        h = self._cohens_h(baseline_rate, treatment_rate)
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        # Sample size per group
        n = 2 * ((z_alpha + z_beta) / h) ** 2
        
        return int(np.ceil(n))
    
    def analyze_template_experiments(self, 
                                    experiment_results: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze all template experiments with statistical rigor
        
        Args:
            experiment_results: Experiment results dataframe
            
        Returns:
            DataFrame with statistical test results
        """
        print("\n[Stats] Statistical Analysis of Template Experiments...")
        
        analysis_results = []
        
        # Get baseline (best performing template as control)
        baseline = experiment_results.nlargest(1, 'ctr').iloc[0]
        
        for _, treatment in experiment_results.iterrows():
            if treatment['template_id'] == baseline['template_id']:
                continue
            
            # Bayesian test
            bayesian_result = self.bayesian_ab_test(
                int(baseline['total_opens']),
                int(baseline['total_sends']),
                int(treatment['total_opens']),
                int(treatment['total_sends'])
            )
            
            # Frequentist test
            freq_result = self.frequentist_ab_test(
                int(baseline['total_opens']),
                int(baseline['total_sends']),
                int(treatment['total_opens']),
                int(treatment['total_sends'])
            )
            
            analysis_results.append({
                'template_id': treatment['template_id'],
                'baseline_template': baseline['template_id'],
                'treatment_ctr': treatment['ctr'],
                'baseline_ctr': baseline['ctr'],
                'absolute_difference': freq_result['absolute_difference'],
                'relative_improvement': freq_result['relative_improvement'],
                'p_value': freq_result['p_value'],
                'is_significant': freq_result['is_significant'],
                'effect_size': freq_result['effect_size'],
                'prob_better_than_baseline': bayesian_result['prob_treatment_better'],
                'bayesian_decision': bayesian_result['decision'],
                'sample_size': int(treatment['total_sends']),
                'statistical_verdict': self._get_verdict(freq_result, bayesian_result)
            })
        
        df_analysis = pd.DataFrame(analysis_results)
        
        print(f"   [OK] Analyzed {len(df_analysis)} template comparisons")
        print(f"   [OK] Significant improvements: {df_analysis['is_significant'].sum()}")
        
        return df_analysis
    
    def _get_verdict(self, freq_result: Dict, bayesian_result: Dict) -> str:
        """
        Combine frequentist and Bayesian results for final verdict
        """
        if freq_result['is_significant'] and bayesian_result['prob_treatment_better'] > 0.95:
            return "STRONG_WINNER"
        elif freq_result['is_significant'] or bayesian_result['prob_treatment_better'] > 0.90:
            return "LIKELY_WINNER"
        elif bayesian_result['prob_treatment_better'] < 0.10:
            return "LIKELY_LOSER"
        else:
            return "INCONCLUSIVE"
    
    def generate_experiment_report(self, 
                                   experiment_results: pd.DataFrame) -> Dict:
        """
        Generate comprehensive experiment report
        
        Args:
            experiment_results: Experiment results
            
        Returns:
            Dictionary with summary statistics and insights
        """
        print("\n[List] Generating Experiment Report...")
        
        # Overall statistics
        total_sends = experiment_results['total_sends'].sum()
        total_opens = experiment_results['total_opens'].sum()
        overall_ctr = total_opens / total_sends if total_sends > 0 else 0
        
        # Performance distribution
        performance_dist = experiment_results['performance_status'].value_counts()
        
        # Best performers
        top_5 = experiment_results.nlargest(5, 'ctr')
        
        # Statistical analysis
        statistical_analysis = self.analyze_template_experiments(experiment_results)
        
        report = {
            'total_templates_tested': len(experiment_results),
            'total_sends': int(total_sends),
            'total_opens': int(total_opens),
            'overall_ctr': float(overall_ctr),
            'performance_distribution': performance_dist.to_dict(),
            'top_5_templates': top_5[['template_id', 'ctr', 'engagement_rate']].to_dict('records'),
            'statistically_significant_winners': int(statistical_analysis['is_significant'].sum()),
            'avg_effect_size': float(statistical_analysis['effect_size'].mean()),
            'bayesian_strong_winners': int((statistical_analysis['bayesian_decision'] == 'TREATMENT WINS').sum())
        }
        
        print(f"   [OK] Overall CTR: {overall_ctr:.2%}")
        print(f"   [OK] Statistically significant winners: {report['statistically_significant_winners']}")
        
        return report

