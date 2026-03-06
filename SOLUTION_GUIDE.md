# Project Aurora — Complete Solution Guide

## A Comprehensive Reference for Understanding Every Aspect of the System

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [Problem Statement Breakdown](#2-problem-statement-breakdown)
3. [Architecture & Design Philosophy](#3-architecture--design-philosophy)
4. [Module-by-Module Deep Dive](#4-module-by-module-deep-dive)
   - 4.1 [Knowledge Bank Engine](#41-knowledge-bank-engine)
   - 4.2 [Data Ingestion Engine](#42-data-ingestion-engine)
   - 4.3 [Segmentation Engine](#43-segmentation-engine)
   - 4.4 [ML Propensity Models](#44-ml-propensity-models)
   - 4.5 [Goal Builder](#45-goal-builder)
   - 4.6 [Theme Engine](#46-theme-engine)
   - 4.7 [Template Generator](#47-template-generator)
   - 4.8 [Timing Optimizer](#48-timing-optimizer)
   - 4.9 [NLP Template Optimizer](#49-nlp-template-optimizer)
   - 4.10 [Schedule Generator](#410-schedule-generator)
   - 4.11 [Performance Classifier](#411-performance-classifier)
   - 4.12 [Multi-Armed Bandit Engine](#412-multi-armed-bandit-engine)
   - 4.13 [Statistical Testing Framework](#413-statistical-testing-framework)
   - 4.14 [Learning Engine](#414-learning-engine)
   - 4.15 [Delta Reporter](#415-delta-reporter)
   - 4.16 [Utility Modules](#416-utility-modules-metrics--validation)
5. [Theories, Algorithms & Strategies Explained](#5-theories-algorithms--strategies-explained)
   - 5.1 [RFM Analysis](#51-rfm-analysis)
   - 5.2 [Hierarchical Clustering (Ward's Method)](#52-hierarchical-clustering-wards-method)
   - 5.3 [Optimal K Selection](#53-optimal-k-selection-silhouette-davies-bouldin-elbow)
   - 5.4 [XGBoost — Gradient Boosted Trees](#54-xgboost--gradient-boosted-trees)
   - 5.5 [LightGBM — Light Gradient Boosting Machine](#55-lightgbm--light-gradient-boosting-machine)
   - 5.6 [Survival Analysis (Kaplan-Meier)](#56-survival-analysis-kaplan-meier)
   - 5.7 [Octalysis Framework — 8 Core Drives](#57-octalysis-framework--8-core-drives)
   - 5.8 [Multi-Armed Bandit Problem](#58-multi-armed-bandit-problem)
   - 5.9 [Thompson Sampling](#59-thompson-sampling)
   - 5.10 [Upper Confidence Bound (UCB)](#510-upper-confidence-bound-ucb)
   - 5.11 [Bayesian A/B Testing](#511-bayesian-ab-testing)
   - 5.12 [Frequentist A/B Testing](#512-frequentist-ab-testing)
   - 5.13 [TF-IDF Vectorization](#513-tf-idf-vectorization)
   - 5.14 [Beta Distribution & Conjugate Priors](#514-beta-distribution--conjugate-priors)
   - 5.15 [Sequential Testing & Alpha Spending](#515-sequential-testing--alpha-spending)
6. [Configuration Reference](#6-configuration-reference)
7. [Data Flow & Pipeline Execution](#7-data-flow--pipeline-execution)
8. [Output Files Reference](#8-output-files-reference)
9. [Key Design Decisions & Why](#9-key-design-decisions--why)
10. [Common Questions & Answers](#10-common-questions--answers)

---

## 1. The Big Picture

### What is Project Aurora?

Project Aurora is a **self-learning notification orchestrator** — a system that figures out:

- **WHO** to talk to (user segmentation)
- **WHAT** to say (theme + template generation)
- **WHEN** to say it (timing optimization)
- **WHY** it works (statistical validation)
- **HOW** to improve continuously (learning from feedback)

In simple terms: most apps send the same notification to every user at the same time. That's wasteful and annoying. Aurora makes notifications *intelligent* — the right message, to the right user, at the right time, improving with every batch of feedback data.

### Why Does This Matter?

In 2025, user communication is the single most powerful growth lever in tech. Yet most notification systems are:

- **Rule-based**: "If user hasn't opened app in 3 days, send reminder" — no nuance
- **Segment-blind**: Same message to a power user and a churning user
- **Timing-agnostic**: Sent at 10 AM because someone decided that's "good"
- **Non-learning**: Never gets better, even with millions of data points

Aurora solves all four problems with ML, statistical testing, and behavioral psychology.

### The SpeakX Context

SpeakX is an AI-powered English learning app targeting Tier 2/3 India (ages 20-45). Users practice speaking English through AI tutors, gamification (streaks, coins, leaderboards), and structured exercises. The goal is **daily habit formation** — users must come back every day to improve.

Key business metrics:
- **Trial → Monthly Conversion** (did the free trial user pay?)
- **Monthly Retention** (did the paid user complete an exercise this month?)
- **W1 Retention** (did the new paid user engage in their first week?)

Aurora is built for SpeakX but designed to be **domain-agnostic** — swap the Knowledge Bank and user data, and the same orchestrator works for fintech, healthtech, SaaS, etc.

---

## 2. Problem Statement Breakdown

The problem statement has **3 tasks** that build on each other:

### Task 1: System Architecture & Intelligence Design (Weight: 30%)

Build the brain of the system:
1. **Knowledge Bank Engine** — Ingest company documentation, auto-extract the North Star metric, feature-to-goal mappings, and allowed tones/hooks
2. **Data Ingestion** — Load user behavioral CSV data, validate it, engineer features
3. **MECE Segmentation** — Create 6-12 mutually exclusive, collectively exhaustive user segments with propensity scores
4. **Goal & Journey Builder** — Define what each segment should achieve at each lifecycle stage

### Task 2: Communication & Timing Intelligence (Weight: 35%)

Build the messaging layer:
1. **Theme Engine** — Map behavioral psychology themes (Octalysis) to each segment
2. **Template Generator** — Create exactly 5 bilingual (English + Hindi) message templates per Segment × Lifecycle × Goal × Theme combination
3. **Timing Optimizer** — Learn optimal time windows per segment using survival analysis
4. **Frequency Optimizer** — Determine daily notification count based on activeness, with uninstall guardrails

### Task 3: Execution & Self-Learning (Weight: 30%)

Build the feedback loop:
1. **Schedule Generator** — Output user-wise notification schedules with gradual journey progression
2. **Performance Classifier** — Classify templates as GOOD/NEUTRAL/BAD from experiment results
3. **Learning Engine** — Suppress bad templates, promote good ones, learn better timing/themes/frequency
4. **Delta Reporter** — Document every change with causal reasoning

### The Two-Phase Demo

- **Iteration 0**: System generates all outputs from raw data (no experiment results exist yet)
- **Iteration 1**: System receives experiment results, learns, and produces improved outputs demonstrating measurable delta

---

## 3. Architecture & Design Philosophy

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MAIN ORCHESTRATOR (main.py)              │
│                    Coordinates all engines in sequence           │
└─────────────┬───────────────────────────────────┬───────────────┘
              │                                   │
    ┌─────────▼──────────┐              ┌─────────▼──────────┐
    │   ITERATION 0      │              │   ITERATION 1      │
    │   (10 Steps)       │              │   (8 Steps)        │
    └────────────────────┘              └────────────────────┘

ITERATION 0 PIPELINE:
═══════════════════════════════════════════════════════════════

Step 1: Knowledge Bank Engine
   ↓ (North Star, Feature-Goal Map, Tone-Hook Matrix)
Step 2: Data Ingestion Engine
   ↓ (Validated + Feature-Engineered User Data)
Step 3: Segmentation Engine (RFM + Hierarchical Clustering)
   ↓ (User Segments with Profiles)
Step 4: ML Propensity Models (XGBoost + LightGBM)
   ↓ (Churn Scores, Engagement Predictions)
Step 5: Goal Builder
   ↓ (Segment × Lifecycle Goals)
Step 6: Theme Engine (Octalysis Framework)
   ↓ (Communication Themes per Segment)
Step 7: Template Generator + NLP Analysis
   ↓ (Bilingual Message Templates)
Step 8: Timing Optimizer (Survival Analysis)
   ↓ (Optimal Time Windows + Frequencies)
Step 9: Schedule Generator
   ↓ (User-wise 7-day Notification Schedules)
Step 10: Multi-Armed Bandit Initialization
   ↓ (Beta(1,1) priors for all templates)

ITERATION 1 PIPELINE:
═══════════════════════════════════════════════════════════════

Step 1: Performance Classifier (GOOD/NEUTRAL/BAD)
   ↓
Step 2: Bayesian Statistical Analysis
   ↓
Step 3: Multi-Armed Bandit Learning (Thompson Sampling)
   ↓
Step 4: NLP Template Optimization
   ↓
Step 5: Timing Re-optimization (Survival Analysis on experiments)
   ↓
Step 6: Intelligent Template Filtering (suppress BAD, promote GOOD)
   ↓
Step 7: Comprehensive Delta Reporting
   ↓
Step 8: Generate Improved Schedule
```

### Design Principles

1. **Config-Driven**: All thresholds live in `config/config.yaml`, not scattered in code. Change a threshold once, it updates everywhere.

2. **Modular Architecture**: Each engine has a single responsibility. The Knowledge Bank doesn't know about templates. The Template Generator doesn't know about bandit learning. This means any component can be swapped or upgraded independently.

3. **Domain-Agnostic Core**: The core pipeline (ingest → segment → template → time → schedule → learn) works for any domain. SpeakX-specific knowledge lives only in the Knowledge Bank text and the user CSV schema.

4. **Progressive Enhancement**: Iteration 0 works with zero experiment data. Iteration 1 enhances everything based on real feedback. The system doesn't break if you only run Iteration 0.

5. **Explainable Decisions**: Every learning decision is logged with causal reasoning — the delta report explains *why* each template was suppressed, *why* timing changed, *why* frequency was adjusted.

---

## 4. Module-by-Module Deep Dive

### 4.1 Knowledge Bank Engine

**File**: `src/knowledge_bank/kb_engine.py` (~632 lines)  
**Purpose**: Extract domain intelligence from unstructured company documentation

#### What It Does

The Knowledge Bank Engine takes raw text (company documentation, product descriptions, PDFs) and automatically extracts three critical pieces of domain intelligence:

1. **Company North Star** (`company_north_star.json`):
   - The single most important metric for the company
   - Definition, rationale, key drivers, and measurement formula
   - Example: For SpeakX → "daily_active_engagement" (users completing exercises daily)

2. **Feature-Goal Map** (`feature_goal_map.json`):
   - Maps every product feature to its business goals
   - Example: "ai_tutor" → primary goal: "engagement_deepening", secondary: ["skill_building", "habit_formation"]

3. **Tone-Hook Matrix** (`allowed_tone_hook_matrix.json`):
   - Allowed/forbidden communication tones
   - Hook examples organized by Octalysis core drives
   - Example: "accomplishment" hooks → ["Complete your first lesson!", "You've unlocked a new level!"]

#### How It Works — Step by Step

1. **Domain Detection**: Scans the input text for domain keywords (edtech, fintech, health, etc.) using frequency scoring. Whichever domain has the most keyword matches wins.

2. **North Star Extraction**: Uses regex pattern matching to find explicit metric mentions (e.g., "north star metric is..."). Falls back to domain-specific defaults (edtech → "daily_active_engagement"). Extracts the definition, rationale, and key drivers.

3. **Feature-Goal Map Extraction**: 
   - First attempts to find explicit feature sections in the text
   - Falls back to noun-phrase extraction to identify features
   - Then infers goals from feature names using keyword matching (e.g., feature name contains "tutor" → goal is "engagement_deepening")
   - Generates descriptions and secondary goals for each feature

4. **Tone-Hook Matrix Generation**: 
   - Reads allowed/forbidden tones from config
   - Generates hook examples for each Octalysis core drive, customized to the detected domain

#### Why This Architecture?

The KB engine uses a **multi-strategy extraction pattern**: try the explicit method first, then fall back progressively to heuristic-based, domain-inferred, and default strategies. This ensures the system always produces valid output regardless of input quality.

The hardcoded defaults are intentional — in a real production system, these would be replaced by an LLM API call, but for this project, deterministic extraction ensures reproducibility (a non-negotiable PS requirement).

---

### 4.2 Data Ingestion Engine

**File**: `src/intelligence/data_ingestion.py` (~155 lines)  
**Purpose**: Load, validate, clean, and feature-engineer user data

#### What It Does

Takes a raw user CSV and transforms it into analysis-ready data with computed behavioral scores.

#### Feature Engineering Pipeline

The engine computes 6 key scores for every user:

| Score | Formula | What It Measures |
|-------|---------|-----------------|
| **Activeness** | 0.3×sessions + 0.3×exercises + 0.2×notif_open + 0.2×has_streak | Overall engagement level |
| **Gamification Propensity** | 0.4×streak + 0.3×coins + 0.3×feature_usage | Responsiveness to game mechanics |
| **Social Propensity** | 0.5×social_features + 0.5×sessions | Responsiveness to social features |
| **AI Tutor Propensity** | 0.6×ai_tutor + 0.2×exercises + 0.2×activeness | Likelihood to engage with AI tutoring |
| **Leaderboard Propensity** | 0.5×leaderboard + 0.3×streak + 0.2×gamification | Competitiveness/leaderboard interest |
| **Churn Risk** | 0.4×(1-sessions) + 0.3×(1-notif_open) + 0.3×no_streak | Probability of leaving the platform |

All inputs are min-max normalized before weighting, so scores are always between 0 and 1.

#### Data Validation

Uses `DataValidator` (from utils) to:
- Check required columns exist (flexible — only `user_id` is truly required)
- Normalize lifecycle stages (title case → lowercase)
- Coerce numeric and boolean types
- Cap outliers (sessions > 50, exercises > 100)
- Fill missing values (median for numerics, mode for categoricals, False for booleans)

#### KB-Driven Feature Columns

If the Knowledge Bank identified features like "ai_tutor" or "leaderboard", the engine checks whether corresponding columns (e.g., `feature_ai_tutor_used`) exist in the CSV. If not, it creates them with default values. This ensures the pipeline works even with incomplete datasets.

---

### 4.3 Segmentation Engine

**File**: `src/intelligence/segmentation.py` (~310 lines)  
**Purpose**: Create 6-12 mutually exclusive (MECE) user segments using ML clustering

#### The Approach: RFM + Hierarchical Clustering

We combine two techniques:

**Step 1 — RFM Analysis** (adapted for engagement context):
- **Recency**: How recently the user was active (proxied by `sessions_last_7d`)
- **Frequency**: How often they engage (proxied by `exercises_completed_7d`)  
- **Monetary**: How valuable their engagement is (proxied by `notif_open_rate_30d` × `motivation_score`)

Each dimension is scored 1-5 using quantile binning, then combined into a composite RFM score. This creates a behavioral baseline.

**Step 2 — Feature Engineering for Clustering**:
The engine creates a rich feature matrix including:
- Core behavioral: activeness, churn_risk
- Propensity scores: gamification, social, AI tutor, leaderboard
- RFM components: rfm_score, rfm_segment encoding
- Derived features: engagement_intensity, streak_consistency, feature_diversity

**Step 3 — Optimal K Selection**:
Instead of guessing the number of segments, the engine tries K=6 through K=12 and picks the best using:
- **Silhouette Score** (primary): Measures how well-separated the clusters are (-1 to +1, higher is better)
- **Davies-Bouldin Index** (secondary): Measures cluster overlap (lower is better)
- **Elbow Method** (fallback): Looks for the "elbow" in the inertia curve

**Step 4 — Hierarchical Clustering**:
Uses **Agglomerative Clustering with Ward's linkage** instead of K-Means. Why?
- Ward's minimizes within-cluster variance, giving more balanced segment sizes
- Hierarchical clustering doesn't depend on random initialization (unlike K-Means)
- Produces a dendrogram structure that's interpretable

**Step 5 — Segment Naming**:
Each segment gets a human-readable name based on its behavioral profile:
- High activeness + high gamification → "Power Gamers"
- Low activeness + high churn risk → "At-Risk Users"
- High social propensity → "Social Learners"
- etc.

#### Output: `user_segments.csv`

Each user gets assigned a `segment_id` and `segment_name`, along with all their propensity scores. The minimum segment size is enforced at 5% of total users to ensure statistical significance.

---

### 4.4 ML Propensity Models

**File**: `src/intelligence/ml_propensity_models.py` (~247 lines)  
**Purpose**: Train gradient-boosted models for churn prediction and engagement forecasting

#### Model 1: Churn Prediction (XGBoost Classifier)

- **Algorithm**: XGBoost (eXtreme Gradient Boosting)
- **Task**: Binary classification — will this user churn? (yes/no)
- **Target**: Users with `churn_risk > 0.7` (from config) labeled as churned
- **Features**: sessions, exercises, streak, coins, notif_open_rate, motivation_score, days_since_signup, activeness
- **Evaluation**: AUC-ROC (for discrimination quality) + 5-fold cross-validation (for robustness)
- **Hyperparameters**: max_depth=4, n_estimators=100, learning_rate=0.1, subsample=0.8

#### Model 2: Engagement Prediction (LightGBM Regressor)

- **Algorithm**: LightGBM (Light Gradient Boosting Machine)
- **Task**: Regression — predict the user's engagement level (0 to 1)
- **Target**: `activeness` score
- **Features**: Same as churn model
- **Evaluation**: RMSE + R² + 5-fold cross-validation
- **Hyperparameters**: num_leaves=31, learning_rate=0.05, n_estimators=200, early_stopping_rounds=10

#### Why Two Different Frameworks?

- **XGBoost** is better for classification tasks and handles class imbalance well
- **LightGBM** is faster for regression and handles continuous targets better
- Using both demonstrates understanding of when to apply each

Both models output feature importances, which tell us which behavioral signals matter most for predicting churn and engagement.

---

### 4.5 Goal Builder

**File**: `src/intelligence/goal_builder.py` (~138 lines)  
**Purpose**: Define lifecycle journey goals for each segment

#### Journey Structure

For each segment, the Goal Builder creates a day-by-day progression:

**Trial Stage (D0-D7):**
| Day | Goal | Sub-Goals | Success Metric |
|-----|------|-----------|---------------|
| D0 | activation | onboarding_complete, first_exercise | exercises_completed >= 1 |
| D1 | habit_formation | second_session, streak_start | streak_current >= 1 |
| D3 | feature_discovery | explore_features | feature_usage >= 2 |
| D7 | conversion_push | demonstrate_value | conversion_intent |

**Paid Stage (D8-D30):**
| Day | Goal | Purpose |
|-----|------|---------|
| D8 | retention | Ensure post-conversion engagement |
| D14 | expansion | Encourage deeper feature adoption |
| D21 | habit_reinforcement | Solidify daily usage pattern |
| D30 | advocacy | Turn users into promoters |

**Churned / Inactive:**
- Churned → `re_engagement` goal (bring them back)
- Inactive → `activation` goal (wake them up)

The goals adapt based on segment characteristics — for example, if a segment has high `gamification_propensity > 0.6`, goals will reference gamification features like streaks and coins.

#### Output: `segment_goals.csv`

Columns: `segment_id`, `segment_name`, `lifecycle_stage`, `lifecycle_day`, `primary_goal`, `sub_goals`, `success_metric`, `priority`

---

### 4.6 Theme Engine

**File**: `src/communication/theme_engine.py` (~114 lines)  
**Purpose**: Map Octalysis behavioral psychology themes to each segment

#### The Octalysis Framework

The engine uses Yu-kai Chou's **Octalysis Framework**, which identifies 8 core psychological drives that motivate human behavior:

| # | Core Drive | What It Means | When to Use |
|---|-----------|---------------|-------------|
| 1 | **Epic Meaning** | "I'm part of something bigger" | Purpose-driven users |
| 2 | **Accomplishment** | "I'm making progress!" | Achievement-oriented users |
| 3 | **Empowerment** | "I have choices and creativity" | Users who value autonomy |
| 4 | **Ownership** | "This is mine, I've invested in it" | Users with sunk cost/investment |
| 5 | **Social Influence** | "Others are doing it too" | Socially-motivated users |
| 6 | **Scarcity** | "This is limited, I might miss out" | FOMO-susceptible users |
| 7 | **Unpredictability** | "What happens next?" | Curiosity-driven users |
| 8 | **Loss Avoidance** | "I don't want to lose what I have" | Users at risk of losing progress |

#### Theme Selection Logic

The engine picks primary and secondary themes per segment × lifecycle based on behavioral signals:

- **High churn risk** → `loss_avoidance` (show them what they'll lose)
- **High gamification propensity** → `accomplishment` (celebrate progress)
- **High social propensity** → `social_influence` (show community activity)
- **Low activeness** → `unpredictability` (create curiosity to re-engage)
- **Paid users** → `ownership` (reinforce value of investment)
- **Trial users** → `epic_meaning` or `empowerment` (inspire them to commit)

Each theme assignment includes a rationale explaining why it was selected (e.g., "Low activeness (0.35) needs discovery and exploration; Secondary theme 'accomplishment' provides complementary motivation").

#### Output: `communication_themes.csv`

Columns: `segment_id`, `segment_name`, `lifecycle_stage`, `primary_theme`, `secondary_theme`, `theme_rationale`

---

### 4.7 Template Generator

**File**: `src/communication/template_generator.py` (~328 lines)  
**Purpose**: Generate bilingual notification templates for every Segment × Lifecycle × Goal × Theme combination

#### Generation Logic

For each unique combination of (segment, lifecycle, goal, theme), the generator creates **exactly 5 template variants**. Why 5?
- The PS requires exactly 5 per combo
- Having variants enables A/B testing — you can't learn which message works better if there's only one
- Statistical testing needs multiple options per group to compute confidence intervals

#### Template Structure

Each template has:

| Field | Description | Example |
|-------|-------------|---------|
| `template_id` | Unique ID (TPL_0001 format) | TPL_0042 |
| `segment_id` | Target segment | 3 |
| `segment_name` | Human-readable segment | "Power Gamers" |
| `lifecycle_stage` | trial/paid/churned/inactive | trial |
| `goal` | What this should achieve | activation |
| `theme` | Octalysis core drive | accomplishment |
| `variant` | Which of the 5 variants (1-5) | 2 |
| `message_title_en` | English title | "🎯 Your Daily Challenge Awaits!" |
| `message_title_hi` | Hindi/Hinglish title | "🎯 Aaj ka Challenge Ready Hai!" |
| `message_body_en` | English body | "You've completed {exercises_completed_7d} exercises this week..." |
| `message_body_hi` | Hindi/Hinglish body | "Tumne is hafte {exercises_completed_7d} exercises complete kiye..." |
| `cta_text_en` | English call-to-action | "Start Now" |
| `cta_text_hi` | Hindi/Hinglish CTA | "Abhi Shuru Karo" |
| `tone` | Message tone | encouraging |
| `hook` | Behavioral hook used | accomplishment |
| `feature_reference` | Product feature referenced | exercises |

#### Bilingual Strategy

Templates are generated in **both English and Hinglish** (Hindi written in Roman script), in the **same row** — not separate rows. This is because:
- SpeakX targets Tier 2/3 India where Hinglish is the primary digital language
- The PS requires bilingual support
- Same-row structure makes it easy for the schedule generator to pick either language

#### Personalization Tokens

Templates include dynamic tokens like `{exercises_completed_7d}`, `{streak_current}`, `{coins_balance}` that get filled with the user's actual data at send time. This creates personalized messages without needing separate templates per user.

#### Tone Selection

Tones are selected based on lifecycle stage and theme:
- Trial + accomplishment → `encouraging`
- Paid + social_influence → `celebratory`
- Churned + loss_avoidance → `urgent`
- Trial + unpredictability → `friendly`

The config defines both allowed and forbidden tones. Forbidden tones (aggressive, desperate, salesy, guilt-tripping, condescending, pushy) are never used.

---

### 4.8 Timing Optimizer

**File**: `src/communication/timing_optimizer.py` (~280 lines)  
**Purpose**: Determine when to send notifications and how many per day

#### 6 Standard Time Windows

| Window | Hours | Typical Use |
|--------|-------|-------------|
| `early_morning` | 06:00 – 08:59 | Morning routine / commute |
| `mid_morning` | 09:00 – 11:59 | Work break |
| `afternoon` | 12:00 – 14:59 | Lunch break |
| `late_afternoon` | 15:00 – 17:59 | End of work |
| `evening` | 18:00 – 20:59 | Prime engagement time |
| `night` | 21:00 – 23:59 | Before bed |

#### Timing Optimization Strategy

**In Iteration 0** (no experiment data):
- Analyzes users' `preferred_hour` distribution per segment
- Maps hours to time windows
- Ranks windows by popularity (what % of users in this segment prefer this window)
- Computes expected CTR and engagement based on behavioral patterns
- Assigns priority rank (1 = best window for this segment)

**In Iteration 1** (with experiment data):
- Uses actual experiment results to compute a **composite score** per time window:
  ```
  composite_score = CTR × 0.5 + engagement_rate × 0.4 - uninstall_rate × 5.0
  ```
  The heavy uninstall penalty (-5.0) ensures the system strongly avoids windows that cause uninstalls
- Re-ranks windows based on real performance data
- Uses **survival analysis** (Kaplan-Meier) when the `lifelines` library is available

#### Frequency Optimization

Daily notification count is based on user activeness:

| Activeness Score | Notifications/Day | Strategy |
|------------------|-------------------|----------|
| > 0.7 (high) | 8 | Max engagement — active users can handle more |
| 0.4 – 0.7 (medium) | 6 | Balanced — don't overwhelm |
| < 0.4 (low) | 4 | Conservative — re-engage gently |

**Lifecycle Adjustments**:
- Trial users get +1 bonus notification (maximize conversion window)
- Churned users get only 2/day (don't push them further away)

#### Uninstall Guardrail (Critical)

```
If uninstall_rate > 2% for any segment → reduce frequency by 2/day
```

This is a **hard guardrail** — even if a segment has high activeness, if they're uninstalling at >2%, the system automatically reduces notification pressure. This is directly from the PS and is verified in `config.yaml`:
```yaml
uninstall_threshold: 0.02
uninstall_reduction: 2
```

---

### 4.9 NLP Template Optimizer

**File**: `src/communication/nlp_template_optimizer.py` (~290 lines)  
**Purpose**: Analyze template quality using NLP techniques

#### Analysis Features

For each template, the NLP optimizer computes:

| Feature | How It Works |
|---------|-------------|
| `word_count` | Token count of message body |
| `avg_word_length` | Average characters per word |
| `sentiment_score` | Custom lexicon-based sentiment (-1 to +1) |
| `positive_ratio` | Fraction of positive words |
| `negative_ratio` | Fraction of negative words |
| `engagement_score` | Weighted count of engagement keywords (gamification, social, urgency, progress) |
| `urgency_score` | Density of urgency words ("now", "today", "limited", "hurry") |
| `personalization_score` | Count of personalization tokens ({name}, {streak}, etc.) |
| `has_emoji` | Whether the message contains emojis |
| `has_numbers` | Whether the message contains numbers |

#### TF-IDF Analysis

Uses **TF-IDF (Term Frequency-Inverse Document Frequency)** vectorization with bigrams to create a numeric representation of each template's content. This enables:
- **Cosine similarity search**: Find templates that are too similar (near-duplicates)
- **Feature correlation analysis**: Which NLP features correlate with high CTR/engagement

#### Optimization Recommendations

When experiment results are available, the optimizer:
1. Merges template NLP features with performance data
2. Computes Pearson correlation between each NLP feature and CTR/engagement
3. Identifies which features predict good performance (e.g., "templates with emojis have 12% higher CTR")
4. Generates actionable recommendations

---

### 4.10 Schedule Generator

**File**: `src/communication/schedule_generator.py` (~168 lines)  
**Purpose**: Generate user-wise 7-day notification schedules

#### How It Works

For each user (up to `max_users`, default 100):
1. **Determine frequency**: Based on activeness score and segment frequency recommendations
2. **Get lifecycle day**: Calculate current day in lifecycle (D0, D1, ..., D30+)
3. **For each of the 7 days**:
   - Get the appropriate goal for this day
   - Find matching templates (same segment × lifecycle × goal)
   - Sample `n` templates randomly (where n = daily frequency)
   - Assign a time slot in the optimal window (15-minute intervals)
   - Assign channel (push notification)

#### Output: `user_notification_schedule.csv`

| Column | Description |
|--------|-------------|
| `user_id` | The user |
| `segment_id`, `segment_name` | Their segment |
| `lifecycle_stage`, `lifecycle_day` | Where they are in the journey |
| `day_offset` | Day 0-6 of the schedule |
| `notif_1_template_id` | First notification template |
| `notif_1_time` | When to send (e.g., "19:45") |
| `notif_1_channel` | Channel (push) |
| `notif_2_*`, `notif_3_*`, ... | Additional notifications |

The schedule shows **gradual journey progression** — a trial user's Day 0 has "activation" goals while Day 3 has "feature_discovery" goals.

---

### 4.11 Performance Classifier

**File**: `src/learning/performance_classifier.py` (~68 lines)  
**Purpose**: Classify template performance from experiment results

#### Classification Rules (from PS)

| Classification | CTR Condition | Engagement Condition | Logic |
|---------------|---------------|---------------------|-------|
| **GOOD** | > 15% | AND > 40% | Both must be true |
| **BAD** | < 5% | OR < 20% | Either is sufficient |
| **NEUTRAL** | Everything else | Everything else | Default |

Note the asymmetry: GOOD requires **both** conditions (AND), while BAD requires **either** (OR). This is intentional — we want to be conservative about labeling something "good" (need strong evidence on both metrics) but aggressive about catching "bad" templates (if *either* metric is terrible, flag it).

#### Statistical Significance

Templates with fewer than `min_sends_significance` (default: 100) sends are flagged — their classification is less trustworthy due to small sample size.

#### Summary Stats

The classifier also computes aggregate statistics used by the Delta Reporter:
- Total templates by classification
- Average CTR, engagement, uninstall rate
- Count of good/neutral/bad templates

---

### 4.12 Multi-Armed Bandit Engine

**File**: `src/learning/multi_armed_bandit.py` (~284 lines)  
**Purpose**: Continuous template optimization using exploration-exploitation algorithms

#### The Multi-Armed Bandit Problem

Imagine you're in a casino with 100 slot machines (one-armed bandits). Each machine has a different (unknown) payout rate. Your goal: maximize total winnings while figuring out which machines are best.

This is exactly our problem:
- Each **template** is a "slot machine"
- Each **send** is a "pull of the arm"
- Each **click/engagement** is a "win"
- We want to find the best templates while still collecting data on uncertain ones

#### Thompson Sampling

Our primary algorithm. Here's how it works:

1. **Prior**: Each template starts with a Beta(1, 1) distribution (uniform — we know nothing)
2. **Update**: When we observe results, we update:
   - α (alpha) += number of clicks (successes)
   - β (beta) += number of non-clicks (failures)
3. **Selection**: To choose which template to send next, randomly sample from each template's Beta(α, β) distribution. Pick the one with the highest sample. This naturally balances:
   - **Exploitation**: Templates with high estimated CTR get sampled higher on average
   - **Exploration**: Templates with high uncertainty (wide distribution) occasionally get sampled very high

#### Upper Confidence Bound (UCB)

An alternative algorithm:
```
UCB_score = mean_CTR + confidence × √(ln(total_sends) / sends_for_this_template)
```

The exploration bonus `√(ln(N)/n)` gets larger for templates that haven't been tested much, ensuring we don't ignore them.

#### Winner/Loser Identification

Using the **95% credible intervals** from the Beta posterior:
- **Winner**: Lower bound of CI > 15% CTR (we're 97.5% confident it's above the "good" threshold)
- **Loser**: Upper bound of CI < 5% CTR (we're 97.5% confident it's below the "bad" threshold)
- **Uncertain**: Need more data (CI spans both thresholds)

This is much more rigorous than just looking at the raw CTR — a template with 2 sends and 100% CTR isn't a real "winner" because the confidence interval is enormous.

---

### 4.13 Statistical Testing Framework

**File**: `src/learning/statistical_testing.py` (~277 lines)  
**Purpose**: Rigorous statistical validation of template performance differences

#### Bayesian A/B Testing

Uses the **Beta-Binomial conjugate model**:
1. Model each template's CTR as Beta(α, β) where α = successes + 1, β = failures + 1
2. Draw 10,000 Monte Carlo samples from each posterior
3. Compare: `P(treatment > control)` = fraction of samples where treatment wins
4. Report: probability of being better, expected lift, credible intervals

**Why Bayesian?**  
- Can say "there's a 94% probability that Template A is better than Template B"
- No arbitrary p-value cutoff
- Works well with small sample sizes (common in notification A/B tests)

#### Frequentist A/B Testing

Uses the **two-proportion z-test**:
1. Pool success rates: `p_pool = (successes₁ + successes₂) / (trials₁ + trials₂)`
2. Standard error: `SE = √(p_pool × (1-p_pool) × (1/n₁ + 1/n₂))`
3. Z-statistic: `z = (p₁ - p₂) / SE`
4. P-value from normal distribution

Also computes **Cohen's h** effect size:
```
h = 2 × arcsin(√p₁) - 2 × arcsin(√p₂)
```
- |h| < 0.2 = small effect
- |h| 0.2-0.8 = medium effect  
- |h| > 0.8 = large effect

#### Sequential Testing

For early stopping during live experiments:
- Uses **O'Brien-Fleming** or **Pocock alpha-spending functions**
- Allows checking significance at interim analyses without inflating Type I error
- O'Brien-Fleming is more conservative early on (harder to stop early) but more powerful at final analysis

#### Combined Verdict

The framework merges frequentist and Bayesian results into a single verdict:
- **STRONG_WINNER**: Both frequentist significant AND Bayesian probability > 95%
- **LIKELY_WINNER**: Bayesian probability > 90%
- **LIKELY_LOSER**: Bayesian probability < 10%
- **INCONCLUSIVE**: Not enough evidence either way

#### Multi-Variant Testing

When comparing more than 2 templates simultaneously, uses **Bonferroni correction** (divide α by number of comparisons) to control family-wise error rate.

---

### 4.14 Learning Engine

**File**: `src/learning/learning_engine.py` (~216 lines)  
**Purpose**: Apply learnings from experiment results to improve all system outputs

#### Four Learning Dimensions

**1. Template Learning** (`_learn_templates`):
- BAD templates → **suppressed** (filtered from active set)
- GOOD templates → **promoted** (weight multiplied by 3×)
- NEUTRAL templates → unchanged
- Every suppression/promotion is logged with full causal reasoning

**2. Timing Learning** (`_learn_timing`):
- Computes composite score per (segment, time_window)
- Suppresses windows with scores in the bottom quartile
- Keeps top 2 windows per segment
- Reports changes: "Removed 'early_morning' window for segment 3: composite score -0.05"

**3. Theme Learning** (`_learn_themes`):
- For each segment, finds the best-performing theme from experiment data
- If that theme differs from the current primary theme AND has CTR > 12%, updates it
- Example: "Changed primary theme for segment 2 from 'accomplishment' to 'social_influence' — experiment CTR 18.5%"

**4. Frequency Learning** (`_learn_frequency`):
- Groups experiment data by segment
- If any segment has mean uninstall_rate > 2% → reduces frequency by 2/day
- This is the same guardrail from the timing optimizer, but now applied based on actual experiment evidence

#### Changes Log

Every learning action is recorded in a `changes_log` list containing:
```python
{
    'entity_type': 'template' | 'timing' | 'theme' | 'frequency',
    'entity_id': <which specific entity changed>,
    'change_type': 'suppression' | 'promotion' | 'optimization',
    'metric_trigger': <the metric that caused the change>,
    'before_value': <old state>,
    'after_value': <new state>,
    'explanation': <causal reasoning string>
}
```

These are the exact 7 fields required by the PS for the Delta Reporter.

---

### 4.15 Delta Reporter

**File**: `src/learning/delta_reporter.py` (~100 lines)  
**Purpose**: Document all changes between Iteration 0 and Iteration 1

#### What It Reports

The Delta Reporter takes the `changes_log` and produces:

1. **learning_delta_report.csv**: Every individual change with causal explanation
2. **Summary metrics**: CTR improvement, engagement improvement, uninstall rate reduction, template count changes
3. **Detailed comparison print**: Side-by-side Iteration 0 vs Iteration 1 statistics

#### 7 Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `entity_type` | What changed | "template" |
| `entity_id` | Which one | "TPL_0042" |
| `change_type` | Type of change | "suppression" |
| `metric_trigger` | What metric caused it | "CTR=0.031, Engagement=0.182" |
| `before_value` | Previous state | "active" |
| `after_value` | New state | "suppressed" |
| `explanation` | Why (causal reasoning) | "Bandit analysis: Consistently underperformed (CTR < 5% or Engagement < 20%). Statistical confidence: (0.02, 0.06)" |

This is the **proof that learning happened** — evaluators will read this file to verify the system isn't doing mock learning.

---

### 4.16 Utility Modules (Metrics & Validation)

#### MetricsCalculator (`src/utils/metrics.py`, ~168 lines)

A static utility class with all propensity score formulas. Key design choice: all `@staticmethod` methods — no state, no side effects, pure functions. This makes them easy to test and reuse.

Contains `calculate_activeness()`, `calculate_gamification_propensity()`, `calculate_social_propensity()`, `calculate_ai_tutor_propensity()`, `calculate_leaderboard_propensity()`, `calculate_churn_risk()`, and performance classification helpers.

#### DataValidator (`src/utils/validation.py`, ~130 lines)

Handles schema validation, type coercion, outlier capping, and missing value imputation. Key feature: **graceful degradation** — if columns are missing, they're added with defaults rather than crashing. This means the system works with incomplete datasets.

---

## 5. Theories, Algorithms & Strategies Explained

### 5.1 RFM Analysis

**RFM (Recency, Frequency, Monetary)** is a customer segmentation technique from marketing analytics.

**Original Meaning (Retail):**
- Recency: When did the customer last purchase? (recent = more likely to buy again)
- Frequency: How often do they purchase? (frequent = loyal)
- Monetary: How much do they spend? (high spenders = valuable)

**Our Adaptation (EdTech Engagement):**
- Recency → `sessions_last_7d` (how recently active?)
- Frequency → `exercises_completed_7d` (how often do they engage?)
- Monetary → `notif_open_rate_30d × motivation_score` (how valuable is their engagement?)

**Scoring**: Each dimension is scored 1-5 using **quantile binning** (pd.qcut). This maps any distribution to a uniform 1-5 scale. The composite score (average of R, F, M) gives a 1.0-5.0 engagement quality score.

**RFM Segment Labels**: Based on composite score:
- Score > 4.0 → "Champions" (best users)
- Score > 3.0 → "Loyal" (solid users)
- Score > 2.0 → "Potential" (could go either way)
- Score ≤ 2.0 → "Lost" (at risk or already gone)

---

### 5.2 Hierarchical Clustering (Ward's Method)

**Hierarchical Clustering** builds a tree (dendrogram) of clusters by iteratively merging the closest groups.

**Ward's Linkage** specifically:
- At each step, merge the two clusters that cause the **minimum increase in total within-cluster variance**
- This produces compact, spherical clusters of similar size
- Unlike single/complete linkage, Ward's avoids the "chaining" effect where one long, thin cluster absorbs everything

**Algorithm**:
1. Start with N clusters (each user = one cluster)
2. Compute Ward distance between all pairs
3. Merge the closest pair
4. Recompute distances
5. Repeat until K clusters remain

**Why not K-Means?**
- K-Means is sensitive to initialization (different random seeds → different results)
- K-Means assumes spherical clusters of equal size
- Hierarchical clustering is deterministic and produces balanced segments
- Both are O(n²) for this data size, so no practical speed difference

---

### 5.3 Optimal K Selection (Silhouette, Davies-Bouldin, Elbow)

Since we need 6-12 segments, we need to decide the exact K. Three methods:

**Silhouette Score** (primary):
- For each point: s = (b - a) / max(a, b)
  - a = average distance to other points in same cluster
  - b = average distance to points in nearest other cluster
- Score ranges -1 to +1. Higher = better separation
- We pick K that maximizes the average silhouette score

**Davies-Bouldin Index** (secondary):
- Measures average similarity between each cluster and its most similar one
- Lower = better (clusters are more distinct)
- DB = (1/K) × Σᵢ maxⱼ≠ᵢ (σᵢ + σⱼ) / d(cᵢ, cⱼ)

**Elbow Method** (fallback):
- Plot K vs. inertia (total within-cluster sum of squares)
- Look for the "elbow" — the point where adding more clusters gives diminishing returns
- Detected algorithmically using the **distance-from-line method** (perpendicular distance from each point to the line connecting K_min to K_max)

---

### 5.4 XGBoost — Gradient Boosted Trees

**XGBoost (eXtreme Gradient Boosting)** is an ensemble learning algorithm:

1. Start with a simple prediction (e.g., base rate of churn)
2. Train a shallow decision tree on the **residuals** (errors of previous prediction)
3. Add the new tree's predictions (weighted by learning rate) to the ensemble
4. Repeat for N trees

**Key Features Used in Our Implementation**:
- `max_depth=4`: Trees are shallow to prevent overfitting
- `learning_rate=0.1`: Each tree contributes a small update
- `n_estimators=100`: 100 sequential trees
- `subsample=0.8`: Each tree sees 80% of data (reduces overfitting)
- `scale_pos_weight`: Handles class imbalance (if churners are rare)

**Why XGBoost for Churn?**
- Handles tabular data extremely well (consistently wins Kaggle competitions)
- Built-in regularization (L1 and L2)
- Handles missing values natively
- Feature importance is directly interpretable

---

### 5.5 LightGBM — Light Gradient Boosting Machine

**LightGBM** is similar to XGBoost but uses two key innovations:

1. **Gradient-based One-Side Sampling (GOSS)**: Instead of using all data points, keeps all points with large gradients (hard to learn) and randomly samples points with small gradients. This speeds up training without losing accuracy.

2. **Exclusive Feature Bundling (EFB)**: Bundles mutually exclusive features together, reducing dimensionality.

**Our Implementation**:
- `num_leaves=31`: Controls tree complexity (leaf-based growth instead of depth-based)
- `learning_rate=0.05`: Smaller steps for finer optimization
- `n_estimators=200`: More trees to compensate for smaller learning rate
- `early_stopping_rounds=10`: Stops training if validation loss doesn't improve for 10 rounds

**Why LightGBM for Engagement?**
- Faster training than XGBoost for regression tasks
- Leaf-based growth often produces better fits for continuous targets
- Better handling of high-cardinality features

---

### 5.6 Survival Analysis (Kaplan-Meier)

**Survival Analysis** models "time to event" — originally used in medical research (time to death), adapted here for "time to engagement".

**Kaplan-Meier Estimator**:
- Non-parametric method that estimates the survival function S(t)
- S(t) = probability that the event hasn't happened by time t
- Handles **censored data** (users who leave the study before the event occurs)

**In Our System**:
- "Event" = clicking a notification
- "Time" = hours since notification was sent
- For each time window, compute the engagement survival curve
- Windows where engagement drops off quickly → send earlier in that window
- Used in Iteration 1 when `lifelines` library is available

**Cox Proportional Hazards** (optional extension):
- Multivariate model: hazard(t) = h₀(t) × exp(β₁x₁ + β₂x₂ + ...)
- Identifies which features (segment, theme, time of day) affect the hazard rate
- Features with positive coefficients → increase the rate of engagement
- Not required by PS but demonstrates advanced statistical thinking

---

### 5.7 Octalysis Framework — 8 Core Drives

**The Octalysis Framework** (by Yu-kai Chou) is a behavioral design framework used in gamification. It identifies 8 fundamental drives:

**White Hat Drives** (positive motivation — feel good):
1. **Epic Meaning & Calling**: Motivation from being part of something bigger ("Join 10M learners changing their lives")
2. **Development & Accomplishment**: Progress, goals, mastery ("You've completed 50% of Level 3!")
3. **Empowerment of Creativity & Feedback**: Freedom and self-expression ("Choose your own learning path")

**Right Brain Drives** (intrinsic — creativity, social, curiosity):
4. **Ownership & Possession**: Collecting, building, investing ("Your vocabulary bank has 342 words!")
5. **Social Influence & Relatedness**: Community, competition, mentorship ("Your friend just passed you on the leaderboard!")

**Black Hat Drives** (negative motivation — create urgency):
6. **Scarcity & Impatience**: Limited availability ("Only 3 spots left in today's group!")
7. **Unpredictability & Curiosity**: Variable rewards ("Spin the wheel for today's bonus!")
8. **Loss & Avoidance**: Fear of losing progress ("Your streak ends in 4 hours!")

**In Our System**: Each segment gets a primary and secondary drive based on its behavioral profile. This determines the messaging tone and hooks. A user with high gamification propensity gets "accomplishment" themes, while a churned user gets "loss_avoidance".

---

### 5.8 Multi-Armed Bandit Problem

The **Multi-Armed Bandit (MAB)** problem is the **exploration vs. exploitation dilemma**:

- **Exploration**: Try unknown options to discover their value
- **Exploitation**: Use the best-known option to maximize reward

Classic example: You're in a casino with 100 slot machines. Each has an unknown payout rate. How should you allocate your plays to maximize total winnings?

**Why This Matters for Notifications**:
- You have hundreds of templates
- Each template has an unknown CTR
- Sending a template is "pulling an arm" — you observe whether the user clicked
- You want to maximize total clicks while learning which templates work

**Naive Approaches Don't Work**:
- **Pure exploration** (send randomly): Wastes sends on bad templates
- **Pure exploitation** (always send the current best): Might miss a better template you haven't tested enough
- **Equal allocation**: Wastes sends on clearly bad templates

---

### 5.9 Thompson Sampling

**Thompson Sampling** is a Bayesian approach to the MAB problem:

**Idea**: Model each arm's reward rate as a probability distribution. Sample from the distribution, and pick the arm with the highest sample.

**For Binary Rewards (click / no-click)**:

1. **Prior**: Each template starts with Beta(1, 1) — uniform distribution (we know nothing)
2. **Observe**: Template gets `s` clicks out of `n` sends
3. **Posterior**: Beta(1 + s, 1 + n - s)
4. **Select**: Sample θ ~ Beta(α, β) for each template. Pick the template with the highest θ.

**Why It Works**:
- Templates with high estimated CTR get sampled high → exploitation
- Templates with uncertain CTR (low sends) have wide distributions → occasionally sampled very high → exploration
- As data accumulates, distributions narrow → system naturally shifts from exploration to exploitation
- Provably optimal (asymptotically) — no tuning parameters needed

**Example**:
- Template A: Beta(51, 450) — ~10% CTR, tight distribution
- Template B: Beta(3, 7) — ~30% CTR, but VERY wide distribution (only 10 sends!)
- Template B might occasionally sample below Template A, correctly reflecting our uncertainty

---

### 5.10 Upper Confidence Bound (UCB)

**UCB** is a frequentist approach to the MAB problem:

```
UCB(i) = x̄ᵢ + c × √(ln(N) / nᵢ)
```

Where:
- x̄ᵢ = average reward of arm i (estimated CTR)
- N = total sends across all arms
- nᵢ = sends for arm i
- c = confidence parameter (tunable; our default = 2.0)

**Exploration Bonus**: `√(ln(N) / nᵢ)` grows when:
- Total sends N increases (more data overall)
- Sends for this arm nᵢ are low (under-explored)

So under-tested templates get a bonus that makes them competitive even if their estimated CTR is low. As nᵢ grows, the bonus shrinks and the true CTR dominates.

**UCB vs Thompson Sampling**:
- UCB is deterministic — same result given same data
- Thompson is stochastic — adds randomness from sampling
- Both achieve near-optimal regret bounds
- Thompson Sampling tends to empirically outperform UCB for most problems
- We implement both — Thompson for primary selection, UCB as an alternative

---

### 5.11 Bayesian A/B Testing

**Traditional (Frequentist) A/B testing** answers: "IF there's no difference, what's the probability of seeing data this extreme?"

**Bayesian A/B testing** answers: "Given the data, what's the probability that Treatment is better than Control?"

**Our Implementation**:
1. Model Control CTR as Beta(α₁, β₁), Treatment CTR as Beta(α₂, β₂)
2. Draw 10,000 Monte Carlo samples from each posterior
3. `P(Treatment > Control)` = count(treatment_samples > control_samples) / 10,000
4. Expected lift = mean(treatment_samples - control_samples) / mean(control_samples)
5. Credible intervals = 2.5th and 97.5th percentiles of (treatment - control)

**Why Bayesian?**
- Direct probability statements ("95% chance Template A is better")
- Works with small samples (doesn't need thousands of observations)
- No significance threshold trap (p < 0.05 is arbitrary)
- Naturally handles sequential testing (can check anytime without penalty)

---

### 5.12 Frequentist A/B Testing

For completeness and rigor, we implement the classical approach too:

**Two-Proportion Z-Test**:
1. H₀: p₁ = p₂ (no difference in CTR)
2. H₁: p₁ ≠ p₂ (there is a difference)
3. Pool: p̂ = (x₁ + x₂) / (n₁ + n₂)
4. SE = √(p̂(1-p̂)(1/n₁ + 1/n₂))
5. z = (p̂₁ - p̂₂) / SE
6. p-value = 2 × P(Z > |z|)

**Effect Size (Cohen's h)**:
```
h = 2 × arcsin(√p₁) - 2 × arcsin(√p₂)
```
Tells you *how big* the difference is, not just whether it exists.

**Combined Verdict**: We merge both paradigms:
- Frequentist p < 0.05 AND Bayesian P > 95% → **STRONG_WINNER**
- Only Bayesian P > 90% → **LIKELY_WINNER**
- Only Bayesian P < 10% → **LIKELY_LOSER**
- Otherwise → **INCONCLUSIVE**

This dual approach is much more robust than using either paradigm alone.

---

### 5.13 TF-IDF Vectorization

**TF-IDF (Term Frequency × Inverse Document Frequency)** converts text into numbers:

**Term Frequency** (TF): How often a word appears in a document
```
TF(word, doc) = count(word in doc) / total_words(doc)
```

**Inverse Document Frequency** (IDF): How rare a word is across all documents
```
IDF(word) = log(N / count_docs_containing_word)
```

**TF-IDF** = TF × IDF — words that are frequent in ONE document but rare across ALL documents get high scores. This means:
- Common words like "the", "is" get low scores (high TF but low IDF)
- Unique, meaningful words get high scores

**In Our System**:
- Each template is a "document"
- We use bigrams (pairs of consecutive words) for richer representation
- The TF-IDF matrix enables cosine similarity search (finding near-duplicate templates)
- Combined with experiment data, we can discover which words/phrases correlate with engagement

---

### 5.14 Beta Distribution & Conjugate Priors

The **Beta distribution** is central to our Bayesian analysis:

**Beta(α, β)**:
- Defined on [0, 1] — perfect for modeling probabilities (like CTR)
- Mean = α / (α + β)
- Variance = αβ / ((α+β)²(α+β+1))
- Higher α+β → narrower distribution (more confident)

**Conjugate Prior**: When the prior and posterior are the same family of distributions:
- Prior: Beta(α, β)
- Likelihood: Binomial (clicks out of sends)
- Posterior: Beta(α + clicks, β + non_clicks)

This is computationally elegant — no complex integrals needed. Just add observed counts to the parameters.

**Why Beta(1, 1) as the prior?**
- Beta(1, 1) = Uniform(0, 1) = "I don't know the CTR, it could be anything"
- This is the **minimally informative prior** — we let the data speak
- After just 10 observations, the prior barely matters anymore

---

### 5.15 Sequential Testing & Alpha Spending

**The Problem**: In traditional A/B testing, you set a sample size upfront and check once. But what if the result is obvious after 10% of the data? You'd waste sends testing a clearly superior template.

**Sequential Testing** lets you check results iteratively without inflating the false positive rate.

**Alpha Spending Functions**:
- The total Type I error budget (α = 0.05) is "spent" across multiple analyses
- **O'Brien-Fleming**: Spends very little alpha early (hard to stop early), saves most for the final check. More conservative but more powerful.
  - Formula: α_k = 2 × (1 - Φ(z_α/2 / √(k/K)))
- **Pocock**: Spends alpha equally across all checks. Easier to stop early but slightly less powerful.
  - Formula: α_k = α (constant at each check)

**In Our System**: Sequential testing is used for ongoing experiments where we want to stop testing underperforming templates early without waiting for full sample size.

---

## 6. Configuration Reference

All thresholds are centralized in `config/config.yaml`:

```yaml
# Segmentation
segmentation:
  n_clusters: 8          # Default number of segments
  min_clusters: 6        # Minimum allowed
  max_clusters: 12       # Maximum allowed
  min_segment_size: 0.05 # At least 5% of users per segment
  random_state: 42       # For reproducibility

# Performance Classification Thresholds
performance:
  good_ctr: 0.15         # >15% CTR to be "GOOD"
  good_engagement: 0.40  # >40% engagement to be "GOOD"
  bad_ctr: 0.05          # <5% CTR to be "BAD"
  bad_engagement: 0.20   # <20% engagement to be "BAD"
  min_sends_significance: 100  # Minimum sends for statistical significance
  churn_risk_threshold: 0.7    # Churn risk score to flag as "churned"

# Frequency Optimization
frequency:
  high_activeness_threshold: 0.7  # Activeness > 0.7 = high
  medium_activeness_threshold: 0.4 # Activeness 0.4-0.7 = medium
  high_activeness_freq: 8         # 8 notifs/day for high
  medium_activeness_freq: 6       # 6 notifs/day for medium
  low_activeness_freq: 4          # 4 notifs/day for low
  trial_bonus: 1                  # +1 for trial users
  churned_freq: 2                 # Only 2/day for churned
  uninstall_threshold: 0.02       # 2% uninstall rate guardrail
  uninstall_reduction: 2          # Reduce by 2/day when triggered

# 6 Standard Time Windows
time_windows:
  early_morning: [6, 9]
  mid_morning: [9, 12]
  afternoon: [12, 15]
  late_afternoon: [15, 18]
  evening: [18, 21]
  night: [21, 24]

# Communication Tones
communication:
  allowed_tones: [encouraging, friendly, aspirational, urgent, celebratory, motivational, supportive]
  forbidden_tones: [aggressive, desperate, salesy, guilt-tripping, condescending, pushy]
  tone_by_lifecycle:
    trial: [encouraging, friendly, aspirational, supportive]
    paid: [celebratory, friendly, aspirational, motivational]
    churned: [friendly, urgent, aspirational, curious]
    inactive: [curious, friendly, inviting]
```

---

## 7. Data Flow & Pipeline Execution

### Iteration 0 Data Flow

```
Input: user_data_sample.csv (500 users) + pdf_content.txt (Knowledge Bank)
                              │
    ┌─────────────────────────┼───────────────────────────────┐
    │ KnowledgeBankEngine     │                               │
    │ • Detects domain        │                               │
    │ • Extracts North Star   │                               │
    │ • Maps features→goals   │                               │
    │ • Builds tone matrix    │                               │
    ├─────────────────────────┘                               │
    │ Outputs: company_north_star.json                        │
    │          feature_goal_map.json                          │
    │          allowed_tone_hook_matrix.json                  │
    ▼                                                         │
    ┌─────────────────────────────────────────────────┐       │
    │ DataIngestionEngine                              │       │
    │ • Validates schema                               │       │
    │ • Fills missing columns                          │       │
    │ • Engineers 6 propensity scores                   │       │
    │ • Normalizes all scores to [0,1]                  │       │
    └──────┬──────────────────────────────────────────┘       │
           │ Engineered user data (500 users × 20+ features)  │
           ▼                                                   │
    ┌──────────────────────────────┐                           │
    │ SegmentationEngine           │                           │
    │ • RFM scoring (1-5 per dim)  │                           │
    │ • Optimal K selection        │                           │
    │ • Hierarchical clustering    │                           │
    │ • Segment naming             │                           │
    └──────┬───────────────────────┘                           │
           │ user_segments.csv (500 users × segment_id)        │
           ▼                                                   │
    ┌──────────────────────────────┐                           │
    │ PropensityModelEngine        │                           │
    │ • XGBoost churn model        │                           │
    │ • LightGBM engagement model  │                           │
    │ • Predict propensities       │                           │
    └──────┬───────────────────────┘                           │
           │ Enhanced user data with ML predictions             │
           ▼                                                   │
    ┌──────────────────────────────┐                           │
    │ GoalBuilder                  │ → segment_goals.csv       │
    │ • Trial D0-D7 progression    │                           │
    │ • Paid D8-D30 retention      │                           │
    │ • Churned re-engagement      │                           │
    └──────┬───────────────────────┘                           │
           ▼                                                   │
    ┌──────────────────────────────┐                           │
    │ ThemeEngine                  │ → communication_themes.csv│
    │ • Octalysis 8 drives         │                           │
    │ • Primary + secondary themes │                           │
    └──────┬───────────────────────┘                           │
           ▼                                                   │
    ┌──────────────────────────────┐                           │
    │ TemplateGenerator            │ → message_templates.csv   │
    │ • 5 variants per combo       │                           │
    │ • Bilingual EN + HI          │                           │
    │ • NLP analysis added         │                           │
    └──────┬───────────────────────┘                           │
           ▼                                                   │
    ┌──────────────────────────────┐                           │
    │ TimingOptimizer              │ → timing_recommendations  │
    │ • 6 time windows             │    .csv                   │
    │ • Behavioral pattern basis   │                           │
    │ • Frequency recommendations  │                           │
    └──────┬───────────────────────┘                           │
           ▼                                                   │
    ┌──────────────────────────────┐                           │
    │ ScheduleGenerator            │ → user_notification       │
    │ • 7-day schedule per user    │    _schedule.csv           │
    │ • Matches template to user   │                           │
    └──────┬───────────────────────┘                           │
           ▼                                                   │
    ┌──────────────────────────────┐                           │
    │ MultiArmedBanditEngine       │ → bandit_state.json       │
    │ • Initialize Beta(1,1) for   │                           │
    │   all templates              │                           │
    └──────────────────────────────┘                           │
```

### Iteration 1 Data Flow

```
Input: experiment_results_sample.csv + all Iteration 0 outputs
                              │
    ┌─────────────────────────┘
    ▼
    ┌──────────────────────────────┐
    │ PerformanceClassifier        │
    │ • Classify GOOD/NEUTRAL/BAD  │ → experiment_results.csv
    │ • Compute summary stats      │
    └──────┬───────────────────────┘
           ▼
    ┌──────────────────────────────┐
    │ StatisticalTestingFramework  │ → statistical_analysis.csv
    │ • Bayesian A/B tests         │
    │ • Frequentist z-tests        │
    │ • Combined verdicts          │
    └──────┬───────────────────────┘
           ▼
    ┌──────────────────────────────┐
    │ MultiArmedBanditEngine       │ → template_rankings.csv
    │ • Update Beta posteriors     │   bandit_learning_report.csv
    │ • Thompson Sampling rankings │   bandit_state.json
    │ • Identify winners/losers    │
    └──────┬───────────────────────┘
           ▼
    ┌──────────────────────────────┐
    │ NLPTemplateOptimizer         │ → templates_nlp_analysis.csv
    │ • Feature-performance        │   nlp_recommendations.csv
    │   correlation                │
    │ • Optimization recommendations│
    └──────┬───────────────────────┘
           ▼
    ┌──────────────────────────────┐
    │ TimingOptimizer (Re-run)     │ → timing_recommendations
    │ • Experiment-based scoring   │    _improved.csv
    │ • Updated frequencies        │   frequency_recommendations
    │                              │    _improved.csv
    └──────┬───────────────────────┘
           ▼
    ┌──────────────────────────────┐
    │ Template Filtering           │ → message_templates
    │ • Suppress losers            │    _improved.csv
    │ • Promote winners (2× weight)│
    └──────┬───────────────────────┘
           ▼
    ┌──────────────────────────────┐
    │ DeltaReporter                │ → learning_delta_report.csv
    │ • Document all changes       │
    │ • Causal reasoning           │
    │ • Iter0 vs Iter1 comparison  │
    └──────┬───────────────────────┘
           ▼
    ┌──────────────────────────────┐
    │ ScheduleGenerator (Re-run)   │ → user_notification_schedule
    │ • Uses improved templates    │    _improved.csv
    │ • Uses improved timing       │
    │ • Uses improved frequencies  │
    └──────────────────────────────┘
```

---

## 8. Output Files Reference

### Task 1 Deliverables

| File | Format | What It Contains |
|------|--------|-----------------|
| `company_north_star.json` | JSON | Primary metric, definition, rationale, key drivers |
| `feature_goal_map.json` | JSON | Product features mapped to business goals |
| `allowed_tone_hook_matrix.json` | JSON | Allowed/forbidden tones, Octalysis hooks with examples |
| `user_segments.csv` | CSV | Every user with segment_id, all propensity scores |
| `segment_goals.csv` | CSV | Goals per segment × lifecycle × day |

### Task 2 Deliverables

| File | Format | What It Contains |
|------|--------|-----------------|
| `communication_themes.csv` | CSV | Primary/secondary Octalysis themes per segment×lifecycle |
| `message_templates.csv` | CSV | All templates (bilingual) with tone, hook, feature reference |
| `timing_recommendations.csv` | CSV | Time window rankings per segment with expected performance |
| `user_notification_schedule.csv` | CSV | Per-user 7-day notification schedule |

### Task 3 Deliverables

| File | Format | What It Contains |
|------|--------|-----------------|
| `experiment_results.csv` | CSV | Classified experiment results (GOOD/NEUTRAL/BAD) |
| `learning_delta_report.csv` | CSV | Every change documented with causal reasoning |

### Additional Outputs (Generated by Pipeline)

| File | Purpose |
|------|---------|
| `communication_themes_improved.csv` | Themes after learning |
| `message_templates_improved.csv` | Templates after suppression/promotion |
| `timing_recommendations_improved.csv` | Timing after experiment-based optimization |
| `frequency_recommendations.csv` | Base frequency recommendations |
| `frequency_recommendations_improved.csv` | Frequency after learning |
| `user_notification_schedule_improved.csv` | Schedule using improved components |
| `statistical_analysis.csv` | Bayesian + Frequentist test results |
| `template_rankings_bandit.csv` | Bandit-based template rankings |
| `bandit_learning_report.csv` | Multi-Armed Bandit learning outputs |
| `bandit_state.json` | Serialized bandit state for persistence |
| `ml_model_performance.csv` | XGBoost/LightGBM evaluation metrics |

---

## 9. Key Design Decisions & Why

### 1. Why Hierarchical Clustering over K-Means?

**Decision**: Agglomerative Clustering with Ward's linkage  
**Why**: 
- Deterministic — same data always → same segments (reproducibility requirement)
- Produces balanced segment sizes (K-Means can create tiny segments)
- Ward linkage minimizes within-cluster variance (compact, well-separated groups)
- Doesn't require assuming spherical cluster shapes

### 2. Why 5 Templates per Combo?

**Decision**: Exactly 5 variants per Segment × Lifecycle × Goal × Theme  
**Why**: 
- PS explicitly requires "exactly 5 message templates"
- 5 variants enable meaningful A/B testing (need multiple options to compare)
- Not too many to dilute sends per template (statistical significance needs enough observations each)

### 3. Why Both Bayesian AND Frequentist Testing?

**Decision**: Run both and combine verdicts  
**Why**:
- Bayesian gives intuitive probability statements ("94% chance Template A is better")
- Frequentist gives traditional statistical significance (p-values, required by most academic reviewers)
- Agreement between both → very strong evidence
- Each catches different edge cases

### 4. Why Thompson Sampling over Epsilon-Greedy?

**Decision**: Thompson Sampling as primary bandit algorithm  
**Why**: 
- Epsilon-Greedy is too simple (randomly explores with fixed probability ε)
- Thompson Sampling naturally adapts exploration based on uncertainty
- Provably optimal (Bayesian regret bound)  
- No hyperparameter tuning needed (ε in epsilon-greedy needs careful selection)

### 5. Why Bilingual in Same Row?

**Decision**: English and Hindi columns in the same CSV row, not separate rows  
**Why**: 
- One template_id maps to one message (in two languages)
- Schedule generator picks one template, then the notification system selects the language at delivery time based on user preference
- Avoids duplicate template IDs and inflated template counts
- Cleaner for A/B testing — you're testing the *message concept*, not the language

### 6. Why Config-Driven Thresholds?

**Decision**: All thresholds in `config/config.yaml`  
**Why**: 
- Change once, applied everywhere
- Makes the system domain-agnostic (swap config for fintech or health)
- PS evaluators can easily verify our thresholds match requirements
- Prevents magic numbers scattered across 17 files

### 7. Why Not Use an LLM for Template Generation?

**Decision**: Rule-based template generation with predefined content patterns  
**Why**:
- PS requires "explainable & reproducible" — LLM outputs vary between runs
- No API key dependency — system runs fully offline
- "Hardcoded outputs" isn't a problem when the hardcoding is in the *generation rules*, not the outputs
- A real production system would use an LLM, but for this evaluation, determinism > creativity

---

## 10. Common Questions & Answers

### Q: "What if the evaluator gives us a completely different user CSV?"

The system handles this gracefully:
- `DataValidator` adds defaults for missing columns
- `DataIngestionEngine` only requires `user_id` as a mandatory column
- Segmentation adapts to whatever features exist
- Templates are generated for whatever segments emerge
- The pipeline won't crash — it will produce reasonable output with whatever data it receives

### Q: "What if there are only 100 users?"

Works fine. The segmentation engine enforces `min_segment_size: 0.05` (5%), so with 100 users, each segment has at least 5 users. The clustering algorithms work with any sample size ≥ K.

### Q: "What makes this 'domain-agnostic'?"

Three things:
1. **Knowledge Bank**: All domain-specific intelligence comes from the KB text. Change the text from "SpeakX English Learning" to "HealthTrack Fitness App" and the system auto-adapts
2. **Config-driven**: Thresholds are in YAML, not code
3. **Feature engineering**: The `DataIngestionEngine` dynamically finds `feature_*_used` columns — add new features to the CSV and they're automatically incorporated

### Q: "How do we know the learning is real and not mock?"

The Delta Report proves it:
1. Every change has a specific `metric_trigger` (e.g., "CTR=0.031")
2. Every change has `before_value` and `after_value` (verifiable)
3. Every change has a causal `explanation` (not just "removed because bad")
4. The improved outputs differ from original outputs in measurable ways
5. Both iteration0 and iteration1 pipelines run end-to-end without errors

### Q: "What happens if experiment_results.csv has templates not in our system?"

They're safely ignored. The bandit engine only processes template IDs that match its internal state. Unknown template IDs are skipped during update.

### Q: "Why do we need both LearningEngine and MultiArmedBanditEngine?"

They serve different purposes:
- **LearningEngine**: Applies broad, rule-based improvements (suppress BAD, promote GOOD, adjust timing/themes/frequency) — makes system-wide decisions
- **MultiArmedBanditEngine**: Does fine-grained, probabilistic template ranking — optimizes which individual template to send next

The `main.py` iteration1 pipeline uses both in sequence: the bandit identifies winners/losers, then the filtering logic applies those decisions.

### Q: "What's the difference between timing_recommendations.csv and timing_recommendations_improved.csv?"

- `timing_recommendations.csv`: Generated in Iteration 0 based only on user behavioral patterns (preferred_hour distributions)
- `timing_recommendations_improved.csv`: Generated in Iteration 1 using actual experiment performance data (CTR, engagement, uninstall rates per window)

The "_improved" version reflects what the system *learned* from real data.

### Q: "How does the schedule show 'gradual journey progression'?"

The `GoalBuilder` assigns different goals for different lifecycle days:
- Day 0 (D0): activation (get them started)
- Day 1 (D1): habit_formation (get them back)
- Day 3 (D3): feature_discovery (explore more)
- Day 7 (D7): conversion_push (convert to paid)

The `ScheduleGenerator` maps each schedule day to the appropriate lifecycle day, so notifications on Day 0 focus on activation while Day 3 notifications focus on feature discovery. This is visible in the schedule output.

### Q: "What does the 'composite_score' in timing_recommendations mean?"

```
composite_score = CTR × 0.5 + engagement_rate × 0.4 - uninstall_rate × 5.0
```

- CTR gets 50% weight (did they click?)
- Engagement gets 40% weight (did they actually do something after clicking?)
- Uninstall gets a heavy negative penalty (5×) — even a small uninstall rate tanks the score
- This ensures we never optimize for clicks at the cost of uninstalls

### Q: "What libraries are used and why?"

| Library | Version | Purpose |
|---------|---------|---------|
| pandas | ≥1.5 | Data manipulation and CSV I/O |
| numpy | ≥1.24 | Numerical computation |
| scikit-learn | ≥1.3 | Clustering, preprocessing, TF-IDF |
| xgboost | ≥2.0 | Churn prediction model |
| lightgbm | ≥4.0 | Engagement prediction model |
| scipy | ≥1.11 | Statistical distributions and tests |
| lifelines | ≥0.27 | Survival analysis (Kaplan-Meier) |
| PyYAML | ≥6.0 | Configuration file parsing |

All specified in `requirements.txt`.

---

*This guide covers every aspect of Project Aurora's design, implementation, and theory. For hands-on usage instructions, see the Presentation & Workflow Guide.*
