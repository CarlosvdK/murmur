# Murmur — Backtesting Strategy

## Goal

Validate that Murmur's swarm engine produces predictions that directionally match real-world outcomes. We are not aiming for statistical precision — we are aiming to be a useful signal that helps small business owners make better decisions.

## What "Accuracy" Means For Us

We define three levels of accuracy:

1. **Direction**: Did we predict the winning variant correctly? (For A/B questions: did we pick the right winner?)
2. **Magnitude**: Did we get the size of the effect roughly right? (e.g., if the real result was "15% increase in signups", did we predict a meaningful positive effect rather than a marginal one?)
3. **Reasoning quality**: Did our persona responses capture the real reasons behind customer behavior? (Hardest to measure, most valuable)

### Scoring rubric for each backtest case:

| Score | Meaning |
|-------|---------|
| 3 | Correct direction + reasonable magnitude + reasoning aligns with reported real-world feedback |
| 2 | Correct direction + reasoning makes sense, but magnitude is off |
| 1 | Correct direction but reasoning is weak or generic |
| 0 | Wrong direction or "depends"/"tie" when there was a clear winner |
| -1 | Confidently wrong (high confidence + wrong direction) |

**Target**: Average score of 1.5+ across all backtest cases before shipping.

## The Eval Loop

```
For each known A/B test case:

1. CREATE a business profile that matches the company/context
2. INPUT the A/B test question into the swarm engine
3. RUN the simulation (standard settings, 15 personas)
4. RECORD:
   - Did we predict the winning variant? (direction)
   - Did our personas' reasoning match the published explanation? (reasoning)
   - What was the confidence level? (calibration)
   - Full raw output for analysis
5. SCORE using the rubric above
6. ANALYZE patterns:
   - Where do we systematically get it wrong?
   - Is there a positive bias? (do we favor the "nicer" option?)
   - Is there a status quo bias? (do we favor "no change"?)
   - Do certain business types perform better/worse?
7. ADJUST prompts based on findings
8. RE-RUN and compare scores
```

## Known Biases to Watch For

Research on synthetic user simulation (particularly from the synthetic-user-research repo and academic literature) identifies these systematic biases:

### 1. Positive Bias
Synthetic users tend to be overly accepting of changes. They say "sure, I'd be fine with that" more than real customers would. 

**Countermeasure**: Persona prompts explicitly instruct personas not to be people-pleasers. We include contrarian/price-sensitive personas by default. The aggregation prompt is instructed to flag suspiciously unanimous positive results.

### 2. Herd Mentality
When personas are exposed to the question framing, they tend to converge on similar responses. Real customers are more diverse.

**Countermeasure**: Personas are interviewed independently (no shared context). Personality traits are deliberately diverse. We track response variance — if all 15 personas say the same thing, that's a flag, not a feature.

### 3. Anchoring to Provided Information
Personas over-weight the information given in the business profile and under-weight what a real customer would actually notice or care about.

**Countermeasure**: Persona prompts ground responses in the persona's own life and habits, not just the business description. We ask "how does this affect YOUR routine?" not "what do you think of this business decision?"

### 4. Missing Context Blindness
The swarm can't know what it doesn't know. If the business profile doesn't mention that there's a competitor across the street, no persona will factor that in.

**Countermeasure**: The confidence system explicitly flags when business profile information is sparse. The aggregation prompt includes a "what we might be missing" section (to be added in v0.2).

## Backtest Case Selection Criteria

Good backtest cases have:
- **Published results**: We know which variant won and ideally by how much
- **Consumer-facing context**: The test is about something a customer would have an opinion on (not backend infrastructure)
- **Translatable to small business**: We can reasonably construct a business profile that mirrors the context
- **Published reasoning**: Ideally we know WHY the winning variant won, not just that it did

See `docs/known_ab_tests.md` for the full list of cases.

## Limitations of Our Backtesting Approach

1. **Scale mismatch**: Our backtest cases are from large companies (Booking.com, Netflix). Our users are small businesses. Customer behavior at scale may differ from local behavior.

2. **Information asymmetry**: The real A/B tests had access to actual user behavior data. Our swarm only has a business description. This is by design (our users don't have data either), but it means our backtests are testing a harder version of the problem.

3. **Prompt overfitting risk**: If we tune prompts specifically to pass backtest cases, we may overfit to those cases without improving general accuracy. Mitigation: keep a holdout set of 3-4 cases that we don't tune against.

4. **Temporal context**: Some A/B test results were influenced by the specific time period (e.g., during COVID). Our simulation doesn't account for macroeconomic context unless explicitly told.

## Backtesting Schedule

| Phase | When | What |
|-------|------|------|
| Baseline | Before any prompt tuning | Run all cases with v0.1 prompts, establish baseline scores |
| Iteration 1 | After first prompt revision | Re-run, compare to baseline |
| Iteration 2 | After second prompt revision | Re-run, compare to iteration 1 |
| Holdout validation | Before shipping | Run holdout cases for the first time |
| Ongoing | Monthly | Add new published cases, re-run periodically |
