# MENTOR GUIDE - QUICK REFERENCE

## 📋 Overview

This is your companion guide to `MENTOR_TEACHING_GUIDE.md`. Use this for quick lookups during meetings.

---

## 🗓️ 6-WEEK SCHEDULE AT A GLANCE

### Week 1: Foundations (3 meetings)
- **Meeting 1.1** - Problem statement deep dive
- **Meeting 1.2** - Core concepts from zero (MECE, Octalysis, propensity, etc.)
- **Meeting 1.3** - Architecture design session

### Week 2: Task 1 - Intelligence Layer (3 meetings)
- **Meeting 2.1** - Knowledge Bank Engine (live coding)
- **Meeting 2.2** - Data Ingestion & Validation
- **Meeting 2.3** - MECE Segmentation Engine

### Week 3: Task 1 Completion & Task 2 Start (3 meetings)
- **Meeting 3.1** - Goal Builder
- **Meeting 3.2** - Theme Engine
- **Meeting 3.3** - Template Generator Part 1

### Week 4: Task 2 Completion (3 meetings)
- **Meeting 4.1** - Template Generator Part 2 & Timing Optimizer
- **Meeting 4.2** - Schedule Generator
- **Meeting 4.3** - Task 1 & 2 Integration Test

### Week 5: Task 3 - Learning Layer (3 meetings)
- **Meeting 5.1** - Performance Classifier
- **Meeting 5.2** - Learning Engine
- **Meeting 5.3** - Delta Reporter

### Week 6: Integration & Presentation (3 meetings)
- **Meeting 6.1** - Complete Iteration 1 Pipeline
- **Meeting 6.2** - Code Quality & Documentation
- **Meeting 6.3** - Final Review & Presentation Prep

---

## 🎯 Teaching Pattern (Use in Every Meeting)

### The Three-Step Pattern:
1. **EXPLAIN** - Tell them what and why
2. **DEMONSTRATE** - Show them how (live coding)
3. **VERIFY** - Make them explain it back

### Code Review Approach:
- ❌ Never say "This is wrong"
- ✅ Say "Walk me through your thinking here"
- ❌ Never give the answer
- ✅ Ask "What happens if we do X instead?"
- ✅ Always ask "Why?" - Make them justify decisions

---

## 📝 Key Concepts to Emphasize

### 1. Domain-Agnostic Design
**Bad:** Hardcoding "English learning" logic
**Good:** Everything driven by Knowledge Bank

### 2. MECE Segmentation
**Key:** Each user in EXACTLY ONE segment, ALL users covered
**Validation:** Programmatic proof required

### 3. Causal Reasoning
**Bad:** "Changed template weight to 3.0"
**Good:** "Template achieved 18% CTR (threshold: 15%), indicating strong resonance. Increased weight to 3.0 to increase selection probability, expected to improve overall CTR by 2-3%."

### 4. Real Learning
**Not:** Manual tweaking between iterations
**Yes:** Data-driven changes with measurable improvements

---

## 🔍 Common Mistakes & How to Guide

### Mistake 1: Skipping Validation
**What they do:** Assume data is clean
**What to ask:** "What happens if a user has -5 sessions?"
**Guide toward:** Comprehensive validation with clear error messages

### Mistake 2: Hardcoding Values
**What they do:** `if segment == "Achievers":`
**What to ask:** "What if we change the segment names?"
**Guide toward:** Use segment_id and propensity scores

### Mistake 3: No Causal Reasoning
**What they do:** "Suppressed template T0001"
**What to ask:** "Why did you suppress it? What was wrong with it?"
**Guide toward:** "Template T0001 had 4% CTR (threshold: 5%), indicating poor user resonance. Suppressed to improve overall performance."

### Mistake 4: Same Strategy for All Segments
**What they do:** Same templates/timing for everyone
**What to ask:** "Should we send the same message to achievers and casual learners?"
**Guide toward:** Segment-specific strategies based on propensities

---

## 💡 Questions to Ask in Each Meeting

### During Design:
- "Why this approach instead of alternatives?"
- "What happens if the data changes?"
- "How would you test this?"
- "What edge cases should we handle?"

### During Coding:
- "Walk me through your logic"
- "What happens if this fails?"
- "How would you debug this?"
- "Can you explain this to a non-technical person?"

### During Review:
- "Does this match the requirements?"
- "Are there any missing validations?"
- "Is the code readable?"
- "Would this work in production?"

---

## 📊 Deliverables Checklist (Use in Week 6)

### Task 1 (5 files):
- [ ] company_north_star.json
- [ ] feature_goal_map.json
- [ ] allowed_tone_hook_matrix.json
- [ ] user_segments.csv (1000 users, MECE validated)
- [ ] segment_goals.csv (104 goals)

### Task 2 (4 files):
- [ ] communication_themes.csv (32 themes)
- [ ] message_templates.csv (720 templates: 360 EN + 360 HI)
- [ ] timing_recommendations.csv (16 windows)
- [ ] user_notification_schedule.csv (700 entries for 100 users)

### Task 3 (4 files):
- [ ] learning_delta_report.csv (31 changes with causal reasoning)
- [ ] message_templates_improved.csv (BAD templates removed)
- [ ] timing_recommendations_improved.csv (optimized windows)
- [ ] communication_themes_improved.csv (refined themes)

---

## 🎤 Presentation Coaching Tips

### Structure (10 minutes):
1. Problem (1 min) - Why this matters
2. Architecture (1.5 min) - Three layers
3. Task 1 (1.5 min) - Intelligence layer
4. Task 2 (1.5 min) - Communication layer
5. Task 3 (2 min) - Learning layer + demo
6. Results (1.5 min) - Metrics improvement
7. Achievements (0.5 min) - Key highlights
8. Q&A (Remaining time)

### Common Presentation Mistakes:
- ❌ Speaking too fast
- ❌ Only saying WHAT, not WHY
- ❌ Not showing actual outputs
- ❌ Not emphasizing learning

### What Evaluators Want to See:
- ✅ Deep understanding of concepts
- ✅ Complete implementation (12/12 deliverables)
- ✅ Real, measurable learning
- ✅ Causal reasoning for all changes
- ✅ Production-quality code

---

## 🚨 Red Flags to Watch For

### Week 1-2:
- Not understanding MECE property
- Hardcoding business logic
- Skipping validation

### Week 3-4:
- Same templates for all segments
- No bilingual support
- Templates too long (>120 chars)

### Week 5-6:
- No causal reasoning in delta report
- Claiming learning without proof
- Metrics not improving

---

## 📞 Quick Answers to Common Questions

**Q: How many segments?**
A: 6-12 optimal, 8 is good default

**Q: How many templates?**
A: 720 total (360 EN + 360 HI)

**Q: What if Iteration 1 is worse?**
A: Check thresholds, ensure statistical significance, review causal reasoning

**Q: How to prove learning?**
A: Measurable metrics + causal reasoning + reproducibility

**Q: What if evaluator changes Knowledge Bank?**
A: System should work without code changes (domain-agnostic design)

---

## 🎯 Success Criteria

By end of Week 6, freshers should be able to:

1. ✅ Explain every design decision with reasoning
2. ✅ Run complete system end-to-end without errors
3. ✅ Generate all 12 deliverables with correct schemas
4. ✅ Demonstrate measurable learning improvements
5. ✅ Provide causal reasoning for all changes
6. ✅ Present confidently with live demo
7. ✅ Answer "why" questions thoughtfully
8. ✅ Handle edge cases gracefully

---

## 📚 Resources to Reference

- **MENTOR_TEACHING_GUIDE.md** - Complete week-by-week guide
- **MENTOR_GUIDE_Project_Aurora.md** - Comprehensive tutorial (50,000 words)
- **SYSTEM_ARCHITECTURE_GUIDE.md** - Technical architecture
- **COMPLETION_REPORT.md** - What the final system looks like
- **main.py** - Complete orchestrator example

---

## 💪 Motivational Reminders

**For You (Mentor):**
- Be patient - learning takes time
- Guide, don't solve - let them struggle a bit
- Celebrate small wins
- Focus on understanding, not just completion

**For Freshers:**
- Understanding > Speed
- Ask "why" constantly
- Test everything
- Document as you go
- Learning is iterative

---

**Remember:** The goal is not just to complete the project, but to deeply understand every concept and decision. Quality over speed!

