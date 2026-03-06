# Project Aurora — Presentation & Workflow Guide

## Everything You Need to Demo, Present, and Answer Questions

---

## Table of Contents

1. [Pre-Presentation Setup](#1-pre-presentation-setup)
2. [Running the System — Step by Step](#2-running-the-system--step-by-step)
3. [Live Demo Script](#3-live-demo-script)
4. [What to Say at Each Step](#4-what-to-say-at-each-step)
5. [Output Walkthrough — What to Show](#5-output-walkthrough--what-to-show)
6. [Handling Evaluator Questions](#6-handling-evaluator-questions)
7. [Troubleshooting Common Issues](#7-troubleshooting-common-issues)
8. [Key Numbers to Remember](#8-key-numbers-to-remember)
9. [Talking Points & Vocabulary](#9-talking-points--vocabulary)
10. [Emergency Scenarios](#10-emergency-scenarios)

---

## 1. Pre-Presentation Setup

### Environment Setup (Do This Before the Demo)

```bash
# 1. Navigate to the project directory
cd d:\Projects\Arora

# 2. Ensure Python 3.10+ is installed
python --version

# 3. Install dependencies (if not already done)
pip install -r requirements.txt

# 4. Verify all sample data exists
dir data\sample\
# Should show: user_data_sample.csv, experiment_results_sample.csv

# 5. Verify config exists
dir config\
# Should show: config.yaml

# 6. Test a quick run (do this 30 minutes before demo)
python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv
```

### Pre-Demo Checklist

- [ ] Python 3.10+ installed and working
- [ ] All pip dependencies installed (no import errors)
- [ ] `data/sample/user_data_sample.csv` exists (500 users)
- [ ] `data/sample/experiment_results_sample.csv` exists
- [ ] `config/config.yaml` exists with correct thresholds
- [ ] Terminal window open and ready
- [ ] Have the output folder (`data/output/`) cleared or ready to overwrite
- [ ] **Test both iteration0 AND iteration1 before the demo**

### If the Evaluator Provides Their Own Data

The system is designed to accept any CSV with at least a `user_id` column. If the evaluator provides:
- **Their own user CSV**: Use it directly — the system handles missing columns gracefully
- **Their own KB text**: Place it as `pdf_content.txt` in the root directory, or the system will use a default
- **Their own experiment results**: Use with `--experiment-results` flag in iteration1

---

## 2. Running the System — Step by Step

### Iteration 0 (Before Learning)

This is the "cold start" — the system generates all intelligence from raw data.

```bash
python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv
```

**What Happens (10 sequential steps)**:

| Step | Engine | Output | Time |
|------|--------|--------|------|
| 1 | Knowledge Bank | north_star.json, feature_goal_map.json, tone_hook_matrix.json | ~2s |
| 2 | Data Ingestion | Validated + feature-engineered user data | ~1s |
| 3 | Segmentation | user_segments.csv (6-12 MECE segments) | ~3s |
| 4 | ML Models | XGBoost churn + LightGBM engagement models | ~5s |
| 5 | Goal Builder | segment_goals.csv | ~1s |
| 6 | Theme Engine | communication_themes.csv | ~1s |
| 7 | Templates + NLP | message_templates.csv + NLP analysis | ~3s |
| 8 | Timing | timing_recommendations.csv + frequencies | ~2s |
| 9 | Schedules | user_notification_schedule.csv | ~3s |
| 10 | Bandit Init | bandit_state.json (Beta(1,1) priors) | ~1s |

**Total Iteration 0 runtime**: ~20-30 seconds

### Iteration 1 (After Learning)

This is the "learning loop" — the system ingests experiment results and improves.

```bash
python main.py --mode iteration1 --user-data data/sample/user_data_sample.csv --experiment-results data/sample/experiment_results_sample.csv
```

**What Happens (8 sequential steps)**:

| Step | Engine | Output | What It Proves |
|------|--------|--------|---------------|
| 1 | Performance Classifier | experiment_results.csv | Templates classified as GOOD/NEUTRAL/BAD |
| 2 | Statistical Testing | statistical_analysis.csv | Bayesian + Frequentist validation |
| 3 | Multi-Armed Bandit | template_rankings.csv | Thompson Sampling rankings |
| 4 | NLP Optimizer | nlp_recommendations.csv | Feature-performance correlations |
| 5 | Timing Re-optimization | timing_improved.csv | Experiment-based timing |
| 6 | Template Filtering | templates_improved.csv | Losers suppressed, winners promoted |
| 7 | Delta Report | learning_delta_report.csv | Every change documented |
| 8 | Improved Schedule | schedule_improved.csv | Schedule using learned outputs |

**Total Iteration 1 runtime**: ~15-25 seconds

---

## 3. Live Demo Script

### Phase 1: Iteration 0 Demo (10-12 minutes)

**Opening Statement** (30 seconds):
> "Project Aurora is a self-learning notification orchestrator. It's designed to solve the fundamental problem in user communication: knowing who to talk to, what to say, when to say it, and learning from every interaction. Let me show you how it works."

**Run Iteration 0** (let it run while narrating):

```bash
python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv
```

While it runs, explain each step as it appears in the terminal output.

**After it completes, show outputs**:

1. **Open `user_segments.csv`** → Show segments with propensity scores
2. **Open `communication_themes.csv`** → Show Octalysis theme assignments with rationale
3. **Open `message_templates.csv`** → Show bilingual templates (EN + HI) with tone/hook
4. **Open `timing_recommendations.csv`** → Show time windows ranked by expected performance
5. **Open `user_notification_schedule.csv`** → Show per-user 7-day schedule

**Key Points to Highlight**:
- "Each segment has unique propensity scores — gamification, social, AI tutor, leaderboard, and churn risk"
- "Templates are bilingual — English and Hindi in the same row, ready for A/B testing"
- "The schedule shows journey progression — Day 0 is about activation, Day 3 is about feature discovery"

### Phase 2: Iteration 1 Demo (8-10 minutes)

**Transition** (15 seconds):
> "Now imagine we've deployed these notifications and collected experiment results. Let me show you what happens when the system learns."

**Run Iteration 1**:

```bash
python main.py --mode iteration1 --user-data data/sample/user_data_sample.csv --experiment-results data/sample/experiment_results_sample.csv
```

**After it completes, show the learning**:

1. **Open `learning_delta_report.csv`** → This is the star of the show
   - Show template suppressions with CTR/engagement metrics
   - Show template promotions with statistical confidence
   - Show timing changes based on experiment data

2. **Open `message_templates_improved.csv`** → Compare row count with original
   - "See — bad templates are gone, good templates have weight 2.0"

3. **Open `timing_recommendations_improved.csv`** → Compare with original
   - "Timing is now based on actual experiment data, not just behavioral patterns"

4. **Show the terminal summary**:
   - Templates Suppressed: X
   - Templates Promoted: Y
   - These are real numbers based on Bayesian credible intervals

**Closing Statement** (30 seconds):
> "Every decision is documented with causal reasoning. The system doesn't just change — it explains why it changed. And the architecture is domain-agnostic: swap the Knowledge Bank and user data, and this same orchestrator works for fintech, healthtech, or any B2C application."

---

## 4. What to Say at Each Step

### Step 1: Knowledge Bank
> "The Knowledge Bank Engine ingests unstructured company documentation and automatically extracts three things: the North Star metric, a feature-to-goal map, and a tone-hook matrix based on the Octalysis behavioral framework. It uses regex-based NLP with multi-strategy fallbacks — try explicit extraction first, then heuristic inference, then domain-specific defaults."

### Step 2: Data Ingestion
> "We load the user behavioral data, validate it, handle missing values, and engineer six key features: activeness score, gamification propensity, social propensity, AI tutor propensity, leaderboard propensity, and churn risk. Each is a weighted composite of normalized behavioral signals."

### Step 3: Segmentation
> "We create mutually exclusive segments using a two-layer approach: first RFM analysis to establish a behavioral baseline, then agglomerative hierarchical clustering with Ward's linkage for the final segmentation. We automatically select the optimal K between 6 and 12 using silhouette scores and Davies-Bouldin index."

### Step 4: ML Models
> "We train two gradient-boosted models: an XGBoost classifier for churn prediction using binary classification with AUC evaluation, and a LightGBM regressor for engagement propensity with early stopping. Both are cross-validated with 5 folds."

### Step 5: Goal Builder
> "Each segment gets a lifecycle journey — trial users go from activation on Day 0, to habit formation on Day 1, to feature discovery by Day 3, and conversion push by Day 7. Paid users progress from retention to expansion to advocacy."

### Step 6: Theme Engine
> "We map Octalysis core drives to segments based on their behavioral profile. High churn risk segments get 'loss avoidance' — show them what they'll lose. High gamification users get 'accomplishment' — celebrate their progress. Each mapping has a documented rationale."

### Step 7: Template Generator
> "For every Segment × Lifecycle × Goal × Theme combination, we generate exactly 5 bilingual templates. Each has an English title, Hindi title, English body, Hindi body, English CTA, Hindi CTA, plus tone, hook, and feature reference. This creates a rich A/B test surface."

### Step 8: Timing Optimizer
> "We optimize across 6 time windows using survival analysis on user behavioral patterns. Frequency is determined by activeness: 8/day for high engagement users, 6 for medium, 4 for low. Plus there's a hard guardrail — if any segment's uninstall rate exceeds 2%, we automatically cut frequency by 2 per day."

### Step 9: Schedule Generator
> "We create a personalized 7-day notification schedule for each user, sampling from their segment's templates and assigning optimal time slots. The schedule shows gradual journey progression."

### Step 10: Bandit Initialization
> "We initialize a Thompson Sampling multi-armed bandit for every template with a uniform Beta(1,1) prior. This is the starting point for Iteration 1's learning."

### Iteration 1 Steps

**Performance Classification**:
> "We classify each experiment result using PS-defined thresholds: GOOD requires both CTR above 15% and engagement above 40%. BAD triggers if either CTR is below 5% or engagement is below 20%. Note the asymmetry — we're conservative about calling something good but aggressive about catching bad ones."

**Statistical Testing**:
> "We run both Bayesian A/B tests using Beta-posterior Monte Carlo sampling and Frequentist two-proportion z-tests. The combined verdict requires agreement from both — STRONG WINNER needs both frequentist significance and Bayesian probability above 95%."

**Multi-Armed Bandit**:
> "We update all bandit posteriors from experiment data. Winners are templates whose 95% credible interval lower bound exceeds the good CTR threshold. Losers have their upper bound below the bad threshold. This is much more rigorous than just looking at raw CTR."

**Delta Report**:
> "Every single change is documented with all 7 required fields: entity type, entity ID, change type, metric trigger, before value, after value, and a causal explanation. This is the proof that the learning is real."

---

## 5. Output Walkthrough — What to Show

### Priority Order (Show These First)

1. **`learning_delta_report.csv`** — The most important file. Shows learning happened.
2. **`user_segments.csv`** — Show the quality of segmentation (propensity scores, segment names)
3. **`message_templates.csv`** — Show bilingual templates with personalization tokens
4. **`user_notification_schedule.csv`** — Show the per-user schedules with journey progression
5. **`timing_recommendations.csv`** → `timing_recommendations_improved.csv` — Before/after comparison

### What to Point Out in Each File

**user_segments.csv**:
- Multiple propensity columns (activeness, gamification, social, ai_tutor, leaderboard, churn_risk)
- Meaningful segment names (not just "Cluster 0")
- RFM scores and segments

**message_templates.csv**:
- Bilingual columns: `message_title_en`, `message_title_hi`, `message_body_en`, `message_body_hi`
- Personalization tokens like `{exercises_completed_7d}`, `{streak_current}`
- Tone and hook fields
- 5 variants per combo (filter by segment_id + lifecycle_stage + goal)

**learning_delta_report.csv**:
- `change_type`: suppression vs promotion
- `metric_trigger`: actual CTR and engagement numbers
- `explanation`: causal reasoning ("Bandit analysis: Consistently underperformed...")

**timing_recommendations.csv**:
- 6 time windows per segment
- `composite_score` showing the ranking formula
- `optimization_method`: "behavioral_pattern" (Iter 0) vs "experiment_learned" (Iter 1)

---

## 6. Handling Evaluator Questions

### Architecture & Design Questions

**Q: "Why did you use hierarchical clustering instead of K-Means?"**
> "Hierarchical clustering with Ward's linkage is deterministic — same data always gives the same result, meeting the reproducibility requirement. It also produces more balanced segment sizes than K-Means, which can create very small clusters."

**Q: "How is this domain-agnostic?"**
> "Three ways: First, all domain-specific knowledge comes from the Knowledge Bank text — change the input text and the system adapts. Second, all thresholds are in config.yaml, not hardcoded. Third, the feature engineering dynamically detects feature columns in the CSV. Swap the data and KB, keep the same pipeline."

**Q: "What happens if we give you different data right now?"**  
> "The system will work. It only strictly requires a user_id column. Missing columns get default values. The segmentation adapts to whatever features exist. Templates generate for whatever segments emerge."

### ML & Algorithm Questions

**Q: "Explain Thompson Sampling."**
> "Each template starts with a Beta(1,1) prior — we know nothing. When we observe clicks and non-clicks, we update: alpha increases by clicks, beta by non-clicks. To select, we sample from each template's Beta distribution and pick the highest. High-CTR templates get sampled high on average — that's exploitation. Uncertain templates have wide distributions and occasionally sample very high — that's exploration. It naturally balances both without tuning."

**Q: "What's the difference between Bayesian and Frequentist A/B testing?"**
> "Frequentist asks 'if there's no difference, what's the probability of seeing this data?' — it gives p-values. Bayesian asks 'given the data, what's the probability Treatment is better?' — it gives direct probability statements. We use both — when they agree, we have strong evidence."

**Q: "Why XGBoost for churn and LightGBM for engagement?"**
> "XGBoost is strong for binary classification with class imbalance — common in churn prediction where most users don't churn. LightGBM is faster for regression and handles continuous targets like engagement scores better, thanks to leaf-wise growth. Using both demonstrates understanding of when to apply each."

**Q: "What is survival analysis doing here?"**
> "Survival analysis models time-to-event — originally 'time to death' in medicine. We adapted it to 'time to engagement' — how quickly users click after receiving a notification in each time window. Windows where engagement happens fastest are ranked higher. We use the Kaplan-Meier estimator from the lifelines library."

### Performance & Learning Questions

**Q: "How do you know the learning is real?"**
> "Open learning_delta_report.csv. Every change has a metric_trigger with real numbers, before and after values, and a causal explanation. Templates are suppressed because their Bayesian credible interval upper bound falls below the 5% CTR threshold — not because of an arbitrary rule."

**Q: "What's the uninstall guardrail?"**  
> "If any segment's uninstall rate exceeds 2%, we reduce their notification frequency by 2 per day regardless of their activeness score. This is in config.yaml — uninstall_threshold: 0.02, uninstall_reduction: 2. It's applied both in initial timing optimization and in the learning loop."

**Q: "What are the performance thresholds?"**
> "GOOD: CTR above 15% AND engagement above 40% — both must be true. BAD: CTR below 5% OR engagement below 20% — either is sufficient. These are from the PS and configured in config.yaml. The asymmetry is intentional — conservative for 'good' calls, aggressive for 'bad' catches."

**Q: "What is the composite score?"**
> "composite_score = CTR × 0.5 + engagement_rate × 0.4 - uninstall_rate × 5.0. CTR gets 50% weight, engagement 40%, and uninstall gets a 5× negative penalty. A tiny uninstall rate can tank the score — this ensures we never optimize clicks at the cost of user loss."

### Technical Deep Dive Questions

**Q: "What is Cohen's h?"**
> "It's an effect size measure for comparing two proportions: h = 2×arcsin(√p₁) - 2×arcsin(√p₂). The arcsin transformation stabilizes variance. Effect sizes below 0.2 are small, 0.2-0.8 medium, above 0.8 large. We use it alongside the z-test to know not just if there's a difference, but how big it is."

**Q: "Explain the Beta distribution."**
> "Beta(α, β) is a probability distribution defined on [0, 1] — perfect for modeling CTR which is a probability. Mean is α/(α+β). As α+β increases, the distribution narrows — we become more confident. It's a conjugate prior to the Binomial likelihood, meaning the posterior is also Beta — just add observed successes and failures to α and β. No complex math needed."

**Q: "What is O'Brien-Fleming alpha spending?"**
> "In sequential testing, we want to check results multiple times without inflating false positives. O'Brien-Fleming spends very little of the 0.05 error budget in early checks and saves most for the final analysis. This makes it hard to stop early but very powerful at the final check. It's ideal for our scenario where we want rigorous final conclusions."

**Q: "How does the NLP optimizer work?"**
> "For each template, we compute: word count, average word length, sentiment score from a custom lexicon, engagement keyword density, urgency score, personalization token count, and emoji/number presence. We also create TF-IDF bigram vectors for cosine similarity search. When paired with experiment data, we correlate these features with CTR to discover what linguistic patterns drive engagement."

---

## 7. Troubleshooting Common Issues

### Issue: "ModuleNotFoundError"

```bash
# Solution: Install missing dependency
pip install <module-name>

# Or reinstall all:
pip install -r requirements.txt
```

### Issue: "lifelines" Warning

The system may show a warning about the `lifelines` library. This is expected — the system gracefully falls back to behavioral pattern analysis if survival analysis isn't available. It does NOT affect output quality.

### Issue: "No data/output directory"

```bash
# The system creates it automatically, but if needed:
mkdir data\output
```

### Issue: Terminal Encoding (Windows)

If you see garbled characters (emojis), the system handles this automatically via UTF-8 encoding in `main.py`. If it persists:
```bash
# Set terminal encoding
chcp 65001
```

### Issue: Iteration 1 Fails

```bash
# Make sure iteration0 was run first (it generates required files)
python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv

# Then run iteration1
python main.py --mode iteration1 --user-data data/sample/user_data_sample.csv --experiment-results data/sample/experiment_results_sample.csv
```

### Issue: Output Files Look Different from Expected

All output files are in `data/output/`. The exact number of segments, templates, and schedule entries depends on the input data. With the sample data (500 users), expect:
- 6-12 segments
- 500+ templates
- 100 users in the schedule (configurable via `max_users`)

---

## 8. Key Numbers to Remember

### Thresholds (From PS)

| What | Value | Where |
|------|-------|-------|
| Good CTR threshold | >15% | config.yaml → performance.good_ctr |
| Good Engagement threshold | >40% | config.yaml → performance.good_engagement |
| Bad CTR threshold | <5% | config.yaml → performance.bad_ctr |
| Bad Engagement threshold | <20% | config.yaml → performance.bad_engagement |
| Uninstall guardrail | >2% → -2/day | config.yaml → frequency.uninstall_threshold |

### Frequency Rules

| Activeness | Notifs/Day | Config Key |
|-----------|-----------|------------|
| > 0.7 | 8 | high_activeness_freq |
| 0.4 – 0.7 | 6 | medium_activeness_freq |
| < 0.4 | 4 | low_activeness_freq |
| Trial bonus | +1 | trial_bonus |
| Churned override | 2 | churned_freq |

### Time Windows (6 total)

| Window | Hours |
|--------|-------|
| early_morning | 06:00 – 08:59 |
| mid_morning | 09:00 – 11:59 |
| afternoon | 12:00 – 14:59 |
| late_afternoon | 15:00 – 17:59 |
| evening | 18:00 – 20:59 |
| night | 21:00 – 23:59 |

### Architecture Numbers

| What | Count |
|------|-------|
| Source files | 17 Python files |
| Total lines of code | ~3,800 |
| ML models trained | 2 (XGBoost + LightGBM) |
| Bandit algorithms | 2 (Thompson Sampling + UCB) |
| Statistical tests | 3 (Bayesian, Frequentist, Sequential) |
| Octalysis core drives | 8 |
| Propensity scores per user | 6 |
| Template variants per combo | 5 |
| Languages per template | 2 (English + Hindi) |
| Delta report fields | 7 |
| Deliverable output files | 12 |

### Evaluation Weights (From PS)

| Dimension | Weight |
|-----------|--------|
| System completeness | 15% |
| Segmentation quality | 15% |
| Messaging intelligence | 25% |
| Timing & frequency | 10% |
| Learning & evolution | 25% |
| Extensibility | 5% |
| Presentation | 5% |

**Focus Areas**: Messaging Intelligence (25%) and Learning & Evolution (25%) together are 50% of the grade. Make sure to spend time showing template quality and the delta report.

---

## 9. Talking Points & Vocabulary

### Terms You Should Use Naturally

- **"Self-learning system"** — not "rules-based" or "hardcoded"
- **"MECE segments"** — Mutually Exclusive, Collectively Exhaustive (every user in exactly one segment)
- **"Propensity scores"** — not "scores" or "numbers"
- **"Octalysis core drives"** — not "themes" alone
- **"Thompson Sampling"** — not "random selection"
- **"Credible intervals"** (Bayesian) — not "confidence intervals" (Frequentist)
- **"Conjugate prior"** — Beta distribution is conjugate to Binomial likelihood
- **"Composite score"** — when discussing timing rankings
- **"Ward's linkage"** — when discussing clustering
- **"Gradient-boosted trees"** — when discussing XGBoost/LightGBM
- **"Survival analysis"** — not "timing analysis"
- **"Causal reasoning"** — when discussing the delta report
- **"Domain-agnostic"** — when discussing extensibility

### Strong Opening Lines

- "Aurora replaces rule-based notification systems with a self-learning orchestrator..."
- "The key insight is that different users respond to different psychological drives..."
- "Every decision is backed by statistical evidence — Bayesian credible intervals, not gut feel..."
- "The system demonstrates measurable improvement between Iteration 0 and Iteration 1..."

### Strong Closing Lines

- "The architecture is domain-agnostic — swap the Knowledge Bank and this works for any B2C application"
- "Every change is documented with causal reasoning — the delta report proves the learning is real"
- "We combine behavioral psychology, statistical rigor, and machine learning into one coherent system"

---

## 10. Emergency Scenarios

### Scenario: The System Crashes Mid-Demo

1. **Stay calm**. Read the error message.
2. Most likely causes: missing file, wrong path, or import error
3. Fix and re-run. The system is idempotent — re-running won't break anything
4. If it keeps crashing, show the output files from a previous run (they're still in `data/output/`)

### Scenario: Evaluator Asks Something You Don't Know

Options:
- "That's a great question. The relevant code is in [specific file] — let me show you." (Buy time while looking at the code)
- "Our current implementation handles this in [module]. Here's the approach..." (Redirect to what you know)
- Be honest if you genuinely don't know a theoretical question — "I'd need to look deeper into the literature on that specific aspect, but here's how we applied the relevant concept..."

### Scenario: Evaluator Provides a Completely Different CSV

This is expected. The system handles it:
1. Run with their CSV: `python main.py --mode iteration0 --user-data <their_file.csv>`
2. Missing columns get defaults
3. Segments will be different (expected — different data, different segments)
4. Templates will be generated for whatever segments emerge
5. If it crashes, check the CSV format (must have `user_id` column)

### Scenario: Output Numbers Look "Wrong"

The outputs depend entirely on input data. With different user data:
- Segment count may differ (6-12, determined by silhouette score)
- Template count depends on number of segments × lifecycles × goals × themes × 5
- Timing recommendations depend on user `preferred_hour` distribution
- This is correct behavior — the system adapts to data

### Scenario: Evaluator Says "This Looks Hardcoded"

Point them to:
1. **Segmentation**: "Run with different data and you get different segments — the clustering is real ML"
2. **Timing**: "Change config.yaml thresholds and the timing output changes"
3. **Learning Delta**: "The delta report shows specific CTR values from experiment data — these numbers come from the data, not from code"
4. **Templates**: "Templates reference segment-specific themes chosen by the Octalysis mapping — change the segments and you get different themes"

### Scenario: "Can You Change a Threshold and Re-Run?"

This is a great opportunity:
1. Open `config/config.yaml`
2. Change `good_ctr: 0.15` to `good_ctr: 0.20` (or whatever they suggest)
3. Re-run iteration1
4. Show the delta report — different templates will be classified differently
5. "See — the system is fully config-driven"

---

## Appendix: Full Command Reference

```bash
# Iteration 0 — Generate all outputs from raw data
python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv

# Iteration 1 — Learn and improve from experiment results
python main.py --mode iteration1 \
  --user-data data/sample/user_data_sample.csv \
  --experiment-results data/sample/experiment_results_sample.csv

# Using custom data (evaluator provides files)
python main.py --mode iteration0 --user-data <path_to_user_csv>
python main.py --mode iteration1 \
  --user-data <path_to_user_csv> \
  --experiment-results <path_to_experiment_csv>

# Help
python main.py --help
```

---

## Appendix: File-to-Concept Quick Map

| If They Ask About... | Show This File |
|----------------------|----------------|
| How segmentation works | `src/intelligence/segmentation.py` |
| How scores are calculated | `src/utils/metrics.py` |
| How templates are generated | `src/communication/template_generator.py` |
| How timing optimization works | `src/communication/timing_optimizer.py` |
| How the bandit learns | `src/learning/multi_armed_bandit.py` |
| How statistical testing works | `src/learning/statistical_testing.py` |
| How learning is applied | main.py iteration1 pipeline (line 240+) |
| How the delta report is generated | `src/learning/delta_reporter.py` |
| What thresholds are used | `config/config.yaml` |
| How the KB extracts intelligence | `src/knowledge_bank/kb_engine.py` |

---

*Review this guide thoroughly before the presentation. Run both iterations at least once beforehand. Know where every output file is and what it contains. If you understand the "why" behind each component, answering questions becomes natural.*
