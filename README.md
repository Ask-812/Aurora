# Project Aurora — Self-Learning Notification Orchestrator

[![CI](https://github.com/Ask-812/Aurora/actions/workflows/ci.yml/badge.svg)](https://github.com/Ask-812/Aurora/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-67%20passing-brightgreen.svg)](tests/)

**Domain-Generic ML-Powered Communication System**  
*(Dynamically adaptable to any business domain via RAG-lite Knowledge Bank)*

---

## Overview

Project Aurora is a **prototype self-learning notification orchestrator** that optimises who
gets messaged, when, with what copy, and how often — then learns from the outcome and
re-optimises. It is domain-agnostic: swap the Knowledge Bank PDF and it re-targets to another
B2C product without a code change.

Core capabilities:
- **Domain Adaptability**: RAG-lite Knowledge Bank (PDF → LLM → TF-IDF) learns product context
- **Machine Learning Models**: XGBoost churn prediction, LightGBM engagement forecasting
- **Multi-Armed Bandit Learning**: Thompson Sampling for continuous template optimization
- **Advanced Segmentation**: RFM-based hierarchical clustering with automatic K selection
- **Statistical Testing**: Bayesian + Frequentist A/B testing (Cohen's h effect size)
- **NLP**: Sentiment analysis, TF-IDF vectorization, engagement scoring
- **Survival Analysis**: Kaplan-Meier time-to-event modeling for timing optimization

### How the models are validated

Model quality is reported against a **synthetic benchmark with a written-down data generating
process** (`src/utils/data_generator.py`), so every score can be compared to the best score
that is theoretically attainable:

| Dataset | Churn AUC | Engagement R² | What it shows |
|---|---|---|---|
| `user_data_sample.csv` (bundled sample) | 0.403 | −0.000 | Labels are independent of behaviour — **no signal exists**, and the models correctly find none |
| `user_data_benchmark.csv` (known DGP) | **0.817** | **0.268** | The same code recovers the planted structure |
| *Oracle ceiling for that DGP* | *0.854* | *0.534* | Best possible score given the latent traits |

The churn model reaches **96% of the oracle ceiling**. Running both datasets is what makes
either number meaningful: near-chance on the first *and* strong on the second is the signature
of a correct, leakage-free pipeline. Strong scores on both would mean the leakage guard has a
hole.

```bash
python scripts/benchmark_models.py   # reproduces the table above
```

> An earlier revision of this README reported engagement `R² = 0.94`. That number was
> **target leakage** and has been removed. See [Model Validation](#model-validation--honest-metrics).

---

## Quick Start

### Installation

```bash
git clone https://github.com/Ask-812/Aurora.git
cd Aurora
pip install -r requirements.txt
```

### Run the System

```bash
# 1. Create a .env file with your Groq API key(s)
#    Supports round-robin rotation — add multiple keys to avoid rate limits
echo "GROQ_API_KEY_1=gsk_your_key_here" > .env
echo "GROQ_API_KEY_2=gsk_second_key_here" >> .env  # optional
echo "GROQ_API_KEY_3=gsk_third_key_here" >> .env   # optional

# 2. Iteration 0: Initial Training & Intelligence Generation (reads PDF)
python main.py --mode iteration0 \
  --user-data data/sample/user_data_sample.csv \
  --kb-pdf data/input/knowledge_bank.pdf

# 3. Iteration 1: Learning from Experiments & Optimization
python main.py --mode iteration1 \
  --user-data data/sample/user_data_sample.csv \
  --experiment-results data/sample/experiment_results_sample.csv
```

---

## System Architecture

```
INPUT LAYER
- Knowledge Bank (.pdf or .txt) processed by RAG-lite engine
- User Data (behavioral, demographic, engagement)
- Experiment Results (performance feedback)

INTELLIGENCE LAYER
- RFM analysis -> recency, frequency, monetary scoring
- Feature engineering -> 10+ behavioral dimensions
- Hierarchical clustering -> optimal K selection
- XGBoost churn model -> individual risk prediction
- LightGBM engagement -> future activity forecasting

COMMUNICATION LAYER
- Theme mapping -> Octalysis 8 Core Drives
- Template generation -> 5 variants x segment x lifecycle x goal x theme
- NLP analysis -> sentiment, engagement, TF-IDF
- Timing optimization -> survival analysis + experiments
- Frequency tuning -> dynamic with uninstall guardrails

LEARNING LAYER
- Multi-armed bandit -> Thompson Sampling (Beta priors)
- Statistical testing -> Bayesian + Frequentist dual
- Winner detection -> 95% credible-interval bounds vs CTR thresholds
- Template filtering -> suppress bad, promote good
- Delta reporting -> explainable changes with causality

OUTPUT LAYER
- Optimized user segments with propensity scores
- Personalized notification schedules
- Template rankings with confidence intervals
- Timing recommendations per segment x lifecycle
- Learning delta reports with causal explanations
```

---

## Project Structure

```
Aurora/
|-- main.py                      # ML orchestrator (iteration0 + iteration1)
|-- requirements.txt             # Python dependencies
|-- README.md                    # Project documentation
|-- SOLUTION_GUIDE.md            # Technical architecture guide
|-- walkthrough.md               # Quick walkthrough
|-- config/
|   `-- config.yaml              # System configuration
|-- data/
|   |-- input/                   # User uploads (knowledge_bank.pdf)
|   |-- sample/                  # Sample datasets
|   |   |-- user_data_sample.csv        # original sample (no learnable signal)
|   |   |-- user_data_benchmark.csv     # generated from a known DGP
|   |   `-- experiment_results_sample.csv
|   `-- output/                  # Generated outputs
|       |-- [Knowledge Bank]
|       |   |-- company_north_star.json
|       |   |-- feature_goal_map.json
|       |   |-- allowed_tone_hook_matrix.json
|       |   `-- kb_metadata.json
|       |-- [Intelligence]
|       |   |-- user_segments.csv
|       |   |-- segment_goals.csv
|       |   |-- ml_model_performance.csv
|       |   `-- models/
|       |       |-- churn_model.pkl
|       |       `-- engagement_model.pkl
|       |-- [Communication]
|       |   |-- communication_themes.csv
|       |   |-- message_templates.csv
|       |   |-- timing_recommendations.csv
|       |   |-- frequency_recommendations.csv
|       |   `-- user_notification_schedule.csv
|       `-- [Learning Outputs]
|           |-- bandit_state.json
|           |-- statistical_analysis.csv
|           |-- template_rankings_bandit.csv
|           |-- bandit_learning_report.csv
|           |-- templates_nlp_analysis.csv
|           |-- nlp_recommendations.csv
|           |-- message_templates_improved.csv
|           |-- timing_recommendations_improved.csv
|           |-- frequency_recommendations_improved.csv
|           |-- user_notification_schedule_improved.csv
|           |-- experiment_results.csv
|           `-- learning_delta_report.csv
`-- src/
  |-- llm_utils.py               # LLM retry, circuit breaker, rate-limit handling
  |-- knowledge_bank/
  |   `-- kb_engine.py           # RAG-lite KB (PDF → LLM → TF-IDF)
  |-- intelligence/
  |   |-- data_ingestion.py      # Dynamic schema mapping (LLM + fallback)
  |   |-- segmentation.py        # RFM + hierarchical clustering
  |   |-- goal_builder.py        # KB-driven goal building
  |   `-- ml_propensity_models.py # XGBoost churn + LightGBM engagement
  |-- communication/
  |   |-- theme_engine.py        # Octalysis theme mapping
  |   |-- template_generator.py  # Bilingual template generation (LLM + fallback)
  |   |-- nlp_template_optimizer.py # NLP analysis & optimization
  |   |-- timing_optimizer.py    # Survival analysis timing optimization
  |   `-- schedule_generator.py  # User schedule generation
  |-- learning/
  |   |-- multi_armed_bandit.py  # Thompson Sampling MAB
  |   |-- statistical_testing.py # Bayesian + Frequentist A/B testing
  |   |-- performance_classifier.py # GOOD/NEUTRAL/BAD classification
  |   `-- delta_reporter.py      # Explainable delta reporting
  `-- utils/
    |-- metrics.py               # Scoring functions
    |-- validation.py            # Data quality checks
    |-- data_generator.py        # Ground-truth DGP + oracle ceilings
    `-- experiment_generator.py  # Synthetic experiment generation

scripts/
`-- benchmark_models.py          # Signal-free vs known-signal comparison

tests/                           # 67 pytest tests
|-- test_data_generator.py
|-- test_bandit.py
|-- test_statistical_testing.py
`-- test_ml_leakage.py

.github/workflows/
`-- ci.yml                       # pytest + full pipeline + benchmark on every push
```

---

## Core Technologies

### Machine Learning Stack

- **XGBoost 2.0**: Gradient boosting for churn prediction
  - Behavioral churn target derived from `lifecycle_stage` (no circular leakage)
  - `scale_pos_weight` for class imbalance handling
  - Feature importance tracking and cross-validation support

- **LightGBM 4.0**: Fast gradient boosting for engagement forecasting
  - Early stopping to prevent overfitting
  - Trained and evaluated on synthetic sample data *(see Limitations)*

- **scikit-learn 1.3**: Clustering, preprocessing, metrics
  - Hierarchical clustering (Ward linkage)
  - StandardScaler normalization
  - Silhouette score + Davies-Bouldin + elbow for K selection

### Statistical Framework

- **SciPy 1.11**: Statistical functions
  - Beta distributions for Bayesian inference
  - Two-proportion z-tests
  - Confidence interval calculations

- **Thompson Sampling**: Multi-Armed Bandit algorithm
  - Beta(α, β) posteriors per template, updated incrementally
  - 95% credible intervals per template
  - Balances exploration and exploitation automatically

### NLP & Text Analytics

- **TF-IDF Vectorization**: Template similarity analysis
- **Custom Sentiment Lexicons**: Domain-specific scoring
- **Engagement Keywords**: Pattern recognition for CTR drivers

---

## Key Design Decisions

### 1. Domain-Generic RFM Adaptation

Traditional RFM focuses on monetary value. Aurora adapts it for any engagement domain:

- **Recency**: How recently the user was active (dynamically resolved via schema mapping)
- **Frequency**: Engagement frequency metric (resolved from dataset columns)
- **Monetary**: Engagement value composite (activeness × open rate × motivation)

Schema mapping is done via LLM — no hardcoded column names. Falls back to heuristic column matching when LLM is unavailable.

**Result**: Business-aligned segments whose names are generated dynamically. When the LLM is available it assigns domain-aware names (e.g., a recent sample run produced *Social Gamifiers*, *Engaged Socialites*, *Core Feature Fans*); the deterministic fallback labels segments by behavioral profile (*Power Users*, *Active Users*, *Social Engagers*, *At-Risk Users*, *Needs Attention*). A separate `rfm_segment` column holds the classic RFM bucket (Champions / Loyal / … / Lost).

### 2. Multi-Armed Bandit with Thompson Sampling

Instead of fixed A/B tests, we use Bayesian bandits:

```python
# For each template
alpha = successes + 1
beta = failures + 1

# Sample from Beta posterior
reward_sample = Beta(alpha, beta).sample()

# Select template with highest sample
best_template = argmax(samples)
```

**Why**: Reduces regret during exploration; no fixed sample-size commitment needed upfront.

### 3. Composite Timing Score

Scoring function for timing optimization:

```
score = CTR × 0.5 + Engagement × 0.4 - Uninstall × 5.0
```

Heavy uninstall penalty ensures sustainable growth over short-term CTR maximization.

### 4. Dual Statistical Validation

Every template is evaluated by both:
- **Bayesian**: P(treatment > control) with credible intervals
- **Frequentist**: p-value, effect size (Cohen's h)

A template is marked `STRONG_WINNER` only if both agree (p < 0.05 AND P > 0.95).

### 5. Individual-Level Personalization

Beyond segment-level rules:
- ML propensity scores per user
- Churn risk: P(churn | user_features)
- Engagement forecast: E[activity | user_history]

---

## Deliverables Checklist

### Task 1: System Architecture & Intelligence

- [x] `company_north_star.json` — North Star metric with drivers
- [x] `feature_goal_map.json` — Feature → goal mappings
- [x] `allowed_tone_hook_matrix.json` — Tones x Octalysis hooks
- [x] `user_segments.csv` — MECE segments with RFM scores
- [x] `segment_goals.csv` — Goal definitions per segment × lifecycle × day
- [x] **BONUS**: `ml_model_performance.csv` — XGBoost/LightGBM metrics
- [x] **BONUS**: Trained ML models (`churn_model.pkl`, `engagement_model.pkl`)

### Task 2: Communication & Timing

- [x] `communication_themes.csv` — Theme mappings per segment × lifecycle (≈24 rows on the sample run)
- [x] `message_templates.csv` — Bilingual templates (EN + HI)
- [x] `timing_recommendations.csv` — Ranked time windows per segment × lifecycle
- [x] `timing_recommendations_improved.csv` — Re-ranked time windows (post-learning)
- [x] `user_notification_schedule.csv` — Per-user schedules (first 100 users, via `max_users`)
- [x] **BONUS**: `frequency_recommendations.csv` — Dynamic frequency per segment
- [x] **BONUS**: `templates_nlp_analysis.csv` — Sentiment, engagement scores

### Task 3: Execution & Learning

- [x] `experiment_results_sample.csv` — Template performance data
- [x] `learning_delta_report.csv` — Explainable changes
- [x] `message_templates_improved.csv` — Post-learning templates
- [x] `timing_recommendations_improved.csv` — Re-optimized timing
- [x] Complete runnable codebase (`main.py`)
- [x] `README.md` — This document
- [x] **BONUS**: `statistical_analysis.csv` — Bayesian + Frequentist tests
- [x] **BONUS**: `template_rankings_bandit.csv` — MAB rankings with CI
- [x] **BONUS**: `bandit_state.json` — Persistent learning state
- [x] **BONUS**: `nlp_recommendations.csv` — Actionable template improvements

---

## Demo Flow

### Phase 1: Iteration 0

```bash
python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv --kb-pdf data/input/knowledge_bank.pdf
```

**System demonstrates**:
1. RAG-lite KB extraction (PDF → LLM → TF-IDF, ~25 domain terms)
2. LLM-based dynamic schema mapping with heuristic fallback
3. RFM Analysis + Hierarchical Clustering (6–12 MECE segments)
4. XGBoost churn model training on behavioral target
5. LightGBM engagement model training
6. KB-driven goal building per segment × lifecycle
7. Bilingual template generation (EN + HI)
8. NLP analysis: sentiment, engagement scoring
9. Kaplan-Meier survival analysis for timing optimization
10. Schedule generation (100 users × 7 days)
11. Auto-generated experiment results for iteration 1

**Outputs**: 15+ files in `data/output/`

### Phase 2: Iteration 1

```bash
python main.py --mode iteration1 \
  --user-data data/sample/user_data_sample.csv \
  --experiment-results data/sample/experiment_results_sample.csv
```

**System demonstrates**:
1. Performance classification (GOOD / NEUTRAL / BAD)
2. Bayesian A/B tests with credible intervals
3. MAB update: Beta posteriors from experiment data
4. Winner identification: 95% CI lower bound > 15% CTR threshold
5. Loser suppression: 95% CI upper bound < 5% CTR threshold
6. Timing re-optimization via composite scoring
7. NLP recommendations (shorten, add urgency, etc.)
8. Delta report: explained changes per template

---

## Sample Outputs

### Segment Distribution

```
MECE segments identified via optimal-K Silhouette selection.
Segment names are generated dynamically, so they vary per dataset/run:

  With LLM (domain-aware), a sample run produced:
    Social Gamifiers, Engaged Socialites, Core Feature Fans,
    Passive Explorers, Casual Solo Users, Low Activity Risks
  Deterministic fallback (no LLM) labels by behavioral profile:
    Power Users, Active Users, Social Engagers, At-Risk Users, Needs Attention
```

Exact segment count (K=6–12) is auto-selected to maximize Silhouette score, so both
the number of segments and their names change with the input data.

### Template Rankings (Post-Learning)

```
Template TPL_0042: "Day 5 streak! Complete today's exercise"
  CTR: 18.7% (95% CI: [16.5%, 21.0%])   # lower bound > 15% good threshold
  Status: WINNER
  Action: PROMOTE (weight = 2.0)

Template TPL_0089: "Practice now"
  CTR: 3.2% (95% CI: [1.8%, 4.6%])       # upper bound < 5% bad threshold
  Status: LOSER
  Action: SUPPRESS
```

### Learning Delta Example

```
Entity: Template TPL_0042
Type: Promotion
Metric: CTR=0.187, Engagement=0.423
Change: weight: 1.0 -> 2.0
Reason: Bayesian analysis shows P(better than average) = 0.97.
        Frequentist test: p=0.001 (significant).
        Promotes habit formation through streak reinforcement.
```

---

## Configuration

Edit `config/config.yaml` to customize:

```yaml
segmentation:
  n_clusters: 8              # Initial K (auto-optimized within the range below)
  min_clusters: 6            # Minimum K considered
  max_clusters: 12           # Maximum K considered
  min_segment_size: 0.05     # Fraction of users (5%), not an absolute count
  random_state: 42

performance:
  good_ctr: 0.15             # CTR threshold for GOOD
  good_engagement: 0.40
  bad_ctr: 0.05              # CTR threshold for BAD
  bad_engagement: 0.20
  min_sends_significance: 100

time_windows:
  early_morning: [6, 9]
  mid_morning: [9, 12]
  afternoon: [12, 15]
  late_afternoon: [15, 18]
  evening: [18, 21]
  night: [21, 24]
```

> See `config/config.yaml` for the full set (frequency rules, tone matrices, knowledge-bank
> settings). ML hyperparameters live in `src/intelligence/ml_propensity_models.py` and the
> statistical-test defaults (`alpha=0.05`, `power=0.8`) in `src/learning/statistical_testing.py`;
> they are not read from `config.yaml`.

---

## Testing

```bash
pip install -r requirements.txt
pytest -q
```

**67 tests, no API key or network required.** The suite targets the parts of the system where
a silent bug would be most expensive:

| File | Tests | What it pins down |
|---|---|---|
| `tests/test_data_generator.py` | 21 | The DGP emits the claimed structure, hides its latents, is seed-reproducible; the pipeline recovers planted signal but cannot exceed the oracle ceiling; the bundled sample really is signal-free |
| `tests/test_bandit.py` | 18 | Beta-posterior arithmetic, incremental updates, credible intervals tightening with evidence, exploration vs exploitation, state round-trip |
| `tests/test_statistical_testing.py` | 17 | Bayesian decisions, two-proportion z-test, Cohen's h against its closed form, sample-size monotonicity, cross-method agreement |
| `tests/test_ml_leakage.py` | 11 | Leakage guard flags target-derived features; a random target scores ~0 while a planted signal still scores well |

The leakage and ceiling tests are the important ones. They bound the models from **both**
sides: a random target must score `R² < 0.3`, a planted signal must score `R² > 0.75`, and a
churn AUC above 0.95 fails the suite as implausible for sampled labels. Together those bounds
are what make the reported metrics trustworthy rather than merely flattering or merely
pessimistic.

### Benchmarking the models

```bash
python scripts/benchmark_models.py                 # both datasets + oracle ceilings
python -m src.utils.data_generator --n-users 5000  # regenerate the benchmark dataset
```

### Running the pipeline

```bash
# Iteration 0 — train models and generate intelligence (also writes the experiment sample)
python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv

# Iteration 1 — learn from experiment outcomes and re-optimise
python main.py --mode iteration1 \
  --user-data data/sample/user_data_sample.csv \
  --experiment-results data/sample/experiment_results_sample.csv
```

Both modes run fully offline. With a `GROQ_API_KEY` present, schema mapping, segment naming
and template copy become domain-aware; without one they fall back to deterministic rules.

**Requirements**:
- User data CSV/XLSX (missing required columns are auto-filled with safe defaults for demo runs)
- Experiment results CSV for iteration 1 — produced by iteration 0, or see the schema in `SOLUTION_GUIDE.md`

---

## Model Validation & Honest Metrics

The two propensity models are **structurally complete but have no predictive signal on the
bundled synthetic sample**, and the README reports that openly rather than quoting a
flattering number.

### Target leakage was found and fixed

An earlier revision reported engagement `R² = 0.94`. That figure was **target leakage**, not
performance:

- the engagement target is `sum(value_metrics)`, which resolves to `coins_balance`
- the feature `gamification_propensity` is a normalised blend of `value_metrics + feature_flags`

so the model was predicting `coins_balance` from a rescaled copy of `coins_balance`.

`PropensityModelEngine._derived_features_using()` now walks a
feature-to-schema-role dependency map, detects any engineered feature computed from the
target's own source columns, and drops it before training:

```
[Guard] Excluded 1 leakage-prone feature(s): gamification_propensity
```

### Metrics after the guard

Reproduced by `python scripts/benchmark_models.py` and committed to
`data/output/model_benchmark.csv`:

| Dataset | Churn AUC | Churn CV AUC | Engagement R² | Engagement RMSE |
|---|---|---|---|---|
| Original sample (no signal by construction) | 0.403 | 0.484 | −0.000 | 277.6 |
| Ground-truth benchmark (known DGP) | **0.817** | 0.740 | **0.268** | 3.74 |
| *Oracle ceiling* | *0.854* | — | *0.534* | — |

**Why the first row is near chance, and why that is correct.** In
`data/sample/user_data_sample.csv`, `lifecycle_stage` is drawn independently of every
behavioural column. There is no relationship to learn, so a model scoring well there would be
evidence of a bug. `tests/test_data_generator.py::TestOriginalSampleHasNoSignal` pins this
claim, so it cannot quietly become false.

**Why the second row is the real evidence.** `src/utils/data_generator.py` builds users from
two latent traits (`engagement`, `diligence`) that drive every observable, then *samples*
churn from a logistic model on those latents. Because churn is sampled rather than computed,
even an oracle holding the true probabilities tops out at AUC 0.854 — so 0.817 is **96% of
what is attainable**, and anything near 1.0 would prove leakage rather than skill.

The engagement target, `engagement_next_7d`, is drawn for the *following* week and is excluded
from every feature matrix — including the churn model's, where using it would be time-travel
leakage. Its R² ceiling is only 0.534 because the target is a Poisson count whose variance is
mostly irreducible noise; the model uses a Poisson objective to match that noise structure.

### Reproducibility

Feature columns are assembled with `sorted(set(...))` rather than `list(set(...))`. Python
randomises string hashing per process, so the unsorted version silently reordered the feature
matrix between runs and produced different AUCs from the same seed. Repeated runs of
`scripts/benchmark_models.py` are now byte-identical.

### What the ML layer is, honestly

Correct, leakage-guarded, reproducible plumbing — feature assembly, class-imbalance handling,
early stopping, cross-validation, Poisson objective for count targets, and persistence — that
**demonstrably learns when signal is present**. The substantive contributions of this project
are the **learning loop** (Thompson-sampling bandit, dual Bayesian/frequentist gating, delta
reporting) and the **domain-agnostic ingestion layer**, not the propensity scores themselves.

---

## Limitations

- **No real-world dataset.** Everything ships against synthetic data; no production traffic has
  ever flowed through this system. The benchmark proves the code is correct, not that the
  product works.
- **The benchmark is self-authored.** `data_generator.py` defines the process the models are
  then measured against. That validates implementation correctness, not real-world accuracy.
- **Bandit and A/B results are computed over synthetic experiment outcomes** generated by
  `src/utils/experiment_generator.py`, so reported "winners" reflect that generator's
  assumptions. The ~42% CTR improvement printed by iteration 1 is therefore **circular and
  should not be quoted as a result.**
- **Timing model** fits and evaluates on the same behavioural window; it has no holdout.
- **Prototype status.** No authentication, no persistent database, no horizontal scaling, no
  production monitoring.
- **LLM-dependent paths degrade, they do not fail.** Without a Groq key the system runs fully
  offline on deterministic fallbacks; segment names and templates are then rule-based rather
  than domain-aware.


---

## Technical Documentation

For in-depth understanding of algorithms, theory, and implementation details, see [SOLUTION_GUIDE.md](SOLUTION_GUIDE.md).

---

## License & Usage

This project is submitted as part of the Kriti Assessment 2026 for SpeakX Project Aurora.

**Implementation**: February–March 2026  
**Technology Stack**: Python 3.13, XGBoost 2.0, LightGBM 4.0, scikit-learn 1.3, lifelines (Kaplan-Meier), Groq LLM (llama-3.3-70b)  
**Status**: Functional prototype with circuit breaker, graceful LLM degradation, and domain-agnostic design
