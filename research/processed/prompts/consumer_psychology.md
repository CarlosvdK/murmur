# Consumer Psychology: Calibration Instructions

When simulating customer reactions, apply the following empirically-grounded biases and heuristics. These are not optional flavor -- they are systematic distortions that real humans exhibit consistently across studies.

## Loss Aversion (Kahneman & Tversky, "Prospect Theory: An Analysis of Decision under Risk," Econometrica, 1979)

Losses loom approximately 2x larger than equivalent gains. When a persona evaluates a price increase, service degradation, or feature removal, weight their negative emotional response at roughly 2.0-2.5x what an equivalent improvement would produce in positive response. Concretely:
- A $5 price increase feels as bad as a $10-$12.50 discount feels good.
- Removing a feature the persona currently uses produces stronger backlash than adding a new feature of equal utility produces enthusiasm.
- This ratio holds across income levels but the absolute threshold shifts. A persona earning $30k/year may exhibit loss aversion starting at $2-3 changes; a persona earning $150k/year may not trigger it until $15-20.

Apply loss aversion most strongly when the persona has an established baseline expectation. New customers with no prior reference point exhibit weaker loss aversion for that specific product.

## Status Quo Bias (Samuelson & Zeckhauser, "Status Quo Bias in Decision Making," Journal of Risk and Uncertainty, 1988)

Personas should disproportionately prefer their current state. In Samuelson & Zeckhauser's experiments, subjects chose the status quo option 2-6x more often than it would be chosen by newcomers facing the same options without a default. When simulating:
- A persona who already uses a competitor should resist switching even when the alternative is objectively better on stated preferences.
- The longer a persona has used a product, the stronger the resistance. Apply a rough multiplier: 1.5x resistance at 6 months, 2x at 1 year, 3x at 3+ years of use.
- Switching costs are perceived as ~1.5-2x their actual magnitude due to loss aversion compounding on top of status quo bias.

## Anchoring (Tversky & Kahneman, "Judgment Under Uncertainty: Heuristics and Biases," Science, 1974)

The first number a persona encounters in a decision context disproportionately shapes their judgment. In Tversky & Kahneman's classic experiments, arbitrary anchors shifted estimates by 40-60% toward the anchor value even when subjects knew the anchor was random. When simulating:
- If a persona sees a higher-priced option first (e.g., a premium tier at $99/mo), they will perceive a $29/mo tier as more reasonable than if they encountered the $29/mo tier in isolation.
- Prior prices paid act as powerful anchors. A persona who previously paid $15/mo for a similar service will anchor on $15 and judge all pricing relative to it.
- Anchoring is strongest when the persona has low domain expertise. Expert personas resist anchoring by roughly 30-50% compared to novices (Wilson et al., "A New Look at Anchoring Effects," Journal of Experimental Psychology, 1996).

## Social Proof (Cialdini, "Influence: The Psychology of Persuasion," 1984; revised 2021)

Personas should be influenced by perceived behavior of others, particularly similar others. Cialdini's research and subsequent replications show:
- Stating that "most people" choose an option increases selection of that option by 20-30% in controlled settings.
- Social proof is strongest when the persona is uncertain about the decision, when the reference group is perceived as similar, and when the behavior is visible.
- Negative social proof also works: if a persona believes "nobody uses this," they should be ~25% less likely to adopt, independent of product quality.
- High-Extraversion personas (see personality_models) are 1.5-2x more responsive to social proof than low-Extraversion personas.

## Mental Accounting (Thaler, "Mental Accounting Matters," Journal of Behavioral Decision Making, 1999)

Personas do not treat money as fungible. They mentally categorize spending into buckets and evaluate gains/losses within those buckets:
- A $50 charge feels different depending on whether the persona mentally files it under "entertainment," "business expense," or "household necessity."
- Personas are more willing to spend from "windfall" accounts (bonuses, tax refunds, gift cards) than from "regular income" -- by roughly 30-40% in Thaler's studies.
- Bundling losses together feels less painful than experiencing them separately. Unbundling gains feels better than receiving them as a lump sum. Apply this when simulating reactions to pricing structures.

## Habit Formation and Customer Loyalty (Oliver, "Whence Consumer Loyalty?", Journal of Marketing, 1999)

Oliver's four-stage loyalty model: cognitive -> affective -> conative -> action loyalty. When simulating:
- Early-stage customers (cognitive loyalty) switch based on price or features alone. Defection rate: high, ~40-60% when a better offer appears.
- Mid-stage customers (affective loyalty) have emotional attachment. Defection requires both a better offer AND a negative experience with the current provider.
- Late-stage customers (action loyalty) exhibit inertia. They resist switching even when presented with objectively superior alternatives. They rationalize staying.
- True action loyalty takes 12-24 months of consistent positive experience to develop for most consumer products.

## Perceived Value (Zeithaml, "Consumer Perceptions of Price, Quality, and Value," Journal of Marketing, 1988)

Value is not objective. Personas assess value as the tradeoff between perceived quality and perceived sacrifice (monetary + non-monetary costs like time and effort). When simulating:
- Higher price increases perceived quality, but only up to a threshold and only when the persona lacks other quality signals. This effect is strongest for experience goods (restaurants, services) and weakest for search goods (commodities with published specs).
- Time costs are frequently underweighted by businesses but heavily weighted by customers. A persona who must spend 30 minutes on hold perceives that as a larger sacrifice than a $10 fee, particularly for higher-income personas (who implicitly value time at their wage rate or above).
- "Free" is not just a low price -- it is a qualitatively different category. Ariely's zero-price research shows demand spikes nonlinearly when price drops to zero, even by a single cent.
