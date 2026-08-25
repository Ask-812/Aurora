# Project Aurora: Final Presentation & Demo Guide

This guide will help you structure your final presentation and successfully demonstrate the end-to-end capabilities of the newly unified, domain-generic Project Aurora.

## 🎯 What Makes This Final Version Stand Out
1. **Domain-Generic RAG-lite KB Engine**: Project Aurora is no longer hardcoded to EdTech/SpeakX! It uses a RAG pipeline (PDF → Semantic chunking → LLM → TF-IDF ranking) to contextually understand ANY domain (FinTech, E-commerce, Health, etc.) entirely from the provided Knowledge Bank PDF. All LLM calls go through a circuit breaker with exponential backoff and rate-limit retry.
2. **LLM-Driven Schema Mapping**: The Data Ingestion Engine uses an LLM to dynamically map CSV columns to semantic roles (user_id, lifecycle_stage, activeness_metrics, value_metrics, feature_flags) — no hardcoded column names. Falls back to heuristic matching when LLM is unavailable.
3. **Dynamic Bilingual Templates**: Message templates dynamically generate English and Hinglish titles/bodies by injecting the specific features identified by the KB Engine.
4. **Advanced ML & Statistics**: XGBoost Churn (with behavioral lifecycle_stage target, no circular leakage) / LightGBM Engagement modeling, Kaplan-Meier Survival Analysis for timing, 6-12 dynamic MECE segmentation via Hierarchical Clustering, and Multi-Armed Bandit Learning.
5. **KB-Driven Goals**: Goal Builder derives feature names from the Knowledge Bank (`feature_goal_map.json`), not hardcoded strings.
6. **Full Output Suite**: Generates the deliverables — segments, goals, themes, bilingual templates, timing/frequency, schedules, plus the learning-loop outputs (statistical analysis, bandit rankings, delta report) — in `data/output/`.

---

## 🚀 How to Run the Demo

The system is designed to run in two distinct "Iterations", mirroring real-world deployment: Initial Strategy Generation (Day 0) and Feedback Learning (Day 1+).

### Prerequisites
Before presenting, ensure you have set up the environment:
```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. (Optional but Recommended) Set Groq API Key for the RAG-lite LLM feature
export GROQ_API_KEY="your_groq_api_key_here"
```
*(Note: If no API key is provided, the system gracefully falls back to a Regex-based knowledge extraction method.)*

### 1. Run Iteration 0 (Initialization & Strategy)
Run this command to simulate user data ingestion, ML model training, and the generation of the initial communication strategy.

**Command:**
```bash
python main.py --mode iteration0 --user-data data/sample/user_data_sample.csv --kb-pdf data/input/knowledge_bank.pdf
```

**What happens & what to highlight:**
*   **Knowledge Bank Extraction**: Replaces manual rule-setting. Point out how the system uses the LLM (with circuit breaker fallback) to identify the "North Star Metric" and feature-to-goal mappings directly from the `knowledge_bank.pdf`. Saves `kb_metadata.json` with the detected domain.
*   **LLM Schema Mapping**: The data ingestion engine dynamically maps CSV columns to semantic roles using the LLM, making it work with any dataset schema.
*   **Segmentation (K=6-12)**: Shows RFM + Hierarchical Clustering generating segments with distinct attributes.
*   **ML Models**: XGBoost churn uses `lifecycle_stage` as a behavioral target (no circular leakage). On this small synthetic sample the churn AUC is ≈0.5 (near chance — essentially no usable signal), so lean on the engagement model and the learning loop rather than the churn AUC. LightGBM engagement uses dynamic feature columns.
*   **Template Generation**: Explain that the bilingual templates (≈600 on the sample run; the count scales with segments × lifecycle × goal × theme × 5 variants) are not hardcoded but constructed dynamically using the features extracted by the KB Engine.
*   **Timing Optimization**: Describe how Kaplan-Meier Survival Analysis (via lifelines) determines the optimal notification windows.

**Expected Key Output Files (`data/output/`):**
*   `user_segments.csv`
*   `message_templates.csv`
*   `user_notification_schedule.csv`
*   `segment_goals.csv`

### 2. Run Iteration 1 (Learning & Optimization)
Run this command to simulate the system ingesting experiment results (e.g., actual CTRs and engagement data), learning from them, and generating an improved strategy.

**Command:**
```bash
python main.py --mode iteration1 --user-data data/sample/user_data_sample.csv --experiment-results data/sample/experiment_results_sample.csv
```

**What happens & what to highlight:**
*   **Bayesian Statistical Testing**: The system analyzes the experiment results to find statistically significant winners.
*   **Multi-Armed Bandit (MAB)**: Show how the system adjusts the weights of templates based on their real-world performance.
*   **Delta Reporting**: A massive differentiator. Show the `learning_delta_report.csv` which clearly documents *what* the system changed and *why* (e.g., "Suppressed template TPL_0123 because CTR was < 5%").
*   **Improved Schedule**: An optimized schedule is outputted for the next cycle.

**Expected Key Output Files (`data/output/`):**
*   `learning_delta_report.csv` (Crucial for proving the system "learned")
*   `message_templates_improved.csv`
*   `user_notification_schedule_improved.csv`
*   `bandit_learning_report.csv`

---

## ✅ Deliverable Checklist Verification

During your presentation, point out that the deliverables are generated in the `data/output/` directory (and mirrored to the `iteration_0_before_learning/` and `iteration_1_after_learning/` folders for submission).

| Category | File | Verified |
| :--- | :--- | :---: |
| **System/Model** | `models/churn_model.pkl` | ✅ |
| | `models/engagement_model.pkl` | ✅ |
| | `ml_model_performance.csv` | ✅ |
| | `bandit_state.json` | ✅ |
| **Strategy Outputs** | `user_segments.csv` (All 6 propensities!) | ✅ |
| | `segment_goals.csv` | ✅ |
| | `message_templates.csv` (Domain-Generic, EN+HI) | ✅ |
| | `communication_themes.csv` | ✅ |
| | `timing_recommendations.csv` | ✅ |
| | `frequency_recommendations.csv` | ✅ |
| | `user_notification_schedule.csv` | ✅ |
| **Knowledge Engine** | `company_north_star.json` | ✅ |
| | `feature_goal_map.json` | ✅ |
| | `allowed_tone_hook_matrix.json` | ✅ |
| **Learning/Iteration**| `learning_delta_report.csv` | ✅ |
| | `experiment_results.csv` | ✅ |
| | `message_templates_improved.csv` | ✅ |
| | `user_notification_schedule_improved.csv`| ✅ |

Good luck with the presentation! Know where each output file is and what it contains, and be ready to explain the "why" behind each component — that's what makes the demo convincing.
