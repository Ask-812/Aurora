# QUICK START GUIDE: Project Aurora
## For Freshers Who Want to Get Started Fast

---

## What You're Building

A **self-learning notification orchestrator** that:
1. Segments users intelligently
2. Generates personalized messages
3. Optimizes timing and frequency
4. **LEARNS from experiment results and improves**

---

## The 3 Tasks (In Plain English)

### TASK 1: Build the Intelligence Engines
**What:** Create the brain of the system
**Outputs:**
- Extract company goals from documents → `company_north_star.json`
- Map features to goals → `feature_goal_map.json`
- Define allowed tones → `allowed_tone_hook_matrix.json`
- Segment users into 6-12 groups → `user_segments.csv`
- Define goals for each segment → `segment_goals.csv`

**Key Concept:** MECE Segmentation
- **M**utually **E**xclusive: Each user in exactly ONE segment
- **C**ollectively **E**xhaustive: ALL users are covered

---

### TASK 2: Build the Communication Layer
**What:** Create smart messaging and timing
**Outputs:**
- Map psychological hooks to segments → `communication_themes.csv`
- Generate 5 templates per segment/goal/theme → `message_templates.csv` (Hindi + English)
- Optimize notification timing → `timing_recommendations.csv`
- Create user schedules → `user_notification_schedule.csv`

**Key Concept:** Octalysis Framework
8 psychological drives that motivate humans:
1. Epic Meaning (be part of something bigger)
2. Accomplishment (make progress)
3. Empowerment (have control)
4. Ownership (build something valuable)
5. Social Influence (others are doing it)
6. Scarcity (limited time)
7. Curiosity (what's next?)
8. Loss Avoidance (don't lose what you have)

---

### TASK 3: Build the Learning Engine
**What:** Make the system improve over time
**Outputs:**
- Classify templates as GOOD/NEUTRAL/BAD → `experiment_results.csv`
- Document all changes → `learning_delta_report.csv`
- Show measurable improvement (Iteration 0 → Iteration 1)

**Key Concept:** Causal Reasoning
Every change must answer:
- WHAT changed?
- WHY did it change?
- WHAT triggered it?
- WHAT improved?

---

## The Critical Requirement: REAL LEARNING

### ❌ NOT Learning (Will Fail)
```python
# Iteration 0
templates = generate_templates()

# Iteration 1
templates = generate_templates()
templates.loc[5, 'weight'] = 2.0  # Manually tweaked
```

### ✅ REAL Learning (Will Pass)
```python
# Iteration 0
templates = generate_templates()

# Iteration 1
experiment_results = load_experiment_results()
bad_templates = experiment_results[experiment_results['ctr'] < 0.05]['template_id']
templates = templates[~templates['template_id'].isin(bad_templates)]

# Prove improvement
delta = calculate_improvement()  # CTR: 11.4% → 13.25%
```

---

## Key Metrics You Must Understand

### CTR (Click-Through Rate)
```
CTR = (Total Opens / Total Sends) × 100
```
**What it means:** Did users open the notification?

### Engagement Rate
```
Engagement Rate = (Total Engagements / Total Opens) × 100
```
**What it means:** After opening, did users DO something?

### Why Both Matter
- High CTR + Low Engagement = Clickbait (BAD)
- Low CTR + High Engagement = Poor messaging (FIXABLE)
- High CTR + High Engagement = Winning template (GOOD)

---

## Classification Rules

| Performance | CTR | Engagement | Action |
|------------|-----|------------|--------|
| GOOD | >15% | >40% | Promote (increase usage) |
| NEUTRAL | 5-15% | 20-40% | Keep as is |
| BAD | <5% | <20% | Suppress (remove) |

---

## Frequency Rules

| Activeness | Notifs/Day | Reasoning |
|-----------|-----------|-----------|
| >0.7 (High) | 7-9 | User is engaged, can handle more |
| 0.4-0.7 (Med) | 5-6 | Balanced approach |
| <0.4 (Low) | 3-4 | Risk of annoyance |

**GUARDRAIL:** If uninstall_rate > 2% → Reduce by 2 notifs/day (regardless of activeness)

---

## Time Windows

```
early_morning:    06:00–08:59
mid_morning:      09:00–11:59
afternoon:        12:00–14:59
late_afternoon:   15:00–17:59
evening:          18:00–20:59
night:            21:00–23:59
```

**Strategy:** Learn which windows work best for each segment

---

## Common Mistakes (And How to Avoid Them)

### 1. Hardcoding Domain Logic
❌ `return "Keep your English learning streak alive!"`
✅ `return f"Keep your {knowledge_bank.get_primary_feature()} going!"`

### 2. Non-MECE Segments
❌ Segment 1: Active users, Segment 2: Gamification lovers (can overlap)
✅ Use clustering to ensure mutual exclusivity

### 3. Generic Templates
❌ "Complete your exercise today!" (same for everyone)
✅ "You're 2 exercises away from 100 coins!" (personalized for achievers)

### 4. Ignoring Uninstall Rate
❌ Send 9 notifs/day even if users are uninstalling
✅ Check uninstall_rate and reduce frequency if > 2%

### 5. Mock Learning
❌ Manually change one value and call it "learning"
✅ Use experiment_results.csv to drive ALL changes

---

## The Demo Flow (What Evaluators Will See)

### Phase 1: Iteration 0 (Before Learning)
1. You provide Knowledge Bank (company docs)
2. You provide user_data.csv
3. System generates all outputs
4. Evaluator reviews segmentation, templates, timing

### Phase 2: Iteration 1 (After Learning)
1. Evaluator provides experiment_results.csv
2. System ingests and analyzes results
3. System makes data-driven changes
4. System generates improved outputs
5. **Evaluator checks for measurable improvement**

### What They're Looking For
- Did CTR improve?
- Did engagement improve?
- Did uninstall rate decrease?
- Can you explain WHY each change was made?

---

## Auto-Fail Conditions (Avoid These!)

1. **Hardcoded outputs** (not data-driven)
2. **Mock learning** (no real Iteration 0 → 1 improvement)
3. **PPT-only demo** (no working system)
4. **No delta** (can't show measurable improvement)
5. **Missing/renamed files** (must match exact names)

---

## Deliverable Files (EXACT NAMES - Don't Change!)

### Task 1
- `company_north_star.json`
- `feature_goal_map.json`
- `allowed_tone_hook_matrix.json`
- `user_segments.csv`
- `segment_goals.csv`

### Task 2
- `communication_themes.csv`
- `message_templates.csv`
- `timing_recommendations.csv`
- `user_notification_schedule.csv`

### Task 3
- `experiment_results.csv`
- `learning_delta_report.csv`
- `README.txt` (≤500 words)

---

## Your Week-by-Week Plan

### Week 1: Understand & Design
- Day 1-2: Read PS deeply, understand concepts
- Day 3-4: Learn MECE, Octalysis, propensity scores
- Day 5-7: Design architecture, define interfaces

### Week 2: Implement
- Day 8-10: Task 1 (KB extraction, segmentation)
- Day 11-13: Task 2 (templates, timing, frequency)
- Day 14-16: Task 3 (schedule generation, classification)

### Week 3: Learning & Polish
- Day 17-19: Implement learning engine
- Day 20-21: Test with new data, fix edge cases
- Day 22-23: Prepare demo, practice explanations
- Day 24: Final review, README

---

## Questions to Ask Yourself

### After Task 1
- [ ] Can each user be in exactly ONE segment?
- [ ] Are all users covered by segments?
- [ ] Do segments have meaningful names?
- [ ] Are propensity scores calculated AND used?

### After Task 2
- [ ] Are templates different for different segments?
- [ ] Do templates use appropriate psychological hooks?
- [ ] Is every template available in Hindi AND English?
- [ ] Does timing vary by segment?
- [ ] Is frequency based on activeness and churn risk?

### After Task 3
- [ ] Does Iteration 1 differ from Iteration 0?
- [ ] Are changes based on experiment_results.csv?
- [ ] Can I show measurable improvement (numbers)?
- [ ] Can I explain WHY each change was made?
- [ ] Is the learning reproducible (same input → same output)?

---

## The One Thing to Remember

**This is not about perfect code. It's about proving you can:**
1. Understand a complex problem
2. Design a system that works
3. Make it learn and improve
4. Explain your decisions clearly

Focus on **understanding**, not just **implementing**.
Focus on **proving**, not just **claiming**.
Focus on **learning**, not just **delivering**.

---

## Need Help?

1. Read the full MENTOR_GUIDE_Project_Aurora.md for detailed explanations
2. Ask yourself: "What if this was a different domain?"
3. Test with new data frequently
4. Explain your approach out loud (rubber duck debugging)
5. Focus on the "why" behind every decision

**You've got this! 🚀**
