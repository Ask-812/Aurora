"""
Project Aurora - Main Orchestrator
Self-Learning Notification System

Usage:
    python main.py --mode iteration0 --user-data data/input/user_data.csv
    python main.py --mode iteration1 --user-data data/input/user_data.csv --experiment-results data/input/experiment_results.csv
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.knowledge_bank.kb_engine import KnowledgeBankEngine
from src.intelligence.data_ingestion import DataIngestionEngine
from src.intelligence.segmentation import SegmentationEngine
from src.intelligence.goal_builder import GoalBuilder
from src.communication.theme_engine import ThemeEngine
from src.communication.template_generator import TemplateGenerator
from src.communication.timing_optimizer import TimingOptimizer
from src.communication.schedule_generator import ScheduleGenerator
from src.learning.performance_classifier import PerformanceClassifier
from src.learning.learning_engine import LearningEngine
from src.learning.delta_reporter import DeltaReporter


def run_iteration_0(user_data_path: str, kb_text: str = None):
    """
    Run Iteration 0 (before learning)
    
    Args:
        user_data_path: Path to user data CSV
        kb_text: Knowledge bank text (optional, uses default if None)
    """
    print("=" * 80)
    print("PROJECT AURORA - ITERATION 0 (Before Learning)")
    print("=" * 80)
    
    output_dir = "data/output"
    
    # Step 1: Process Knowledge Bank
    print("\n" + "=" * 80)
    print("STEP 1: KNOWLEDGE BANK EXTRACTION")
    print("=" * 80)
    
    kb_engine = KnowledgeBankEngine()
    if kb_text is None:
        kb_text = "SpeakX English Learning Platform"
    
    kb_data = kb_engine.process_knowledge_bank(kb_text)
    kb_engine.save_outputs(output_dir)
    
    # Step 2: Data Ingestion
    print("\n" + "=" * 80)
    print("STEP 2: USER DATA INGESTION")
    print("=" * 80)
    
    ingestion_engine = DataIngestionEngine()
    user_data = ingestion_engine.load_and_validate(user_data_path)
    user_data = ingestion_engine.engineer_features(user_data)
    
    stats = ingestion_engine.get_summary_stats(user_data)
    print("\n📊 User Data Summary:")
    print(f"   Total Users: {stats['total_users']}")
    print(f"   Lifecycle Distribution: {stats['lifecycle_distribution']}")
    print(f"   Avg Sessions/Week: {stats['avg_sessions']:.1f}")
    print(f"   Avg Exercises/Week: {stats['avg_exercises']:.1f}")
    print(f"   Avg Activeness: {stats['avg_activeness']:.2f}")
    print(f"   Avg Churn Risk: {stats['avg_churn_risk']:.2f}")
    
    # Step 3: Segmentation
    print("\n" + "=" * 80)
    print("STEP 3: USER SEGMENTATION")
    print("=" * 80)
    
    segmentation_engine = SegmentationEngine()
    user_data = segmentation_engine.create_segments(user_data)
    segmentation_engine.save_segments(user_data, output_dir)
    
    # Step 4: Goal Building
    print("\n" + "=" * 80)
    print("STEP 4: GOAL & JOURNEY BUILDING")
    print("=" * 80)
    
    goal_builder = GoalBuilder()
    segment_goals = goal_builder.build_goals(segmentation_engine.segment_profiles)
    goal_builder.save_goals(output_dir)
    
    # Step 5: Theme Generation
    print("\n" + "=" * 80)
    print("STEP 5: THEME GENERATION")
    print("=" * 80)
    
    theme_engine = ThemeEngine(kb_data['tone_hook_matrix'])
    themes = theme_engine.generate_themes(segmentation_engine.segment_profiles)
    theme_engine.save_themes(output_dir)
    
    # Step 6: Template Generation
    print("\n" + "=" * 80)
    print("STEP 6: TEMPLATE GENERATION")
    print("=" * 80)
    
    template_generator = TemplateGenerator(kb_data, themes)
    templates = template_generator.generate_templates(segment_goals)
    template_generator.save_templates(output_dir)
    
    # Step 7: Timing Optimization
    print("\n" + "=" * 80)
    print("STEP 7: TIMING OPTIMIZATION")
    print("=" * 80)
    
    timing_optimizer = TimingOptimizer()
    timing_recs = timing_optimizer.optimize_timing_iteration0(user_data)
    timing_optimizer.save_timing(output_dir)
    
    # Step 8: Schedule Generation
    print("\n" + "=" * 80)
    print("STEP 8: SCHEDULE GENERATION")
    print("=" * 80)
    
    schedule_generator = ScheduleGenerator()
    schedules = schedule_generator.generate_schedules(
        user_data, None, templates, timing_recs, segment_goals, max_users=100
    )
    schedule_generator.save_schedules(output_dir)
    
    # Summary
    print("\n" + "=" * 80)
    print("ITERATION 0 COMPLETE")
    print("=" * 80)
    print(f"\n✓ All outputs saved to: {output_dir}/")
    print("\nGenerated files:")
    print("   Task 1:")
    print("   • company_north_star.json")
    print("   • feature_goal_map.json")
    print("   • allowed_tone_hook_matrix.json")
    print("   • user_segments.csv")
    print("   • segment_goals.csv")
    print("   Task 2:")
    print("   • communication_themes.csv")
    print("   • message_templates.csv")
    print("   • timing_recommendations.csv")
    print("   • user_notification_schedule.csv")
    
    print("\n📝 Next Steps:")
    print("   1. Review the generated outputs")
    print("   2. Create experiment_results.csv with performance data")
    print("   3. Run Iteration 1 with: python main.py --mode iteration1 --user-data <path> --experiment-results <path>")
    
    return {
        'user_data': user_data,
        'segmentation_engine': segmentation_engine,
        'goal_builder': goal_builder,
        'themes': themes,
        'templates': templates,
        'timing_recs': timing_recs
    }


def run_iteration_1(user_data_path: str, experiment_results_path: str):
    """
    Run Iteration 1 (after learning)
    
    Args:
        user_data_path: Path to user data CSV
        experiment_results_path: Path to experiment results CSV
    """
    print("=" * 80)
    print("PROJECT AURORA - ITERATION 1 (After Learning)")
    print("=" * 80)
    
    # First, run iteration 0 to get base state
    print("\n🔄 Running Iteration 0 first to establish baseline...")
    iter0_data = run_iteration_0(user_data_path)
    
    # Load experiment results
    print("\n" + "=" * 80)
    print("STEP 9: LOADING EXPERIMENT RESULTS")
    print("=" * 80)
    
    print(f"\n📊 Loading experiment results from {experiment_results_path}...")
    experiment_results = pd.read_csv(experiment_results_path)
    print(f"   Loaded {len(experiment_results)} experiment records")
    
    # Classify performance
    print("\n" + "=" * 80)
    print("STEP 10: PERFORMANCE CLASSIFICATION")
    print("=" * 80)
    
    classifier = PerformanceClassifier()
    experiment_results = classifier.classify_performance(experiment_results)
    iter0_stats = classifier.get_summary_stats(experiment_results)
    
    # Apply learning
    print("\n" + "=" * 80)
    print("STEP 11: LEARNING ENGINE")
    print("=" * 80)
    
    learning_engine = LearningEngine()
    improved_templates, improved_timing, improved_themes, changes_log = learning_engine.learn_and_improve(
        iter0_data['templates'],
        iter0_data['timing_recs'],
        iter0_data['themes'],
        experiment_results
    )
    
    # Calculate iteration 1 stats
    iter1_results = experiment_results[
        experiment_results['template_id'].isin(improved_templates['template_id'])
    ]
    iter1_stats = classifier.get_summary_stats(iter1_results) if len(iter1_results) > 0 else iter0_stats
    
    # Generate delta report
    print("\n" + "=" * 80)
    print("STEP 12: DELTA REPORTING")
    print("=" * 80)
    
    delta_reporter = DeltaReporter()
    delta_report = delta_reporter.generate_delta_report(changes_log, iter0_stats, iter1_stats)
    delta_reporter.save_delta_report("data/output")
    delta_reporter.print_detailed_summary(iter0_stats, iter1_stats)
    
    # Save improved outputs
    output_dir = "data/output"
    improved_templates.to_csv(f"{output_dir}/message_templates_improved.csv", index=False)
    improved_timing.to_csv(f"{output_dir}/timing_recommendations_improved.csv", index=False)
    improved_themes.to_csv(f"{output_dir}/communication_themes_improved.csv", index=False)
    
    print("\n" + "=" * 80)
    print("ITERATION 1 COMPLETE")
    print("=" * 80)
    print(f"\n✓ All improved outputs saved to: {output_dir}/")
    print("\nGenerated files:")
    print("   • learning_delta_report.csv")
    print("   • message_templates_improved.csv")
    print("   • timing_recommendations_improved.csv")
    print("   • communication_themes_improved.csv")
    
    return {
        'improved_templates': improved_templates,
        'improved_timing': improved_timing,
        'improved_themes': improved_themes,
        'delta_report': delta_report,
        'iter0_stats': iter0_stats,
        'iter1_stats': iter1_stats
    }


def generate_sample_data():
    """Generate sample user data for testing"""
    import pandas as pd
    import numpy as np
    
    print("\n🎲 Generating sample user data...")
    
    np.random.seed(42)
    n_users = 1000
    
    # Generate user data
    data = {
        'user_id': [f'U{i:04d}' for i in range(n_users)],
        'lifecycle_stage': np.random.choice(['trial', 'paid', 'churned', 'inactive'], 
                                           n_users, p=[0.4, 0.35, 0.15, 0.1]),
        'days_since_signup': np.random.randint(0, 90, n_users),
        'age_band_region': np.random.choice(['20-30_Tier2', '30-40_Tier1', '20-30_Tier3'], n_users),
        'sessions_last_7d': np.random.poisson(5, n_users),
        'exercises_completed_7d': np.random.poisson(8, n_users),
        'streak_current': np.random.poisson(3, n_users),
        'coins_balance': np.random.randint(0, 1000, n_users),
        'feature_ai_tutor_used': np.random.choice([True, False], n_users, p=[0.6, 0.4]),
        'feature_leaderboard_viewed': np.random.choice([True, False], n_users, p=[0.4, 0.6]),
        'preferred_hour': np.random.randint(6, 23, n_users),
        'notif_open_rate_30d': np.random.beta(2, 5, n_users),
        'motivation_score': np.random.beta(5, 2, n_users)
    }
    
    df = pd.DataFrame(data)
    
    # Save to file
    output_path = Path('data/sample/user_data_sample.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✓ Generated {n_users} sample users")
    print(f"✓ Saved to: {output_path}")
    
    return str(output_path)


def generate_experiment_results():
    """Generate sample experiment results for testing Iteration 1"""
    print("\n🎲 Generating sample experiment results...")
    
    np.random.seed(42)
    
    # Generate results for 50 templates across 8 segments
    n_templates = 50
    n_segments = 8
    
    results = []
    template_id = 1
    
    for seg_id in range(n_segments):
        for _ in range(n_templates // n_segments):
            # Simulate varying performance
            performance_type = np.random.choice(['good', 'neutral', 'bad'], p=[0.2, 0.5, 0.3])
            
            if performance_type == 'good':
                ctr = np.random.uniform(0.15, 0.25)
                engagement = np.random.uniform(0.40, 0.60)
                uninstall = np.random.uniform(0.005, 0.015)
            elif performance_type == 'neutral':
                ctr = np.random.uniform(0.08, 0.14)
                engagement = np.random.uniform(0.25, 0.38)
                uninstall = np.random.uniform(0.010, 0.020)
            else:  # bad
                ctr = np.random.uniform(0.02, 0.06)
                engagement = np.random.uniform(0.10, 0.22)
                uninstall = np.random.uniform(0.020, 0.035)
            
            total_sends = np.random.randint(500, 2000)
            total_opens = int(total_sends * ctr)
            total_engagements = int(total_opens * engagement)
            
            results.append({
                'template_id': f'T{template_id:04d}',
                'segment_id': seg_id,
                'lifecycle_stage': np.random.choice(['trial', 'paid']),
                'goal': np.random.choice(['activation', 'habit_formation', 'retention']),
                'theme': np.random.choice(['accomplishment', 'loss_avoidance', 'social_influence', 'curiosity']),
                'notification_window': np.random.choice(['early_morning', 'evening', 'afternoon', 'night']),
                'total_sends': total_sends,
                'total_opens': total_opens,
                'total_engagements': total_engagements,
                'ctr': ctr,
                'engagement_rate': engagement,
                'uninstall_rate': uninstall
            })
            
            template_id += 1
    
    df = pd.DataFrame(results)
    
    # Save to file
    output_path = Path('data/sample/experiment_results_sample.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✓ Generated {len(results)} experiment results")
    print(f"✓ Saved to: {output_path}")
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description='Project Aurora - Self-Learning Notification Orchestrator')
    parser.add_argument('--mode', choices=['iteration0', 'iteration1', 'generate-sample', 'generate-experiment'], 
                       default='generate-sample',
                       help='Execution mode')
    parser.add_argument('--user-data', type=str, help='Path to user data CSV')
    parser.add_argument('--experiment-results', type=str, help='Path to experiment results CSV')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'generate-sample':
            sample_path = generate_sample_data()
            print("\n📝 To run Iteration 0 with this data:")
            print(f"   python main.py --mode iteration0 --user-data {sample_path}")
        
        elif args.mode == 'generate-experiment':
            exp_path = generate_experiment_results()
            print("\n📝 To run Iteration 1 with this data:")
            print(f"   python main.py --mode iteration1 --user-data data/sample/user_data_sample.csv --experiment-results {exp_path}")
        
        elif args.mode == 'iteration0':
            if not args.user_data:
                print("❌ Error: --user-data is required for iteration0 mode")
                return
            
            run_iteration_0(args.user_data)
        
        elif args.mode == 'iteration1':
            if not args.user_data or not args.experiment_results:
                print("❌ Error: --user-data and --experiment-results are required for iteration1 mode")
                return
            
            run_iteration_1(args.user_data, args.experiment_results)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
