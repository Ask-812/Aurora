# CONCEPT MAP: Project Aurora
## Visual Guide to All Concepts and Their Relationships

---

## The Big Picture

```
                    ┌─────────────────────────────────────┐
                    │   NOTIFICATION ORCHESTRATOR         │
                    │   (Self-Learning System)            │
                    └─────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │   WHO     │   │   WHAT    │   │   WHEN    │
            │ (Segments)│   │(Messages) │   │ (Timing)  │
            └───────────┘   └───────────┘   └───────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │   HOW MUCH    │
                            │  (Frequency)  │
                            └───────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │   WHY         │
                            │  (Learning)   │
                            └───────────────┘
```

---

## Core Concept Hierarchy

```
PROJECT AURORA
│
├── DOMAIN AGNOSTIC DESIGN
│   ├── Knowledge Bank (company-specific intelligence)
│   │   ├── North Star Metric
│   │   ├── Feature-Goal Mappings
│   │   ├── Allowed Tones
│   │   └── Behavioral Hooks
│   │
│   └── Orchestrator Core (domain-independent logic)
│       ├── Segmentation Engine
│       ├── Template Generator
│       ├── Timing Optimizer
│       └── Learning Engine
│
├── USER INTELLIGENCE (WHO)
│   ├── MECE Segmentation
│   │   ├── Mutually Exclusive (no overlap)
│   │   └── Collectively Exhaustive (all covered)
│   │
│   ├── Propensity Scores
│   │   ├── Gamification Propensity
│   │   ├── Social Propensity
│   │   ├── AI Tutor Propensity
│   │   └── Feature-specific Propensities
│   │
│   ├── Behavioral Scores
│   │   ├── Activeness Score
│   │   └── Churn Risk Score
│   │
│   └── Lifecycle Stages
│       ├── Trial (D0-D7)
│       ├── Paid (D8-D30)
│       ├── Churned
│       └── Inactive
│
├── MESSAGE INTELLIGENCE (WHAT)
│   ├── Octalysis Framework (8 Core Drives)
│   │   ├── Epic Meaning & Calling
│   │   ├── Development & Accomplishment
│   │   ├── Empowerment of Creativity
│   │   ├── Ownership & Possession
│   │   ├── Social Influence & Relatedness
│   │   ├── Scarcity & Impatience
│   │   ├── Unpredictability & Curiosity
│   │   └── Loss & Avoidance
│   │
│   ├── Theme Mapping
│   │   ├── Segment → Theme
│   │   ├── Lifecycle → Theme
│   │   └── Goal → Theme
│   │
│   ├── Template Generation
│   │   ├── Personalization (segment-specific)
│   │   ├── Bilingual Support (Hindi + English)
│   │   ├── Tone Alignment (brand voice)
│   │   └── Feature References
│   │
│   └── Journey Progression
│       ├── D0: Activation
│       ├── D1-D2: Habit Formation
│       ├── D3-D5: Feature Discovery
│       ├── D6-D7: Conversion Readiness
│       └── D8+: Retention & Expansion
│
├── TIMING INTELLIGENCE (WHEN)
│   ├── Time Windows (6 standard windows)
│   │   ├── Early Morning (06:00-08:59)
│   │   ├── Mid Morning (09:00-11:59)
│   │   ├── Afternoon (12:00-14:59)
│   │   ├── Late Afternoon (15:00-17:59)
│   │   ├── Evening (18:00-20:59)
│   │   └── Night (21:00-23:59)
│   │
│   ├── Segment-Specific Timing
│   │   ├── User Preferred Hour Analysis
│   │   ├── Window Performance Analysis
│   │   └── Optimal Window Selection
│   │
│   └── Timing Optimization (Learning)
│       ├── Suppress Low-Performing Windows
│       └── Promote High-Performing Windows
│
├── FREQUENCY INTELLIGENCE (HOW MUCH)
│   ├── Activeness-Based Frequency
│   │   ├── High (>0.7): 7-9 notifs/day
│   │   ├── Medium (0.4-0.7): 5-6 notifs/day
│   │   └── Low (<0.4): 3-4 notifs/day
│   │
│   ├── Lifecycle Adjustments
│   │   ├── Trial: +1 (more aggressive)
│   │   ├── Paid: baseline
│   │   └── Churned: 2 (very conservative)
│   │
│   └── Guardrails
│       └── Uninstall Rate > 2% → Reduce by 2
│
└── LEARNING INTELLIGENCE (WHY & HOW)
    ├── Performance Metrics
    │   ├── CTR (Click-Through Rate)
    │   │   └── (Opens / Sends) × 100
    │   ├── Engagement Rate
    │   │   └── (Engagements / Opens) × 100
    │   └── Uninstall Rate
    │       └── (Uninstalls / Total Users) × 100
    │
    ├── Performance Classification
    │   ├── GOOD (CTR >15%, Engagement >40%)
    │   ├── NEUTRAL (CTR 5-15%, Engagement 20-40%)
    │   └── BAD (CTR <5% OR Engagement <20%)
    │
    ├── Learning Actions
    │   ├── Template Suppression (remove BAD)
    │   ├── Template Promotion (increase GOOD weight)
    │   ├── Timing Optimization (shift windows)
    │   ├── Theme Refinement (update primary themes)
    │   └── Frequency Adjustment (reduce if high uninstall)
    │
    ├── Causal Reasoning
    │   ├── What changed?
    │   ├── Why did it change?
    │   ├── What triggered it?
    │   ├── What is expected impact?
    │   └── How to verify improvement?
    │
    └── Delta Measurement
        ├── CTR Improvement
        ├── Engagement Improvement
        ├── Uninstall Rate Reduction
        └── Template Count Changes
```

---

## Concept Relationships

### 1. Segmentation → Everything Else

```
USER DATA
    │
    ▼
FEATURE ENGINEERING
    │
    ├─→ Activeness Score ────────────┐
    ├─→ Gamification Propensity ─────┤
    ├─→ Social Propensity ───────────┼─→ CLUSTERING → SEGMENTS
    └─→ Churn Risk ──────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
            THEME SELECTION   TEMPLATE SELECTION   TIMING SELECTION
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
                              PERSONALIZED SCHEDULE
```

**Key Insight:** Segments are the foundation. Everything else depends on knowing which segment a user belongs to.

---

### 2. Lifecycle Stage → Communication Strategy

```
LIFECYCLE STAGE
    │
    ├─→ TRIAL (D0-D7)
    │   ├─→ Goal: Activation, Habit Formation
    │   ├─→ Tone: Encouraging, Friendly
    │   ├─→ Theme: Curiosity, Accomplishment
    │   ├─→ Frequency: High (7-9/day)
    │   └─→ Timing: Multiple windows
    │
    ├─→ PAID (D8-D30)
    │   ├─→ Goal: Retention, Value Delivery
    │   ├─→ Tone: Celebratory, Aspirational
    │   ├─→ Theme: Accomplishment, Ownership
    │   ├─→ Frequency: Moderate (5-7/day)
    │   └─→ Timing: Optimal windows
    │
    ├─→ CHURNED
    │   ├─→ Goal: Re-engagement
    │   ├─→ Tone: Urgent, Friendly
    │   ├─→ Theme: Loss Avoidance, Social Proof
    │   ├─→ Frequency: Low (2-3/week)
    │   └─→ Timing: Best performing window only
    │
    └─→ INACTIVE
        ├─→ Goal: Activation or Graceful Exit
        ├─→ Tone: Curious, Friendly
        ├─→ Theme: Curiosity, Epic Meaning
        ├─→ Frequency: Very Low (1-2/week)
        └─→ Timing: Single window
```

**Key Insight:** Same user, different stage = completely different strategy.

---

### 3. Propensity Scores → Theme Selection

```
USER PROPENSITY PROFILE
    │
    ├─→ High Gamification (>0.7)
    │   └─→ Themes: Accomplishment, Ownership
    │       └─→ Messages: Coins, Streaks, Badges
    │
    ├─→ High Social (>0.7)
    │   └─→ Themes: Social Influence, Competition
    │       └─→ Messages: Leaderboards, Peer Comparison
    │
    ├─→ High Churn Risk (>0.6)
    │   └─→ Themes: Loss Avoidance, Scarcity
    │       └─→ Messages: Streak Breaking, Limited Time
    │
    └─→ Low Engagement (<0.4)
        └─→ Themes: Curiosity, Empowerment
            └─→ Messages: Discovery, Flexibility
```

**Key Insight:** Match the message motivation to what the user cares about.

---

### 4. Performance Metrics → Learning Actions

```
EXPERIMENT RESULTS
    │
    ├─→ Template Performance
    │   │
    │   ├─→ CTR >15% & Engagement >40%
    │   │   └─→ GOOD → Promote (weight × 3)
    │   │
    │   ├─→ CTR 5-15% & Engagement 20-40%
    │   │   └─→ NEUTRAL → Keep as is
    │   │
    │   └─→ CTR <5% OR Engagement <20%
    │       └─→ BAD → Suppress (remove)
    │
    ├─→ Timing Performance
    │   │
    │   ├─→ Window CTR >15%
    │   │   └─→ Promote (increase allocation)
    │   │
    │   └─→ Window CTR <5%
    │       └─→ Suppress (remove from schedule)
    │
    ├─→ Frequency Performance
    │   │
    │   └─→ Uninstall Rate >2%
    │       └─→ Reduce frequency by 2
    │
    └─→ Theme Performance
        │
        └─→ Theme CTR significantly higher
            └─→ Update primary theme for segment
```

**Key Insight:** Every metric threshold triggers a specific learning action.

---

### 5. Iteration 0 → Iteration 1 (The Learning Loop)

```
ITERATION 0 (Assumptions)
    │
    ├─→ Segments based on clustering
    ├─→ Themes based on propensity scores
    ├─→ Timing based on preferred_hour
    ├─→ Frequency based on activeness
    └─→ Templates generated for all combinations
    │
    ▼
RUN EXPERIMENT
    │
    ▼
COLLECT RESULTS (experiment_results.csv)
    │
    ├─→ Template CTR & Engagement
    ├─→ Window CTR by Segment
    ├─→ Uninstall Rate by Segment
    └─→ Theme Performance by Segment
    │
    ▼
ANALYZE & LEARN
    │
    ├─→ Classify Templates (GOOD/NEUTRAL/BAD)
    ├─→ Identify Underperforming Windows
    ├─→ Check Uninstall Rate Guardrails
    └─→ Compare Theme Performance
    │
    ▼
APPLY LEARNING
    │
    ├─→ Suppress BAD Templates
    ├─→ Promote GOOD Templates
    ├─→ Remove Low-CTR Windows
    ├─→ Reduce Frequency if Uninstall >2%
    └─→ Update Primary Themes
    │
    ▼
ITERATION 1 (Data-Driven)
    │
    ├─→ Fewer but better templates
    ├─→ Optimized timing windows
    ├─→ Adjusted frequency
    └─→ Refined themes
    │
    ▼
MEASURE DELTA
    │
    ├─→ CTR: 11.4% → 13.25% (+1.85%)
    ├─→ Engagement: 32% → 36% (+4%)
    ├─→ Uninstall: 2.5% → 1.5% (-1%)
    └─→ Templates: 40 → 32 (8 suppressed)
```

**Key Insight:** Learning is a closed loop. Results → Analysis → Actions → Improved Results.

---

## Concept Dependencies

### What Depends on What?

```
Knowledge Bank
    └─→ Everything (domain-agnostic design)

User Data
    └─→ Segmentation
        └─→ Theme Selection
            └─→ Template Generation
                └─→ Schedule Generation

Segments
    └─→ Goals
        └─→ Templates
            └─→ Schedule

Lifecycle Stage
    └─→ Goals
        └─→ Tone
            └─→ Templates

Propensity Scores
    └─→ Themes
        └─→ Templates

Activeness Score
    └─→ Frequency
        └─→ Schedule

Experiment Results
    └─→ Learning Actions
        └─→ Updated Components
            └─→ Improved Schedule
```

**Key Insight:** You can't skip steps. Each component depends on previous ones.

---

## Critical Thresholds (Numbers to Remember)

```
SEGMENTATION
├─→ Number of segments: 6-12
├─→ Minimum segment size: 5% of total users
└─→ MECE validation: sum(segments) = total users

PROPENSITY SCORES
├─→ High: >0.7
├─→ Medium: 0.4-0.7
└─→ Low: <0.4

PERFORMANCE CLASSIFICATION
├─→ GOOD: CTR >15% AND Engagement >40%
├─→ BAD: CTR <5% OR Engagement <20%
└─→ NEUTRAL: Everything else

FREQUENCY
├─→ High activeness: 7-9 notifs/day
├─→ Medium activeness: 5-6 notifs/day
├─→ Low activeness: 3-4 notifs/day
└─→ Guardrail: Uninstall >2% → Reduce by 2

TIMING
├─→ Number of windows: 6
├─→ Window duration: 3 hours each
└─→ Suppress threshold: CTR <5%

LEARNING
├─→ Minimum sends for significance: 100
├─→ Template suppression: CTR <5% OR Engagement <20%
├─→ Template promotion: CTR >15% AND Engagement >40%
└─→ Frequency reduction: Uninstall rate >2%
```

---

## Common Confusions Clarified

### 1. Segmentation vs Personas

```
PERSONAS (Wrong Approach)
├─→ "Young Professionals"
├─→ "College Students"
└─→ "Homemakers"
    │
    └─→ Problem: Overlapping, subjective, not data-driven

SEGMENTS (Correct Approach)
├─→ "Highly Active Achievers" (activeness >0.7, gamification >0.7)
├─→ "Casual Learners" (activeness 0.4-0.7, gamification <0.3)
└─→ "At-Risk Churners" (churn_risk >0.7)
    │
    └─→ Solution: MECE, data-driven, behavioral
```

---

### 2. CTR vs Engagement

```
SCENARIO 1: High CTR, Low Engagement
├─→ CTR: 20% (200 opens out of 1000 sends)
├─→ Engagement: 10% (20 actions out of 200 opens)
└─→ Interpretation: Clickbait. Users open but don't act. BAD.

SCENARIO 2: Low CTR, High Engagement
├─→ CTR: 8% (80 opens out of 1000 sends)
├─→ Engagement: 50% (40 actions out of 80 opens)
└─→ Interpretation: Poor messaging but good content. NEUTRAL (fixable).

SCENARIO 3: High CTR, High Engagement
├─→ CTR: 18% (180 opens out of 1000 sends)
├─→ Engagement: 45% (81 actions out of 180 opens)
└─→ Interpretation: Winning template. GOOD.
```

---

### 3. Iteration 0 vs Iteration 1

```
ITERATION 0 (Before Learning)
├─→ Based on: Assumptions, heuristics, best practices
├─→ Segmentation: Clustering algorithm
├─→ Timing: User preferred_hour
├─→ Frequency: Activeness score
├─→ Templates: All generated variants
└─→ Performance: Unknown (estimated)

ITERATION 1 (After Learning)
├─→ Based on: Experiment results, data-driven insights
├─→ Segmentation: Same (segments don't change)
├─→ Timing: Optimized (suppress bad windows, promote good)
├─→ Frequency: Adjusted (reduced if high uninstall)
├─→ Templates: Filtered (BAD suppressed, GOOD promoted)
└─→ Performance: Improved (measurable delta)
```

---

### 4. Domain-Specific vs Domain-Agnostic

```
DOMAIN-SPECIFIC (Wrong)
├─→ Code: if user.streak > 5: return "Keep learning English!"
├─→ Problem: Hardcoded "English learning" logic
└─→ Result: Breaks with different domain

DOMAIN-AGNOSTIC (Correct)
├─→ Code: feature = kb.get_primary_feature(); return f"Keep {feature} going!"
├─→ Solution: Logic driven by Knowledge Bank
└─→ Result: Works with any domain (just swap KB)
```

---

## Visual Summary: The Complete System

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOTIFICATION ORCHESTRATOR                     │
│                    (Self-Learning System)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT: Knowledge Bank + User Data                              │
│     │                                                            │
│     ▼                                                            │
│  INTELLIGENCE LAYER (Task 1)                                    │
│     ├─→ Extract company intelligence (KB Engine)                │
│     ├─→ Segment users (MECE, propensity scores)                 │
│     └─→ Define goals & journeys                                 │
│     │                                                            │
│     ▼                                                            │
│  COMMUNICATION LAYER (Task 2)                                   │
│     ├─→ Map themes (Octalysis)                                  │
│     ├─→ Generate templates (personalized, bilingual)            │
│     ├─→ Optimize timing (segment-specific windows)              │
│     ├─→ Calculate frequency (activeness + guardrails)           │
│     └─→ Generate schedules (user-wise, journey-aligned)         │
│     │                                                            │
│     ▼                                                            │
│  OUTPUT: Iteration 0 (before learning)                          │
│     │                                                            │
│     ▼                                                            │
│  RUN EXPERIMENT → Collect Results                               │
│     │                                                            │
│     ▼                                                            │
│  LEARNING LAYER (Task 3)                                        │
│     ├─→ Classify performance (GOOD/NEUTRAL/BAD)                 │
│     ├─→ Suppress BAD templates                                  │
│     ├─→ Promote GOOD templates                                  │
│     ├─→ Optimize timing windows                                 │
│     ├─→ Adjust frequency (if uninstall >2%)                     │
│     ├─→ Refine themes                                           │
│     └─→ Document changes (causal reasoning)                     │
│     │                                                            │
│     ▼                                                            │
│  OUTPUT: Iteration 1 (after learning) + Delta Report            │
│     │                                                            │
│     └─→ MEASURABLE IMPROVEMENT                                  │
│         ├─→ CTR ↑                                               │
│         ├─→ Engagement ↑                                        │
│         ├─→ Uninstall Rate ↓                                    │
│         └─→ Template Quality ↑                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## The One Concept to Rule Them All

```
                    ┌─────────────────────┐
                    │   SELF-LEARNING     │
                    │   (The Core Idea)   │
                    └─────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │   DATA    │   │  ANALYSIS │   │  ACTION   │
    │ (Results) │   │(Learning) │   │(Improve)  │
    └───────────┘   └───────────┘   └───────────┘
            │               │               │
            └───────────────┼───────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  MEASURABLE   │
                    │  IMPROVEMENT  │
                    └───────────────┘
```

**Everything else is just implementation details.**

The core requirement is: **Prove that your system gets better over time using data, not guesses.**

---

**END OF CONCEPT MAP**

*Use this as a reference while reading the detailed guides. Understanding how concepts relate to each other is as important as understanding the concepts themselves.*
