# Topic 3: Multiple Comparisons & P-Hacking

**Source**: Prof. Uri Simonsohn, "Thinking with Data" MiBA 2025/2026

## Key Concepts for Murmur

### Multiple Comparisons Problem
- If you run 1 test with no real effect: 5% chance of false positive
- If you run 20 tests: ~64% chance at least one looks significant
- The probability of SOME comparison being wrong goes up with more comparisons
- "The probability of a given coincidence is nearly 0; the probability of some coincidence is nearly 1"

### Why This Matters for Murmur
Our swarm engine essentially runs multiple "comparisons" — each persona is a separate data point. If we cherry-pick the most dramatic persona responses, we are p-hacking our own output.

### Five Forms of P-Hacking

**1. Data Peeking (stopping early)**
- Checking results daily and stopping when significant
- Airbnb price filter example: significant at day 7, effect disappeared by day 36
- **Murmur caveat**: "If you tested this with real customers, don't stop the test early just because initial results look good"

**2. Outcome Switching**
- Measuring many outcomes, reporting only the significant one
- Falabella: measured 6 different purchase metrics, reported the one that worked
- **Murmur caveat**: "We asked your personas about [specific question]. The answer applies to that question only, not to related metrics."

**3. Subgroups**
- Finding effects only in specific customer segments
- "It works for women aged 25-34 on weekends" — probably noise
- **Murmur caveat**: When personas cluster by demographic, flag that subgroup patterns may not be reliable

**4. Kitchen Sink Regression**
- Adding many variables exploratorily, some will appear significant by chance
- **Murmur caveat**: If a user uploads lots of data dimensions, we should warn that patterns in small subsets may be noise

**5. Ranked Outcomes**
- Comparing best vs worst performers — extreme ranks regress to mean
- Wallet experiment: 12 wallets in 16 cities, ranked return rates — mostly noise
- NFL draft scouting: team differences look meaningful but match random noise
- **Murmur caveat**: When personas are ranked by enthusiasm, the top and bottom may be unreliable

### Solutions
1. **Bonferroni correction**: Adjust significance threshold by number of comparisons (p < .05/N)
2. **Pre-registration**: Decide analysis before collecting data
3. **Replication**: Run the same test again — cheap for businesses

### Murmur Design Implications
- Our aggregator should NOT cherry-pick the most dramatic responses
- When showing "standout voices," explicitly note these are selected for illustration, not proof
- If a user runs the same question multiple times, flag when results change (regression to mean, not real signal)
- Consider running each simulation twice internally and only reporting findings that appear in both runs
