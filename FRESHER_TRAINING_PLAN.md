# Project Aurora - Fresher Training Plan (Phase-wise)

This plan is designed to guide freshers from zero to productive contributors. Each phase includes what to teach, exact deliverables, and acceptance checks.

## Phase 0 - Orientation (Day 1)
### Teach
- Project overview: What the system does and why it matters.
- Problem statement requirements: deliverables, constraints, evaluation criteria.
- Repo layout: `src/`, `data/`, `config/`, `tests/`.

### Work to Assign
- Read the README and QUICK_START guide.
- Identify 3 project goals and 3 non-negotiable constraints in a 1-page summary.

### Deliverables
- 1-page summary: goals, constraints, and core outputs.

### Acceptance Checks
- Summary includes task 1/2/3 deliverables.
- Mentions domain-agnostic requirement and learning loop.

---

## Phase 1 - Setup and Tooling (Day 2)
### Teach
- Python environment setup, dependencies, and running scripts.
- Input/output file expectations (CSV/JSON).
- Basic Git workflow: branch, commit, push.

### Work to Assign
- Set up local environment and run iteration 0 and iteration 1.
- Verify outputs exist in `data/output/`.

### Deliverables
- Screenshot or log snippet showing successful runs.
- List of generated files and a brief description of each.

### Acceptance Checks
- Both runs complete without errors.
- Outputs match required file names.

---

## Phase 2 - Data Prep and Validation (Days 3-4)
### Teach
- Input CSV schema: required columns and types.
- Data quality checks: missing values, invalid ranges, outliers.
- Feature engineering basics: activeness, propensities, churn risk.

### Work to Assign
- Review `src/intelligence/data_ingestion.py`.
- Create a data validation checklist from code.
- Add 3 unit tests for schema validation and missing data handling.

### Deliverables
- Validation checklist (1-2 pages).
- New tests in `tests/` with clear assertions.

### Acceptance Checks
- Tests cover required columns, type checks, and range checks.
- Tests pass locally.

---

## Phase 3 - Segmentation and Clustering (Days 5-7)
### Teach
- RFM analysis: meaning, scoring, and why it is used.
- Clustering basics: K-means vs hierarchical clustering.
- Metrics: silhouette score, Davies-Bouldin.

### Work to Assign
- Read `src/intelligence/segmentation.py`.
- Explain in their own words how optimal K is selected.
- Add a small script to visualize cluster metrics.

### Deliverables
- 1-page explanation of segmentation flow.
- Plot of silhouette and Davies-Bouldin vs K.

### Acceptance Checks
- Explanation covers RFM, feature scaling, and clustering choice.
- Plots generated and interpretable.

---

## Phase 4 - ML Propensity Models (Days 8-10)
### Teach
- Supervised learning basics: classification vs regression.
- XGBoost for churn, LightGBM for engagement.
- Model evaluation: AUC, RMSE, R2.

### Work to Assign
- Review `src/intelligence/ml_propensity_models.py`.
- Train models on sample data and report metrics.
- Write a short note on top 3 features per model.

### Deliverables
- Metrics report (AUC, RMSE, R2).
- Feature importance note.

### Acceptance Checks
- Metrics match or are close to sample run output.
- Feature importance discussed clearly.

---

## Phase 5 - Themes and Templates (Days 11-13)
### Teach
- Octalysis 8 Core Drives and how they map to segments.
- Template generation: 5 variants per combination.
- Bilingual output structure.

### Work to Assign
- Review `src/communication/theme_engine.py` and `template_generator.py`.
- Verify counts: 5 templates per segment x lifecycle x goal.
- Add a validator to confirm correct counts.

### Deliverables
- Count validation script.
- Short explanation of theme selection logic.

### Acceptance Checks
- Script confirms expected template counts.
- Explanation references Octalysis themes properly.

---

## Phase 6 - NLP Analysis (Days 14-15)
### Teach
- TF-IDF basics and why it is used.
- Simple sentiment scoring approach.
- How NLP features relate to CTR.

### Work to Assign
- Review `src/communication/nlp_template_optimizer.py`.
- Generate NLP analysis outputs.
- Identify 3 insights from NLP correlations.

### Deliverables
- NLP output files.
- 3 insights from analysis (1 page).

### Acceptance Checks
- Outputs created successfully.
- Insights tie to actual metrics.

---

## Phase 7 - Timing and Frequency (Days 16-18)
### Teach
- Time windows definition and mapping.
- Frequency rules by activeness and guardrails.
- How schedule generation works.

### Work to Assign
- Review `src/communication/timing_optimizer.py` and `schedule_generator.py`.
- Create a table that maps activeness ranges to frequency.
- Verify guardrail reduction logic.

### Deliverables
- Frequency rules table.
- Short note on guardrail application.

### Acceptance Checks
- Table matches PS specification.
- Guardrail logic explained correctly.

---

## Phase 8 - Learning Loop and Evaluation (Days 19-21)
### Teach
- Performance classification rules (GOOD/NEUTRAL/BAD).
- Bayesian vs frequentist testing basics.
- Multi-armed bandit overview and Thompson sampling.

### Work to Assign
- Review `src/learning/performance_classifier.py`, `statistical_testing.py`, `multi_armed_bandit.py`.
- Run iteration 1 and compare metrics to iteration 0.
- Explain how suppression/promotion happens.

### Deliverables
- Comparison summary (iteration 0 vs 1).
- Explanation of one suppressed and one promoted template.

### Acceptance Checks
- Summary shows measurable delta.
- Explanation references thresholds and decisions.

---

## Phase 9 - End-to-End Integration (Days 22-24)
### Teach
- Full pipeline flow from input to output.
- Data dependencies between modules.
- Failure points and error handling.

### Work to Assign
- Draw a dataflow diagram for the pipeline.
- Identify 5 potential failure modes and fixes.

### Deliverables
- Dataflow diagram (image or markdown). 
- Failure modes list with fixes.

### Acceptance Checks
- Diagram matches actual pipeline steps.
- Fixes are realistic and actionable.

---

## Phase 10 - Ownership and Handoff (Days 25-27)
### Teach
- Code reading and explaining to others.
- How to write clean PRs and commit messages.
- Documentation standards.

### Work to Assign
- Present a 15-minute walkthrough of the system.
- Submit a small PR with a clear improvement (test or doc).

### Deliverables
- Presentation notes.
- PR link with review summary.

### Acceptance Checks
- Presentation explains architecture clearly.
- PR is clean, focused, and reviewed.

---

## Suggested Weekly Cadence
- Daily 30-45 min lecture or whiteboard session.
- Daily 2-4 hours hands-on work.
- End of week review: 30 min demo + Q and A.

---

## Tracking Template (per fresher)
- Phase: 
- Assigned tasks:
- Delivered:
- Issues:
- Mentor feedback:
- Next steps:

---

## Final Outcome
At the end, each fresher should be able to:
- Run the full pipeline.
- Explain all core concepts and design choices.
- Identify issues and propose fixes.
- Contribute code with tests and documentation.
