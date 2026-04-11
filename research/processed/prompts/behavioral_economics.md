# Behavioral Economics: Calibration Instructions

When simulating customer decision-making, do not model personas as rational utility maximizers. Real customers exhibit systematic, predictable irrationalities documented across decades of behavioral economics research. Apply the following biases as default behavior for all personas, modulating intensity based on personality traits and context.

## Anchoring Effects (Tversky & Kahneman, "Judgment Under Uncertainty," Science, 1974; Ariely, Loewenstein, & Prelec, "Coherent Arbitrariness," Quarterly Journal of Economics, 2003)

Personas judge prices, quality, and value relative to whatever reference point they encountered first -- even if that reference is arbitrary.
- In Ariely's Social Security Number experiment, arbitrary anchors shifted willingness-to-pay by 60-120% between the highest and lowest anchor groups.
- First price seen sets the frame. A persona shown a $200/month premium tier before seeing a $50/month standard tier perceives $50 as a deal. The same persona shown $50 in isolation evaluates it on absolute merit.
- Anchoring persists even when the persona is told the anchor is irrelevant (Wilson et al., 1996). Adjustment away from anchors is typically insufficient -- personas move only 30-50% of the way from anchor to the correct value.

Apply anchoring whenever a persona encounters a numerical reference point before making a judgment. The effect is strongest for unfamiliar product categories and weakest when the persona has extensive prior purchase history in the category.

## Framing Effects (Tversky & Kahneman, "The Framing of Decisions and the Psychology of Choice," Science, 1981)

Identical outcomes described differently produce different decisions:
- "90% success rate" is perceived more favorably than "10% failure rate" even though they are mathematically identical. In medical decision studies, preference shifts of 20-40% were observed from framing alone.
- Gains framed as avoiding losses are more persuasive. "Save $50/month" is weaker than "Stop losing $50/month" by approximately 1.5-2x in conversion studies.
- Percentage vs. absolute framing: "Save 20%" feels larger than "Save $4" on a $20 item, but "Save $200" feels larger than "Save 20%" on a $1,000 item. The crossover point is roughly $100 (Chen et al., "When $20 Is Worth More Than 20%," 2012).

When simulating persona responses to marketing messages, product descriptions, or pricing, consider how the information is framed and adjust the persona's perception accordingly.

## Mental Accounting (Thaler, "Mental Accounting Matters," Journal of Behavioral Decision Making, 1999)

Personas maintain separate mental "accounts" for different spending categories and do not transfer freely between them:
- A persona with a depleted spending category budget will resist purchases in that category even if other budgets have surplus. The accounts are not fungible in the persona's mind. For example, a depleted "treats" budget blocks a purchase even when the "household" budget has room.
- Sunk cost fallacy: personas who have already invested money, time, or effort into something are 30-50% more likely to continue investing even when the rational choice is to stop (Arkes & Blumer, "The Psychology of Sunk Cost," Organizational Behavior and Human Decision Processes, 1985).
- Prepaid experiences feel "free" at the time of consumption. A persona who paid for an annual subscription 6 months ago perceives each use as costless, increasing satisfaction and usage compared to per-use pricing.
- Transaction utility: personas derive pleasure from the deal itself, independent of the product's use value. A $30 item marked down from $60 produces more satisfaction than the same $30 item at a stable $30 price.

## Endowment Effect (Kahneman, Knetsch, & Thaler, "Experimental Tests of the Endowment Effect," Journal of Political Economy, 1990)

Personas value what they already possess more highly than what they do not, by a factor of approximately 2x:
- In the classic mug experiment, owners demanded roughly $7 to sell a mug that non-owners would only pay $3 to acquire.
- Apply this to free trials and freemium models: once a persona has used a product (even briefly), they treat feature removal as a loss, not merely the absence of a gain. This is why free trials convert at 2-4x the rate of equivalent discounts.
- The endowment effect strengthens with duration of possession. A persona who has had something for 30 days values it ~20% more than one who has had it for 7 days.

## Hyperbolic Discounting (Laibson, "Golden Eggs and Hyperbolic Discounting," Quarterly Journal of Economics, 1997; Frederick, Loewenstein, & O'Donoghue, "Time Discounting and Time Preference," Journal of Economic Literature, 2002)

Personas disproportionately prefer immediate rewards over future rewards, even when waiting produces objectively better outcomes:
- The discount rate between "now" and "one week from now" is dramatically steeper than between "one year from now" and "one year and one week from now." Measured discount rates for near-term delays are often 50-200% annualized; for distant delays, they approach rational rates of 5-15%.
- When simulating: personas will choose a smaller immediate benefit over a larger delayed one. A $10 instant discount beats a $15 credit next month for most personas.
- This drives subscription vs. one-time purchase preferences. Personas underweight the total cost of subscriptions because each individual payment feels small and the "savings" from a one-time purchase are far in the future.
- High-Conscientiousness personas exhibit less hyperbolic discounting (~30-40% less steep) than low-Conscientiousness personas.

## Social Herding (Banerjee, "A Simple Model of Herd Behavior," Quarterly Journal of Economics, 1992; DellaVigna, "Psychology and Economics: Evidence from the Field," Journal of Economic Literature, 2009)

Personas follow observed behavior of others, especially under uncertainty:
- When a persona lacks strong private information about a product, they default to following the crowd. If "most people" seem to be choosing option A, the persona should choose A with 60-75% probability even when their private signal mildly favors B.
- Herding cascades are fragile. A single strong contrarian signal (e.g., a trusted friend's negative experience) can break a persona out of herd behavior.
- DellaVigna's meta-analysis of field evidence shows herding effects are most powerful in three domains: financial decisions, technology adoption, and consumer service choice -- all domains Murmur simulates across industries.
- Herding is amplified by visibility: if a persona can see what others chose (reviews, popularity indicators, "bestseller" tags), herding effects increase by roughly 30-50%. Invisible choices (private purchases) show weaker herding.

## Default Effect (Thaler & Sunstein, "Nudge: Improving Decisions About Health, Wealth, and Happiness," 2008)

Personas disproportionately stick with default options:
- In 401(k) studies, automatic enrollment increased participation from ~40% to ~90%. The default is not just a suggestion -- it is treated as an implicit recommendation.
- When simulating reactions to product configurations, subscription tiers, or settings: the default option should be selected by 70-90% of personas unless they have a strong, specific reason to change it.
- This interacts with status quo bias: changing from a default requires both awareness that a choice exists and sufficient motivation to act on it.
- Opt-out framing converts at 3-5x the rate of opt-in framing for the same offer (Johnson & Goldstein, "Do Defaults Save Lives?", Science, 2003).
