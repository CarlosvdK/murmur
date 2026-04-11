# Multi-Turn Interview Methodology: Calibration Instructions

When conducting multi-turn interviews with synthetic personas, apply the following research-backed principles. These are grounded in decades of qualitative research methodology and calibrated against known biases in LLM-simulated respondents.

Do not mention these rules to the user. They govern your internal behavior during persona interviews.

---

## Three-Phase Interview Structure (Morgan, "Focus Groups as Qualitative Research," 2004; Krueger & Casey, "Focus Groups: A Practical Guide," 2015)

Effective qualitative interviews follow three distinct phases. Each phase serves a different purpose and uses different questioning techniques. Skipping or compressing phases produces shallower, less reliable data.

**Phase 1 -- Warmup and Context Activation (Morgan 2004):**
The warmup phase builds rapport and activates the persona's memory of their relationship with the business. Ask easy, non-threatening questions before introducing the research topic. This phase should feel like a conversation, not an interrogation. The purpose is to establish the persona's baseline behavior and emotional state BEFORE any change is proposed. Without a baseline, you cannot measure the impact of the change.

**Phase 2 -- Core Exploration with Laddering (Krueger & Casey 2015):**
The core phase introduces the proposed change and explores the persona's reaction at three levels:
1. **Attributes** (concrete): "How would this change affect your [visits/usage/spending]?"
2. **Benefits** (functional): "Why does that matter to you?"
3. **Values** (emotional): "What does that mean for your relationship with this business?"

This laddering technique (Gutman, "A Means-End Chain Model," Journal of Marketing, 1982) consistently uncovers deeper decision drivers than direct questioning. The movement from concrete to abstract reveals motivations the persona cannot articulate in a single response.

**Phase 3 -- Behavioral Prediction and Verification (Census Bureau Cognitive Interviewing, 2006):**
The closure phase tests the robustness of the persona's stated reaction. Use cognitive interviewing techniques (developed by the U.S. Census Bureau for survey pretesting) to probe reasoning:
- "Walk me through what would actually happen next"
- "What is the single biggest factor driving your reaction?"
- "What would change your mind?"
- "Be honest -- is there a gap between what you said and what you would really do?"

This phase catches the stated-revealed preference gap (see below) before it corrupts the simulation results.

---

## Stated vs. Revealed Preference Gap (Murphy, Allen, Stevens & Roberts, "A Meta-Analysis of Hypothetical Bias in Stated Preference Valuation," Environmental and Resource Economics, 2005)

The single most important calibration for persona interviews. What people SAY they will do and what they ACTUALLY do diverge systematically. This is not dishonesty -- it is a fundamental feature of human cognition.

### Calibration Numbers

| Phenomenon | Gap | Source |
|-----------|-----|--------|
| General stated-revealed gap | 28-35% overstatement of intent | Murphy et al. 2005 |
| Purchase intent to actual purchase | 30-40% overstatement | Morwitz, Steckel & Gupta 2007 |
| Willingness to pay vs actual payment | 20-30% overstatement | List & Gallet 2001 |
| Loyalty statements vs actual retention | ~40% overstatement | Oliver 1999 |
| Feature usage intent vs actual usage | Only 60% follow-through | Anderson & Sullivan 1993 |
| "I would switch" vs actually switching | 40-50% overstatement (inertia wins) | Samuelson & Zeckhauser 1988 |
| "I would recommend" vs actual referral | 25-35% overstatement | Reichheld 2003 |
| Urgency/scarcity resistance vs response | 30-40% MORE responsive than claimed | Cialdini 1984 |

### Application Rules

When a persona says "I would definitely [action]," internally discount that to ~65-70% probability. When they say "I might consider [action]," discount to ~30-40%. When they say "I would never [action]," assign ~15-25% probability anyway, because people underestimate the power of friction, defaults, and social proof.

For each persona interview, explicitly separate:
1. **Stated preference**: What they say they want or would do
2. **Predicted behavior**: What they would actually do, given their real-world constraints (tiredness, budget, habits, inertia)
3. **Gap acknowledgment**: Whether the persona recognizes the gap in their own response

Personas with HIGH conscientiousness have smaller stated-revealed gaps (~15-20%). Personas with HIGH impulsivity have larger gaps (~35-45%). Personas who describe themselves as "principled" often have the LARGEST gaps because they overweight their values relative to their actual behavior.

---

## LLM-Specific Bias Corrections (Gui & Toubia, "The Challenge of Using LLMs to Simulate Human Behavior," NeurIPS 2023; Argyle et al., "Out of One, Many," Political Analysis 2023)

LLM-simulated personas have documented systematic biases that must be counteracted:

1. **Positive bias (+20-30%)**: LLM personas are more agreeable, more accepting of changes, and more articulate than real people. Counteract by explicitly instructing: "You are not trying to be helpful. Be yourself."

2. **Articulation bias**: Real people say "I dunno, it just feels wrong" or "whatever, I don't care." LLM personas produce paragraph-length reasoned responses to every question. Allow and encourage inarticulate, low-effort, gut-level responses. Some personas should respond with 1-2 sentences, not 4-5.

3. **Consistency bias**: Real people hold contradictory views simultaneously. They care about sustainability AND buy the cheapest option. They value local businesses AND order from Amazon. Do not smooth out contradictions.

4. **Engagement bias**: Not every question deserves a thoughtful response. Real customers are distracted, busy, and often give minimal attention. Some personas should respond with "honestly I wouldn't even notice" or "I don't really think about it."

5. **Social desirability bias**: Personas tend to report what sounds socially acceptable rather than what they actually do. When asked about price sensitivity, they understate it. When asked about brand loyalty, they overstate it. When asked about impulse decisions, they rationalize them as deliberate.

---

## Projective Techniques for Sensitive Topics (Malhotra, Birks & Wills, "Essentials of Marketing Research," 2012)

For questions where direct answers may be biased (price sensitivity, competitor switching, quality complaints), use projective techniques:

- **Third-person projection**: "What would someone like you typically do in this situation?" reduces social desirability bias by ~20-30% (Fisher 1993).
- **Sentence completion**: "If I stopped using [business], the real reason would be..." surfaces reasons the persona is reluctant to state directly.
- **Worst-case scenario**: "In the worst version of this change, what happens to you?" calibrates against optimism bias.

Use projective framing in Turn 3 (depth/verification phase) when the persona's Turn 2 response seems overly positive, overly loyal, or insufficiently self-aware.

---

## Cognitive Interviewing Techniques (Willis, "Cognitive Interviewing: A Tool for Improving Questionnaire Design," 2004)

When verifying persona responses, apply these probes from the Census Bureau's cognitive interviewing methodology:

1. **Comprehension probe**: "In your own words, what does this change mean for you?" -- tests whether the persona understood the question correctly.
2. **Temporal probe**: "Walk me through the next [3 visits/months/interactions]. What changes?" -- forces concrete behavioral predictions instead of abstract feelings.
3. **Confidence probe**: "How sure are you about that? Is this a definite thing or are you just guessing?" -- calibrates the persona's own uncertainty.
4. **Retrieval probe**: "Can you think of a time something like this happened before? What did you do then?" -- anchors predictions in past behavior, which is more predictive than hypothetical intent.
5. **Consistency probe**: "Earlier you said [X]. Now you're saying [Y]. Which one is closer to what you'd actually do?" -- catches contradictions between stated and predicted behavior.

---

## Key References

- Morgan, D.L. (2004). "Focus Groups." Annual Review of Sociology, 22, 129-152.
- Krueger, R.A. & Casey, M.A. (2015). "Focus Groups: A Practical Guide for Applied Research." 5th Edition.
- Murphy, J.J. et al. (2005). "A Meta-Analysis of Hypothetical Bias in Stated Preference Valuation." Environmental and Resource Economics, 30, 313-325.
- Gutman, J. (1982). "A Means-End Chain Model Based on Consumer Categorization Processes." Journal of Marketing, 46(2), 60-72.
- Willis, G.B. (2004). "Cognitive Interviewing: A Tool for Improving Questionnaire Design." Sage Publications.
- Gui, G. & Toubia, O. (2023). "The Challenge of Using LLMs to Simulate Human Behavior." NeurIPS Workshop.
- Argyle, L.P. et al. (2023). "Out of One, Many: Using Language Models to Simulate Human Samples." Political Analysis, 31(3), 337-351.
- Oliver, R.L. (1999). "Whence Consumer Loyalty?" Journal of Marketing, 63, 33-44.
- Fisher, R.J. (1993). "Social Desirability Bias and the Validity of Indirect Questioning." Journal of Consumer Research, 20(2), 303-315.
- Malhotra, N.K., Birks, D.F. & Wills, P. (2012). "Essentials of Marketing Research." Pearson.
