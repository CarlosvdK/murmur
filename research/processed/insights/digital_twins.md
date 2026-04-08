# Digital Twins & LLM Simulation -- Key Insights

## Insight from: park2023generative
**Finding:** LLM agents with structured memory (observations, reflections, plans) produce emergent social behaviors that human evaluators rate as more believable than scripted agents.
**Strength:** High (3,500 citations, UIST best paper)
**Application:** Use structured persona profiles (not just demographic lists) -- include habits, routines, relationships, and recent experiences.
**Prompt fragment:** "This persona has a memory of their relationship with this business. Consider their past experiences, routines, and emotional connections when responding."

## Insight from: park2024thousand
**Finding:** When LLMs are conditioned on 2-hour interviews with real people, they can predict that person's survey responses with 85% accuracy. Demographic data alone achieves only 60%.
**Strength:** High (85 citations for 2024 paper, Stanford HAI)
**Application:** The more specific data we have about a customer (from the business owner's input), the more accurate our persona. Push for rich relationship data, not just demographics.
**Prompt fragment:** "Your accuracy depends on data richness. With only demographics, expect ~60% fidelity. With relationship history and behavioral patterns, expect ~85%."

## Insight from: argyle2023out
**Finding:** LLMs can produce response distributions that match real demographic subgroups when conditioned on backstories ("silicon sampling"). Works best for well-represented demographics, worst for underrepresented groups.
**Strength:** High (750 citations, Political Analysis)
**Application:** Ensure persona diversity covers the actual customer base demographics. Flag when simulating underrepresented groups where LLM training data may be sparse.
**Prompt fragment:** "Generate diverse personas that represent the actual customer base. Flag any persona whose demographic group may be underrepresented in training data."

## Insight from: gui2023challenge
**Finding:** LLM personas exhibit systematic positive bias (20-30% higher acceptance rates than real humans) and homogeneity bias (less variance in responses than real populations). The bias is worst for controversial or emotionally charged topics.
**Strength:** High (45 citations for 2023, Columbia Business School)
**Application:** Apply anti-positive-bias correction. Explicitly instruct personas to resist, complain, and express frustration. Inject at least 20-30% negative reactions even for seemingly positive changes.
**Prompt fragment:** "CRITICAL: LLM personas tend to be ~25% more accepting than real humans. Deliberately include resistance, frustration, and indifference. At least 30% of personas should express some form of negative or skeptical reaction."

## Insight from: kim2024augmented
**Finding:** AI-augmented surveys that combine human responses with LLM predictions can predict opinion distributions for unsurveyed populations with r=0.85 correlation.
**Strength:** Medium (35 citations, emerging methodology)
**Application:** Murmur's approach of combining business owner knowledge with LLM simulation is validated. The owner's input serves as the "human response" that grounds the simulation.
**Prompt fragment:** "The business owner's description of their customers serves as ground truth. Calibrate all persona responses against this baseline rather than generic assumptions."
