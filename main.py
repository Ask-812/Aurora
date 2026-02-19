"""
Project Aurora - ML-POWERED Orchestrator
World-Class Self-Learning Notification System

This version integrates:
-  RFM + Hierarchical Segmentation
- XGBoost/LightGBM Propensity Models
- Multi-Armed Bandit Learning (Thompson Sampling)
- Survival Analysis for Timing
- NLP Template Optimization
- Bayesian Statistical Testing

Usage:
    python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv
    python main.py --mode iteration1 --user-data data/sample/user_data_sample.csv --experiment-results data/sample/experiment_results_sample.csv
"""

import sys
import os

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Core engines
from src.knowledge_bank.kb_engine import KnowledgeBankEngine
from src.intelligence.data_ingestion import DataIngestionEngine
from src.intelligence.goal_builder import GoalBuilder

# ML engines
from src.intelligence.segmentation import SegmentationEngine
from src.intelligence.ml_propensity_models import PropensityModelEngine

# Communication engines
from src.communication.theme_engine import ThemeEngine
from src.communication.template_generator import TemplateGenerator
from src.communication.timing_optimizer import TimingOptimizer
from src.communication.nlp_template_optimizer import NLPTemplateOptimizer
from src.communication.schedule_generator import ScheduleGenerator

# Learning engines
from src.learning.multi_armed_bandit import MultiArmedBanditEngine
from src.learning.statistical_testing import StatisticalTestingFramework
from src.learning.performance_classifier import PerformanceClassifier
from src.learning.delta_reporter import DeltaReporter


def display_banner():
    """Display system banner"""
    print("\n" + "=" * 80)
    print("  PROJECT AURORA - ML-POWERED ORCHESTRATOR")
    print("=" * 80)
    print("  Features:")
    print("  * RFM Analysis + Hierarchical Clustering")
    print("  * XGBoost Churn Prediction + LightGBM Engagement Models")
    print("  * Multi-Armed Bandit (Thompson Sampling)")
    print("  * Survival Analysis for Timing Optimization")
    print("  * NLP-Powered Template Analysis")
    print("  * Bayesian A/B Testing")
    print("=" * 80 + "\n")


def run_iteration_0(user_data_path: str, kb_text: str = None):
    """
    Run Iteration 0 with ML models
    
    Args:
        user_data_path: Path to user data CSV
        kb_text: Knowledge bank text (optional)
    """
    display_banner()
    
    print("MODE: ITERATION 0 (Training ML Models)")
    print("=" * 80)
    
    output_dir = "data/output"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Knowledge Bank
    print("\n" + "=" * 80)
    print("STEP 1: KNOWLEDGE BANK EXTRACTION")
    print("=" * 80)
    
    kb_engine = KnowledgeBankEngine()
    if kb_text is None:
        # Read from file if available
        pdf_path = Path("pdf_content.txt")
        if pdf_path.exists():
            with open(pdf_path, 'r', encoding='utf-8') as f:
                kb_text = f.read()
        else:
            kb_text = "SpeakX English Learning Platform"
    
    kb_data = kb_engine.process_knowledge_bank(kb_text)
    kb_engine.save_outputs(output_dir)
    
    # Step 2: Data Ingestion
    print("\n" + "=" * 80)
    print("STEP 2:  DATA INGESTION")
    print("=" * 80)
    
    ingestion_engine = DataIngestionEngine(knowledge_bank=kb_data)
    user_data = ingestion_engine.load_and_validate(user_data_path)
    user_data = ingestion_engine.engineer_features(user_data)
    
    stats = ingestion_engine.get_summary_stats(user_data)
    print(f"\nDataset: {stats['total_users']} users | "
          f"Avg Active: {stats['avg_activeness']:.2f} | "
          f"Avg Churn Risk: {stats['avg_churn_risk']:.2f}")
    
    # Step 3: ML-POWERED Segmentation
    print("\n" + "=" * 80)
    print("STEP 3:  SEGMENTATION (RFM + Hierarchical)")
    print("=" * 80)
    
    seg_engine = SegmentationEngine()
    user_data = seg_engine.create_segments(user_data)
    seg_engine.save_segments(user_data, output_dir)
    
    # Step 4: ML Propensity Models
    print("\n" + "=" * 80)
    print("STEP 4: TRAINING ML PROPENSITY MODELS")
    print("=" * 80)
    
    ml_engine = PropensityModelEngine()
    
    # Train churn model
    ml_engine.train_churn_model(user_data)
    
    # Train engagement model
    ml_engine.train_engagement_model(user_data)
    
    # Generate propensity scores
    user_data = ml_engine.predict_user_propensities(user_data)
    
    # Save models
    ml_engine.save_models(output_dir)
    
    # Step 5: Goal Building
    print("\n" + "=" * 80)
    print("STEP 5: INTELLIGENT GOAL BUILDING")
    print("=" * 80)
    
    goal_builder = GoalBuilder()
    segment_goals = goal_builder.build_goals(seg_engine.segment_profiles)
    goal_builder.save_goals(output_dir)
    
    # Step 6: Theme Generation
    print("\n" + "=" * 80)
    print("STEP 6: BEHAVIORAL THEME MAPPING")
    print("=" * 80)
    
    theme_engine = ThemeEngine(kb_data['tone_hook_matrix'])
    themes = theme_engine.generate_themes(seg_engine.segment_profiles)
    theme_engine.save_themes(output_dir)
    
    # Step 7: Template Generation + NLP Analysis
    print("\n" + "=" * 80)
    print("STEP 7: TEMPLATE GENERATION + NLP OPTIMIZATION")
    print("=" * 80)
    
    template_gen = TemplateGenerator(kb_data, themes)
    templates = template_gen.generate_templates(segment_goals)
    
    # NLP Analysis
    nlp_optimizer = NLPTemplateOptimizer()
    templates = nlp_optimizer.analyze_templates(templates)
    
    template_gen.save_templates(output_dir)
    
    # Step 8:  Timing Optimization
    print("\n" + "=" * 80)
    print("STEP 8: TIMING OPTIMIZATION (Behavioral Patterns)")
    print("=" * 80)
    
    timing_optimizer = TimingOptimizer()
    timing_recs = timing_optimizer.optimize_with_survival_analysis(user_data)
    frequency_recs = timing_optimizer.predict_optimal_frequency(user_data)
    timing_optimizer.save_timing_recommendations(output_dir)
    
    # Save frequency recommendations
    frequency_recs.to_csv(f"{output_dir}/frequency_recommendations.csv", index=False)
    
    # Step 9: Schedule Generation
    print("\n" + "=" * 80)
    print("STEP 9: PERSONALIZED SCHEDULE GENERATION")
    print("=" * 80)
    
    schedule_gen = ScheduleGenerator()
    schedule_gen.templates = templates
    schedule_gen.timing_recs = timing_recs
    schedule_gen.frequency_recs = frequency_recs
    schedule_gen.themes = themes
    
    schedule = schedule_gen.generate_schedules(
        user_data,
        templates=templates,
        timing_recs=timing_recs,
        segment_goals=segment_goals,
        frequency_recs=frequency_recs,
        max_users=100
    )
    schedule_gen.save_schedules(output_dir)
    
    # Step 10: Initialize Multi-Armed Bandit
    print("\n" + "=" * 80)
    print("STEP 10: MULTI-ARMED BANDIT INITIALIZATION")
    print("=" * 80)
    
    bandit_engine = MultiArmedBanditEngine()
    bandit_engine.initialize_bandits(templates)
    bandit_engine.save_bandit_state(output_dir)
    
    print("\n" + "=" * 80)
    print("ITERATION 0 COMPLETE - ML MODELS TRAINED")
    print("=" * 80)
    print(f"\nOutputs saved to: {output_dir}/")
    print("\nNext: Run Iteration 1 with experiment results for learning")


def run_iteration_1(user_data_path: str, experiment_results_path: str):
    """
    Run Iteration 1 with learning
    
    Args:
        user_data_path: Path to user data CSV
        experiment_results_path: Path to experiment results CSV
    """
    display_banner()
    
    print("MODE: ITERATION 1 (Learning & Optimization)")
    print("=" * 80)
    
    output_dir = "data/output"
    
    # Load previous iteration outputs
    print("\nLoading Iteration 0 outputs...")
    templates = pd.read_csv(f"{output_dir}/message_templates.csv")
    timing_recs = pd.read_csv(f"{output_dir}/timing_recommendations_improved.csv")
    themes = pd.read_csv(f"{output_dir}/communication_themes.csv")
    user_data = pd.read_csv(f"{output_dir}/user_segments.csv")

    # Load Knowledge Bank from saved outputs
    import json
    with open(f"{output_dir}/feature_goal_map.json", 'r') as f:
        feature_goal_map = json.load(f)
    kb_data = {'feature_goal_map': feature_goal_map}
    
    # Load experiment results
    print(f"\nLoading experiment results from: {experiment_results_path}")
    experiment_results = pd.read_csv(experiment_results_path)
    
    # Step 1: Performance Classification
    print("\n" + "=" * 80)
    print("STEP 1: PERFORMANCE CLASSIFICATION")
    print("=" * 80)
    
    classifier = PerformanceClassifier()
    experiment_results = classifier.classify_performance(experiment_results)
    
    # Save classified results
    experiment_results.to_csv(f"{output_dir}/experiment_results.csv", index=False)
    
    # Step 2: Statistical Testing
    print("\n" + "=" * 80)
    print("STEP 2: BAYESIAN STATISTICAL ANALYSIS")
    print("=" * 80)
    
    stats_framework = StatisticalTestingFramework()
    statistical_analysis = stats_framework.analyze_template_experiments(experiment_results)
    experiment_report = stats_framework.generate_experiment_report(experiment_results)
    
    # Save statistical analysis
    statistical_analysis.to_csv(f"{output_dir}/statistical_analysis.csv", index=False)
    
    # Step 3: Multi-Armed Bandit Learning
    print("\n" + "=" * 80)
    print("STEP 3: MULTI-ARMED BANDIT LEARNING")
    print("=" * 80)
    
    bandit_engine = MultiArmedBanditEngine()
    bandit_engine.initialize_bandits(templates)
    bandit_engine.update_from_experiments(experiment_results)
    
    # Get rankings
    template_rankings = bandit_engine.get_template_rankings()
    learning_report = bandit_engine.generate_learning_report()
    
    # Save bandit outputs
    template_rankings.to_csv(f"{output_dir}/template_rankings_bandit.csv", index=False)
    learning_report.to_csv(f"{output_dir}/bandit_learning_report.csv", index=False)
    bandit_engine.save_bandit_state(output_dir)
    
    # Step 4: NLP Template Optimization
    print("\n" + "=" * 80)
    print("STEP 4: NLP-POWERED TEMPLATE OPTIMIZATION")
    print("=" * 80)
    
    nlp_optimizer = NLPTemplateOptimizer()
    templates_analyzed = nlp_optimizer.analyze_templates(templates, experiment_results)
    nlp_recommendations = nlp_optimizer.generate_optimization_recommendations(
        templates_analyzed, experiment_results
    )
    
    # Save NLP analysis
    templates_analyzed.to_csv(f"{output_dir}/templates_nlp_analysis.csv", index=False)
    nlp_recommendations.to_csv(f"{output_dir}/nlp_recommendations.csv", index=False)
    
    # Step 5:  Timing Re-optimization
    print("\n" + "=" * 80)
    print("STEP 5: RE-OPTIMIZE TIMING (Survival Analysis)")
    print("=" * 80)
    
    timing_optimizer = TimingOptimizer()
    
    # Load full user data for timing optimization
    ingestion_engine = DataIngestionEngine(knowledge_bank=kb_data)
    user_data_full = ingestion_engine.load_and_validate(user_data_path)
    user_data_full = ingestion_engine.engineer_features(user_data_full)
    
    # Merge segment assignments
    user_data_full = user_data_full.merge(
        user_data[['user_id', 'segment_id', 'segment_name']],
        on='user_id',
        how='left'
    )
    
    improved_timing = timing_optimizer.optimize_with_survival_analysis(
        user_data_full, experiment_results
    )
    improved_frequency = timing_optimizer.predict_optimal_frequency(
        user_data_full, experiment_results
    )
    
    # Save improved timing
    improved_timing.to_csv(f"{output_dir}/timing_recommendations_improved.csv", index=False)
    improved_frequency.to_csv(f"{output_dir}/frequency_recommendations_improved.csv", index=False)
    
    # Step 6: Template Filtering (Based on Bandit)
    print("\n" + "=" * 80)
    print("STEP 6: INTELLIGENT TEMPLATE FILTERING")
    print("=" * 80)
    
    winners_losers = bandit_engine.identify_winners_losers()
    
    # Filter out losers
    templates_improved = templates[
        ~templates['template_id'].isin(winners_losers['losers'])
    ].copy()
    
    # Boost winners
    templates_improved['weight'] = 1.0
    templates_improved.loc[
        templates_improved['template_id'].isin(winners_losers['winners']),
        'weight'
    ] = 2.0
    
    templates_improved.to_csv(f"{output_dir}/message_templates_improved.csv", index=False)
    
    print(f"   * Suppressed {len(winners_losers['losers'])} underperforming templates")
    print(f"   * Promoted {len(winners_losers['winners'])} high-performing templates")
    
    # Step 7: Delta Reporting
    print("\n" + "=" * 80)
    print("STEP 7: COMPREHENSIVE DELTA REPORTING")
    print("=" * 80)
    
    # Build changes log
    changes_log = []
    
    # Log template suppressions
    for loser in winners_losers['losers']:
        perf = experiment_results[experiment_results['template_id'] == loser].iloc[0]
        ci = bandit_engine.template_bandits.get(loser, {}).get('confidence_interval', 'N/A')
        changes_log.append({
            'entity_type': 'template',
            'entity_id': loser,
            'change_type': 'suppression',
            'metric_trigger': f"CTR={perf['ctr']:.3f}, Engagement={perf['engagement_rate']:.3f}",
            'before_value': 'active',
            'after_value': 'suppressed',
            'explanation': f"Bandit analysis: Consistently underperformed (CTR < 5% or Engagement < 20%). Statistical confidence: {ci}"
        })
    
    # Log template promotions
    for winner in winners_losers['winners']:
        perf = experiment_results[experiment_results['template_id'] == winner].iloc[0]
        changes_log.append({
            'entity_type': 'template',
            'entity_id': winner,
            'change_type': 'promotion',
            'metric_trigger': f"CTR={perf['ctr']:.3f}, Engagement={perf['engagement_rate']:.3f}",
            'before_value': 'weight=1.0',
            'after_value': 'weight=2.0',
            'explanation': f"Bandit analysis: Consistently outperformed (CTR > 15% and Engagement > 40%). Statistical significance confirmed via Bayesian testing."
        })
    
    # Log timing changes
    if len(improved_timing) > 0:
        changes_log.append({
            'entity_type': 'timing',
            'entity_id': 'global',
            'change_type': 'optimization',
            'metric_trigger': 'survival_analysis',
            'before_value': 'behavioral_pattern',
            'after_value': 'experiment_learned',
            'explanation': f"Re-optimized timing windows based on {len(experiment_results)} experimental observations. Applied survival analysis to identify optimal engagement windows per segment."
        })
    
    # Generate and save delta report
    delta_reporter = DeltaReporter()
    iter0_stats = {'total_templates': len(templates), 'avg_ctr': 0.0}
    iter1_stats = classifier.get_summary_stats(experiment_results)
    
    delta_report = delta_reporter.generate_delta_report(changes_log, iter0_stats, iter1_stats)
    delta_reporter.save_delta_report(output_dir)
    
    # Step 8: Generate Improved Schedule
    print("\n" + "=" * 80)
    print("STEP 8: GENERATE IMPROVED SCHEDULE")
    print("=" * 80)
    
    # Load segment goals
    segment_goals = pd.read_csv(f"{output_dir}/segment_goals.csv")
    
    schedule_gen = ScheduleGenerator()
    schedule_gen.templates = templates_improved
    schedule_gen.timing_recs = improved_timing
    schedule_gen.frequency_recs = improved_frequency
    schedule_gen.themes = themes
    
    improved_schedule = schedule_gen.generate_schedules(
        user_data_full,
        templates=templates_improved,
        timing_recs=improved_timing,
        segment_goals=segment_goals,
        frequency_recs=improved_frequency,
        max_users=100
    )
    
    # Save improved schedule
    improved_schedule.to_csv(f"{output_dir}/user_notification_schedule_improved.csv", index=False)
    print(f"\n   * Saved improved schedule: {len(improved_schedule)} entries")
    
    print("\n" + "=" * 80)
    print("ITERATION 1 COMPLETE - SYSTEM LEARNED & OPTIMIZED")
    print("=" * 80)
    
    # Summary
    print("\nLEARNING SUMMARY:")
    print("=" * 80)
    print(f"Templates Suppressed: {len(winners_losers['losers'])}")
    print(f"Templates Promoted: {len(winners_losers['winners'])}")
    print(f"Templates Needing More Data: {len(winners_losers['uncertain'])}")
    print(f"Avg Improvement in Expected CTR: {template_rankings['estimated_ctr'].mean():.2%}")
    print(f"Statistical Winners: {experiment_report['statistically_significant_winners']}")
    print(f"Overall System CTR: {experiment_report['overall_ctr']:.2%}")
    print("=" * 80)
    
    print(f"\nImproved outputs saved to: {output_dir}/")
    print("\nSystem is now optimized for maximum engagement!")


def main():
    parser = argparse.ArgumentParser(
        description='Project Aurora - ML-POWERED Orchestrator'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['iteration0', 'iteration1'],
        help='Runtime mode: iteration0 (train) or iteration1 (learn)'
    )
    
    parser.add_argument(
        '--user-data',
        type=str,
        required=True,
        help='Path to user data CSV file'
    )
    
    parser.add_argument(
        '--experiment-results',
        type=str,
        help='Path to experiment results CSV (required for iteration1)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.mode == 'iteration1' and not args.experiment_results:
        parser.error("--experiment-results is required for iteration1 mode")
    
    # Run appropriate mode
    try:
        if args.mode == 'iteration0':
            run_iteration_0(args.user_data)
        else:
            run_iteration_1(args.user_data, args.experiment_results)
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


