# MENTOR GUIDE: Project Aurora - Self-Learning Notification Orchestrator
## A Zero-to-Hero Tutorial for Freshers

---

## TABLE OF CONTENTS

1. [Understanding the Problem Statement](#section-1)
2. [Core Concepts from Zero](#section-2)
3. [Task-by-Task Deep Dive](#section-3)
4. [Common Mistakes & Why They Happen](#section-4)
5. [Evaluator Mindset](#section-5)
6. [Learning vs Claiming](#section-6)
7. [Mentor Notes: How to Guide](#section-7)

---

<a name="section-1"></a>
## 1. UNDERSTANDING THE PROBLEM STATEMENT

### 1.1 The Opening Paragraph - Line by Line Analysis

**LINE: "Across EdTech, Consumer Apps, FinTech, HealthTech, and SaaS, user communication is the single most powerful, yet most poorly engineered, growth lever."**

**INTENT:** This is not just context—it's telling you the SCOPE of your solution.

**COMMON MISREAD:** Freshers think "Oh, this is just about SpeakX notifications."

**CORRECT INTERPRETATION:** Your system must be **domain-agnostic**. The evaluator wants to see that you could swap SpeakX data with a FinTech app's data and your orchestrator would still work. This means:
- No hardcoded "English learning" logic
- No assumptions about what "engagement" means
- Everything driven by the Knowledge Bank

**WHY THIS MATTERS:** Evaluators will test extensibility. They might ask: "What if I give you Paytm user data instead?" If your code breaks, you fail.

---

**LINE: "Today's notification systems are: Rule-based, Segment-blind, Timing-agnostic"**

**INTENT:** This defines what you're REPLACING.

**WHAT IT MEANS:**
- **Rule-based:** "If user hasn't opened app in 3 days, send notification" ← This is dumb. It doesn't learn.
- **Segment-blind:** Same message to everyone ← Ignores that different users need different motivation
- **Timing-agnostic:** Send at 10 AM to everyone ← Ignores that some users are active at 6 AM, others at 9 PM

**YOUR SYSTEM MUST:**
- Be **data-driven** (not rule-based)
- Be **segment-aware** (different strategies for different user types)
- Be **timing-intelligent** (learn when each segment responds best)
- **LEARN AND IMPROVE** (this is the core differentiator)

---

**LINE: "By 2030, intelligent communication orchestration will be the competitive moat"**

**INTENT:** This is vision-setting. It tells you this is a REAL product problem, not an academic exercise.

**EVALUATOR EXPECTATION:** They want to see product thinking, not just code. Can you explain WHY this matters to a business? Can you articulate the ROI?

---

### 1.2 The Core Challenge Statement

**"Your challenge is to build that system: a self-learning notification orchestrator"**

**CRITICAL WORD: "self-learning"**

This is NOT:
- A notification scheduler (that's trivial)
- A template generator (that's just string manipulation)
- A segmentation tool (that's just clustering)

This IS:
- A system that gets BETTER over time
- A system that LEARNS from experiment results
- A system that can EXPLAIN why it made changes

**COMMON MISTAKE:** Freshers build Iteration 0, then manually tweak some values for Iteration 1, and call it "learning."

**WHAT EVALUATORS WANT:** Causal reasoning. "Template X had 3% CTR in segment Y during evening window → System suppresses it → System tries Template Z instead → CTR improves to 12% → System documents this as a learned improvement."

---

### 1.3 Domain-Agnostic Architecture

**LINE: "EdTech (SpeakX) is the reference domain, but your architecture must be domain-agnostic"**

**WHAT THIS MEANS IN CODE:**

❌ **BAD (Domain-Specific):**
```python
def generate_message(user):
    if user.streak > 5:
        return "Keep your English learning streak alive!"
```

✅ **GOOD (Domain-Agnostic):**
```python
def generate_message(user, knowledge_bank):
    north_star = knowledge_bank.get_north_star_metric()
    feature = knowledge_bank.get_feature_for_goal(user.current_goal)
    hook = knowledge_bank.get_hook_for_segment(user.segment)
    return template_engine.generate(user, feature, hook, north_star)
```

**WHY:** In the good version, if you swap the knowledge_bank from SpeakX to Paytm, the code doesn't change. Only the data changes.

---


<a name="section-2"></a>
## 2. CORE CONCEPTS FROM ZERO

### 2.1 What is a "Knowledge Bank"?

**CONCEPT:** A structured repository of company-specific intelligence.

**WHY IT EXISTS:** Different companies have different:
- Goals (SpeakX wants daily practice, Netflix wants watch time, Paytm wants transactions)
- Features (AI tutor vs movie recommendations vs cashback)
- Tones (motivational vs entertaining vs urgent)

**WHAT IT CONTAINS:**
1. **North Star Metric:** The ONE metric that defines success
   - For SpeakX: "Daily Active Engaged Users"
   - For Netflix: "Hours Watched"
   - For Paytm: "Transaction Volume"

2. **Feature → Goal Mappings:** Which features drive which goals
   - "AI Tutor" → "Speaking Confidence"
   - "Leaderboard" → "Competitive Engagement"

3. **Allowed Tones:** How the brand communicates
   - SpeakX: Encouraging, friendly, aspirational
   - NOT: Aggressive, salesy, desperate

4. **Behavioral Hooks:** What motivates users (based on Octalysis)

**COMMON MISTAKE:** Freshers hardcode these values in Python dictionaries.

**CORRECT APPROACH:** Parse from text/markdown/PDF → Extract using NLP/LLM → Store in structured JSON → Reference dynamically

**WHY:** When evaluator gives you a NEW company's KB, your system should auto-infer these, not require code changes.

---

### 2.2 What is "MECE Segmentation"?

**MECE = Mutually Exclusive, Collectively Exhaustive**

**CONCEPT:** Every user belongs to EXACTLY ONE segment, and ALL users are covered.

**WHY IT MATTERS:**
- **Mutually Exclusive:** User can't be in two segments (prevents conflicting strategies)
- **Collectively Exhaustive:** No user is left out (everyone gets appropriate communication)

**EXAMPLE OF BAD SEGMENTATION:**
```
Segment 1: Active users (sessions > 5/week)
Segment 2: Gamification lovers (uses coins/streaks)
Segment 3: Churned users (no activity in 7 days)
```

**PROBLEM:** A user can be BOTH active AND a gamification lover. Not mutually exclusive.

**EXAMPLE OF GOOD SEGMENTATION:**
```
Segment 1: Highly Active Achievers (high activity + high gamification)
Segment 2: Casual Learners (moderate activity + low gamification)
Segment 3: Social Competitors (moderate activity + high leaderboard usage)
Segment 4: At-Risk Churners (low activity + declining engagement)
Segment 5: Dormant Users (no activity in 7+ days)
```

**HOW TO CREATE MECE SEGMENTS:**
1. Identify key behavioral dimensions (activity, feature usage, motivation)
2. Use clustering algorithms (K-means, hierarchical)
3. Validate: Sum of segment sizes = total users
4. Validate: No user appears in multiple segments

**COMMON MISTAKE:** Creating 20+ segments. Evaluators want 6-12. Why?
- Too few (2-3): Not personalized enough
- Too many (20+): Overfitting, hard to manage, no statistical significance

---

### 2.3 What are "Propensity Scores"?

**CONCEPT:** Probability that a user will respond positively to a specific type of motivation.

**EXAMPLE:**
```
User A:
- gamification_propensity: 0.85 (loves coins, streaks, badges)
- social_propensity: 0.20 (doesn't care about leaderboards)
- ai_tutor_propensity: 0.60 (uses it sometimes)
```

**HOW TO CALCULATE:**
```python
gamification_propensity = (
    0.4 * normalized(streak_current) +
    0.3 * normalized(coins_balance) +
    0.3 * normalized(gamification_feature_usage_frequency)
)
```

**WHY IT MATTERS:** Tells you WHAT to emphasize in messages.
- High gamification propensity → "You're just 2 exercises away from 100 coins!"
- Low gamification propensity → "Practice speaking with AI tutor today"

**COMMON MISTAKE:** Freshers calculate propensity but never USE it in message selection.

**CORRECT USAGE:** Template selection should filter by propensity match.

---

### 2.4 What is "Octalysis Framework"?

**CONCEPT:** A behavioral psychology framework identifying 8 core drives that motivate humans.

**THE 8 CORE DRIVES:**

1. **Epic Meaning & Calling**
   - "You're part of something bigger"
   - Example: "Join 1 million Indians becoming confident English speakers"

2. **Development & Accomplishment**
   - "You're making progress"
   - Example: "You've completed 15 exercises this week—your best yet!"

3. **Empowerment of Creativity & Feedback**
   - "You have control and can experiment"
   - Example: "Try the new role-play scenarios and see your improvement"

4. **Ownership & Possession**
   - "You've built something valuable"
   - Example: "You've earned 500 coins—unlock premium content"

5. **Social Influence & Relatedness**
   - "Others are doing it, you should too"
   - Example: "Rahul from your city is #1 on the leaderboard"

6. **Scarcity & Impatience**
   - "Limited time/availability"
   - Example: "Only 3 hours left to maintain your 7-day streak"

7. **Unpredictability & Curiosity**
   - "What will happen next?"
   - Example: "Unlock a surprise reward after your next exercise"

8. **Loss & Avoidance**
   - "Don't lose what you have"
   - Example: "Your streak will break in 2 hours—complete one quick exercise"

**WHY THIS MATTERS:** Different segments respond to different drives.
- Achievers → Development & Accomplishment
- Social users → Social Influence
- Casual users → Unpredictability & Curiosity
- At-risk users → Loss & Avoidance

**COMMON MISTAKE:** Using the same hook for everyone. "Don't lose your streak!" doesn't work for users who don't care about streaks.

**CORRECT APPROACH:** Match theme to segment propensity.

---

### 2.5 What is "Lifecycle Stage"?

**CONCEPT:** Where a user is in their journey with the product.

**THE STAGES:**

1. **Trial (D0-D7):** First 7 days after signup
   - Goal: Activation, habit formation
   - Strategy: Onboarding, education, quick wins
   - Frequency: Higher (7-9 notifications/day acceptable)

2. **Paid (D8-D30):** Converted to paid subscription
   - Goal: Retention, value delivery
   - Strategy: Feature discovery, progress celebration
   - Frequency: Moderate (5-7 notifications/day)

3. **Churned:** Stopped using after being active
   - Goal: Re-engagement
   - Strategy: Win-back offers, nostalgia, FOMO
   - Frequency: Lower (2-3 notifications/week)

4. **Inactive:** Never really engaged
   - Goal: Activation or graceful exit
   - Strategy: Value reminders, last-chance offers
   - Frequency: Very low (1-2 notifications/week)

**WHY IT MATTERS:** Same user, different stage = different communication strategy.

**EXAMPLE:**
- Trial user: "Complete your first exercise and earn 50 coins!"
- Paid user: "You're on a 10-day streak—keep going!"
- Churned user: "We miss you! Here's what's new since you left"

**COMMON MISTAKE:** Treating all users the same regardless of lifecycle stage.

---

### 2.6 What is "CTR" and "Engagement Rate"?

**CTR (Click-Through Rate):**
```
CTR = (Total Opens / Total Sends) × 100
```

**WHAT IT MEASURES:** Did the user open/click the notification?

**EXAMPLE:**
- Sent 1000 notifications
- 150 users opened
- CTR = 15%

**Engagement Rate:**
```
Engagement Rate = (Total Engagements / Total Opens) × 100
```

**WHAT IT MEASURES:** After opening, did the user DO something (complete exercise, use feature)?

**EXAMPLE:**
- 150 users opened
- 60 users completed an exercise
- Engagement Rate = 40%

**WHY BOTH MATTER:**
- High CTR, Low Engagement = Clickbait (bad)
- Low CTR, High Engagement = Poor messaging (fixable)
- High CTR, High Engagement = Winning template (promote)

**COMMON MISTAKE:** Optimizing only for CTR. Evaluators want BOTH.

---

### 2.7 What is "Timing Optimization"?

**CONCEPT:** Sending notifications when users are most likely to engage.

**THE 6 TIME WINDOWS:**
```
early_morning:    06:00–08:59  (commute, morning routine)
mid_morning:      09:00–11:59  (work break)
afternoon:        12:00–14:59  (lunch break)
late_afternoon:   15:00–17:59  (post-lunch slump)
evening:          18:00–20:59  (back home, relaxation)
night:            21:00–23:59  (before bed)
```

**WHY THESE WINDOWS:** Based on typical Indian user behavior patterns.

**HOW TO OPTIMIZE:**
1. **Iteration 0:** Use user's `preferred_hour` from data
2. **Iteration 1:** Learn from experiment results
   - If "evening" window has 20% CTR for Segment A
   - But "early_morning" has 8% CTR
   - → Shift more notifications to evening for Segment A

**COMMON MISTAKE:** Sending all notifications at the same time to all users.

**CORRECT APPROACH:** Segment-specific timing strategies.

---

### 2.8 What is "Frequency Optimization"?

**CONCEPT:** How many notifications per day based on user tolerance.

**THE STRATEGY:**

| Activeness Score | Notifs/Day | Churn Risk | Reasoning |
|-----------------|------------|------------|-----------|
| > 0.7 (High)    | 7-9        | Low        | User is engaged, can handle more |
| 0.4-0.7 (Med)   | 5-6        | Medium     | Balanced approach |
| < 0.4 (Low)     | 3-4        | High       | Risk of annoyance, be conservative |

**ACTIVENESS SCORE CALCULATION:**
```python
activeness = (
    0.3 * normalized(sessions_last_7d) +
    0.3 * normalized(exercises_completed_7d) +
    0.2 * normalized(notif_open_rate_30d) +
    0.2 * (1 if streak_current > 0 else 0)
)
```

**THE GUARDRAIL:**
```
IF uninstall_rate > 2% for any segment:
    THEN reduce frequency by 2 notifications/day
    REGARDLESS of activeness score
```

**WHY THE GUARDRAIL:** Prevents over-communication that drives uninstalls.

**COMMON MISTAKE:** Ignoring uninstall_rate and spamming users.

---


<a name="section-3"></a>
## 3. TASK-BY-TASK DEEP DIVE

### TASK 1: System Architecture & Intelligence Design

---

#### 1.1 Knowledge Bank Engine

**WHAT IT DOES:** Ingests company documentation and extracts structured intelligence.

**INPUT:** Text/Markdown/PDF files containing:
- Company mission
- Product features
- Target metrics
- Communication guidelines

**OUTPUT:** Three JSON files:

**1. `company_north_star.json`**
```json
{
  "north_star_metric": "Daily Active Engaged Users",
  "definition": "Users who complete at least 1 exercise per day",
  "why_it_matters": "Habit formation drives retention and word-of-mouth",
  "measurement": "COUNT(DISTINCT user_id WHERE exercises_completed > 0 AND date = today)"
}
```

**HOW TO BUILD IT:**

**Approach 1: LLM-based extraction (Recommended)**
```python
def extract_north_star(kb_text):
    prompt = """
    Analyze this company knowledge base and extract:
    1. The primary success metric (North Star)
    2. How it's defined
    3. Why it matters to the business
    
    Knowledge Base:
    {kb_text}
    
    Return as JSON.
    """
    response = llm.generate(prompt)
    return json.loads(response)
```

**Approach 2: Rule-based extraction (Fallback)**
```python
def extract_north_star(kb_text):
    # Look for patterns like "key metric", "north star", "primary goal"
    patterns = [
        r"north star.*?is (.*?)[\.\n]",
        r"key metric.*?is (.*?)[\.\n]",
        r"we measure success by (.*?)[\.\n]"
    ]
    for pattern in patterns:
        match = re.search(pattern, kb_text, re.IGNORECASE)
        if match:
            return {"north_star_metric": match.group(1)}
    return None
```

**WHY BOTH APPROACHES:** LLM is smarter but requires API. Rule-based is deterministic but limited.

**EVALUATOR EXPECTATION:** System should work even if KB format changes slightly.

---

**2. `feature_goal_map.json`**
```json
{
  "features": [
    {
      "feature_name": "AI Tutor",
      "feature_id": "ai_tutor",
      "primary_goal": "speaking_confidence",
      "secondary_goals": ["pronunciation_improvement", "conversation_practice"],
      "user_segments_most_relevant": ["casual_learners", "ai_enthusiasts"],
      "engagement_driver_score": 0.85
    },
    {
      "feature_name": "Leaderboard",
      "feature_id": "leaderboard",
      "primary_goal": "competitive_engagement",
      "secondary_goals": ["social_motivation", "consistency"],
      "user_segments_most_relevant": ["achievers", "social_competitors"],
      "engagement_driver_score": 0.72
    }
  ]
}
```

**HOW TO EXTRACT:**
1. Identify all features mentioned in KB
2. For each feature, find associated goals/outcomes
3. Infer which user types would care most
4. Assign engagement driver score based on frequency of mention + sentiment

**COMMON MISTAKE:** Listing features without connecting them to goals.

**WHY IT MATTERS:** When generating messages, you need to know which feature to highlight for which goal.

---

**3. `allowed_tone_hook_matrix.json`**
```json
{
  "allowed_tones": ["encouraging", "friendly", "aspirational", "urgent", "celebratory"],
  "forbidden_tones": ["aggressive", "desperate", "salesy", "guilt-tripping"],
  "tone_by_lifecycle": {
    "trial": ["encouraging", "friendly", "aspirational"],
    "paid": ["celebratory", "friendly", "aspirational"],
    "churned": ["friendly", "urgent", "aspirational"],
    "inactive": ["curious", "friendly"]
  },
  "hooks_by_segment": {
    "achievers": ["accomplishment", "progress", "mastery"],
    "social_competitors": ["social_influence", "leaderboard", "comparison"],
    "casual_learners": ["curiosity", "ease", "flexibility"],
    "at_risk": ["loss_avoidance", "streak", "investment"]
  }
}
```

**HOW TO BUILD:**
1. Extract brand voice guidelines from KB
2. Map tones to lifecycle stages (trial users need encouragement, churned users need urgency)
3. Map Octalysis hooks to segment propensities

**WHY IT MATTERS:** Prevents generating messages that violate brand voice or annoy users.

---

#### 1.2 User Data Ingestion

**WHAT IT DOES:** Validates, cleans, and structures user behavioral data.

**INPUT:** `user_data.csv` with schema:

```
user_id, lifecycle_stage, days_since_signup, age_band_region,
sessions_last_7d, exercises_completed_7d, streak_current, coins_balance,
feature_ai_tutor_used, feature_leaderboard_viewed, preferred_hour,
notif_open_rate_30d, motivation_score
```

**VALIDATION RULES:**

1. **Schema Validation:**
```python
required_columns = [
    'user_id', 'lifecycle_stage', 'days_since_signup',
    'sessions_last_7d', 'exercises_completed_7d'
]

def validate_schema(df):
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
```

2. **Data Type Validation:**
```python
def validate_types(df):
    assert df['user_id'].dtype == 'object', "user_id must be string"
    assert df['days_since_signup'].dtype in ['int64', 'int32'], "days_since_signup must be int"
    assert df['lifecycle_stage'].isin(['trial', 'paid', 'churned', 'inactive']).all()
```

3. **Range Validation:**
```python
def validate_ranges(df):
    assert (df['preferred_hour'] >= 0).all() and (df['preferred_hour'] <= 23).all()
    assert (df['notif_open_rate_30d'] >= 0).all() and (df['notif_open_rate_30d'] <= 1).all()
```

4. **Missing Data Handling:**
```python
def handle_missing(df):
    # For numeric: fill with median
    df['sessions_last_7d'].fillna(df['sessions_last_7d'].median(), inplace=True)
    
    # For boolean: fill with False (conservative)
    df['feature_ai_tutor_used'].fillna(False, inplace=True)
    
    # For categorical: fill with mode
    df['lifecycle_stage'].fillna(df['lifecycle_stage'].mode()[0], inplace=True)
```

**COMMON MISTAKE:** Skipping validation and assuming data is clean.

**WHY IT MATTERS:** Evaluator will test with messy data. Your system must handle it gracefully.

---

#### 1.3 MECE Segmentation Engine

**WHAT IT DOES:** Clusters users into mutually exclusive, collectively exhaustive segments.

**APPROACH:**

**Step 1: Feature Engineering**
```python
def engineer_features(df):
    # Activeness score
    df['activeness'] = (
        0.3 * normalize(df['sessions_last_7d']) +
        0.3 * normalize(df['exercises_completed_7d']) +
        0.2 * df['notif_open_rate_30d'] +
        0.2 * (df['streak_current'] > 0).astype(int)
    )
    
    # Gamification propensity
    df['gamification_propensity'] = (
        0.4 * normalize(df['streak_current']) +
        0.3 * normalize(df['coins_balance']) +
        0.3 * (df['feature_ai_tutor_used'].astype(int))
    )
    
    # Social propensity
    df['social_propensity'] = (
        0.6 * df['feature_leaderboard_viewed'].astype(int) +
        0.4 * normalize(df['sessions_last_7d'])  # Active users more likely to be social
    )
    
    # Churn risk
    df['churn_risk'] = (
        0.4 * (1 - normalize(df['sessions_last_7d'])) +
        0.3 * (1 - df['notif_open_rate_30d']) +
        0.3 * (df['streak_current'] == 0).astype(int)
    )
    
    return df
```

**Step 2: Clustering**
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def create_segments(df, n_segments=8):
    # Select features for clustering
    features = ['activeness', 'gamification_propensity', 
                'social_propensity', 'churn_risk']
    
    X = df[features].values
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Cluster
    kmeans = KMeans(n_clusters=n_segments, random_state=42)
    df['segment_id'] = kmeans.fit_predict(X_scaled)
    
    return df, kmeans
```

**Step 3: Segment Naming**
```python
def name_segments(df):
    segment_names = {}
    
    for seg_id in df['segment_id'].unique():
        seg_data = df[df['segment_id'] == seg_id]
        
        # Calculate segment characteristics
        avg_activeness = seg_data['activeness'].mean()
        avg_gamification = seg_data['gamification_propensity'].mean()
        avg_social = seg_data['social_propensity'].mean()
        avg_churn_risk = seg_data['churn_risk'].mean()
        
        # Name based on dominant characteristics
        if avg_churn_risk > 0.7:
            name = "At-Risk Churners"
        elif avg_activeness > 0.7 and avg_gamification > 0.7:
            name = "Highly Active Achievers"
        elif avg_social > 0.7:
            name = "Social Competitors"
        elif avg_activeness < 0.3:
            name = "Dormant Users"
        elif avg_gamification < 0.3 and avg_activeness > 0.4:
            name = "Casual Learners"
        else:
            name = f"Segment_{seg_id}"
        
        segment_names[seg_id] = name
    
    df['segment_name'] = df['segment_id'].map(segment_names)
    return df
```

**OUTPUT: `user_segments.csv`**
```csv
user_id,segment_id,segment_name,activeness,gamification_propensity,social_propensity,churn_risk
U001,1,Highly Active Achievers,0.85,0.90,0.60,0.15
U002,3,Casual Learners,0.55,0.30,0.40,0.45
U003,5,At-Risk Churners,0.20,0.15,0.10,0.85
```

**VALIDATION:**
```python
def validate_mece(df):
    # Mutually Exclusive: Each user in exactly one segment
    assert df['user_id'].nunique() == len(df), "Users appear in multiple segments"
    
    # Collectively Exhaustive: All users are segmented
    assert df['segment_id'].notna().all(), "Some users not segmented"
    
    # Reasonable segment sizes (no segment < 5% of total)
    segment_sizes = df['segment_id'].value_counts(normalize=True)
    assert (segment_sizes > 0.05).all(), "Some segments too small"
```

**COMMON MISTAKE:** Creating segments but not validating MECE property.

---

#### 1.4 Goal & Journey Builder

**WHAT IT DOES:** Defines what each segment should achieve at each lifecycle stage.

**OUTPUT: `segment_goals.csv`**
```csv
segment_id,segment_name,lifecycle_stage,lifecycle_day,primary_goal,sub_goals,success_metric
1,Highly Active Achievers,trial,D0,activation,"onboarding_complete,first_exercise",exercises_completed >= 1
1,Highly Active Achievers,trial,D1,habit_formation,"second_exercise,streak_start",streak_current >= 2
1,Highly Active Achievers,trial,D3,feature_discovery,"ai_tutor_used,coins_earned",feature_ai_tutor_used = True
1,Highly Active Achievers,trial,D7,conversion_readiness,"consistent_usage,value_realized",sessions_last_7d >= 5
1,Highly Active Achievers,paid,D8,retention,"continued_engagement",exercises_completed >= 1
1,Highly Active Achievers,paid,D15,expansion,"feature_exploration,leaderboard",feature_leaderboard_viewed = True
```

**HOW TO BUILD:**

```python
def build_journey(segment_id, segment_name, lifecycle_stage):
    if lifecycle_stage == 'trial':
        return [
            {
                'day': 'D0',
                'primary_goal': 'activation',
                'sub_goals': ['onboarding_complete', 'first_exercise'],
                'success_metric': 'exercises_completed >= 1'
            },
            {
                'day': 'D1',
                'primary_goal': 'habit_formation',
                'sub_goals': ['second_exercise', 'streak_start'],
                'success_metric': 'streak_current >= 2'
            },
            # ... more days
        ]
    elif lifecycle_stage == 'paid':
        return [
            {
                'day': 'D8',
                'primary_goal': 'retention',
                'sub_goals': ['continued_engagement'],
                'success_metric': 'exercises_completed >= 1'
            },
            # ... more days
        ]
```

**WHY IT MATTERS:** This defines the "journey" that notifications will guide users through.

**COMMON MISTAKE:** Same goals for all segments. Achievers and Casual Learners need different journeys.

---


### TASK 2: Communication & Timing Intelligence

---

#### 2.1 Theme Engine

**WHAT IT DOES:** Maps Octalysis core drives to segments and lifecycle stages.

**OUTPUT: `communication_themes.csv`**
```csv
segment_id,segment_name,lifecycle_stage,primary_theme,secondary_theme,theme_rationale
1,Highly Active Achievers,trial,accomplishment,epic_meaning,"Achievers respond to progress and being part of something bigger"
1,Highly Active Achievers,paid,accomplishment,ownership,"Celebrate achievements and investment in learning"
3,Casual Learners,trial,curiosity,empowerment,"Spark interest without pressure"
3,Casual Learners,paid,flexibility,curiosity,"Emphasize ease and discovery"
5,At-Risk Churners,trial,loss_avoidance,scarcity,"Prevent abandonment with urgency"
5,At-Risk Churners,paid,loss_avoidance,social_proof,"Show what they're missing"
```

**HOW TO BUILD:**

```python
def assign_themes(segment_profile):
    """
    segment_profile = {
        'activeness': 0.85,
        'gamification_propensity': 0.90,
        'social_propensity': 0.60,
        'churn_risk': 0.15
    }
    """
    
    themes = []
    
    # High gamification → Accomplishment
    if segment_profile['gamification_propensity'] > 0.7:
        themes.append(('accomplishment', 0.9))
        themes.append(('ownership', 0.7))
    
    # High social → Social Influence
    if segment_profile['social_propensity'] > 0.7:
        themes.append(('social_influence', 0.85))
    
    # High churn risk → Loss Avoidance
    if segment_profile['churn_risk'] > 0.6:
        themes.append(('loss_avoidance', 0.95))
        themes.append(('scarcity', 0.75))
    
    # Low engagement → Curiosity
    if segment_profile['activeness'] < 0.4:
        themes.append(('curiosity', 0.80))
        themes.append(('empowerment', 0.60))
    
    # Sort by score and return top 2
    themes.sort(key=lambda x: x[1], reverse=True)
    return themes[0][0], themes[1][0] if len(themes) > 1 else None
```

**LIFECYCLE ADJUSTMENTS:**
```python
def adjust_for_lifecycle(primary_theme, lifecycle_stage):
    if lifecycle_stage == 'trial':
        # Trial users need encouragement, not pressure
        if primary_theme == 'loss_avoidance':
            return 'curiosity'  # Soften the approach
    
    elif lifecycle_stage == 'churned':
        # Churned users need urgency
        if primary_theme == 'curiosity':
            return 'loss_avoidance'  # Increase urgency
    
    return primary_theme
```

**WHY IT MATTERS:** Wrong theme = wrong motivation = low engagement.

**EXAMPLE:**
- Sending "Don't lose your streak!" to a casual learner who doesn't care about streaks = wasted notification
- Sending "Try something new today" to an achiever = missed opportunity to celebrate progress

---

#### 2.2 Template Generator

**WHAT IT DOES:** Creates 5 message variants for each combination of segment × lifecycle × goal × theme.

**OUTPUT: `message_templates.csv`**
```csv
template_id,segment_id,lifecycle_stage,goal,theme,language,content,tone,hook,feature_reference
T001,1,trial,activation,accomplishment,en,"Start your English speaking journey today! Complete your first exercise.",encouraging,progress,exercises
T001_hi,1,trial,activation,accomplishment,hi,"आज अपनी अंग्रेजी बोलने की यात्रा शुरू करें! अपना पहला अभ्यास पूरा करें।",encouraging,progress,exercises
T002,1,trial,activation,accomplishment,en,"Join 1M+ Indians becoming confident speakers. Your first step awaits!",aspirational,epic_meaning,community
T003,1,trial,habit_formation,accomplishment,en,"Day 2 of your journey! Keep the momentum going—complete today's exercise.",motivational,consistency,streak
T004,1,trial,habit_formation,ownership,en,"You've earned 50 coins! Complete another exercise to unlock more rewards.",celebratory,rewards,coins
T005,1,trial,feature_discovery,curiosity,en,"Ready to speak with an AI tutor? Try your first conversation today.",inviting,discovery,ai_tutor
```

**HOW TO BUILD:**

**Approach 1: Template-based generation**
```python
TEMPLATES = {
    'accomplishment': [
        "You've completed {count} exercises this week—{encouragement}!",
        "Day {day} of your journey! {action_prompt}",
        "{milestone_achieved}! Keep the momentum going.",
    ],
    'loss_avoidance': [
        "Your {asset} will expire in {time}—{action_prompt}",
        "Don't lose your {achievement}! {action_prompt}",
    ],
    'social_influence': [
        "{peer_name} from {location} is #{rank} on the leaderboard. Can you beat them?",
        "Join {count} users who practiced today!",
    ]
}

def generate_template(segment, lifecycle, goal, theme):
    base_templates = TEMPLATES[theme]
    
    # Fill in variables based on segment and goal
    if theme == 'accomplishment':
        return base_templates[0].format(
            count="{exercises_completed_7d}",
            encouragement="your best yet"
        )
```

**Approach 2: LLM-based generation (Better)**
```python
def generate_with_llm(segment, lifecycle, goal, theme, language):
    prompt = f"""
    Generate a notification message with these constraints:
    
    Segment: {segment['name']} (activeness: {segment['activeness']}, gamification: {segment['gamification_propensity']})
    Lifecycle: {lifecycle}
    Goal: {goal}
    Theme: {theme} (Octalysis core drive)
    Language: {language}
    
    Requirements:
    - 10-15 words max
    - Tone: {get_allowed_tone(lifecycle)}
    - Include relevant feature reference
    - Personalization placeholder: {{user_name}}, {{streak_current}}, etc.
    - Bilingual if language=hi
    
    Return JSON: {{"content": "...", "tone": "...", "hook": "...", "feature": "..."}}
    """
    
    response = llm.generate(prompt)
    return json.loads(response)
```

**BILINGUAL REQUIREMENT:**
```python
def generate_bilingual(template_en):
    # Option 1: Translation API
    template_hi = translate(template_en, target='hi')
    
    # Option 2: LLM translation (better for context)
    prompt = f"Translate this notification to Hindi, maintaining tone and personalization: {template_en}"
    template_hi = llm.generate(prompt)
    
    return template_en, template_hi
```

**VALIDATION:**
```python
def validate_template(template):
    # Length check
    word_count = len(template['content'].split())
    assert 5 <= word_count <= 20, f"Template too long/short: {word_count} words"
    
    # Tone check
    assert template['tone'] in ALLOWED_TONES, f"Invalid tone: {template['tone']}"
    
    # Personalization check
    assert '{' in template['content'] or '{{' in template['content'], "No personalization"
    
    # Feature reference check
    assert template['feature_reference'] in VALID_FEATURES, "Invalid feature"
```

**COMMON MISTAKE:** Generating generic templates that don't use segment characteristics.

**CORRECT APPROACH:** Templates should reflect segment propensities.
- High gamification segment → Mention coins, streaks, badges
- Low gamification segment → Mention learning outcomes, flexibility

---

#### 2.3 Timing Optimizer

**WHAT IT DOES:** Determines optimal notification windows for each segment.

**OUTPUT: `timing_recommendations.csv`**
```csv
segment_id,segment_name,lifecycle_stage,time_window,priority,expected_ctr,rationale
1,Highly Active Achievers,trial,early_morning,1,0.18,"Active users check phones early"
1,Highly Active Achievers,trial,evening,2,0.15,"Post-work engagement"
3,Casual Learners,trial,evening,1,0.12,"Relaxed time for learning"
3,Casual Learners,trial,night,2,0.10,"Before bed browsing"
5,At-Risk Churners,trial,afternoon,1,0.08,"Mid-day reminder"
```

**HOW TO BUILD (Iteration 0):**

```python
def initial_timing_strategy(segment_profile, user_data):
    """
    Use user's preferred_hour as starting point
    """
    preferred_hours = user_data.groupby('segment_id')['preferred_hour'].agg(['mean', 'std'])
    
    recommendations = []
    
    for seg_id in segment_profile['segment_id'].unique():
        avg_hour = preferred_hours.loc[seg_id, 'mean']
        
        # Map hour to window
        primary_window = hour_to_window(avg_hour)
        
        # Add secondary window (offset by 6-8 hours)
        secondary_hour = (avg_hour + 7) % 24
        secondary_window = hour_to_window(secondary_hour)
        
        recommendations.append({
            'segment_id': seg_id,
            'time_window': primary_window,
            'priority': 1,
            'expected_ctr': 0.12  # Initial estimate
        })
        
        recommendations.append({
            'segment_id': seg_id,
            'time_window': secondary_window,
            'priority': 2,
            'expected_ctr': 0.08
        })
    
    return pd.DataFrame(recommendations)

def hour_to_window(hour):
    if 6 <= hour < 9:
        return 'early_morning'
    elif 9 <= hour < 12:
        return 'mid_morning'
    elif 12 <= hour < 15:
        return 'afternoon'
    elif 15 <= hour < 18:
        return 'late_afternoon'
    elif 18 <= hour < 21:
        return 'evening'
    else:
        return 'night'
```

**ITERATION 1 (After Learning):**
```python
def learn_timing(experiment_results):
    """
    Analyze which windows performed best for each segment
    """
    timing_performance = experiment_results.groupby(
        ['segment_id', 'notification_window']
    ).agg({
        'ctr': 'mean',
        'engagement_rate': 'mean',
        'total_sends': 'sum'
    }).reset_index()
    
    # Filter for statistical significance (min 100 sends)
    timing_performance = timing_performance[timing_performance['total_sends'] >= 100]
    
    # Rank windows by performance
    timing_performance['rank'] = timing_performance.groupby('segment_id')['ctr'].rank(ascending=False)
    
    # Update recommendations
    new_recommendations = timing_performance[timing_performance['rank'] <= 2].copy()
    new_recommendations['priority'] = new_recommendations['rank'].astype(int)
    new_recommendations['expected_ctr'] = new_recommendations['ctr']
    
    return new_recommendations
```

**WHY IT MATTERS:** Sending at wrong time = notification ignored or dismissed.

---

#### 2.4 Frequency Optimizer

**WHAT IT DOES:** Determines how many notifications per day for each user.

**OUTPUT: Embedded in `user_notification_schedule.csv`**

**HOW TO BUILD:**

```python
def calculate_frequency(user):
    """
    Returns number of notifications per day
    """
    activeness = user['activeness']
    churn_risk = user['churn_risk']
    lifecycle = user['lifecycle_stage']
    
    # Base frequency by activeness
    if activeness > 0.7:
        base_freq = 8
    elif activeness > 0.4:
        base_freq = 6
    else:
        base_freq = 4
    
    # Adjust for lifecycle
    if lifecycle == 'trial':
        base_freq += 1  # More aggressive in trial
    elif lifecycle == 'churned':
        base_freq = 2  # Very conservative
    
    # Adjust for churn risk
    if churn_risk > 0.7:
        base_freq = max(3, base_freq - 2)  # Reduce to avoid annoyance
    
    return base_freq

def apply_guardrail(segment_id, base_freq, experiment_results):
    """
    Check uninstall rate and reduce if needed
    """
    segment_uninstall = experiment_results[
        experiment_results['segment_id'] == segment_id
    ]['uninstall_rate'].mean()
    
    if segment_uninstall > 0.02:  # 2% threshold
        adjusted_freq = max(2, base_freq - 2)
        return adjusted_freq, f"Reduced due to {segment_uninstall:.1%} uninstall rate"
    
    return base_freq, "No adjustment needed"
```

**COMMON MISTAKE:** Ignoring uninstall_rate and causing user annoyance.

---


### TASK 3: Execution & Self-Learning

---

#### 3.1 Schedule Generator

**WHAT IT DOES:** Creates day-by-day notification schedules for each user.

**OUTPUT: `user_notification_schedule.csv`**
```csv
user_id,segment_id,lifecycle_stage,lifecycle_day,notif_1_template_id,notif_1_time,notif_1_channel,notif_2_template_id,notif_2_time,notif_2_channel,notif_3_template_id,notif_3_time,notif_3_channel
U001,1,trial,D0,T001,07:30,push,T005,12:00,push,T010,19:00,push
U001,1,trial,D1,T003,07:30,push,T006,13:00,push,T011,19:30,push
U001,1,trial,D2,T004,07:45,push,T007,12:30,push,T012,19:00,push
U002,3,trial,D0,T020,19:00,push,T021,21:00,push,,,
U002,3,trial,D1,T022,19:30,push,T023,21:30,push,,,
```

**HOW TO BUILD:**

```python
def generate_schedule(user, segment_goals, templates, timing_recs, frequency):
    """
    Generate notification schedule for a user
    """
    schedule = []
    
    # Get user's lifecycle stage and days
    lifecycle = user['lifecycle_stage']
    days_since_signup = user['days_since_signup']
    
    # Get goals for this segment and lifecycle
    goals = segment_goals[
        (segment_goals['segment_id'] == user['segment_id']) &
        (segment_goals['lifecycle_stage'] == lifecycle)
    ]
    
    # Get timing windows for this segment
    windows = timing_recs[
        timing_recs['segment_id'] == user['segment_id']
    ].sort_values('priority')
    
    # For each day in the journey
    for day in range(min(days_since_signup, 30)):  # Cap at 30 days
        lifecycle_day = f"D{day}"
        
        # Get goal for this day
        day_goal = goals[goals['lifecycle_day'] == lifecycle_day]
        if day_goal.empty:
            continue
        
        goal = day_goal.iloc[0]['primary_goal']
        
        # Get templates for this goal
        available_templates = templates[
            (templates['segment_id'] == user['segment_id']) &
            (templates['lifecycle_stage'] == lifecycle) &
            (templates['goal'] == goal)
        ]
        
        # Select templates based on frequency
        num_notifs = frequency[user['user_id']]
        selected_templates = available_templates.sample(min(num_notifs, len(available_templates)))
        
        # Assign times from windows
        notif_schedule = {
            'user_id': user['user_id'],
            'segment_id': user['segment_id'],
            'lifecycle_stage': lifecycle,
            'lifecycle_day': lifecycle_day
        }
        
        for i, (idx, template) in enumerate(selected_templates.iterrows()):
            window = windows.iloc[i % len(windows)]['time_window']
            time = sample_time_from_window(window)
            
            notif_schedule[f'notif_{i+1}_template_id'] = template['template_id']
            notif_schedule[f'notif_{i+1}_time'] = time
            notif_schedule[f'notif_{i+1}_channel'] = 'push'
        
        schedule.append(notif_schedule)
    
    return pd.DataFrame(schedule)

def sample_time_from_window(window):
    """
    Sample a random time within the window
    """
    windows = {
        'early_morning': (6, 9),
        'mid_morning': (9, 12),
        'afternoon': (12, 15),
        'late_afternoon': (15, 18),
        'evening': (18, 21),
        'night': (21, 24)
    }
    
    start, end = windows[window]
    hour = random.randint(start, end - 1)
    minute = random.choice([0, 15, 30, 45])
    
    return f"{hour:02d}:{minute:02d}"
```

**JOURNEY PROGRESSION:**

The schedule must show **gradual progression** through goals:
- D0: Activation (first exercise)
- D1-D2: Habit formation (streak building)
- D3-D5: Feature discovery (AI tutor, leaderboard)
- D6-D7: Conversion readiness (value realization)
- D8+: Retention and expansion

**COMMON MISTAKE:** Random template selection without considering journey progression.

**CORRECT APPROACH:** Templates should align with the user's current goal in their journey.

---

#### 3.2 Performance Classification

**WHAT IT DOES:** Classifies templates as GOOD, NEUTRAL, or BAD based on experiment results.

**INPUT: `experiment_results.csv`**
```csv
template_id,segment_id,lifecycle_stage,goal,theme,notification_window,total_sends,total_opens,total_engagements,ctr,engagement_rate,uninstall_rate,performance_status
T001,1,trial,activation,accomplishment,early_morning,1000,180,75,0.18,0.42,0.01,GOOD
T002,1,trial,activation,accomplishment,early_morning,1000,80,25,0.08,0.31,0.015,NEUTRAL
T003,1,trial,habit_formation,accomplishment,evening,1000,40,10,0.04,0.25,0.025,BAD
```

**HOW TO CLASSIFY:**

```python
def classify_performance(experiment_results):
    """
    Classify each template based on CTR and engagement rate
    """
    def classify_row(row):
        ctr = row['ctr']
        engagement = row['engagement_rate']
        
        # GOOD: High CTR AND high engagement
        if ctr > 0.15 and engagement > 0.40:
            return 'GOOD'
        
        # BAD: Low CTR OR low engagement
        elif ctr < 0.05 or engagement < 0.20:
            return 'BAD'
        
        # NEUTRAL: Everything else
        else:
            return 'NEUTRAL'
    
    experiment_results['performance_status'] = experiment_results.apply(classify_row, axis=1)
    
    return experiment_results
```

**WHY BOTH METRICS MATTER:**

Example scenarios:
1. **High CTR (18%), Low Engagement (15%):** Clickbait template. Users open but don't act. → BAD
2. **Low CTR (4%), High Engagement (45%):** Poor messaging but good content. → BAD (not reaching users)
3. **High CTR (16%), High Engagement (42%):** Winning template. → GOOD

**COMMON MISTAKE:** Classifying based on CTR alone.

---

#### 3.3 Learning Engine

**WHAT IT DOES:** Uses experiment results to improve future outputs.

**LEARNING ACTIONS:**

**1. Template Suppression**
```python
def suppress_bad_templates(templates, experiment_results):
    """
    Remove BAD templates from future use
    """
    bad_templates = experiment_results[
        experiment_results['performance_status'] == 'BAD'
    ]['template_id'].unique()
    
    templates_filtered = templates[~templates['template_id'].isin(bad_templates)]
    
    return templates_filtered, bad_templates
```

**2. Template Promotion**
```python
def promote_good_templates(templates, experiment_results):
    """
    Increase usage probability of GOOD templates
    """
    good_templates = experiment_results[
        experiment_results['performance_status'] == 'GOOD'
    ]['template_id'].unique()
    
    # Add weight column
    templates['weight'] = 1.0
    templates.loc[templates['template_id'].isin(good_templates), 'weight'] = 3.0
    
    return templates
```

**3. Timing Optimization**
```python
def optimize_timing(timing_recs, experiment_results):
    """
    Learn better timing patterns from results
    """
    # Calculate performance by segment × window
    window_performance = experiment_results.groupby(
        ['segment_id', 'notification_window']
    ).agg({
        'ctr': 'mean',
        'engagement_rate': 'mean',
        'total_sends': 'sum'
    }).reset_index()
    
    # Filter for statistical significance
    window_performance = window_performance[window_performance['total_sends'] >= 100]
    
    # Identify underperforming windows
    for seg_id in window_performance['segment_id'].unique():
        seg_data = window_performance[window_performance['segment_id'] == seg_id]
        
        # Find worst performing window
        worst_window = seg_data.loc[seg_data['ctr'].idxmin()]
        
        if worst_window['ctr'] < 0.05:
            # Suppress this window for this segment
            timing_recs = timing_recs[
                ~((timing_recs['segment_id'] == seg_id) & 
                  (timing_recs['time_window'] == worst_window['notification_window']))
            ]
    
    return timing_recs
```

**4. Theme Refinement**
```python
def refine_themes(themes, experiment_results):
    """
    Learn which themes work best for each segment
    """
    theme_performance = experiment_results.groupby(
        ['segment_id', 'theme']
    ).agg({
        'ctr': 'mean',
        'engagement_rate': 'mean'
    }).reset_index()
    
    # For each segment, identify best performing theme
    for seg_id in theme_performance['segment_id'].unique():
        seg_themes = theme_performance[theme_performance['segment_id'] == seg_id]
        best_theme = seg_themes.loc[seg_themes['ctr'].idxmax()]['theme']
        
        # Update primary theme
        themes.loc[themes['segment_id'] == seg_id, 'primary_theme'] = best_theme
    
    return themes
```

**5. Frequency Adjustment**
```python
def adjust_frequency(frequency_map, experiment_results):
    """
    Adjust notification frequency based on uninstall rates
    """
    uninstall_by_segment = experiment_results.groupby('segment_id')['uninstall_rate'].mean()
    
    adjustments = {}
    
    for seg_id, uninstall_rate in uninstall_by_segment.items():
        if uninstall_rate > 0.02:  # 2% threshold
            # Reduce frequency for all users in this segment
            for user_id, freq in frequency_map.items():
                if user_segment[user_id] == seg_id:
                    new_freq = max(2, freq - 2)
                    adjustments[user_id] = {
                        'old': freq,
                        'new': new_freq,
                        'reason': f'High uninstall rate: {uninstall_rate:.1%}'
                    }
                    frequency_map[user_id] = new_freq
    
    return frequency_map, adjustments
```

**CAUSAL REASONING:**

The system must explain WHY it made changes:

```python
def explain_change(entity_type, entity_id, change_type, metric_trigger, before, after):
    """
    Generate causal explanation for a change
    """
    explanations = {
        'template_suppression': f"Template {entity_id} had {metric_trigger['ctr']:.1%} CTR (threshold: 5%), indicating poor user response. Suppressed to improve overall engagement.",
        
        'timing_shift': f"Window {before} had {metric_trigger['ctr']:.1%} CTR for segment {entity_id}, while {after} had {metric_trigger['new_ctr']:.1%}. Shifted to optimize engagement.",
        
        'frequency_reduction': f"Segment {entity_id} had {metric_trigger['uninstall_rate']:.1%} uninstall rate (threshold: 2%). Reduced frequency from {before} to {after} notifications/day to prevent churn.",
        
        'theme_change': f"Theme {before} had {metric_trigger['ctr']:.1%} CTR, while {after} had {metric_trigger['new_ctr']:.1%} for segment {entity_id}. Updated primary theme to improve resonance."
    }
    
    return explanations.get(change_type, "Change made based on performance data")
```

**MEASURABLE DELTA:**

The system must show quantifiable improvement:

```python
def calculate_delta(iteration_0_results, iteration_1_results):
    """
    Calculate improvement metrics
    """
    delta = {
        'avg_ctr_improvement': iteration_1_results['ctr'].mean() - iteration_0_results['ctr'].mean(),
        'avg_engagement_improvement': iteration_1_results['engagement_rate'].mean() - iteration_0_results['engagement_rate'].mean(),
        'uninstall_rate_reduction': iteration_0_results['uninstall_rate'].mean() - iteration_1_results['uninstall_rate'].mean(),
        'templates_improved': len(iteration_1_results[iteration_1_results['performance_status'] == 'GOOD']) - len(iteration_0_results[iteration_0_results['performance_status'] == 'GOOD'])
    }
    
    return delta
```

**COMMON MISTAKE:** Making random changes and calling it "learning."

**CORRECT APPROACH:** Every change must be:
1. Triggered by a specific metric threshold
2. Causally explained
3. Measurably better

---

#### 3.4 Delta Reporter

**WHAT IT DOES:** Documents every change made during learning.

**OUTPUT: `learning_delta_report.csv`**
```csv
entity_type,entity_id,change_type,metric_trigger,before_value,after_value,explanation
template,T003,suppression,ctr=0.04,active,suppressed,"CTR below 5% threshold, indicating poor user response"
template,T001,promotion,ctr=0.18,weight=1.0,weight=3.0,"CTR above 15% threshold, increased usage probability"
timing,segment_1,window_shift,night_ctr=0.03,night,early_morning,"Night window underperformed (3% CTR), shifted to early_morning (18% CTR)"
frequency,segment_5,reduction,uninstall_rate=0.025,6,4,"Uninstall rate exceeded 2% threshold, reduced to prevent churn"
theme,segment_3,primary_change,curiosity_ctr=0.08,curiosity,accomplishment,"Accomplishment theme outperformed (14% vs 8% CTR)"
```

**HOW TO BUILD:**

```python
def generate_delta_report(changes_log):
    """
    Compile all changes into a structured report
    """
    report = []
    
    for change in changes_log:
        report.append({
            'entity_type': change['entity_type'],
            'entity_id': change['entity_id'],
            'change_type': change['change_type'],
            'metric_trigger': format_metric(change['metric']),
            'before_value': change['before'],
            'after_value': change['after'],
            'explanation': change['explanation']
        })
    
    return pd.DataFrame(report)

def format_metric(metric):
    """
    Format metric for readability
    """
    if 'ctr' in metric:
        return f"ctr={metric['ctr']:.2f}"
    elif 'uninstall_rate' in metric:
        return f"uninstall_rate={metric['uninstall_rate']:.3f}"
    elif 'engagement_rate' in metric:
        return f"engagement_rate={metric['engagement_rate']:.2f}"
    return str(metric)
```

**WHY IT MATTERS:** Evaluators want to see:
1. What changed
2. Why it changed
3. What triggered the change
4. What was the before/after state

**COMMON MISTAKE:** Vague explanations like "Improved based on data."

**CORRECT APPROACH:** Specific, causal explanations with metric thresholds.

---


<a name="section-4"></a>
## 4. COMMON MISTAKES & WHY THEY HAPPEN

### 4.1 Hardcoding Domain Logic

**MISTAKE:**
```python
def generate_message(user):
    if user.streak > 5:
        return "Keep your English learning streak alive!"
```

**WHY FRESHERS DO THIS:** It's the easiest, most direct solution. They're thinking about solving the immediate problem (SpeakX notifications) rather than the general problem (notification orchestration).

**WHY IT'S WRONG:** The PS explicitly says "domain-agnostic." If evaluator provides Paytm data, this code breaks.

**HOW TO FIX:**
```python
def generate_message(user, knowledge_bank):
    north_star = knowledge_bank.get_north_star_metric()
    if user.get_metric_value(north_star) > threshold:
        feature = knowledge_bank.get_primary_feature()
        return f"Keep your {feature} going!"
```

**MENTOR GUIDANCE:** Ask: "What if this was a fitness app instead of a learning app? Would your code still work?"

---

### 4.2 Mock Learning

**MISTAKE:**
```python
# Iteration 0
templates = generate_templates()

# Iteration 1 (after "learning")
templates = generate_templates()  # Same function, same output
templates.loc[5, 'weight'] = 2.0  # Manually tweak one value
```

**WHY FRESHERS DO THIS:** They don't understand what "self-learning" means. They think changing ANY value counts as learning.

**WHY IT'S WRONG:** Learning must be:
1. Data-driven (based on experiment_results.csv)
2. Causal (explainable why)
3. Measurable (quantifiable improvement)

**HOW TO FIX:**
```python
# Iteration 0
templates = generate_templates()
schedule_0 = generate_schedule(templates)

# Iteration 1
experiment_results = load_experiment_results()
bad_templates = identify_bad_templates(experiment_results)
templates_filtered = suppress_templates(templates, bad_templates)
timing_optimized = optimize_timing(experiment_results)
schedule_1 = generate_schedule(templates_filtered, timing_optimized)

# Prove learning
delta = calculate_improvement(schedule_0, schedule_1, experiment_results)
```

**MENTOR GUIDANCE:** Ask: "Show me the line of code where experiment_results.csv influences your output. If I change the CSV, does your output change?"

---

### 4.3 Ignoring MECE Property

**MISTAKE:**
```python
segments = {
    'active_users': df[df['sessions_last_7d'] > 5],
    'gamification_lovers': df[df['streak_current'] > 3],
    'churned_users': df[df['sessions_last_7d'] == 0]
}
```

**WHY FRESHERS DO THIS:** They're thinking in terms of "user types" rather than "mutually exclusive segments."

**WHY IT'S WRONG:** A user can be BOTH active AND a gamification lover. This creates conflicting strategies.

**HOW TO FIX:**
```python
# Use clustering to ensure mutual exclusivity
from sklearn.cluster import KMeans

features = df[['activeness', 'gamification_propensity', 'social_propensity']]
kmeans = KMeans(n_clusters=8)
df['segment_id'] = kmeans.fit_predict(features)

# Validate MECE
assert df['user_id'].nunique() == len(df), "Users in multiple segments"
assert df['segment_id'].notna().all(), "Some users not segmented"
```

**MENTOR GUIDANCE:** Ask: "Can a user be in two segments at once? If yes, your segmentation is wrong."

---

### 4.4 Optimizing Only CTR

**MISTAKE:**
```python
def classify_template(ctr):
    if ctr > 0.15:
        return 'GOOD'
    elif ctr < 0.05:
        return 'BAD'
    else:
        return 'NEUTRAL'
```

**WHY FRESHERS DO THIS:** CTR is the most obvious metric. They forget about engagement.

**WHY IT'S WRONG:** High CTR with low engagement = clickbait. Users open but don't act.

**EXAMPLE:**
- Template A: "URGENT: Your account will be deleted!" → 25% CTR, 5% engagement (clickbait)
- Template B: "Complete today's exercise to maintain your streak" → 15% CTR, 45% engagement (effective)

**HOW TO FIX:**
```python
def classify_template(ctr, engagement_rate):
    if ctr > 0.15 and engagement_rate > 0.40:
        return 'GOOD'
    elif ctr < 0.05 or engagement_rate < 0.20:
        return 'BAD'
    else:
        return 'NEUTRAL'
```

**MENTOR GUIDANCE:** Ask: "What if a template has 20% CTR but only 10% engagement? Is that good?"

---

### 4.5 Ignoring Uninstall Rate

**MISTAKE:**
```python
# Set frequency based only on activeness
if activeness > 0.7:
    frequency = 9  # Max notifications
```

**WHY FRESHERS DO THIS:** They're optimizing for engagement, forgetting about user annoyance.

**WHY IT'S WRONG:** Over-communication drives uninstalls, even for active users.

**HOW TO FIX:**
```python
def calculate_frequency(activeness, segment_uninstall_rate):
    if activeness > 0.7:
        base_freq = 9
    else:
        base_freq = 5
    
    # Guardrail
    if segment_uninstall_rate > 0.02:
        base_freq = max(2, base_freq - 2)
    
    return base_freq
```

**MENTOR GUIDANCE:** Ask: "What if your notifications are so frequent that users uninstall the app? How do you prevent that?"

---

### 4.6 Generic Templates

**MISTAKE:**
```python
templates = [
    "Complete your exercise today!",
    "Keep learning!",
    "Don't give up!"
]
```

**WHY FRESHERS DO THIS:** They're focused on generating templates, not personalizing them.

**WHY IT'S WRONG:** These templates don't use segment characteristics, lifecycle stage, or behavioral hooks.

**HOW TO FIX:**
```python
def generate_template(segment, lifecycle, goal, theme):
    if segment['gamification_propensity'] > 0.7:
        # High gamification segment
        if theme == 'accomplishment':
            return "You've earned {coins_balance} coins—complete another exercise to reach {next_milestone}!"
    elif segment['social_propensity'] > 0.7:
        # High social segment
        if theme == 'social_influence':
            return "{peer_name} from {location} just completed 5 exercises. Can you beat them?"
    # ... more personalization
```

**MENTOR GUIDANCE:** Ask: "How does this template differ for an achiever vs a casual learner?"

---

### 4.7 No Journey Progression

**MISTAKE:**
```python
# Same templates for D0, D1, D2, ... D30
for day in range(30):
    schedule[day] = random.choice(templates)
```

**WHY FRESHERS DO THIS:** They're thinking of notifications as isolated events, not as a journey.

**WHY IT'S WRONG:** Users have different goals on different days. D0 is about activation, D7 is about conversion readiness.

**HOW TO FIX:**
```python
journey_map = {
    'D0': 'activation',
    'D1-D2': 'habit_formation',
    'D3-D5': 'feature_discovery',
    'D6-D7': 'conversion_readiness',
    'D8+': 'retention'
}

def generate_schedule(user, day):
    goal = get_goal_for_day(day, journey_map)
    templates = filter_templates_by_goal(goal)
    return select_template(templates, user)
```

**MENTOR GUIDANCE:** Ask: "What should a user achieve on Day 0 vs Day 7? Should the messages be the same?"

---

### 4.8 Vague Delta Explanations

**MISTAKE:**
```csv
entity_type,change_type,explanation
template,suppression,"Removed because it didn't perform well"
timing,shift,"Changed to improve engagement"
```

**WHY FRESHERS DO THIS:** They don't understand what "causal reasoning" means.

**WHY IT'S WRONG:** Evaluators want to see:
1. What metric triggered the change
2. What was the threshold
3. What was the before/after value

**HOW TO FIX:**
```csv
entity_type,entity_id,change_type,metric_trigger,before_value,after_value,explanation
template,T003,suppression,ctr=0.04,active,suppressed,"CTR of 4% below 5% threshold. Only 40 opens out of 1000 sends. Suppressed to improve overall engagement."
timing,segment_1,window_shift,night_ctr=0.03 vs early_morning_ctr=0.18,night,early_morning,"Night window had 3% CTR (30/1000 opens) while early_morning had 18% CTR (180/1000 opens) for this segment. Shifted to optimize engagement."
```

**MENTOR GUIDANCE:** Ask: "Why did you make this change? What specific number in the data told you to do this?"

---

### 4.9 Missing Bilingual Support

**MISTAKE:**
```python
templates = [
    "Complete your exercise today!",
    "Keep your streak alive!"
]
```

**WHY FRESHERS DO THIS:** They forget the requirement or think it's optional.

**WHY IT'S WRONG:** PS explicitly requires Hindi + English for each template.

**HOW TO FIX:**
```python
templates = [
    {
        'template_id': 'T001',
        'language': 'en',
        'content': "Complete your exercise today!"
    },
    {
        'template_id': 'T001_hi',
        'language': 'hi',
        'content': "आज अपना अभ्यास पूरा करें!"
    }
]
```

**MENTOR GUIDANCE:** Ask: "Show me the Hindi version of this template."

---

### 4.10 Not Testing with New Data

**MISTAKE:**
```python
# Hardcoded for the provided sample data
if user_id == 'U001':
    segment = 'achievers'
```

**WHY FRESHERS DO THIS:** They're optimizing for the demo, not for extensibility.

**WHY IT'S WRONG:** Evaluator will test with NEW data. Hardcoded logic will fail.

**HOW TO FIX:**
```python
# Dynamic segmentation
def assign_segment(user_data):
    features = extract_features(user_data)
    segment_id = clustering_model.predict(features)
    return segment_id
```

**MENTOR GUIDANCE:** Ask: "What if I give you a CSV with 10,000 new users? Will your code work without changes?"

---


<a name="section-5"></a>
## 5. EVALUATOR MINDSET

### 5.1 What Evaluators Look For

**1. SYSTEM COMPLETENESS (15%)**

Evaluators check:
- ✅ Does it run end-to-end without errors?
- ✅ Can I provide new KB and user CSV at runtime?
- ✅ Are all deliverable files generated?
- ✅ Is the file naming exact (not `user_segments_final.csv` when spec says `user_segments.csv`)?

**Red Flags:**
- ❌ "Please edit config.py with your data path" → Should accept CLI arguments
- ❌ Missing files or renamed files
- ❌ Crashes on new data
- ❌ Requires manual intervention between steps

**What They're Testing:** Can this system be deployed in production? Or is it just a demo?

---

**2. SEGMENTATION QUALITY (15%)**

Evaluators check:
- ✅ Are segments mutually exclusive? (MECE)
- ✅ Are segment sizes reasonable? (No 95% in one segment, 1% in others)
- ✅ Do segments have meaningful names? (Not just "Cluster_0")
- ✅ Are propensity scores calculated and used?
- ✅ Do segments differ meaningfully in behavior?

**Red Flags:**
- ❌ Overlapping segments
- ❌ Generic names like "Segment A, Segment B"
- ❌ All segments have similar characteristics
- ❌ Propensity scores calculated but never used

**What They're Testing:** Do you understand user segmentation? Or did you just run K-means blindly?

---

**3. MESSAGING INTELLIGENCE (25%)**

Evaluators check:
- ✅ Are templates personalized by segment?
- ✅ Do templates use appropriate Octalysis hooks?
- ✅ Is bilingual support complete and accurate?
- ✅ Do templates align with lifecycle stage and goal?
- ✅ Is tone appropriate for brand and context?

**Red Flags:**
- ❌ Same template for all segments
- ❌ Generic messages like "Complete your task today"
- ❌ Missing Hindi translations
- ❌ Inappropriate tone (aggressive for trial users, casual for churned users)
- ❌ No personalization placeholders

**What They're Testing:** Can you think like a product manager? Do you understand user psychology?

---

**4. TIMING & FREQUENCY (10%)**

Evaluators check:
- ✅ Are timing windows segment-specific?
- ✅ Is frequency based on activeness and churn risk?
- ✅ Is the uninstall rate guardrail implemented?
- ✅ Does timing improve in Iteration 1 based on data?

**Red Flags:**
- ❌ Same time for all users
- ❌ Ignoring uninstall rate
- ❌ No timing optimization in Iteration 1
- ❌ Unrealistic frequency (20 notifications/day)

**What They're Testing:** Do you understand user tolerance? Can you balance engagement and annoyance?

---

**5. LEARNING & EVOLUTION (25%)**

Evaluators check:
- ✅ Does Iteration 1 differ from Iteration 0?
- ✅ Are changes data-driven (based on experiment_results.csv)?
- ✅ Is there measurable improvement (delta)?
- ✅ Are changes causally explained?
- ✅ Is the learning reproducible (same input → same output)?

**Red Flags:**
- ❌ Iteration 1 is identical to Iteration 0
- ❌ Changes are random or manual
- ❌ No delta report or vague explanations
- ❌ "Learning" that makes things worse
- ❌ Non-deterministic output (different results each run)

**What They're Testing:** Do you understand machine learning? Can you build systems that improve over time?

**THIS IS THE MOST IMPORTANT SECTION.** 25% of your grade depends on proving real learning.

---

**6. EXTENSIBILITY (5%)**

Evaluators check:
- ✅ Can the system work with a different domain (FinTech, HealthTech)?
- ✅ Is logic driven by Knowledge Bank, not hardcoded?
- ✅ Can it handle different data schemas (with validation)?

**Red Flags:**
- ❌ Hardcoded "English learning" logic
- ❌ Assumes specific column names without validation
- ❌ Breaks when given different KB

**What They're Testing:** Is this a product or a one-off script?

---

**7. PRESENTATION (5%)**

Evaluators check:
- ✅ Can you explain your approach clearly?
- ✅ Can you walk through Iteration 0 → Iteration 1 delta?
- ✅ Can you answer "why" questions about design decisions?
- ✅ Is your README clear and concise?

**Red Flags:**
- ❌ Reading from slides
- ❌ Can't explain why you made certain choices
- ❌ Defensive when questioned
- ❌ README is a wall of text or too vague

**What They're Testing:** Can you communicate technical decisions? Will you be effective in a team?

---

### 5.2 How Evaluators Test

**TEST 1: New Data**
```
Evaluator provides:
- New user_data.csv (different users, different distributions)
- New company KB (different domain, different features)

Expected: System runs without code changes, generates appropriate outputs
```

**TEST 2: Edge Cases**
```
Evaluator provides:
- CSV with missing values
- CSV with outliers (user with 1000 sessions/day)
- KB with unusual format

Expected: System handles gracefully with validation and error messages
```

**TEST 3: Learning Verification**
```
Evaluator provides:
- experiment_results.csv with all BAD templates

Expected: Iteration 1 suppresses bad templates, shows measurable improvement
```

**TEST 4: Extensibility**
```
Evaluator asks: "What if this was a fitness app instead?"

Expected: You explain how Knowledge Bank would change, but orchestrator logic stays the same
```

**TEST 5: Causal Reasoning**
```
Evaluator asks: "Why did you suppress Template T003?"

Expected: "It had 4% CTR, below the 5% threshold. Only 40 users opened out of 1000 sends, indicating poor resonance with the segment."

NOT: "Because it didn't perform well."
```

---

### 5.3 Auto-Fail Conditions

**1. Hardcoded Outputs**
```python
# This will auto-fail
user_segments = pd.DataFrame({
    'user_id': ['U001', 'U002', 'U003'],
    'segment': ['achievers', 'casual', 'churned']
})
```

**2. Mock Learning**
```python
# This will auto-fail
def iteration_1():
    return iteration_0()  # No actual learning
```

**3. PPT-Only Demo**
```
Evaluator: "Show me the system running."
You: "Here are slides explaining how it would work."
→ AUTO-FAIL
```

**4. No Delta**
```
Evaluator: "What improved from Iteration 0 to 1?"
You: "The system learned."
Evaluator: "Show me the numbers."
You: "Um..."
→ AUTO-FAIL
```

**5. Missing/Renamed Files**
```
Expected: user_segments.csv
You deliver: user_segments_final_v2.csv
→ AUTO-FAIL
```

**WHY SO STRICT:** In production, systems must follow specs exactly. APIs, databases, and downstream systems depend on exact file names and schemas.

---

### 5.4 What Impresses Evaluators

**1. Proactive Validation**
```python
def validate_input(df):
    """
    Validates input data and provides helpful error messages
    """
    if 'user_id' not in df.columns:
        raise ValueError("Missing required column: user_id. Please ensure CSV has columns: user_id, lifecycle_stage, ...")
    
    if df['user_id'].duplicated().any():
        raise ValueError(f"Duplicate user_ids found: {df[df['user_id'].duplicated()]['user_id'].tolist()}")
    
    print(f"✓ Validation passed: {len(df)} users, {df.columns.tolist()}")
```

**2. Thoughtful Edge Case Handling**
```python
def calculate_activeness(user):
    """
    Handles edge cases gracefully
    """
    if user['days_since_signup'] == 0:
        # New user, no history yet
        return 0.5  # Neutral score
    
    if user['sessions_last_7d'] > 50:
        # Likely a bot or data error
        logger.warning(f"User {user['user_id']} has unusually high sessions: {user['sessions_last_7d']}")
        return 0.9  # Cap at high but not perfect
    
    # Normal calculation
    return normalize(user['sessions_last_7d'])
```

**3. Clear Causal Explanations**
```python
def explain_suppression(template_id, metrics):
    """
    Provides detailed reasoning for template suppression
    """
    return f"""
    Template {template_id} suppressed due to poor performance:
    - CTR: {metrics['ctr']:.1%} (threshold: 5%)
    - Engagement: {metrics['engagement_rate']:.1%} (threshold: 20%)
    - Total sends: {metrics['total_sends']}
    - Total opens: {metrics['total_opens']}
    
    Analysis: Only {metrics['total_opens']} users out of {metrics['total_sends']} opened this notification,
    and only {metrics['total_engagements']} took action. This indicates the message did not resonate
    with the target segment ({metrics['segment_name']}).
    
    Action: Suppressed from future use. Recommend analyzing successful templates in this segment
    to understand what messaging works better.
    """
```

**4. Quantified Improvements**
```python
def show_delta(iteration_0, iteration_1):
    """
    Shows clear before/after metrics
    """
    print("=== LEARNING DELTA ===")
    print(f"Average CTR: {iteration_0['ctr'].mean():.1%} → {iteration_1['ctr'].mean():.1%} (+{(iteration_1['ctr'].mean() - iteration_0['ctr'].mean()):.1%})")
    print(f"Average Engagement: {iteration_0['engagement_rate'].mean():.1%} → {iteration_1['engagement_rate'].mean():.1%} (+{(iteration_1['engagement_rate'].mean() - iteration_0['engagement_rate'].mean()):.1%})")
    print(f"Uninstall Rate: {iteration_0['uninstall_rate'].mean():.2%} → {iteration_1['uninstall_rate'].mean():.2%} ({(iteration_0['uninstall_rate'].mean() - iteration_1['uninstall_rate'].mean()):.2%})")
    print(f"Templates: {len(iteration_0)} → {len(iteration_1)} ({len(iteration_0) - len(iteration_1)} suppressed)")
```

**5. Domain-Agnostic Design**
```python
class NotificationOrchestrator:
    """
    Domain-agnostic orchestrator that works with any KB
    """
    def __init__(self, knowledge_bank):
        self.kb = knowledge_bank
        self.north_star = self.kb.get_north_star()
        self.features = self.kb.get_features()
        self.tones = self.kb.get_allowed_tones()
    
    def generate_message(self, user, goal):
        # No hardcoded domain logic
        feature = self.kb.get_feature_for_goal(goal)
        tone = self.kb.get_tone_for_lifecycle(user.lifecycle_stage)
        hook = self.kb.get_hook_for_segment(user.segment)
        
        return self.template_engine.generate(user, feature, tone, hook)
```

---


<a name="section-6"></a>
## 6. LEARNING VS CLAIMING: PROVING ITERATION 1 IS BETTER

### 6.1 What "Learning" Actually Means

**NOT LEARNING:**
```python
# Iteration 0
templates = generate_templates()

# Iteration 1
templates = generate_templates()
templates.loc[5, 'weight'] = 2.0  # Manually changed
```
**Why:** No connection to experiment_results.csv. Change is arbitrary.

---

**REAL LEARNING:**
```python
# Iteration 0
templates = generate_templates()
schedule_0 = generate_schedule(templates)

# Iteration 1
experiment_results = load_experiment_results()

# Learn from data
bad_templates = experiment_results[experiment_results['ctr'] < 0.05]['template_id']
templates_filtered = templates[~templates['template_id'].isin(bad_templates)]

good_templates = experiment_results[experiment_results['ctr'] > 0.15]['template_id']
templates_filtered.loc[templates_filtered['template_id'].isin(good_templates), 'weight'] = 3.0

schedule_1 = generate_schedule(templates_filtered)

# Prove improvement
delta = calculate_delta(schedule_0, schedule_1, experiment_results)
```
**Why:** Changes are driven by experiment_results.csv. Improvement is measurable.

---

### 6.2 The Learning Loop

```
┌─────────────────────────────────────────────────────────────┐
│                     ITERATION 0                              │
│  (Before Learning - Based on Assumptions)                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Generate Segments    │
                │  Generate Templates   │
                │  Generate Schedule    │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   Run Experiment      │
                │   Collect Results     │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ experiment_results.csv│
                │  - CTR per template   │
                │  - Engagement rates   │
                │  - Uninstall rates    │
                └───────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     ITERATION 1                              │
│  (After Learning - Based on Data)                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Analyze Results      │
                │  - Classify templates │
                │  - Identify patterns  │
                │  - Find improvements  │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Apply Learning       │
                │  - Suppress BAD       │
                │  - Promote GOOD       │
                │  - Optimize timing    │
                │  - Adjust frequency   │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Generate New Schedule│
                │  (Improved)           │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Calculate Delta      │
                │  - CTR improvement    │
                │  - Engagement up      │
                │  - Uninstalls down    │
                └───────────────────────┘
```

---

### 6.3 Measurable Delta Examples

**EXAMPLE 1: Template Suppression**

**Iteration 0:**
```csv
template_id,segment_id,ctr,engagement_rate,total_sends
T001,1,0.18,0.42,1000
T002,1,0.08,0.31,1000
T003,1,0.04,0.25,1000
T004,1,0.15,0.38,1000
T005,1,0.12,0.35,1000
```

**Learning:**
- T003 has 4% CTR (below 5% threshold) → Suppress
- T001 has 18% CTR (above 15% threshold) → Promote

**Iteration 1:**
```csv
template_id,segment_id,ctr,engagement_rate,total_sends,weight
T001,1,0.18,0.42,1500,3.0
T002,1,0.08,0.31,800,1.0
T004,1,0.15,0.38,1200,1.0
T005,1,0.12,0.35,1000,1.0
```
(T003 removed, T001 gets more sends due to higher weight)

**Delta:**
- Average CTR: 11.4% → 13.25% (+1.85%)
- Templates in use: 5 → 4 (1 suppressed)
- High-performing template usage: 20% → 30% of sends

---

**EXAMPLE 2: Timing Optimization**

**Iteration 0:**
```csv
segment_id,time_window,ctr,total_sends
1,early_morning,0.18,2000
1,evening,0.15,2000
1,night,0.03,2000
```

**Learning:**
- Night window has 3% CTR → Suppress for this segment
- Early morning has 18% CTR → Increase allocation

**Iteration 1:**
```csv
segment_id,time_window,ctr,total_sends
1,early_morning,0.18,3500
1,evening,0.15,2500
```
(Night window removed, sends redistributed)

**Delta:**
- Average CTR: 12% → 16.75% (+4.75%)
- Wasted sends (night): 2000 → 0
- Optimal window usage: 33% → 58%

---

**EXAMPLE 3: Frequency Adjustment**

**Iteration 0:**
```csv
segment_id,frequency,uninstall_rate,total_users
5,6,0.025,1000
```

**Learning:**
- Segment 5 has 2.5% uninstall rate (above 2% threshold)
- Reduce frequency by 2 notifications/day

**Iteration 1:**
```csv
segment_id,frequency,uninstall_rate,total_users
5,4,0.015,1000
```

**Delta:**
- Uninstall rate: 2.5% → 1.5% (-1.0%)
- Users retained: 25 more users (1000 × 0.01)
- Notifications sent: 6000/day → 4000/day (more sustainable)

---

### 6.4 Causal Reasoning Framework

For every change, answer these questions:

**1. WHAT changed?**
- "Template T003 was suppressed"
- "Timing window for Segment 1 shifted from night to early_morning"
- "Frequency for Segment 5 reduced from 6 to 4 notifications/day"

**2. WHY did it change?**
- "CTR of 4% was below the 5% threshold"
- "Night window had 3% CTR while early_morning had 18% CTR"
- "Uninstall rate of 2.5% exceeded the 2% guardrail"

**3. WHAT was the trigger?**
- "experiment_results.csv showed T003 had only 40 opens out of 1000 sends"
- "experiment_results.csv showed night window underperformed by 15 percentage points"
- "experiment_results.csv showed 25 uninstalls out of 1000 users in Segment 5"

**4. WHAT is the expected impact?**
- "Removing T003 will increase average CTR by reallocating sends to better templates"
- "Shifting to early_morning will increase CTR from 12% to ~16%"
- "Reducing frequency will decrease uninstall rate from 2.5% to ~1.5%"

**5. HOW do you verify improvement?**
- "Compare average CTR before/after: 11.4% → 13.25%"
- "Compare segment CTR before/after: 12% → 16.75%"
- "Compare uninstall rate before/after: 2.5% → 1.5%"

---

### 6.5 Delta Report Template

```csv
entity_type,entity_id,change_type,metric_trigger,before_value,after_value,expected_impact,actual_impact,explanation
template,T003,suppression,ctr=0.04,active,suppressed,+1.5% avg CTR,+1.85% avg CTR,"Template had 4% CTR (40/1000 opens), below 5% threshold. Suppressed to reallocate sends to better-performing templates. Actual improvement exceeded expectation."

timing,segment_1,window_shift,night_ctr=0.03 vs early_morning_ctr=0.18,night,early_morning,+4% segment CTR,+4.75% segment CTR,"Night window had 3% CTR (60/2000 opens) while early_morning had 18% CTR (360/2000 opens). Shifted 2000 sends from night to early_morning, improving segment performance."

frequency,segment_5,reduction,uninstall_rate=0.025,6,4,-1% uninstall rate,-1.0% uninstall rate,"Segment had 2.5% uninstall rate (25/1000 users), exceeding 2% guardrail. Reduced frequency from 6 to 4 notifications/day to prevent churn. Uninstall rate decreased to 1.5% as expected."

theme,segment_3,primary_change,curiosity_ctr=0.08 vs accomplishment_ctr=0.14,curiosity,accomplishment,+6% segment CTR,+5.5% segment CTR,"Curiosity theme had 8% CTR while accomplishment theme had 14% CTR for this segment. Updated primary theme to better match segment propensities (gamification_propensity=0.75)."
```

**KEY ELEMENTS:**
1. **Metric Trigger:** The specific number that triggered the change
2. **Before/After:** Clear state transition
3. **Expected Impact:** What you predicted would happen
4. **Actual Impact:** What actually happened (from re-running with new parameters)
5. **Explanation:** Causal reasoning connecting trigger → action → impact

---

### 6.6 How to Prove Learning to Evaluators

**STEP 1: Show Iteration 0 Outputs**
```
"Here's the initial schedule generated with 5 templates per segment,
using user preferred_hour for timing, and activeness-based frequency."
```

**STEP 2: Show Experiment Results**
```
"We ran the Iteration 0 schedule and collected results.
Here's what we found:
- Template T003 had 4% CTR (bad)
- Template T001 had 18% CTR (good)
- Night window had 3% CTR for Segment 1 (bad)
- Segment 5 had 2.5% uninstall rate (above threshold)"
```

**STEP 3: Show Learning Logic**
```
"Based on these results, the system made these changes:
1. Suppressed T003 (CTR < 5%)
2. Promoted T001 (CTR > 15%, weight 1.0 → 3.0)
3. Removed night window for Segment 1 (CTR < 5%)
4. Reduced frequency for Segment 5 (uninstall rate > 2%)"
```

**STEP 4: Show Iteration 1 Outputs**
```
"Here's the new schedule after learning.
Notice:
- T003 no longer appears
- T001 appears more frequently (30% of sends vs 20%)
- No night notifications for Segment 1
- Segment 5 users get 4 notifications/day instead of 6"
```

**STEP 5: Show Delta**
```
"Measurable improvements:
- Average CTR: 11.4% → 13.25% (+1.85%)
- Segment 1 CTR: 12% → 16.75% (+4.75%)
- Segment 5 uninstall rate: 2.5% → 1.5% (-1.0%)
- Templates in use: 5 → 4 (1 suppressed)
- High-performing template usage: 20% → 30%"
```

**STEP 6: Answer "Why" Questions**
```
Evaluator: "Why did you suppress T003?"
You: "It had 4% CTR, which is below our 5% threshold. Only 40 users
out of 1000 opened it, indicating poor resonance with the segment.
By suppressing it and reallocating those sends to better templates,
we improved average CTR by 1.85%."

Evaluator: "How do you know this is better?"
You: "We can see in the delta report that average CTR increased from
11.4% to 13.25%. This means more users are opening notifications,
which leads to higher engagement and better retention."
```

---


<a name="section-7"></a>
## 7. MENTOR NOTES: HOW TO GUIDE, QUESTION, AND EVALUATE

### 7.1 Guiding Freshers Through the Problem

**WEEK 1: Understanding the Problem**

**Day 1-2: Problem Statement Deep Dive**

**Mentor Activity:**
- Read PS together, line by line
- For each section, ask: "What is this asking for? Why does it exist?"
- Identify keywords: "self-learning," "domain-agnostic," "MECE," "causal reasoning"

**Questions to Ask:**
1. "What's the difference between a notification scheduler and a notification orchestrator?"
2. "Why does the PS emphasize 'domain-agnostic'? What would break if we hardcoded SpeakX logic?"
3. "What does 'self-learning' mean? How is it different from 'configurable'?"

**Expected Struggles:**
- Freshers will want to jump to code immediately
- They'll focus on Task 1 and ignore Tasks 2-3
- They'll miss the "domain-agnostic" requirement

**Mentor Intervention:**
- "Before writing any code, let's map out the data flow. What are the inputs? What are the outputs? What happens in between?"
- "Let's list all the deliverables. Which ones depend on which?"
- "If I gave you a fitness app's data instead of SpeakX, what would change? What would stay the same?"

---

**Day 3-4: Concept Building**

**Mentor Activity:**
- Teach core concepts: MECE, Octalysis, propensity scores, lifecycle stages
- Use examples from other domains (not just SpeakX)
- Draw diagrams showing relationships

**Questions to Ask:**
1. "Can you explain MECE in your own words? Give me an example of non-MECE segmentation."
2. "Which Octalysis drive would work best for a user who's about to churn? Why?"
3. "What's the difference between CTR and engagement rate? Why do we need both?"

**Expected Struggles:**
- Confusing segments with personas
- Not understanding why propensity scores matter
- Thinking all users should get the same frequency

**Mentor Intervention:**
- "Let's take 5 sample users and manually segment them. What features would you use? How would you ensure they don't overlap?"
- "Let's write 3 different messages for the same goal but different segments. How do they differ?"
- "What happens if we send 10 notifications/day to a casual user? What about an active user?"

---

**Day 5-7: Architecture Design**

**Mentor Activity:**
- Help design the system architecture
- Identify components: KB Engine, Segmentation Engine, Template Generator, etc.
- Define interfaces between components

**Questions to Ask:**
1. "What does the Knowledge Bank Engine output? What format?"
2. "How does the Template Generator know which templates to create?"
3. "Where does the Learning Engine get its data from?"

**Expected Struggles:**
- Monolithic design (one giant script)
- No clear separation of concerns
- Hardcoded dependencies

**Mentor Intervention:**
- "Let's draw boxes for each component. What data flows between them?"
- "If we wanted to swap out the segmentation algorithm, what would we need to change?"
- "Let's define the interface: What inputs does this component need? What outputs does it produce?"

---

**WEEK 2: Implementation**

**Day 8-10: Task 1 Implementation**

**Mentor Activity:**
- Guide through KB extraction (LLM or rule-based)
- Help with data validation and cleaning
- Review segmentation logic

**Questions to Ask:**
1. "How do you validate that the input CSV has all required columns?"
2. "What happens if a user has missing data? How do you handle it?"
3. "How do you verify that your segments are MECE?"

**Expected Struggles:**
- Skipping validation
- Poor handling of missing data
- Segments that aren't mutually exclusive

**Mentor Intervention:**
- "Let's write a validation function first. What checks do we need?"
- "Let's create a test CSV with missing values. Does your code handle it?"
- "Let's verify MECE: Sum up segment sizes. Does it equal total users? Check for duplicates."

---

**Day 11-13: Task 2 Implementation**

**Mentor Activity:**
- Guide through theme mapping
- Help with template generation (LLM or template-based)
- Review timing and frequency logic

**Questions to Ask:**
1. "How do you decide which theme to use for a segment?"
2. "How do you ensure templates are personalized, not generic?"
3. "How do you calculate the optimal notification frequency?"

**Expected Struggles:**
- Generic templates
- Same timing for all users
- Ignoring uninstall rate guardrail

**Mentor Intervention:**
- "Let's look at a high-gamification segment. What should the template emphasize?"
- "Let's look at user preferred_hour distribution by segment. Do you see patterns?"
- "What if uninstall rate is 3%? What does your code do?"

---

**Day 14-16: Task 3 Implementation**

**Mentor Activity:**
- Guide through schedule generation
- Help with performance classification
- Review learning logic

**Questions to Ask:**
1. "How do you ensure the schedule shows journey progression?"
2. "What makes a template 'BAD'? What do you do with it?"
3. "How do you prove that Iteration 1 is better than Iteration 0?"

**Expected Struggles:**
- Random template selection
- No real learning (just manual tweaks)
- Vague delta explanations

**Mentor Intervention:**
- "Let's trace one user's journey from D0 to D7. Do the goals progress logically?"
- "Let's load experiment_results.csv. Show me the line of code where it influences your output."
- "Let's calculate the delta. What metrics improved? By how much?"

---

### 7.2 Socratic Questioning Techniques

**TECHNIQUE 1: The "Why" Chain**

```
Fresher: "I'm using K-means for segmentation."
Mentor: "Why K-means?"
Fresher: "Because it's a clustering algorithm."
Mentor: "Why clustering? Why not rule-based segmentation?"
Fresher: "Because we want data-driven segments."
Mentor: "Good. Why is that important?"
Fresher: "Because different users behave differently, and we want to discover patterns."
Mentor: "Excellent. Now, how do you decide the number of clusters?"
```

**GOAL:** Make them articulate their reasoning, not just implement.

---

**TECHNIQUE 2: The "What If" Challenge**

```
Fresher: "I'm hardcoding the feature names."
Mentor: "What if I give you a different company's KB?"
Fresher: "Um... I'd need to change the code."
Mentor: "What if you had 100 different companies? Would you change the code 100 times?"
Fresher: "No, that's not scalable."
Mentor: "So how can you make it work for any company?"
Fresher: "I should extract feature names from the KB dynamically."
Mentor: "Exactly. Show me how you'd do that."
```

**GOAL:** Make them think about extensibility and edge cases.

---

**TECHNIQUE 3: The "Prove It" Demand**

```
Fresher: "My system learns from the data."
Mentor: "Prove it. Show me the code."
Fresher: "Here, I load experiment_results.csv."
Mentor: "Good. Now show me where it changes your output."
Fresher: "Um... I'm not sure."
Mentor: "Let's trace it. What happens after you load the CSV?"
Fresher: "I classify templates as GOOD or BAD."
Mentor: "And then?"
Fresher: "I... should suppress the BAD ones."
Mentor: "Show me that code. Does it exist?"
```

**GOAL:** Make them prove claims with code, not just words.

---

**TECHNIQUE 4: The "Explain to a 5-Year-Old"**

```
Fresher: "I'm using propensity scores to optimize template selection."
Mentor: "Explain that like I'm 5 years old."
Fresher: "Um... propensity scores are probabilities that..."
Mentor: "Simpler. Pretend I don't know what probability means."
Fresher: "Okay. Some users like games and points. Some users don't. Propensity score tells us how much a user likes games."
Mentor: "Good! So if a user has high gamification propensity, what kind of message should we send?"
Fresher: "One that mentions coins, streaks, badges."
Mentor: "Perfect. Now show me the code that does that."
```

**GOAL:** Test true understanding. If they can't explain simply, they don't understand.

---

### 7.3 Code Review Checklist

**ARCHITECTURE:**
- [ ] Is the code modular (separate files/classes for each component)?
- [ ] Are there clear interfaces between components?
- [ ] Is domain logic separated from orchestration logic?
- [ ] Can the system work with different domains without code changes?

**DATA VALIDATION:**
- [ ] Are input CSVs validated for schema?
- [ ] Are data types checked?
- [ ] Are ranges validated (e.g., hour 0-23)?
- [ ] Is missing data handled gracefully?
- [ ] Are error messages helpful?

**SEGMENTATION:**
- [ ] Are segments mutually exclusive?
- [ ] Are segments collectively exhaustive?
- [ ] Are segment sizes reasonable (no 95% in one segment)?
- [ ] Are segments named meaningfully?
- [ ] Are propensity scores calculated?
- [ ] Are propensity scores actually used?

**TEMPLATES:**
- [ ] Are templates personalized by segment?
- [ ] Do templates use appropriate Octalysis hooks?
- [ ] Is bilingual support complete (Hindi + English)?
- [ ] Do templates align with lifecycle stage and goal?
- [ ] Are templates not generic ("Complete your task today")?
- [ ] Do templates include personalization placeholders?

**TIMING & FREQUENCY:**
- [ ] Is timing segment-specific?
- [ ] Is frequency based on activeness and churn risk?
- [ ] Is the uninstall rate guardrail implemented?
- [ ] Are timing windows reasonable (not all at 3 AM)?

**LEARNING:**
- [ ] Does Iteration 1 differ from Iteration 0?
- [ ] Are changes based on experiment_results.csv?
- [ ] Is there measurable improvement (delta)?
- [ ] Are changes causally explained?
- [ ] Is learning reproducible (deterministic)?
- [ ] Are BAD templates suppressed?
- [ ] Are GOOD templates promoted?
- [ ] Is timing optimized based on data?
- [ ] Is frequency adjusted based on uninstall rate?

**DELIVERABLES:**
- [ ] Are all files generated?
- [ ] Are file names exact (not `user_segments_final.csv`)?
- [ ] Are CSV/JSON formats correct?
- [ ] Is the README clear and concise (≤500 words)?

**DEMO:**
- [ ] Does the system run end-to-end without errors?
- [ ] Can it accept new data at runtime?
- [ ] Is the demo flow clear (Iteration 0 → Results → Iteration 1)?
- [ ] Can the fresher explain design decisions?
- [ ] Can the fresher answer "why" questions?

---

### 7.4 Evaluation Rubric

**SYSTEM COMPLETENESS (15 points)**
- 15: Runs end-to-end, accepts new data, all files generated, exact naming
- 12: Runs end-to-end, minor issues with new data or file naming
- 9: Runs with provided data, breaks with new data
- 6: Partially runs, missing some deliverables
- 3: Doesn't run, major errors
- 0: No working system

**SEGMENTATION QUALITY (15 points)**
- 15: MECE, meaningful names, propensity scores used, segments differ meaningfully
- 12: MECE, reasonable names, propensity scores calculated but underutilized
- 9: MECE, generic names, propensity scores missing
- 6: Not MECE, or segments too similar
- 3: Segments exist but poorly designed
- 0: No segmentation

**MESSAGING INTELLIGENCE (25 points)**
- 25: Personalized by segment, appropriate hooks, bilingual, aligned with lifecycle/goal, appropriate tone
- 20: Personalized, bilingual, mostly aligned, minor tone issues
- 15: Some personalization, bilingual, generic in places
- 10: Generic templates, bilingual, no personalization
- 5: Generic templates, missing Hindi
- 0: No templates or completely generic

**TIMING & FREQUENCY (10 points)**
- 10: Segment-specific, activeness-based, uninstall guardrail, optimized in Iteration 1
- 8: Segment-specific, activeness-based, guardrail implemented
- 6: Some timing logic, frequency logic, missing guardrail
- 4: Basic timing, no frequency optimization
- 2: Same time for all users
- 0: No timing logic

**LEARNING & EVOLUTION (25 points)**
- 25: Clear delta, data-driven changes, causal explanations, measurable improvement, reproducible
- 20: Clear delta, data-driven, good explanations, measurable improvement
- 15: Some delta, partially data-driven, vague explanations
- 10: Minimal delta, changes not clearly data-driven
- 5: No real delta, manual tweaks
- 0: No learning, Iteration 1 = Iteration 0

**EXTENSIBILITY (5 points)**
- 5: Domain-agnostic, KB-driven, works with different domains
- 4: Mostly domain-agnostic, minor hardcoding
- 3: Some hardcoding, would need changes for new domain
- 2: Significant hardcoding
- 1: Completely SpeakX-specific
- 0: Not extensible

**PRESENTATION (5 points)**
- 5: Clear explanation, answers "why" questions, good README, confident
- 4: Clear explanation, mostly answers questions, good README
- 3: Adequate explanation, struggles with some questions
- 2: Poor explanation, can't answer "why" questions
- 1: Reads from slides, defensive
- 0: No presentation or completely unprepared

**TOTAL: 100 points**

**GRADING:**
- 90-100: Excellent (A)
- 80-89: Good (B)
- 70-79: Satisfactory (C)
- 60-69: Needs Improvement (D)
- <60: Unsatisfactory (F)

**AUTO-FAIL CONDITIONS (regardless of score):**
- Hardcoded outputs
- Mock learning (no real Iteration 0 → 1 improvement)
- PPT-only demo (no working system)
- No delta or vague delta
- Missing/renamed deliverable files

---

### 7.5 Common Mentor Mistakes to Avoid

**MISTAKE 1: Giving Solutions Too Early**

❌ **Bad:**
```
Fresher: "I'm not sure how to segment users."
Mentor: "Use K-means with 8 clusters on activeness, gamification_propensity, and social_propensity."
```

✅ **Good:**
```
Fresher: "I'm not sure how to segment users."
Mentor: "What makes users different from each other?"
Fresher: "Some are active, some aren't."
Mentor: "Good. What else?"
Fresher: "Some like gamification, some don't."
Mentor: "Excellent. So if you had to group users based on these differences, how would you do it?"
```

**WHY:** Freshers need to develop problem-solving skills, not just implement solutions.

---

**MISTAKE 2: Accepting Vague Answers**

❌ **Bad:**
```
Fresher: "My system learns from the data."
Mentor: "Great! Moving on..."
```

✅ **Good:**
```
Fresher: "My system learns from the data."
Mentor: "Show me. Which line of code does the learning?"
Fresher: "Um... here, I load the CSV."
Mentor: "Loading is not learning. What changes based on what's in the CSV?"
```

**WHY:** Vague understanding leads to vague implementations.

---

**MISTAKE 3: Focusing Only on Code**

❌ **Bad:**
```
Mentor: "Let's review your code line by line."
[Spends 2 hours on syntax and style]
```

✅ **Good:**
```
Mentor: "Before we look at code, explain your approach. How does the system work?"
Fresher: [Explains]
Mentor: "Good. Now show me the code that implements that."
```

**WHY:** Understanding the approach is more important than perfect syntax.

---

**MISTAKE 4: Not Testing Edge Cases**

❌ **Bad:**
```
Mentor: "Your code works with the sample data. Good job!"
```

✅ **Good:**
```
Mentor: "Your code works with the sample data. Now let's test with:
- A CSV with missing values
- A CSV with only 10 users
- A CSV with 10,000 users
- A different company's KB
Does it still work?"
```

**WHY:** Production systems must handle edge cases.

---

**MISTAKE 5: Letting Them Skip Validation**

❌ **Bad:**
```
Fresher: "I'll add validation later."
Mentor: "Okay, let's move on to the next task."
```

✅ **Good:**
```
Fresher: "I'll add validation later."
Mentor: "No, let's add it now. What happens if the CSV is missing a column?"
Fresher: "It will crash."
Mentor: "Exactly. Let's write validation first, then continue."
```

**WHY:** Validation is not optional. It's a core requirement.

---

### 7.6 Success Indicators

**WEEK 1:**
- [ ] Fresher can explain the problem in their own words
- [ ] Fresher can articulate why domain-agnostic design matters
- [ ] Fresher can explain MECE, Octalysis, propensity scores
- [ ] Fresher has drawn an architecture diagram
- [ ] Fresher has identified all deliverables and dependencies

**WEEK 2:**
- [ ] Fresher has working validation for input data
- [ ] Fresher has MECE segmentation with meaningful names
- [ ] Fresher has personalized templates (not generic)
- [ ] Fresher has timing and frequency logic with guardrails
- [ ] Fresher has schedule generation with journey progression

**WEEK 3:**
- [ ] Fresher has performance classification logic
- [ ] Fresher has learning logic that uses experiment_results.csv
- [ ] Fresher can show measurable delta between Iteration 0 and 1
- [ ] Fresher can explain causal reasoning for each change
- [ ] Fresher has all deliverable files with exact naming

**DEMO DAY:**
- [ ] System runs end-to-end without errors
- [ ] System accepts new data at runtime
- [ ] Fresher can walk through Iteration 0 → 1 delta
- [ ] Fresher can answer "why" questions confidently
- [ ] Fresher can explain design decisions and trade-offs

---

## FINAL MENTOR ADVICE

**To the Mentor:**

Your job is not to build the system for them. Your job is to:
1. **Guide** them to discover solutions
2. **Question** their assumptions and decisions
3. **Challenge** them to think deeper
4. **Validate** their understanding
5. **Celebrate** their progress

The best freshers are not those who write perfect code. They're those who:
- Ask good questions
- Explain their reasoning clearly
- Learn from mistakes quickly
- Think about edge cases
- Care about extensibility

Your goal is to develop these qualities, not just deliver a working system.

**To the Fresher:**

This problem is hard. That's the point.

You're not expected to know everything. You're expected to:
- **Learn** new concepts quickly
- **Think** critically about design decisions
- **Prove** your claims with code and data
- **Explain** your reasoning clearly
- **Iterate** based on feedback

The evaluators don't care if you use fancy algorithms. They care if you:
- Understand the problem deeply
- Build a system that works end-to-end
- Prove real learning (Iteration 0 → 1)
- Can explain why you made each decision

Focus on understanding, not just implementation.
Focus on proving, not just claiming.
Focus on learning, not just delivering.

Good luck! 🚀

---

## APPENDIX: Quick Reference

### Key Metrics
- **CTR:** (Opens / Sends) × 100
- **Engagement Rate:** (Engagements / Opens) × 100
- **Activeness Score:** Weighted combination of sessions, exercises, notif_open_rate, streak
- **Propensity Scores:** Probability of responding to specific motivation types

### Classification Thresholds
- **GOOD:** CTR > 15% AND Engagement > 40%
- **BAD:** CTR < 5% OR Engagement < 20%
- **NEUTRAL:** Everything else

### Frequency Rules
- High activeness (>0.7): 7-9 notifs/day
- Medium activeness (0.4-0.7): 5-6 notifs/day
- Low activeness (<0.4): 3-4 notifs/day
- **Guardrail:** If uninstall_rate > 2%, reduce by 2 notifs/day

### Time Windows
- early_morning: 06:00–08:59
- mid_morning: 09:00–11:59
- afternoon: 12:00–14:59
- late_afternoon: 15:00–17:59
- evening: 18:00–20:59
- night: 21:00–23:59

### Octalysis 8 Core Drives
1. Epic Meaning & Calling
2. Development & Accomplishment
3. Empowerment of Creativity & Feedback
4. Ownership & Possession
5. Social Influence & Relatedness
6. Scarcity & Impatience
7. Unpredictability & Curiosity
8. Loss & Avoidance

### Deliverable Files (Exact Names)
- `company_north_star.json`
- `feature_goal_map.json`
- `allowed_tone_hook_matrix.json`
- `user_segments.csv`
- `segment_goals.csv`
- `communication_themes.csv`
- `message_templates.csv`
- `timing_recommendations.csv`
- `user_notification_schedule.csv`
- `experiment_results.csv`
- `learning_delta_report.csv`
- `README.txt` (≤500 words)

---

**END OF MENTOR GUIDE**

*This document is designed to be a comprehensive resource for mentors guiding freshers through the Project Aurora problem statement. Use it as a reference, adapt it to your mentoring style, and remember: the goal is learning, not just delivery.*
