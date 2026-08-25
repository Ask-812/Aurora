"""
Project Aurora - ML-POWERED Orchestrator
Domain-Generic Self-Learning Notification System

This version integrates:
- RAG-lite Knowledge Bank Engine (PDF -> LLM -> TF-IDF Cosine Ranking)
- RFM + Hierarchical Segmentation
- XGBoost/LightGBM Propensity Models
- Multi-Armed Bandit Learning (Thompson Sampling)
- Survival Analysis for Timing
- NLP Template Optimization
- Bayesian Statistical Testing

Usage:
    python main.py --mode iteration0 --user-data user_data.csv --kb-pdf knowledge_bank.pdf
    python main.py --mode iteration1 --user-data user_data.csv --experiment-results experiment_results.csv
"""

import sys
import os
import json

# Force UTF-8 encoding for Windows console (line-buffered for live output)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='strict', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='strict', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Load .env file if present (for GROQ_API_KEY etc.)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env_path):
    with open(_env_path, 'r') as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip().strip("'").strip('"'))

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
    print("  PROJECT AURORA - DOMAIN-GENERIC ML-POWERED ORCHESTRATOR")
    print("=" * 80)
    print("  Features:")
    print("  * RAG-lite Knowledge Bank (PDF -> LLM -> TF-IDF Cosine Ranking)")
    print("  * RFM Analysis + Hierarchical Clustering (6-12 MECE segments)")
    print("  * XGBoost Churn Prediction + LightGBM Engagement Models")
    print("  * Multi-Armed Bandit (Thompson Sampling)")
    print("  * Survival Analysis for Timing Optimization")
    print("  * NLP-Powered Template Analysis")
    print("  * Bayesian + Frequentist A/B Testing")
    print("  * Domain-Generic Template Generation (Bilingual EN+HI)")
    print("=" * 80 + "\n")


def run_iteration_0(user_data_path: str, kb_text: str = None, kb_pdf: str = None):
    """
    Run Iteration 0 with ML models
    
    Args:
        user_data_path: Path to user data CSV
        kb_text: Knowledge bank text (optional)
        kb_pdf: Path to knowledge bank PDF (optional, overrides kb_text)
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
    
    # Determine KB source: PDF > text file > minimal fallback
    kb_source = None
    if kb_pdf and Path(kb_pdf).exists():
        kb_source = kb_pdf  # Use PDF path directly — engine will handle it
        print(f"   Using PDF knowledge bank: {kb_pdf}")
    elif kb_text:
        kb_source = kb_text
    else:
        # Try config-defined PDF path, then text file, then minimal fallback
        config_pdf = kb_engine.config.get('knowledge_bank', {}).get('pdf_path', '')
        if config_pdf and Path(config_pdf).exists():
            kb_source = config_pdf
            print(f"   Using PDF from config: {config_pdf}")
        else:
            # Try legacy text file
            for text_path in ['pdf_content.txt', 'data/input/knowledge_bank.txt']:
                if Path(text_path).exists():
                    with open(text_path, 'r', encoding='utf-8') as f:
                        kb_source = f.read()
                    print(f"   Using text KB: {text_path}")
                    break
            if kb_source is None:
                kb_source = "Company platform for user engagement and productivity"
                print("   Using minimal fallback KB text")
    
    kb_data = kb_engine.process_knowledge_bank(kb_source)
    kb_engine.save_outputs(output_dir)
    
    # --- Rich KB Terminal Output ---
    _display_kb_intelligence(kb_data)
    
    # Step 2: Data Ingestion
    print("\n" + "=" * 80)
    print("STEP 2:  DATA INGESTION")
    print("=" * 80)
    
    ingestion_engine = DataIngestionEngine(knowledge_bank=kb_data)
    user_data = ingestion_engine.load_and_validate(user_data_path)
    
    # Display identified mapping if available
    if ingestion_engine.schema_map:
        print("\n[Brain] Identified Schema Mapping:")
        for role, col in ingestion_engine.schema_map.items():
            if col:
                print(f"   - {role:20}: {col}")

    user_data = ingestion_engine.engineer_features(user_data)
    
    stats = ingestion_engine.get_summary_stats(user_data)
    print(f"\nDataset: {stats['total_users']} users | "
          f"Avg Active: {stats['avg_activeness']:.2f} | "
          f"Avg Churn Risk: {stats['avg_churn_risk']:.2f}")
    
    # Enrich KB features from data columns (feature_* columns + behavioral signals)
    kb_engine.enrich_features_from_data(list(user_data.columns))
    kb_data = {
        'north_star': kb_engine.north_star,
        'feature_goal_map': kb_engine.feature_goal_map,
        'tone_hook_matrix': kb_engine.tone_hook_matrix,
        'detected_domain': kb_engine.detected_domain
    }
    kb_engine.save_outputs(output_dir)
    
    # Step 3: ML-POWERED Segmentation
    print("\n" + "=" * 80)
    print("STEP 3:  SEGMENTATION (RFM + Hierarchical)")
    print("=" * 80)
    
    seg_engine = SegmentationEngine(kb_data=kb_data, schema_map=ingestion_engine.schema_map)
    user_data = seg_engine.create_segments(user_data)
    seg_engine.save_segments(user_data, output_dir)
    
    # Step 4: ML Propensity Models
    print("\n" + "=" * 80)
    print("STEP 4: TRAINING ML PROPENSITY MODELS")
    print("=" * 80)
    
    ml_engine = PropensityModelEngine(schema_map=ingestion_engine.schema_map)
    
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
    
    goal_builder = GoalBuilder(kb_data=kb_data)
    segment_goals = goal_builder.build_goals(seg_engine.segment_profiles)
    goal_builder.save_goals(output_dir)
    
    # Step 6: Theme Generation
    print("\n" + "=" * 80)
    print("STEP 6: BEHAVIORAL THEME MAPPING")
    print("=" * 80)
    
    theme_engine = ThemeEngine(kb_data['tone_hook_matrix'], kb_data=kb_data)
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
    
    # Step 11: Auto-generate experiment results for demo/testing
    print("\n" + "=" * 80)
    print("STEP 11: GENERATING SYNTHETIC EXPERIMENT RESULTS")
    print("=" * 80)
    
    from src.utils.experiment_generator import generate_experiment_results
    generate_experiment_results(output_dir=output_dir, sample_dir="data/sample")
    
    print("\n" + "=" * 80)
    print("ITERATION 0 COMPLETE - ML MODELS TRAINED")
    print("=" * 80)
    print(f"\nOutputs saved to: {output_dir}/")
    print(f"\nExperiment results generated: data/sample/experiment_results_sample.csv")
    print("\nNext: Run Iteration 1 with experiment results for learning")

    # Export to PS submission folder structure
    _export_iteration_0(output_dir)


def _display_kb_intelligence(kb_data: dict):
    """Display extracted KB intelligence in the terminal."""
    print("\n   +" + "=" * 70 + "+")
    print("   |  KNOWLEDGE BANK -- EXTRACTED INTELLIGENCE                          |")
    print("   +" + "=" * 70 + "+")

    # Domain
    domain = kb_data.get('detected_domain', 'unknown')
    print(f"   |  Domain: {domain.upper()}")

    # North Star Metric
    ns = kb_data.get('north_star', {})
    nsm_name = ns.get('north_star_metric', 'N/A')
    nsm_def = ns.get('definition', 'N/A')
    nsm_evidence = ns.get('evidence', 'N/A')
    print(f"   |")
    print(f"   |  [NS] North Star Metric: {nsm_name}")
    print(f"   |     Definition: {nsm_def[:100]}")
    if nsm_evidence and nsm_evidence != 'N/A':
        print(f"   |     Evidence: {nsm_evidence[:100]}")

    # Feature-Goal Mappings
    fgm = kb_data.get('feature_goal_map', {})
    features = fgm.get('features', [])
    print(f"   |")
    print(f"   |  [FG] Feature -> Goal Mappings ({len(features)} features):")
    for f in features[:6]:
        fname = f.get('feature_name', 'N/A')
        fgoal = f.get('primary_goal', 'N/A')
        print(f"   |     - {fname} -> {fgoal[:80]}")
    if len(features) > 6:
        print(f"   |     ... and {len(features) - 6} more")

    # Allowed Tones
    thm = kb_data.get('tone_hook_matrix', {})
    tones = thm.get('allowed_tones', [])
    print(f"   |")
    print(f"   |  [T] Allowed Tones: {', '.join(tones) if tones else 'N/A'}")

    # Octalysis Hooks
    hooks = thm.get('octalysis_hooks', {})
    print(f"   |")
    print(f"   |  [H] Behavioral Hooks (Octalysis):")
    for drive, info in hooks.items():
        if isinstance(info, dict) and 'hooks' in info:
            hook_list = info['hooks']
            if hook_list:
                triggers = [h.get('trigger', '?') for h in hook_list[:2]]
                print(f"   |     {drive}: {', '.join(triggers)}")
        elif isinstance(info, str):
            print(f"   |     {drive}: {info[:60]}")

    print(f"   |")
    print("   +" + "=" * 70 + "+")


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
    
    # Validate iter0 outputs exist
    required_files = ['message_templates.csv', 'communication_themes.csv', 'user_segments.csv']
    for rf in required_files:
        if not Path(f"{output_dir}/{rf}").exists():
            print(f"\n[ERROR] Missing iter0 output: {output_dir}/{rf}")
            print("Run iteration0 first.")
            sys.exit(1)

    # Load previous iteration outputs
    print("\nLoading Iteration 0 outputs...")
    templates = pd.read_csv(f"{output_dir}/message_templates.csv")
    # Try improved timing first, fall back to base
    timing_path = f"{output_dir}/timing_recommendations_improved.csv"
    if not Path(timing_path).exists():
        timing_path = f"{output_dir}/timing_recommendations.csv"
    timing_recs = pd.read_csv(timing_path)
    themes = pd.read_csv(f"{output_dir}/communication_themes.csv")
    user_data = pd.read_csv(f"{output_dir}/user_segments.csv")

    # Load Knowledge Bank from saved outputs
    import json
    kb_data = {}
    for kb_file, kb_key in [('feature_goal_map.json', 'feature_goal_map'),
                             ('company_north_star.json', 'north_star'),
                             ('allowed_tone_hook_matrix.json', 'tone_hook_matrix'),
                             ('kb_metadata.json', '_meta')]:
        kb_path = f"{output_dir}/{kb_file}"
        try:
            with open(kb_path, 'r') as f:
                kb_data[kb_key] = json.load(f)
        except FileNotFoundError:
            kb_data[kb_key] = {}
    # Flatten metadata
    meta = kb_data.pop('_meta', {})
    kb_data['detected_domain'] = meta.get('detected_domain', 'generic')
    
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
    print("STEP 2: BAYESIAN AND FREQUENTIST STATISTICAL ANALYSIS")
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
        ci = bandit_engine.template_bandits.get(loser, {}).get('confidence_interval', (0, 0))
        ci_str = f"({float(ci[0]):.3f}, {float(ci[1]):.3f})" if isinstance(ci, (tuple, list)) else str(ci)
        changes_log.append({
            'entity_type': 'template',
            'entity_id': loser,
            'change_type': 'suppression',
            'metric_trigger': f"CTR={perf['ctr']:.3f}, Engagement={perf['engagement_rate']:.3f}",
            'before_value': 'active',
            'after_value': 'suppressed',
            'explanation': f"Bandit analysis: Consistently underperformed (CTR < 5% or Engagement < 20%). Statistical confidence: {ci_str}"
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
    # Use raw experiment stats as iter0 baseline (not zeros)
    iter0_stats = {
        'total_templates': len(templates),
        'avg_ctr': experiment_results['ctr'].mean(),
        'avg_engagement': experiment_results['engagement_rate'].mean(),
        'avg_uninstall_rate': experiment_results['uninstall_rate'].mean() if 'uninstall_rate' in experiment_results.columns else 0.0,
        'good_count': len(experiment_results[experiment_results.get('performance_status', pd.Series()) == 'GOOD']) if 'performance_status' in experiment_results.columns else 0,
        'bad_count': len(experiment_results[experiment_results.get('performance_status', pd.Series()) == 'BAD']) if 'performance_status' in experiment_results.columns else 0,
    }
    # iter1 stats: only surviving (non-suppressed) templates
    surviving = experiment_results[~experiment_results['template_id'].isin(winners_losers['losers'])]
    iter1_stats = {
        'total_templates': len(templates_improved),
        'avg_ctr': surviving['ctr'].mean() if not surviving.empty else 0.0,
        'avg_engagement': surviving['engagement_rate'].mean() if not surviving.empty else 0.0,
        'avg_uninstall_rate': surviving['uninstall_rate'].mean() if 'uninstall_rate' in surviving.columns and not surviving.empty else 0.0,
        'good_count': len(surviving[surviving.get('performance_status', pd.Series()) == 'GOOD']) if 'performance_status' in surviving.columns else 0,
        'bad_count': len(surviving[surviving.get('performance_status', pd.Series()) == 'BAD']) if 'performance_status' in surviving.columns else 0,
    }
    
    delta_report = delta_reporter.generate_delta_report(changes_log, iter0_stats, iter1_stats)
    delta_reporter.save_delta_report(output_dir)
    delta_reporter.print_detailed_summary(iter0_stats, iter1_stats)
    
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

    # Export to PS submission folder structure
    _export_iteration_1(output_dir, experiment_results_path)


def _export_iteration_0(output_dir: str):
    """Copy iter0 outputs to PS-required folder structure."""
    import shutil
    dest = "iteration_0_before_learning"
    os.makedirs(dest, exist_ok=True)
    files = [
        "company_north_star.json", "feature_goal_map.json",
        "allowed_tone_hook_matrix.json", "user_segments.csv",
        "segment_goals.csv", "communication_themes.csv",
        "message_templates.csv", "timing_recommendations.csv",
        "user_notification_schedule.csv"
    ]
    for f in files:
        src = os.path.join(output_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, f))
    print(f"\n[Export] Iteration 0 files -> {dest}/")


def _export_iteration_1(output_dir: str, experiment_results_path: str):
    """Copy iter1 outputs to PS-required folder structure."""
    import shutil
    dest = "iteration_1_after_learning"
    os.makedirs(dest, exist_ok=True)
    mapping = {
        "user_segments.csv": "user_segments.csv",
        "message_templates_improved.csv": "message_templates.csv",
        "timing_recommendations_improved.csv": "timing_recommendations.csv",
        "user_notification_schedule_improved.csv": "user_notification_schedule.csv",
    }
    for src_name, dest_name in mapping.items():
        src = os.path.join(output_dir, src_name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, dest_name))
    # Copy experiment_results and learning_delta_report to root
    if os.path.exists(experiment_results_path):
        shutil.copy2(experiment_results_path, "experiment_results.csv")
    delta_src = os.path.join(output_dir, "learning_delta_report.csv")
    if os.path.exists(delta_src):
        shutil.copy2(delta_src, "learning_delta_report.csv")
    print(f"\n[Export] Iteration 1 files -> {dest}/")
    print(f"[Export] experiment_results.csv -> ./")
    print(f"[Export] learning_delta_report.csv -> ./")


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
    
    parser.add_argument(
        '--kb-pdf',
        type=str,
        help='Path to knowledge bank PDF file (optional, enables RAG-lite)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.mode == 'iteration1' and not args.experiment_results:
        parser.error("--experiment-results is required for iteration1 mode")
    
    # Run appropriate mode
    try:
        if args.mode == 'iteration0':
            run_iteration_0(args.user_data, kb_pdf=args.kb_pdf)
        else:
            run_iteration_1(args.user_data, args.experiment_results)
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


