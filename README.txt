PROJECT AURORA - SELF-LEARNING NOTIFICATION ORCHESTRATOR
========================================================

A domain-agnostic, self-learning notification system that segments users, generates
personalized messages, optimizes timing/frequency, and continuously improves through
data-driven learning.

QUICK START
-----------

1. Install dependencies:
   pip install -r requirements.txt

2. Generate sample data:
   python main.py --mode generate-sample

3. Run Iteration 0 (before learning):
   python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv

4. Review outputs in data/output/:
   - company_north_star.json
   - feature_goal_map.json
   - allowed_tone_hook_matrix.json
   - user_segments.csv
   - segment_goals.csv

SYSTEM ARCHITECTURE
-------------------

The system consists of four main layers:

1. KNOWLEDGE BANK LAYER
   - Extracts company intelligence from documents
   - Identifies North Star metric, features, tones, and behavioral hooks
   - Domain-agnostic design allows swapping between companies

2. INTELLIGENCE LAYER
   - Validates and cleans user data
   - Engineers behavioral features (activeness, propensity scores, churn risk)
   - Creates MECE segments using K-means clustering
   - Builds goal hierarchies for each segment × lifecycle stage

3. COMMUNICATION LAYER (In Progress)
   - Maps Octalysis themes to segments
   - Generates personalized, bilingual templates
   - Optimizes notification timing windows
   - Calculates frequency based on activeness and guardrails
   - Creates user-wise notification schedules

4. LEARNING LAYER (In Progress)
   - Classifies template performance (GOOD/NEUTRAL/BAD)
   - Suppresses underperforming templates
   - Optimizes timing based on experiment results
   - Adjusts frequency if uninstall rate > 2%
   - Documents all changes with causal reasoning

KEY FEATURES
------------

✓ MECE Segmentation: Mutually exclusive, collectively exhaustive user segments
✓ Propensity Scores: Gamification, social, and feature-specific propensities
✓ Behavioral Scoring: Activeness and churn risk calculations
✓ Goal-Driven: Journey progression from activation to advocacy
✓ Data Validation: Comprehensive input validation and cleaning
✓ Domain-Agnostic: Works with any company by swapping Knowledge Bank

DELIVERABLES
------------

Task 1 Outputs (✓ Complete):
- company_north_star.json: North Star metric and key drivers
- feature_goal_map.json: Feature-to-goal mappings with engagement scores
- allowed_tone_hook_matrix.json: Tones, Octalysis hooks, and segment mappings
- user_segments.csv: User segment assignments with propensity scores
- segment_goals.csv: Goals for each segment × lifecycle stage combination

Task 2 Outputs (In Progress):
- communication_themes.csv: Theme mappings per segment
- message_templates.csv: Personalized, bilingual templates
- timing_recommendations.csv: Optimal notification windows
- user_notification_schedule.csv: Day-by-day user schedules

Task 3 Outputs (In Progress):
- experiment_results.csv: Performance classification
- learning_delta_report.csv: Documented improvements with causal reasoning

TECHNICAL DETAILS
-----------------

Segmentation Algorithm:
- Features: activeness, gamification_propensity, social_propensity, churn_risk
- Method: K-means clustering (k=8)
- Validation: MECE property enforced
- Naming: Based on dominant behavioral characteristics

Propensity Score Formulas:
- Activeness = 0.3*sessions + 0.3*exercises + 0.2*notif_open + 0.2*has_streak
- Gamification = 0.4*streak + 0.3*coins + 0.3*feature_usage
- Social = 0.6*leaderboard_viewed + 0.4*sessions
- Churn Risk = 0.4*(1-sessions) + 0.3*(1-notif_open) + 0.3*no_streak

Performance Thresholds:
- GOOD: CTR > 15% AND Engagement > 40%
- BAD: CTR < 5% OR Engagement < 20%
- NEUTRAL: Everything else

Frequency Rules:
- High activeness (>0.7): 7-9 notifications/day
- Medium activeness (0.4-0.7): 5-6 notifications/day
- Low activeness (<0.4): 3-4 notifications/day
- Guardrail: If uninstall_rate > 2%, reduce by 2 notifications/day

CURRENT STATUS
--------------

✓ Complete:
  - Knowledge Bank extraction
  - Data ingestion and validation
  - Feature engineering
  - MECE segmentation
  - Goal and journey building
  - Sample data generation

⏳ In Progress:
  - Theme engine
  - Template generator (bilingual support)
  - Timing optimizer
  - Schedule generator
  - Performance classifier
  - Learning engine
  - Delta reporter

NEXT STEPS
----------

1. Complete communication layer (themes, templates, timing, schedules)
2. Implement learning engine with experiment results processing
3. Add bilingual template generation (Hindi + English)
4. Create delta reporter with causal reasoning
5. Build comprehensive test suite
6. Add visualization dashboard for segment analysis

DESIGN PRINCIPLES
-----------------

1. Domain-Agnostic: No hardcoded business logic, all driven by Knowledge Bank
2. Data-Driven: All decisions based on metrics, not assumptions
3. MECE Segments: Mutually exclusive, collectively exhaustive
4. Causal Reasoning: Every change explained with metric triggers
5. Measurable Learning: Quantifiable improvement from Iteration 0 to 1
6. Production-Ready: Validation, error handling, logging throughout

TESTING
-------

Run with sample data:
  python main.py --mode generate-sample
  python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv

The system validates:
- Schema compliance
- Data quality
- MECE property
- Segment size distribution
- Feature ranges

CONFIGURATION
-------------

Edit config/config.yaml to adjust:
- Number of segments (default: 8)
- Performance thresholds
- Frequency rules
- Time windows
- Output paths

CONTACT & SUPPORT
-----------------

For questions or issues, refer to:
- MENTOR_GUIDE_Project_Aurora.md: Comprehensive tutorial
- SYSTEM_ARCHITECTURE_GUIDE.md: Technical architecture
- QUICK_START_GUIDE.md: Fast-track overview
- CONCEPT_MAP.md: Visual concept relationships

VERSION: 1.0.0 (Iteration 0 Complete)
LAST UPDATED: February 9, 2026
