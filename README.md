# Project Aurora — Self-Learning Notification Orchestrator

**Domain-Generic ML-Powered Communication System**  
*(Dynamically adaptable to any business domain via RAG-lite Knowledge Bank)*

---

## Overview

Project Aurora is a **prototype self-learning notification orchestrator** built to intelligently optimize user communication through a two-iteration pipeline. It is designed to be domain-agnostic — swap the Knowledge Bank PDF and it adapts to any B2C product.

Core capabilities:
- **Domain Adaptability**: RAG-lite Knowledge Bank (PDF → LLM → TF-IDF) learns product context
- **Machine Learning Models**: XGBoost churn prediction, LightGBM engagement forecasting
- **Multi-Armed Bandit Learning**: Thompson Sampling for continuous template optimization
- **Advanced Segmentation**: RFM-based hierarchical clustering with automatic K selection
- **Statistical Testing**: Bayesian + Frequentist A/B testing (Cohen's h effect size)
- **NLP**: Sentiment analysis, TF-IDF vectorization, engagement scoring
- **Survival Analysis**: Kaplan-Meier time-to-event modeling for timing optimization

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
|   |   |-- user_data_sample.csv
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
    `-- experiment_generator.py  # Synthetic experiment generation
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

**46 tests, no API key or network required.** The suite deliberately targets the parts of the
system where a silent bug would be most expensive:

| File | Tests | What it pins down |
|---|---|---|
| `tests/test_ml_leakage.py` | 11 | Leakage guard flags target-derived features; the model recovers a *planted* signal but scores ~0 on a random target |
| `tests/test_bandit.py` | 18 | Beta-posterior arithmetic, incremental updates, credible intervals tightening with evidence, exploration vs exploitation, state round-trip |
| `tests/test_statistical_testing.py` | 17 | Bayesian decisions, two-proportion z-test, Cohen's h against its closed form, sample-size monotonicity, cross-method agreement |

The leakage tests are the important ones: they assert that a random target scores `R² < 0.3`
*and* that a genuine relationship still scores `R² > 0.75`. Together those two bounds are what
make the honest metrics above trustworthy rather than just pessimistic.

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

### Metrics after the guard (1,000-row synthetic sample, seed 42)

Reproduced from the committed `data/output/ml_model_performance.csv`:

| Model | Metric | Value | Interpretation |
|---|---|---|---|
| Churn (XGBoost) | Test AUC | 0.429 | No signal — labels are near-random vs behaviour |
| Churn (XGBoost) | 5-fold CV AUC | 0.474 ± 0.039 | Confirms no signal |
| Engagement (LightGBM) | R² | -0.005 | No signal — no better than predicting the mean |
| Engagement (LightGBM) | RMSE | 278.3 | On a target ranging 0–1000 |

These numbers are **the honest result of removing leakage**, and they are expected: in
`data/sample/user_data_sample.csv`, `lifecycle_stage` is drawn independently of the
behavioural columns, so there is no learnable relationship for either model to find. A model
that scored well here would be evidence of a bug, not of skill.

The ML layer should therefore be read as **validated plumbing** — correct feature assembly,
class-imbalance handling, early stopping, cross-validation, persistence and a leakage guard —
that is ready for a dataset with real signal. `tests/test_ml_leakage.py` proves the pipeline
*does* recover a relationship when one genuinely exists.

The substantive contributions of this project are in the **learning loop** (Thompson-sampling
bandit, dual Bayesian/frequentist gating, delta reporting) and the **domain-agnostic
ingestion layer**, not in the propensity scores.

---

## Limitations

- **No real-world dataset.** Everything ships against a synthetic 1,000-user sample; no
  production traffic has ever flowed through this system.
- **Propensity models have no signal on the sample data** (see the table above). Do not
  extrapolate these metrics.
- **Bandit and A/B results are computed over synthetic experiment outcomes** generated by
  `src/utils/experiment_generator.py`, so "winners" reflect that generator's assumptions.
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
