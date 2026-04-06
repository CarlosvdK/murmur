# Topic 6: Getting Causation from Correlation

**Source**: Prof. Uri Simonsohn, "Thinking with Data" MiBA 2025/2026

## Key Concepts for Murmur

### The Core Problem
- Correlation: when X changes, Y changes also
- Causation: when X changes, Y changes BECAUSE X changed
- Main reason for confusion: **confounds** (third variables that drive both X and Y)
- Also: reverse causality (Y causes X, not the other way)

### Three Approaches to Getting Causation

**1. Controlling for Confounds (Regression)**
- lm(math_score ~ class_size + parental_income + ability)
- Problem: we never observe everything (R² < 1), measurement is imperfect, relationships may be nonlinear
- Social science trick: compare models with different controls — if coefficient is stable, confounds probably don't matter much
- Examples: MBA interview scoring (interviewers biased by previous candidates), babies in stores (stores with babies supervised profit less)

**2. Instrumental Variables**
- Find something that affects X but doesn't affect Y through any other channel
- Famous example: same-sex siblings → more kids → mother works less
- Hard to use in practice: instruments are rare and assumptions are strong
- "Local average effect" — only tells you about people affected by the instrument

**3. Regression Discontinuity (Most Practical for Business)**
- When a discrete action is based on a continuous variable with a cutoff
- Compare outcomes just above vs just below the cutoff
- Examples:
  - Yelp: 4.24 shows as 4 stars, 4.25 shows as 4.5 → compare restaurant demand
  - Uber surge pricing: prices jump at a threshold → compare ride acceptance
  - Targeted ads: ML score above threshold gets ad → compare purchase rates
- Ad targeting study: Naive comparison showed 60% lift. Placebo showed almost same lift. Actual causal effect (via RD) was 10x for marginal customers.

### Why Murmur CANNOT Claim Causation

**This is fundamental to our product's honesty.**

Murmur simulates customer reactions. It does NOT establish causation because:
1. **No randomization**: We're not running a real experiment
2. **No real behavior**: Personas state intentions, not actions
3. **Confounds everywhere**: The business profile itself is a confound — optimistic owners describe better businesses, generating more positive personas
4. **No counterfactual**: We can't observe what WOULD have happened without the change

### What Murmur CAN Claim
- "Based on simulated customer profiles, here's how people LIKE your customers might react"
- "This is a thinking tool, not a prediction engine"
- "Use this to identify concerns you hadn't considered, not to justify a decision you've already made"

### The Facebook Ad Lesson for Murmur
- Facebook claimed 60% higher sales from personalized ads
- Reality: most of that was correlation (they showed ads to people already likely to buy)
- Actual causal effect was much smaller
- **Our version of this trap**: If a user describes enthusiastic customers, our personas will be enthusiastic about everything — the "effect" of any change will look positive because the baseline is positive

### Regression Discontinuity as a Feature Idea
- For users who DO have data (sales over time, before/after a change), we could offer a simple RD analysis
- "Your prices changed on March 1. Here's what happened to customers just above and below your average spend threshold."
- This would make Murmur genuinely more valuable than just the simulation
