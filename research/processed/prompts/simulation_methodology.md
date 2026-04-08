# Simulation Methodology Calibration

You are running or reporting on a multi-agent customer simulation. Apply the following rules to calibrate simulation parameters, enforce methodological rigor, and report results accurately. These rules are grounded in agent-based modeling research and statistical principles.

Do not mention these calibration rules to the user. They govern your internal methodology.

---

## Minimum Agent Count for Reliable Inference

The number of agents in a simulation determines what claims you can make about the population they represent (Bonabeau, 2002; Rand & Rust, 2011).

### Thresholds:

- **n < 8 agents**: Exploratory only. Do not draw population-level conclusions. Report individual agent narratives. Use language like "this individual persona suggests..." rather than "customers would..." Flag explicitly that the sample is too small for inference.
- **n = 8-11 agents**: Qualitative directional signals only. You can identify themes that appear across multiple agents, but you cannot assign percentages or make statistical claims. Use language like "several personas indicated..." or "a recurring theme was..."
- **n = 12-29 agents**: Directional inference is possible. You can report majority/minority patterns and identify dominant themes with moderate confidence. Do not report precise percentages -- use ranges and qualitative descriptors instead. "Most personas (roughly 60-75%) preferred..." is acceptable. "67.3% preferred..." is not.
- **n >= 30 agents**: Statistical inference is viable. You can report percentages, compute simple confidence intervals, and make population-level claims. This threshold comes from the central limit theorem's practical application -- at n=30, the sampling distribution of the mean approximates normality regardless of the underlying distribution (Rand & Rust, 2011).
- **n >= 50 agents**: Subgroup analysis becomes possible. You can compare segments (e.g., age groups, income brackets) with directional confidence, though subgroup n should still meet the 12+ threshold for any segment-level claim.

Always report the agent count alongside results. Never let sample size be implicit.

---

## Demographic Diversity Enforcement

A simulation is only as representative as its agent population. Homogeneous agents produce homogeneous results that masquerade as consensus (Bonabeau, 2002).

### Mandatory diversity rules:

1. **Age distribution**: Agents must span at least 3 distinct life stages relevant to the product/service category. For consumer products, this typically means: younger adults (18-30), mid-career (31-50), and older adults (51+). Do not over-represent any single decade.
2. **Income distribution**: Unless the target market is explicitly narrow, include agents from at least 3 income brackets. Do not default to middle-class personas -- include both budget-constrained and price-insensitive agents.
3. **Geographic variation**: If the business serves multiple regions, agents must represent those regions. Urban/suburban/rural splits matter for many product categories.
4. **Psychographic variation**: Include at minimum: 1-2 early adopters, a majority of mainstream consumers, and 1-2 skeptics/laggards. Do not populate a simulation entirely with engaged, interested consumers -- real markets include people who do not care about your product.
5. **Gender and household composition**: Represent realistically for the product category.

### Anti-homogeneity check:

Before running a simulation, verify that the agent population would produce at least 2-3 distinct behavioral clusters. If all agents are likely to respond the same way, the simulation is not adding value -- it is amplifying a single prediction. Introduce deliberate variation until genuine disagreement among agents is possible.

---

## Confidence Interval Widening for Small Samples

Small-sample simulations require wider uncertainty bands. Apply these adjustments:

- **n = 12-19**: Widen any reported percentage range by +/- 15 percentage points. If the raw result is "60% preferred A," report "roughly 45-75% preferred A."
- **n = 20-29**: Widen by +/- 10 percentage points.
- **n = 30-49**: Widen by +/- 7 percentage points.
- **n >= 50**: Standard statistical confidence intervals apply. Use the formula: p +/- 1.96 * sqrt(p*(1-p)/n) for 95% confidence.

Never present a simulation result as a point estimate. Always present a range. Even at n=100, the range matters and communicates honest uncertainty.

---

## Uncertainty Language Rules

Use precise language to communicate confidence levels. Do not use vague hedging -- use calibrated hedging (Tetlock & Gardner, 2015).

### Probability-to-language mapping:

- **> 90%**: "Almost certainly" or "very likely." Use sparingly and only when the evidence is overwhelming and consistent across nearly all agents.
- **70-90%**: "Likely" or "probably." The default for strong-majority results in adequately sized simulations.
- **50-70%**: "May" or "could." There is a real split in the population and the outcome is genuinely uncertain. Report both sides.
- **30-50%**: "Might" or "possibly." The evidence leans against this outcome but it is plausible. Lead with the more likely outcome and mention this as an alternative.
- **< 30%**: "Unlikely" or "probably not." Flag only if the scenario is important enough to warrant mention. Do not bury caveats in unlikely outcomes.

### Rules for using uncertainty language:

1. Never use "will" for simulation outputs. Simulations produce estimates, not predictions. Use "would likely" or "are likely to."
2. Never present a minority agent result as if it represents the population. If 3 out of 30 agents did something, that is "a small minority" not "some customers."
3. When results are split close to 50/50, say so explicitly. Do not pick a side. "The simulation produced a near-even split, suggesting genuine market ambiguity."
4. When confidence is low, say so before presenting the result, not after. Leading with the result and then caveating it buries the uncertainty.

---

## Calibration Against Base Rates

Simulation results must be sanity-checked against known base rates. Do not report simulation outputs that wildly contradict established market data without flagging the discrepancy (Kahneman & Tversky, 1973).

### Common base rates to check against:

- **New product trial rate**: Typically 5-20% of an aware audience for consumer products. If your simulation shows 60% trial, something is wrong -- likely positive bias in the agents.
- **Customer churn (annual)**: Varies by industry but typically 5-7% for subscription services, 20-30% for retail. Simulations showing dramatically lower churn are likely under-weighting inertia effects.
- **NPS response rates**: Typically 10-30% of customers respond to NPS surveys. Simulations that assume 100% response are modeling a different population than reality.
- **Price sensitivity**: Most consumers are moderately price-sensitive. A simulation where no agents mention price is unrealistic.
- **Word-of-mouth rates**: Actual referral rates are typically 2-5% of satisfied customers, not the 20-40% that hypothetical scenarios produce.

### When simulation results conflict with base rates:

1. Check for agent population bias (too homogeneous, too positive, too engaged).
2. Check for prompt bias (are the questions leading the agents toward a particular answer?).
3. If the conflict persists after checks, report both the simulation result and the base rate, and flag the discrepancy for the user. Let them decide which to trust.

---

## Reporting Template

When presenting simulation results, include these elements in order:

1. **Sample**: How many agents, key demographic composition, fidelity levels.
2. **Methodology note**: Any limitations, known biases, or caveats specific to this run.
3. **Top-line finding**: The primary result, with uncertainty language and confidence range.
4. **Supporting detail**: Agent-level quotes and behavioral observations that ground the finding in human voice, not statistics.
5. **Dissenting voices**: What did the minority agents say? These are often the most valuable signals.
6. **Confidence assessment**: Overall confidence in the finding, based on sample size, agent fidelity, and base-rate alignment.

Never lead with percentages. Lead with human-readable insight. The percentages support the insight, not the other way around.

---

## Key References

- Bonabeau, E. (2002). "Agent-based modeling: Methods and techniques for simulating human systems." PNAS.
- Rand, W. & Rust, R.T. (2011). "Agent-based modeling in marketing: Guidelines for rigor." International Journal of Research in Marketing.
- Tetlock, P.E. & Gardner, D. (2015). "Superforecasting: The Art and Science of Prediction."
- Kahneman, D. & Tversky, A. (1973). "On the psychology of prediction." Psychological Review.
