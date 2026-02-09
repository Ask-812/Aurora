# SYSTEM ARCHITECTURE GUIDE
## Project Aurora - Self-Learning Notification Orchestrator

---

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  • Knowledge Bank (PDF/Text/Markdown)                           │
│  • User Data CSV (behavioral, demographic, psychographic)       │
│  • Experiment Results CSV (performance metrics)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE LAYER (Task 1)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │  Knowledge Bank      │      │  User Data           │        │
│  │  Engine              │      │  Ingestion Engine    │        │
│  │                      │      │                      │        │
│  │  • Extract North Star│      │  • Validate schema   │        │
│  │  • Map features      │      │  • Clean data        │        │
│  │  • Define tones      │      │  • Handle missing    │        │
│  └──────────────────────┘      └──────────────────────┘        │
│              │                            │                     │
│              └────────────┬───────────────┘                     │
│                           ▼                                     │
│              ┌──────────────────────┐                           │
│              │  Segmentation Engine │                           │
│              │                      │                           │
│              │  • Feature engineer  │                           │
│              │  • Cluster (K-means) │                           │
│              │  • Calculate scores  │                           │
│              │  • Ensure MECE       │                           │
│              └──────────────────────┘                           │
│                           │                                     │
│                           ▼                                     │
│              ┌──────────────────────┐                           │
│              │  Goal & Journey      │                           │
│              │  Builder             │                           │
│              │                      │                           │
│              │  • Define goals      │                           │
│              │  • Map to lifecycle  │                           │
│              │  • Create progression│                           │
│              └──────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 COMMUNICATION LAYER (Task 2)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │  Theme Engine        │      │  Template Generator  │        │
│  │                      │      │                      │        │
│  │  • Map Octalysis     │      │  • Generate variants │        │
│  │  • Segment matching  │      │  • Personalize       │        │
│  │  • Lifecycle adjust  │      │  • Bilingual support │        │
│  └──────────────────────┘      └──────────────────────┘        │
│              │                            │                     │
│              └────────────┬───────────────┘                     │
│                           ▼                                     │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │  Timing Optimizer    │      │  Frequency Optimizer │        │
│  │                      │      │                      │        │
│  │  • Analyze windows   │      │  • Calculate based   │        │
│  │  • Segment-specific  │      │    on activeness     │        │
│  │  • Learn from data   │      │  • Apply guardrails  │        │
│  └──────────────────────┘      └──────────────────────┘        │
│              │                            │                     │
│              └────────────┬───────────────┘                     │
│                           ▼                                     │
│              ┌──────────────────────┐                           │
│              │  Schedule Generator  │                           │
│              │                      │                           │
│              │  • User-wise plans   │                           │
│              │  • Journey alignment │                           │
│              │  • Time distribution │                           │
│              └──────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING LAYER (Task 3)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │  Performance         │      │  Learning Engine     │        │
│  │  Classifier          │      │                      │        │
│  │                      │      │  • Suppress BAD      │        │
│  │  • Analyze CTR       │      │  • Promote GOOD      │        │
│  │  • Analyze engagement│      │  • Optimize timing   │        │
│  │  • Classify templates│      │  • Adjust frequency  │        │
│  └──────────────────────┘      └──────────────────────┘        │
│              │                            │                     │
│              └────────────┬───────────────┘                     │
│                           ▼                                     │
│              ┌──────────────────────┐                           │
│              │  Delta Reporter      │                           │
│              │                      │                           │
│              │  • Document changes  │                           │
│              │  • Causal reasoning  │                           │
│              │  • Measure improvement│                          │
│              └──────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  • All JSON/CSV deliverables                                    │
│  • Iteration 0 outputs (before learning)                        │
│  • Iteration 1 outputs (after learning)                         │
│  • Delta report (measurable improvements)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Iteration 0 (Before Learning)

```
Knowledge Bank (PDF)
        │
        ▼
   [KB Engine]
        │
        ├─→ company_north_star.json
        ├─→ feature_goal_map.json
        └─→ allowed_tone_hook_matrix.json
        
User Data (CSV)
        │
        ▼
   [Validation]
        │
        ▼
   [Feature Engineering]
        │
        ├─→ activeness_score
        ├─→ gamification_propensity
        ├─→ social_propensity
        └─→ churn_risk
        │
        ▼
   [Clustering]
        │
        └─→ user_segments.csv
        
Segments + KB
        │
        ▼
   [Goal Builder]
        │
        └─→ segment_goals.csv
        
Segments + Goals + KB
        │
        ▼
   [Theme Engine]
        │
        └─→ communication_themes.csv
        
Themes + Segments + Goals
        │
        ▼
   [Template Generator]
        │
        └─→ message_templates.csv (5 per segment/goal/theme, bilingual)
        
User Data + Segments
        │
        ▼
   [Timing Optimizer]
        │
        └─→ timing_recommendations.csv
        
User Data + Segments + Templates + Timing
        │
        ▼
   [Schedule Generator]
        │
        └─→ user_notification_schedule.csv
```

---

## Data Flow: Iteration 1 (After Learning)

```
experiment_results.csv
        │
        ▼
   [Performance Classifier]
        │
        ├─→ GOOD templates (CTR > 15%, Engagement > 40%)
        ├─→ NEUTRAL templates (5-15% CTR, 20-40% Engagement)
        └─→ BAD templates (CTR < 5% OR Engagement < 20%)
        │
        ▼
   [Learning Engine]
        │
        ├─→ [Template Suppression]
        │   │
        │   └─→ Remove BAD templates
        │
        ├─→ [Template Promotion]
        │   │
        │   └─→ Increase weight of GOOD templates
        │
        ├─→ [Timing Optimization]
        │   │
        │   └─→ Suppress underperforming windows
        │       Promote high-performing windows
        │
        ├─→ [Theme Refinement]
        │   │
        │   └─→ Update primary themes based on performance
        │
        └─→ [Frequency Adjustment]
            │
            └─→ Reduce if uninstall_rate > 2%
        │
        ▼
   [Updated Components]
        │
        ├─→ message_templates.csv (filtered, weighted)
        ├─→ timing_recommendations.csv (optimized)
        ├─→ communication_themes.csv (refined)
        └─→ frequency_map (adjusted)
        │
        ▼
   [Schedule Generator]
        │
        └─→ user_notification_schedule.csv (IMPROVED)
        │
        ▼
   [Delta Calculator]
        │
        ├─→ CTR improvement
        ├─→ Engagement improvement
        ├─→ Uninstall rate reduction
        └─→ Template count changes
        │
        ▼
   [Delta Reporter]
        │
        └─→ learning_delta_report.csv
            (entity, change, trigger, before, after, explanation)
```

---

## Component Interfaces

### Knowledge Bank Engine

**Input:**
- Company documentation (text/PDF/markdown)

**Output:**
```json
{
  "north_star": {...},
  "features": [...],
  "tones": [...],
  "hooks": [...]
}
```

**Key Methods:**
- `extract_north_star(text) → dict`
- `extract_features(text) → list`
- `extract_tones(text) → list`
- `map_features_to_goals(text) → dict`

---

### Segmentation Engine

**Input:**
- User data DataFrame
- Number of segments (6-12)

**Output:**
```csv
user_id, segment_id, segment_name, activeness, gamification_propensity, social_propensity, churn_risk
```

**Key Methods:**
- `engineer_features(df) → df`
- `cluster_users(df, n_clusters) → df`
- `name_segments(df) → df`
- `validate_mece(df) → bool`

---

### Template Generator

**Input:**
- Segment profiles
- Goals
- Themes
- Knowledge Bank

**Output:**
```csv
template_id, segment_id, lifecycle_stage, goal, theme, language, content, tone, hook, feature_reference
```

**Key Methods:**
- `generate_template(segment, goal, theme, language) → dict`
- `personalize_template(template, user) → str`
- `translate_to_hindi(template_en) → str`
- `validate_template(template) → bool`

---

### Learning Engine

**Input:**
- Experiment results DataFrame
- Current templates
- Current timing recommendations
- Current themes

**Output:**
- Updated templates (filtered, weighted)
- Updated timing recommendations
- Updated themes
- Delta report

**Key Methods:**
- `classify_performance(experiment_results) → df`
- `suppress_bad_templates(templates, bad_list) → df`
- `promote_good_templates(templates, good_list) → df`
- `optimize_timing(timing_recs, experiment_results) → df`
- `adjust_frequency(frequency_map, experiment_results) → dict`
- `generate_delta_report(changes) → df`

---

## Key Algorithms

### 1. MECE Segmentation

```
INPUT: User data with behavioral features
OUTPUT: Segment assignments (mutually exclusive, collectively exhaustive)

ALGORITHM:
1. Feature Engineering
   - Calculate activeness = 0.3*sessions + 0.3*exercises + 0.2*notif_open + 0.2*streak
   - Calculate gamification_propensity = 0.4*streak + 0.3*coins + 0.3*feature_usage
   - Calculate social_propensity = 0.6*leaderboard + 0.4*sessions
   - Calculate churn_risk = 0.4*(1-sessions) + 0.3*(1-notif_open) + 0.3*no_streak

2. Standardization
   - Scale all features to mean=0, std=1

3. Clustering
   - Apply K-means with k=6-12
   - Use elbow method or silhouette score to choose k

4. Naming
   - For each cluster, calculate mean of each feature
   - Name based on dominant characteristics
   - Example: High activeness + High gamification → "Highly Active Achievers"

5. Validation
   - Check: Each user in exactly one segment (mutual exclusivity)
   - Check: All users are segmented (collective exhaustiveness)
   - Check: No segment < 5% of total users (reasonable distribution)
```

---

### 2. Template Performance Classification

```
INPUT: Experiment results with CTR and engagement_rate
OUTPUT: Performance classification (GOOD/NEUTRAL/BAD)

ALGORITHM:
For each template:
  IF CTR > 0.15 AND engagement_rate > 0.40:
    classification = GOOD
  ELSE IF CTR < 0.05 OR engagement_rate < 0.20:
    classification = BAD
  ELSE:
    classification = NEUTRAL

RATIONALE:
- GOOD: High open rate AND high action rate → Effective
- BAD: Low open rate OR low action rate → Ineffective
- NEUTRAL: Moderate performance → Keep but don't promote
```

---

### 3. Timing Optimization

```
INPUT: Experiment results with CTR by segment × window
OUTPUT: Optimized timing recommendations

ALGORITHM (Iteration 0):
1. For each segment:
   - Calculate mean preferred_hour from user data
   - Map to primary time window
   - Select secondary window (offset by 6-8 hours)
   - Assign priority (1 = primary, 2 = secondary)

ALGORITHM (Iteration 1):
1. For each segment:
   - Group experiment results by notification_window
   - Calculate mean CTR per window
   - Filter for statistical significance (min 100 sends)
   
2. For each segment:
   - Identify worst performing window (CTR < 0.05)
   - Suppress this window
   - Identify best performing windows (top 2 by CTR)
   - Promote these windows
   
3. Update timing_recommendations.csv with new priorities
```

---

### 4. Frequency Adjustment

```
INPUT: User activeness, segment uninstall_rate
OUTPUT: Notifications per day

ALGORITHM:
1. Base Frequency Calculation:
   IF activeness > 0.7:
     base_freq = 8
   ELSE IF activeness > 0.4:
     base_freq = 6
   ELSE:
     base_freq = 4

2. Lifecycle Adjustment:
   IF lifecycle_stage == 'trial':
     base_freq += 1  # More aggressive in trial
   ELSE IF lifecycle_stage == 'churned':
     base_freq = 2   # Very conservative

3. Guardrail Check:
   IF segment_uninstall_rate > 0.02:
     base_freq = max(2, base_freq - 2)  # Reduce by 2, minimum 2

4. Return adjusted frequency
```

---

### 5. Learning Delta Calculation

```
INPUT: Iteration 0 results, Iteration 1 results
OUTPUT: Measurable improvements

ALGORITHM:
1. Calculate aggregate metrics:
   - avg_ctr_0 = mean(iteration_0['ctr'])
   - avg_ctr_1 = mean(iteration_1['ctr'])
   - ctr_improvement = avg_ctr_1 - avg_ctr_0
   
   - avg_engagement_0 = mean(iteration_0['engagement_rate'])
   - avg_engagement_1 = mean(iteration_1['engagement_rate'])
   - engagement_improvement = avg_engagement_1 - avg_engagement_0
   
   - avg_uninstall_0 = mean(iteration_0['uninstall_rate'])
   - avg_uninstall_1 = mean(iteration_1['uninstall_rate'])
   - uninstall_reduction = avg_uninstall_0 - avg_uninstall_1

2. Calculate template changes:
   - templates_suppressed = count(templates in iter_0 but not in iter_1)
   - templates_promoted = count(templates with increased weight)

3. Return delta report with all improvements
```

---

## Design Patterns

### 1. Strategy Pattern (Domain Agnostic Design)

```python
class NotificationOrchestrator:
    def __init__(self, knowledge_bank):
        self.kb = knowledge_bank  # Injected dependency
        
    def generate_message(self, user, goal):
        # No hardcoded domain logic
        feature = self.kb.get_feature_for_goal(goal)
        tone = self.kb.get_tone_for_lifecycle(user.lifecycle)
        hook = self.kb.get_hook_for_segment(user.segment)
        
        return self.template_engine.generate(user, feature, tone, hook)
```

**Why:** Allows swapping domains without code changes

---

### 2. Pipeline Pattern (Data Processing)

```python
def process_user_data(csv_path):
    df = load_csv(csv_path)
    df = validate_schema(df)
    df = clean_data(df)
    df = engineer_features(df)
    df = segment_users(df)
    return df
```

**Why:** Clear, testable, modular data transformations

---

### 3. Observer Pattern (Learning Loop)

```python
class LearningEngine:
    def __init__(self):
        self.observers = []  # Components that need updates
        
    def register_observer(self, observer):
        self.observers.append(observer)
        
    def learn_from_results(self, experiment_results):
        changes = self.analyze_results(experiment_results)
        
        # Notify all observers of changes
        for observer in self.observers:
            observer.update(changes)
```

**Why:** Decouples learning logic from component updates

---

## Testing Strategy

### Unit Tests
- Test each component independently
- Mock dependencies
- Test edge cases (missing data, outliers, empty inputs)

### Integration Tests
- Test data flow between components
- Test with sample data
- Verify output formats

### End-to-End Tests
- Test complete Iteration 0 flow
- Test complete Iteration 1 flow
- Verify measurable delta

### Validation Tests
- Test MECE property of segments
- Test bilingual support
- Test guardrail enforcement
- Test with new/different data

---

## Performance Considerations

### Scalability
- **Current:** 1,000-10,000 users
- **Target:** 100,000+ users
- **Optimization:** Vectorized operations, batch processing

### Latency
- **KB Extraction:** 5-10 seconds (one-time)
- **Segmentation:** 1-2 seconds (per run)
- **Template Generation:** 10-30 seconds (per run)
- **Schedule Generation:** 5-10 seconds (per 1000 users)

### Memory
- **User Data:** ~1MB per 10,000 users
- **Templates:** ~100KB per 1000 templates
- **Schedules:** ~5MB per 10,000 users × 30 days

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production System                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │  API Layer   │      │  Scheduler   │                    │
│  │              │      │              │                    │
│  │  • Accept KB │      │  • Cron jobs │                    │
│  │  • Accept CSV│      │  • Triggers  │                    │
│  │  • Return    │      │  • Monitoring│                    │
│  │    outputs   │      │              │                    │
│  └──────────────┘      └──────────────┘                    │
│         │                      │                            │
│         └──────────┬───────────┘                            │
│                    ▼                                        │
│       ┌──────────────────────┐                              │
│       │  Orchestrator Core   │                              │
│       │  (Your System)       │                              │
│       └──────────────────────┘                              │
│                    │                                        │
│         ┌──────────┼──────────┐                             │
│         ▼          ▼          ▼                             │
│  ┌──────────┐ ┌────────┐ ┌─────────┐                       │
│  │ Database │ │ Cache  │ │ Storage │                       │
│  │          │ │        │ │         │                       │
│  │ • Users  │ │ • KB   │ │ • CSVs  │                       │
│  │ • Results│ │ • Segs │ │ • Logs  │                       │
│  └──────────┘ └────────┘ └─────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

This architecture is designed to be:
1. **Modular:** Each component has clear responsibilities
2. **Extensible:** Easy to add new features or domains
3. **Testable:** Each component can be tested independently
4. **Scalable:** Can handle growing user bases
5. **Maintainable:** Clear interfaces and documentation

The key to success is understanding how data flows through the system and ensuring each component does its job well.
