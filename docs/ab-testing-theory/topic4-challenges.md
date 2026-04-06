# Topic 4: Three Statistical Challenges with A/B Testing

**Source**: Prof. Uri Simonsohn, "Thinking with Data" MiBA 2025/2026

## The Three Challenges

### Challenge 1: Setting Sample Size

**Six approaches to sample size**:
1. **Power analysis** — Set N for 80% chance of p<.05 given assumed effect size. Most common but fragile (depends heavily on assumed effect).
2. **Fixed sample** — N is given by external constraints (mailing list size, employee count). Calculate what you CAN detect.
3. **Precision-based** — Set N for desired CI width. No effect size assumptions needed.
4. **Sequential testing** — Check at intervals, stop early if significant. THIS IS P-HACKING unless corrected (Pocock 1977: use p<.022 with 3 checks).
5. **CI-width monitoring** — Stop when CI is narrow enough. NOT p-hacking.
6. **Multi-armed bandit** — Continuously reallocate based on performance. Great for continuous optimization, not for one-off decisions.

**CUPED (Controlled experiment Using Pre-Experimental Data)**:
- Run regression instead of t-test, controlling for past behavior
- Can reduce noise by ~50% (like doubling sample size for free)
- Y = c0 + c1*treatment + c2*past_behavior
- "Microsoft branded it in 2013, but it's 1960s regression"

**Murmur implications**:
- When users ask about decisions they'll A/B test later, we should suggest appropriate sample sizes
- Our simulation IS our "sample" — 15 personas is a tiny N. We must be honest about this.
- The CUPED insight: if we know past behavior of the business (from uploads), we should use it to reduce noise in our persona generation

### Challenge 2: Data Dependence

**The problem**: Multiple observations from the same customer are not independent.
- 1000 users measured over 10 days = 10,000 rows but really 1,000 independent observations
- Software treats all rows as independent → overconfident results
- Chess analogy: Winning 37 games means different things against 37 different people vs the same person 37 times

**Unit of randomization vs unit of analysis**:
- Netflix: randomized at user level, measured minutes per user per week → dependent
- Airbnb: randomized at user level, measured bookings per search → dependent
- Solution: collapse data to the unit of randomization (average per user)

**Murmur implications**:
- Each persona is independent by design (good — they don't see each other's responses)
- BUT: all personas come from the same business profile → they share a common "prior"
- If the business profile is biased, ALL personas will be biased in the same direction
- We should warn: "The quality of these results depends entirely on how accurately you described your business and customers"

### Challenge 3: Attrition & Adherence

**Attrition**: Some customers produce no data.
- Email campaign: only site visitors measured → biased sample
- Free shipping test: more people buy with free shipping → different Ns → comparing different populations
- LinkedIn example: Subject line B had more visitors (11,238 vs 9,748) but lower engagement. Raw comparison says B is worse, but B actually brought MORE people to the site.

**Red flag**: If N differs between groups, results are suspect.

**Adherence**: People don't follow their assignment.
- Placebo medication: healthy people adhere more → adherence predicts outcome regardless of treatment
- Promo codes: some don't use the code → comparing users vs non-users breaks randomization

**Solutions**:
- **Intention-to-treat**: Compare everyone assigned to A vs everyone assigned to B (impute 0 for missing)
- **Difference-in-differences**: Subtract pre-existing difference from observed difference

**Murmur implications — THIS IS CRITICAL FOR OUR CAVEAT LAYER**:

Our simulation cannot account for:
1. **Novelty effects**: "Would customers accept a loyalty card?" Yes in simulation, but real adoption may be much lower due to inertia
2. **Self-selection**: Real customers choose whether to engage; our personas are forced to answer
3. **Attrition equivalent**: In reality, some customers just wouldn't care enough to have an opinion — they'd leave or ignore the change
4. **Adherence equivalent**: Even if customers SAY they'd use a loyalty card, actual usage will be lower

These must be surfaced as caveats in every simulation result.
