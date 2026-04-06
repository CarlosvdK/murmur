# Topic 5: Regression to the Mean & Evaluating Interventions

**Source**: Prof. Uri Simonsohn, "Thinking with Data" MiBA 2025/2026

## Key Concepts for Murmur

### What Is Regression to the Mean (RTM)?
- Random processes return to their average over time
- After an extreme outcome (good or bad), the next outcome will likely be closer to the mean
- NOT because of any causal force — just because extreme outcomes include extreme randomness
- Die analogy: after rolling a 1, "cheering" doesn't help — the next roll just averages to 3.5

### When RTM Biases Evaluations
Three conditions must all hold:
1. **Measuring change** (after - before)
2. **Following extreme performance** (intervention triggered by outlier)
3. **Performance has random noise** (always true in business)

### Examples
- Students with low grades get tutoring → grades improve → "tutoring works!" (but it's partly RTM)
- Football team fires coach after bad streak → performance improves → "new coach is better!" (but matched untreated teams show same improvement)
- Bottom 10% of customers targeted with incentives → they buy more → "incentive works!" (but they would have bought more anyway)

### The RTM Trap for Murmur Users

**This is one of the most important caveats we must surface.**

When a small business owner says:
- "Sales have been terrible this month, should I run a promotion?"
- "My Yelp reviews dropped, should I change my menu?"
- "Foot traffic is way down, should I close on Mondays?"

They are asking BECAUSE things are extreme. Even if they do nothing, things will likely improve due to RTM.

**Murmur must warn**: "You're asking this question because things are [good/bad] right now. Some of that is likely random. Even without changes, you'd expect things to move back toward your normal. Our simulation shows how customers would react to the change itself, but can't account for the natural bounce-back you'd get anyway."

### Solutions
1. **A/B test** (overkill for most small businesses)
2. **Control group**: Compare to a similar group that didn't get the intervention
   - "A bit less extreme, same time" — compare bottom 10% to bottom 10-20%
   - "Same extreme, different time" — compare this month's bottom 10% to last year's
3. **Regression with levels** — Outcome_t = a + b*Outcome_{t-1} + c*intervention
   - The coefficient on intervention is NOT biased by RTM

### Choosing Metrics (Valuable Aside)
- Sales = ability + effort + stable circumstances + noise
- If you want to measure effort, choose metrics that isolate it
- Options: absolute change, percentage change, relative to overall trend, within-person rank
- **Murmur implication**: When we show persona responses, we should help users think about WHICH metric matters for their decision, not just "positive vs negative"
