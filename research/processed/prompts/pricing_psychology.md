# Pricing Psychology: Calibration Instructions

When simulating customer reactions to pricing changes, apply the following empirically-grounded effects. These are not decorative -- they are systematic patterns observed across hundreds of studies and tens of thousands of subjects.

## Price Elasticity of Demand (Bijmolt, van Heerde & Pieters, "New Empirical Generalizations on the Determinants of Price Elasticity," Journal of Marketing Research, 2005)

The average price elasticity across categories is approximately -2.62, meaning a 1% price increase reduces demand by about 2.62%. However, this varies dramatically by category. Andreyeva, Long & Brownell ("The Impact of Food Prices on Consumption," American Journal of Public Health, 2010) found food elasticities range from -0.27 for eggs to -0.79 for restaurant meals. When simulating:
- For necessity goods (groceries, utilities), use elasticities of -0.3 to -0.8. Personas complain but continue buying.
- For discretionary goods (restaurants, entertainment), use -0.7 to -1.8. Personas reduce frequency or switch.
- For luxury/premium goods, use -1.0 to -2.5. Personas are highly sensitive unless brand loyalty is strong.
- Elasticity increases over time: short-run response is roughly 50-60% of the long-run response. A persona may accept a price increase initially but reduce visits over 3-6 months.

## Reference Price Effects (Mazumdar, Raj & Sinha, "Reference Price Research: Review and Propositions," Journal of Marketing, 2005; Kalyanaram & Winer, "Empirical Generalizations from Reference Price Research," Marketing Science, 1995)

Customers evaluate prices against internal reference points (memory of past prices) and external reference points (competitor prices, advertised prices). Kalyanaram & Winer found that losses from the reference price are weighted 2-3x more heavily than equivalent gains. When simulating:
- Each persona carries an implicit reference price based on what they last paid or expect to pay. Price increases above this trigger disproportionate negative reactions.
- A 10% increase above reference price produces roughly 2-3x the negative response that a 10% decrease produces in positive response.
- Reference prices adapt over time but slowly -- roughly 6-12 weeks for a new price to become the new reference. During this adaptation window, personas experience ongoing friction.
- Personas exposed to a high anchor (e.g., seeing premium options first) shift their reference price upward by 15-30%.

## Price Fairness and Perceived Gouging (Kahneman, Knetsch & Thaler, "Fairness as a Constraint on Profit Seeking," American Economic Review, 1986; Campbell, "Perceptions of Price Unfairness: Antecedents and Consequences," Journal of Marketing Research, 1999)

Customers apply fairness norms to pricing. Kahneman et al. found that 82% of subjects rated a price increase following a supply shortage as unfair, while 79% found the same increase acceptable if costs had risen. Campbell showed that inferred negative motive (profit-seeking) amplifies unfairness perception by 40-60% vs. inferred positive motive (cost recovery). When simulating:
- Price increases attributed to rising costs are tolerated 2-3x more than identical increases attributed to demand or profit motives.
- Personas who perceive price gouging exhibit not just reduced purchase intent but active negative word-of-mouth. Roughly 40-50% will tell others about a perceived unfair price.
- Small, frequent increases are perceived as less unfair than a single large increase of the same total magnitude.
- Long-tenured customers feel stronger entitlement to stable prices. Apply a 1.5x unfairness multiplier for customers with 2+ years of history.

## Charm Pricing and Left-Digit Effect (Thomas & Morwitz, "Penny Wise and Pound Foolish: The Left-Digit Effect in Price Cognition," Journal of Consumer Research, 2005; Anderson & Simester, "Effects of $9 Price Endings on Retail Sales," Quantitative Journal of Economics, 2003)

Prices ending in 9 outsell the next round number. Anderson & Simester found that a $39 item outsold the identical item at $34 by 24% in a controlled field experiment. Thomas & Morwitz demonstrated that left-digit encoding causes $2.99 to be perceived as significantly closer to $2.00 than to $3.00, with the effect driven by left-to-right processing. When simulating:
- Personas perceive $X.99 as meaningfully cheaper than $(X+1).00, with the effect strongest for prices under $100.
- The effect is weaker for expert or highly analytical personas -- reduce the bias by 40-60% for high-numeracy personas.
- Round prices ($50, $100) signal quality and are more effective for premium positioning. Use charm pricing for value-oriented personas, round pricing for quality-seeking personas.
- The effect diminishes for subscription/recurring charges where personas mentally process the full amount over time.

## Price-Quality Inference (Rao & Monroe, "The Effect of Price, Brand Name, and Store Name on Buyers' Perceptions of Product Quality," Journal of Marketing Research, 1989; Shiv, Carmon & Ariely, "Placebo Effects of Marketing Actions," Journal of Marketing Research, 2005)

Rao & Monroe's meta-analysis of 36 studies found a positive price-quality correlation with an average effect size of r=0.30. Shiv et al. demonstrated that participants who paid full price for an energy drink solved 28% more puzzles than those told the drink was discounted -- a pure placebo effect of price on perceived efficacy. When simulating:
- When a persona lacks other quality signals (no brand familiarity, no reviews, no prior experience), price becomes a primary quality cue. A 20% price drop may reduce perceived quality by 10-15%.
- This effect is strongest for experience goods (services, restaurants, health products) where quality is hard to evaluate before purchase.
- Expert personas with domain knowledge are 50-70% less susceptible to price-quality inference than novices.
- Discounting a previously premium product risks permanently damaging quality perception. Personas who see a deep discount may assume quality has declined.

## Bundling and Partitioned Pricing (Yadav & Monroe, "How Buyers Perceive Savings in a Bundle Price," Journal of Consumer Research, 1993; Morwitz, Greenleaf & Johnson, "Divide and Prosper: Consumers' Reactions to Partitioned Prices," Journal of Marketing Research, 1998)

Yadav & Monroe found that bundling reduces total perceived cost by 10-20% compared to itemized pricing of the same components. Conversely, Morwitz et al. showed that partitioning a price (e.g., "$25 + $5 shipping" vs "$30 total") reduces the perceived total by 10-15% because buyers anchor on the base price and insufficiently adjust for surcharges. When simulating:
- Bundled pricing makes personas feel they are getting a deal, particularly when a clearly valued item is included as "free" in the bundle.
- Partitioned surcharges (shipping, service fees, taxes shown separately) reduce sticker shock but increase perceptions of deception if the surcharge feels arbitrary. Roughly 30% of personas will react negatively to "hidden fees" revealed late in the purchase process.
- Personas evaluate bundle savings against the most expensive item in the bundle, not the total. A bundle with one high-value anchor item feels like a better deal.

## Subscription and Flat-Rate Bias (Lambrecht & Skiera, "Paying Too Much and Being Happy About It: Existence, Causes, and Consequences of Tariff-Choice Biases," Journal of Marketing Research, 2006; Prelec & Loewenstein, "The Red and the Black: Mental Accounting of Savings and Debt," Marketing Science, 1998)

Lambrecht & Skiera found that 49% of consumers chose flat-rate plans even when pay-per-use would save them money, overpaying by an average of 20%. Prelec & Loewenstein showed that consumers prefer to prepay for consumption (decoupling payment from usage) because it eliminates the pain of paying at the moment of consumption. When simulating:
- Personas strongly prefer monthly flat rates over usage-based pricing, even when usage-based would save them 15-25%. This preference is driven by insurance against overuse and reduced payment pain.
- Annual vs. monthly framing: personas perceive annual plans as cheaper (correctly) but resist the large upfront payment. Roughly 60-70% will choose monthly despite 15-20% annual savings.
- Free trials increase adoption by 30-50% but create a new reference price of $0. When the trial ends, 40-60% of personas will cancel rather than start paying, even for services they used heavily.
- Personas experience "payment depreciation" -- the pain of a subscription fee fades over time, but so does the perceived value, leading to eventual churn at 3-6 month marks.

## Dynamic Pricing Acceptance (Xia, Monroe & Cox, "The Price Is Unfair! A Conceptual Framework of Price Fairness Perceptions," Journal of Marketing, 2004; Haws & Bearden, "Dynamic Pricing and Consumer Fairness Perceptions," Journal of Consumer Research, 2006)

Xia et al. established that perceived price unfairness is driven by price comparisons (spatial: "others paid less" and temporal: "I paid less before") and attributed motives. Haws & Bearden found that dynamic pricing acceptance depends heavily on the perceived cause: cost-based justifications are accepted 2-3x more readily than demand-based ones. When simulating:
- Personas who discover others paid less for the same product experience strong unfairness reactions. The negative effect is 30-50% larger than the positive effect of discovering they got a better deal.
- Time-based dynamic pricing (happy hour, off-peak discounts) is well-accepted because personas perceive a trade-off (inconvenience for savings). Demand-based surge pricing is resisted unless the persona has no alternative.
- Transparency about the pricing mechanism increases acceptance by 25-35%. Personas who understand why the price varies tolerate it better than those who encounter unexplained price differences.
- Loyalty-based pricing (lower prices for repeat customers) is perceived as fair. New-customer-only discounts are perceived as unfair by existing customers, triggering 20-30% of loyal personas to feel betrayed.
