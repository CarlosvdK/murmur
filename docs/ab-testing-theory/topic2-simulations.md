# Topic 2: Simulations & Evaluating Statistical Tests

**Source**: Prof. Uri Simonsohn, "Thinking with Data" MiBA 2025/2026

## Key Concepts for Murmur

### Monte Carlo Simulations
- Traditional stats: abstract assumptions → hard math → closed-form solution
- Simulations: concrete assumptions → generate many datasets → count how often things happen
- Pseudocode pattern: Specify population → Loop { Sample, Calculate, Save } → Analyze

### Central Limit Theorem
- The average of any variable is normally distributed (even if the variable isn't)
- This is why t-tests work on non-normal data — we test means

### Standard Error
- SE = SD / sqrt(N)
- More observations → smaller error → more precise estimates
- **Murmur relevance**: More personas → more stable aggregate results, but with diminishing returns

### Evaluating Confidence Intervals
- A 95% CI procedure is "valid" if 95% of CIs it generates include the true value
- Known as CI "coverage"
- Can test with simulation: generate data with known truth, check if CI captures it

### Evaluating P-Values (False Positive Rate)
- When A=B (no real effect), p<.05 should happen exactly 5% of the time
- **FPR (False Positive Rate)**: How often do you get p<.05 when nothing is happening?
- Valid test: FPR = 5%
- Conservative test: FPR < 5% (too hard to find real effects)
- Anti-conservative/invalid test: FPR > 5% (too easy to get false positives)

### Murmur Implications
1. **Our swarm IS a simulation** — we should think about it with the same rigor
2. We need to test our own system: when we feed it a business where we KNOW the answer, does it get it right?
3. False positive rate matters: if Murmur says "yes, raise prices" when the answer is truly neutral, that's a false positive
4. We should run Monte Carlo-style evaluations on our own prompts using the backtesting cases
5. Our "confidence" rating should be calibrated: when we say "high confidence," we should actually be right most of the time
