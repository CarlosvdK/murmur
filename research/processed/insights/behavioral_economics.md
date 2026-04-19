# Behavioral Economics -- Key Insights

## Insight from: tversky1974judgment / ariely2003coherent
**Finding:** People anchor numerical judgments to whatever reference they encountered first, even when the anchor is demonstrably random. Willingness-to-pay shifts 60-120% between the highest and lowest arbitrary anchors.
**Strength:** Very High (Tversky & Kahneman in *Science*, Ariely et al. in *QJE*, tens of thousands of citations combined)
**Application:** When a simulation includes pricing, the first price seen sets the frame. A persona shown a $200 premium tier before a $50 standard tier treats $50 as a deal; the same persona without the anchor evaluates $50 on absolute merit.
**Prompt fragment:** "Anchoring is strong: the first price or quantity a persona sees sets the reference. Adjustment from the anchor is typically 30-50% of the way to the correct value, not the full distance."

## Insight from: tversky1981framing
**Finding:** Logically identical outcomes produce different choices depending on framing. "90% success" beats "10% failure" by 20-40% in medical decision studies; loss-avoidance frames ("stop losing $50/month") outperform equivalent gain frames ("save $50/month") by roughly 1.5-2x.
**Strength:** Very High (*Science* 1981, foundational)
**Application:** When simulating reactions to marketing copy, subscription offers, or price presentations, the persona reaction depends on how the information is framed, not just the underlying value.
**Prompt fragment:** "Loss-framed offers are ~1.5-2x more persuasive than equivalent gain frames. Percentage framing wins below ~$100, absolute-dollar framing wins above."

## Insight from: thaler1999mental
**Finding:** People maintain non-fungible mental accounts for different spending categories. A depleted "treats" budget blocks purchases even when the "household" account has surplus. Prepaid experiences feel free at consumption time, and transaction utility ("the deal") delivers satisfaction independent of use value.
**Strength:** Very High (Thaler, Nobel-prize work)
**Application:** When personas are near a real or perceived budget cap in one category, they resist purchases in that category even if total financial resources are adequate.
**Prompt fragment:** "Mental accounts are non-fungible. Personas with a depleted category budget will decline purchases in that category even when total resources allow it."

## Insight from: arkes1985sunk
**Finding:** Sunk costs (money, time, effort already spent) increase willingness to continue by 30-50% even when continuing is objectively worse than stopping.
**Strength:** High (classic finding, widely replicated)
**Application:** Personas who have already invested in a product, subscription, or routine are substantially harder to move away from it -- even when the rational move is to switch. Loyalty programmes that lock in sunk effort (progress bars, status tiers) show outsized retention effects.
**Prompt fragment:** "Personas with significant sunk investment (money, time, loyalty progress) should weight continuation 30-50% higher than the rational calculation would suggest."

## Insight from: kahneman1990endowment
**Finding:** People value what they already possess roughly 2x more than the same thing before possession. Free trials convert at 2-4x the rate of equivalent discounts because the endowment effect turns "removing the trial" into a loss rather than the absence of a gain.
**Strength:** Very High (*JPE* 1990, foundational)
**Application:** Simulating reactions to feature removals, subscription downgrades, or policy changes must weight loss aversion: taking something away is felt ~2x more strongly than adding an equivalent gain.
**Prompt fragment:** "Loss aversion ratio ~2:1. Removing a feature or benefit hits personas roughly twice as hard as adding an equivalent new one."

## Insight from: laibson1997hyperbolic / frederick2002discounting
**Finding:** Discount rates between "now" and "one week from now" are dramatically steeper than between "one year" and "one year and one week." Near-term annualised discount rates are 50-200%; distant rates approach 5-15%.
**Strength:** Very High (*QJE* 1997; *JEL* 2002 meta-analysis)
**Application:** Personas overwhelmingly prefer small immediate rewards over larger delayed ones. A $10 instant discount beats a $15 credit next month for most personas. Conscientiousness reduces but does not eliminate the effect.
**Prompt fragment:** "Hyperbolic discounting: immediate rewards beat larger delayed ones for most personas. Apply strongest to Low-Conscientiousness personas (~30-40% more hyperbolic than High-C)."

## Insight from: johnson2003defaults / thaler2008nudge
**Finding:** Defaults drive 70-90% of choices in opt-out versus opt-in studies. Automatic 401(k) enrolment lifts participation from ~40% to ~90%; opt-out organ donation rates are ~3-5x opt-in rates. The default is treated as an implicit recommendation.
**Strength:** Very High (*Science* 2003; widely replicated across policy domains)
**Application:** The status-quo arm of any simulation holds a huge advantage purely because it is the default. When personas disagree with a proposed change, many will still end up with the change if it becomes the default.
**Prompt fragment:** "Defaults are sticky: 70-90% of personas accept the default option unless they have a specific reason to change it. Opt-out framing converts at 3-5x the rate of equivalent opt-in framing."

## Insight from: banerjee1992herd / dellavigna2009psychology
**Finding:** Under uncertainty, people follow the crowd. With weak private information, personas choose the majority option 60-75% of the time even when private signal mildly favours the alternative. Visible choices show ~30-50% stronger herding than invisible ones.
**Strength:** Very High (*QJE* 1992; *JEL* 2009 meta-analysis)
**Application:** Social-proof, popularity indicators, and visible review counts amplify herding. Personas with high Openness or strong prior experience resist herding; personas with low product familiarity default to the crowd.
**Prompt fragment:** "Under uncertainty, personas herd: visible crowd choices pull 60-75% of low-familiarity personas to the majority option. Visibility amplifies herding by ~30-50%."

## Insight from: thaler1980positive / murphy2005metanalysis
**Finding:** Across hypothetical-survey vs. revealed-preference studies, stated willingness-to-pay exceeds actual willingness-to-pay by roughly 28% on average. Gap is largest for commitments, opt-in programmes, and changes that would require effort.
**Strength:** Very High (Murphy et al. meta-analysis of ~83 studies)
**Application:** Survey-style persona answers systematically overstate positive intention and understate effort costs. Applies across price, loyalty, and feature-adoption questions.
**Prompt fragment:** "Hypothetical-bias correction: stated intentions overstate actual behaviour by ~28% on average. Apply larger corrections (up to 40-50%) for opt-in, commitment, and friction-heavy tactics."
