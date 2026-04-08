# Review Bias & Silent Majority -- Key Insights

## Insight from: gao2015vocal
**Finding:** Online ratings reflect a vocal minority, not the actual population. Less than 1.5% of customers write reviews. Reviewers are systematically more extreme (both positive and negative) than non-reviewers. The silent majority holds moderate opinions.
**Strength:** Very High (850 citations, MIS Quarterly)
**Application:** Any simulation that uses review data must correct for this bias. At least 55-70% of generated personas should represent the silent majority with moderate views.
**Prompt fragment:** "CRITICAL: Reviews represent <2% of customers. The silent majority (55-70% of the customer base) holds moderate, non-extreme views. Do not calibrate persona reactions based on what reviewers say -- reviewers are outliers."

## Insight from: karaman2021extremity
**Finding:** Online ratings exhibit extremity bias -- the distribution is bimodal (lots of 5-stars and 1-stars, few 3-stars). The true distribution of customer satisfaction is approximately normal (bell curve) centered around 3.5-4.0.
**Strength:** High (200+ citations, Management Science)
**Application:** Compress extreme ratings by ~30% toward the center. The true satisfaction distribution is bell-shaped, not U-shaped.
**Prompt fragment:** "When interpreting review data, compress extreme ratings by 30%. A 4.5-star average on Google likely represents a true satisfaction of ~4.0. A 3.0 average likely represents ~3.3."

## Insight from: hu2009overcoming
**Finding:** Product review distributions are J-shaped (heavily skewed toward positive) because satisfied customers are more likely to review, and because dissatisfied customers often don't bother -- they just leave.
**Strength:** High (900+ citations)
**Application:** Negative signals in reviews are more informative than positive ones. One negative review represents many more unhappy customers who didn't write.
**Prompt fragment:** "Each negative review represents approximately 10-20 unhappy customers who didn't write. Each positive review represents approximately 3-5 happy customers who didn't write. Weight negative signals more heavily."

## Insight from: luca2016reviews
**Finding:** A one-star increase on Yelp leads to a 5-9% increase in revenue for independent restaurants. Reviews have real economic impact, but the effect is stronger for independent businesses than chains.
**Strength:** Very High (3,000+ citations, Harvard Business School)
**Application:** For small/independent businesses (Murmur's target), review sentiment matters more than for chains. Customer reactions to changes that might generate reviews are amplified.
**Prompt fragment:** "For independent small businesses, every customer interaction that might generate a review (positive or negative) has outsized impact. Weight review-generating scenarios more heavily in predictions."
