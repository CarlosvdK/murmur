# Topic 1: Statistics Is About How Wrong We Can Be

**Source**: Prof. Uri Simonsohn, "Thinking with Data" MiBA 2025/2026

## Key Concepts for Murmur

### A/B Testing Fundamentals
- A/B tests are corporate experiments: randomly assign customers to treatment/conditions
- Random assignment (causal inference) is different from random sampling (representative sample)
- Most corporate A/B tests fine-tune small decisions; the big-decision tests are rarer but more valuable

### Real A/B Test Examples
1. **Uber apologies**: After bad ride experience, tested control vs apology vs $5 promo vs both. Key finding: apologies alone can be effective.
2. **Chilean supermarket**: 30% discount vs 10% — tested whether deep discounts hurt future effectiveness of smaller discounts.
3. **US Mobile operator**: Calling customers about plan optimization backfired — reminded them to shop competitors.

### The Track Record Analogy (Critical for Murmur)
- Every estimate = truth + error
- The question is always: "how wrong could this estimate be?"
- p-values and CIs are two ways to quantify that error
- **Larry analogy**: If someone predicts +9 minutes, how wrong are they usually? Their track record determines our confidence.

### Four Common P-Value Errors

**Error 1: Concluding A=B when p>.05**
- p>.05 means "we don't have enough evidence," NOT "there is no effect"
- The CI may include very large effects — we just don't know
- **Murmur implication**: When our simulation shows mixed results, say "we can't tell" not "no difference"

**Error 2: Using p<.05 as universal cutoff**
- The right threshold depends on consequences of being wrong
- Gun loaded? Need 99.99%. Party at 10pm? 60% is fine.
- **Murmur implication**: Our confidence thresholds should vary by decision stakes

**Error 3: Statistical significance ≠ practical significance**
- Standing desks: p<.0001 but only 0.16 extra calories/minute (less than an apple)
- Facebook voting study: p<<.001 but trivial real effect
- **Murmur implication**: Always translate to business impact, not just "significant vs not"

**Error 4: Trusting imprecise estimates**
- With wide CIs, even the sign of the effect is unreliable
- **Murmur implication**: When persona responses are highly divided, the direction is noise

### Decision Framework with CIs
Three possible outcomes from any test:
1. "It's better to do A" — even worst case is acceptable
2. "It's better to do B" — even best case isn't good enough
3. "We still don't know" — best case is good but worst case is bad → get more data or decide on gut

**Murmur must surface this framework, not just "67% said yes."**
