# Simulation Methodology -- Key Insights

## Insight from: murphy2005metanalysis
**Finding:** Across 83 hypothetical-vs-revealed preference studies, stated willingness-to-pay exceeded actual willingness-to-pay by a median of ~28%. The hypothetical bias is larger (40-50%) for commitment, opt-in, and effort-requiring decisions.
**Strength:** Very High (*Environmental & Resource Economics* meta-analysis)
**Application:** Any simulation that asks "would you..." must correct for hypothetical bias. For friction-reducing tactics (guest checkout, one-click, default opt-in), personas predict they will not be influenced; real users overwhelmingly are.
**Prompt fragment:** "Apply Murphy-style correction: stated intention overstates actual behaviour by ~28% on average, up to 40-50% for opt-in and commitment questions."

## Insight from: guitoubia2023llm
**Finding:** LLM-generated synthetic respondents systematically overstate acceptance of changes by 20-30% relative to matched real panels. The overshoot is largest for decisions framed as helpful or pro-social and smallest for clearly self-interested price decisions.
**Strength:** Medium-High (recent; direction of effect is consistent across replications)
**Application:** Persona-based simulations need an "anti-agreeableness" correction. Without it, LLM personas drift toward polite, thoughtful, accepting answers regardless of prompt framing. Structural anti-bias (fixed OCEAN levels, silent-majority proportions) is more effective than prompt-level admonitions.
**Prompt fragment:** "LLM personas exhibit a ~20-30% optimism bias. Structurally enforce diverse traits and silent-majority proportions -- do not rely on prompt-level 'be honest' instructions alone."

## Insight from: park2023generative / argyle2022out
**Finding:** Generative agents can approximate group-level behavioural patterns when conditioned on rich demographic and psychological context, but individual-level predictions remain substantially noisier than panels. Group-level aggregates (distribution of reactions) are more reliable than pointing to a specific persona's future behaviour.
**Strength:** Medium-High (Park et al. 2023 Stanford; Argyle et al. 2022 *Political Analysis*)
**Application:** Murmur-style aggregation (swarm of 15+ personas with distribution-level analysis) is methodologically defensible. Individual persona forecasts should be treated as illustrative, not predictive.
**Prompt fragment:** "Group-level aggregates are defensible; individual-level persona predictions are illustrative. Present distributions of reactions, not point predictions about any one persona."

## Insight from: neurips2025anchoring (structured demographic anchoring)
**Finding:** Fixing persona demographic fields (age, income tier, visit frequency, price sensitivity) before LLM narrative generation produces persona distributions closer to ground-truth panels than freeform LLM generation. Narrative quality suffers slightly; predictive accuracy improves measurably.
**Strength:** Medium (recent NeurIPS workshop; direction consistent)
**Application:** Murmur's manifest-constrained generation path implements this. Freeform generation should be the fallback, not the default. When review data is unavailable, synthesise demographic priors rather than dropping the manifest.
**Prompt fragment:** "Structured anchor first, narrative second. Demographic fields (age, income, visit frequency, price sensitivity) are fixed before LLM generation; the LLM only adds narrative within those constraints."

## Insight from: gao2015vocal / iclr2024silent
**Finding:** The silent majority (55-70% of customers who never review or respond to surveys) drives more actual business outcomes than the vocal minority that shapes perception. Silent-majority modelling improves simulation accuracy by 10-20% on outcome-sensitive questions.
**Strength:** High (*MIS Quarterly* 2015; ICLR 2024 simulation calibration work)
**Application:** Persona manifests must explicitly allocate 55-70% of the swarm to silent-majority personas with moderate views, habitual engagement, and low complaint propensity. Without this, aggregations over-index on the loudest quintile.
**Prompt fragment:** "Silent majority is 55-70% of the swarm. These personas never review, never complain publicly, and defect quietly. Their presence pulls aggregate predictions toward lived-outcome reality."

## Insight from: simonsohn2020three (three-outcome decision framework)
**Finding:** Field experiments and simulations should report three outcomes: "do it", "don't do it", or "we cannot tell." Forcing a binary answer when the confidence interval crosses zero produces false precision and degrades long-run decision quality.
**Strength:** High (Simonsohn methodology work)
**Application:** Murmur's impact estimator and aggregator must return "cannot tell" / "tie" when evidence is mixed, not default to a confident recommendation. Users need permission to wait for more data, not just go/no-go buttons.
**Prompt fragment:** "Three outcomes, not two: proceed, avoid, or 'we cannot tell -- gather more data.' Ties and low-confidence mixed signals must not be forced into a confident recommendation."

## Insight from: tversky1974judgment (confidence calibration)
**Finding:** Human judges -- and LLM judges -- are systematically overconfident in their own predictions. Stated "high confidence" predictions are correct 65-75% of the time rather than the implied 90%+. Frequency calibration requires explicit structural rules, not subjective self-assessment.
**Strength:** Very High (foundational calibration literature)
**Application:** Do not let the aggregator claim "high" confidence on self-report alone. Cap confidence based on objective conditions: persona success rate, business profile completeness, context-narrative length, known stated-vs-revealed tactic presence.
**Prompt fragment:** "Confidence must be earned structurally: tie 'high' to objective conditions (thick profile, >80% persona success, no known stated-vs-revealed tactic). Default to 'medium' when any condition fails."

## Insight from: holtgraves2004social (social desirability)
**Finding:** Respondents (and LLM agents trained on human data) systematically skew toward socially desirable answers. They overstate eco-friendly choices, understate impulse purchases, and overstate likelihood of opting into prosocial programmes.
**Strength:** High (*Psychological Assessment* and follow-ups)
**Application:** Prompt-level "be honest" instructions modestly reduce but do not eliminate social-desirability bias. Explicit two-shot elicitation (stated then actual, without allowing consistency pressure between the two) surfaces the gap more reliably than a single question.
**Prompt fragment:** "Two-shot elicitation: ask the stated preference in one turn, then ask the ACTUAL behaviour in a follow-up that explicitly instructs the persona not to be consistent with the first answer. The gap between the two is the key signal."
