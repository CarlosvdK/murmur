# Review Bias: Calibration Instructions

When simulating whether a persona would leave a review, what rating they would give, and what they would say, apply the following empirically-documented biases. The key insight: online reviews are a deeply distorted signal. Your job is to model the distortion accurately so the simulation can surface what the silent majority actually thinks.

## The Vocal Minority (Gao et al., "Vocal Minority and Silent Majority: How Do Online Ratings Reflect Population Perceptions of Quality?", MIS Quarterly, 2015)

Fewer than 1.5% of customers leave reviews on any given platform. This is not a random 1.5% -- it is systematically skewed:
- Reviewers are disproportionately those with extreme experiences (very positive or very negative).
- The silent majority holds moderate opinions (3-4 stars on a 5-point scale) but almost never bothers to articulate them.
- When simulating a cohort of personas, no more than 1-2% should spontaneously produce a review. The rest must be explicitly prompted or incentivized.

When determining which personas review, use these heuristics:
- High-Extraversion personas are ~2x more likely to review than low-Extraversion personas.
- High-Neuroticism personas are ~1.5x more likely to review after a negative experience specifically.
- High-Agreeableness personas suppress complaints -- they are less likely to leave negative reviews even when dissatisfied. They may leave positive reviews to "be nice."

## Extremity Bias and the J-Shaped Distribution (Hu et al., "Overcoming the J-shaped Distribution of Product Reviews," Communications of the ACM, 2009; Karaman, "Extremity Bias in Online Reviews," 2021)

Online review distributions are not normal. They follow a J-shaped (or bimodal) pattern:
- 5-star reviews are dramatically overrepresented, typically 40-60% of all reviews.
- 1-star reviews are the second largest category, typically 15-25%.
- 2-star, 3-star, and 4-star reviews are underrepresented relative to actual sentiment distribution.
- The true population sentiment for most products is approximately normally distributed around 3.5-4.0 stars.

When a persona does leave a review, bias their rating toward the extremes:
- A persona whose true satisfaction is 3.5/5 will round up to 4 or 5 roughly 60% of the time, and round down to 3 roughly 30%, and occasionally post a 2 (10%).
- A persona whose true satisfaction is 2.5/5 will post a 1-star review roughly 40% of the time, despite their experience being moderate-negative rather than terrible.
- Personas in the 3.0-3.5 range are the least likely to review at all. If they do, their reviews tend to be short and muted.

## Platform-Specific Distortions (Luca, "Reviews, Reputation, and Revenue: The Case of Yelp.com," Harvard Business School Working Paper, 2016)

Different review platforms have different systematic biases:
- Google Reviews skew positive (average ~4.1-4.3 stars). Negative experiences are underrepresented because Google's review flow is frictionless for positive reviews but offers no strong emotional trigger for negative ones. Many Google reviews come from prompts (e.g., "How was your visit?") which catch people in a default-positive state.
- Yelp historically skewed more negative because its filtering algorithm suppressed many positive reviews from infrequent reviewers. Yelp's population also self-selects for "critical reviewer" identity.
- Amazon reviews skew toward a J-shape but vary enormously by product category. Verified purchase reviews are more moderate than unverified.
- When simulating reviews for a specific platform, adjust the distribution accordingly. Default to the Google-positive skew for general local business simulations.

## What This Means for Simulation

When generating a simulated cohort response:
1. First, determine the true satisfaction distribution across all personas (this will approximate a normal distribution).
2. Then, select which personas actually review (~1-2%, biased toward extreme experiences and high-Extraversion).
3. Then, distort the reviewing personas' ratings toward the extremes (J-shaped).
4. The gap between Step 1 and Step 3 is the insight Murmur provides -- surfacing the silent majority.

Always generate both outputs: what the reviews would look like AND what the full population actually feels. Flag the gap explicitly. This is Murmur's core value proposition.

## Review Content Patterns

When generating review text:
- Negative reviews are on average 2-3x longer than positive reviews (Gao et al., 2015). Dissatisfied personas write detailed complaints. Satisfied personas write "Great place!" or similar brief endorsements.
- Negative reviews disproportionately focus on a single specific incident. Positive reviews are more likely to be holistic ("everything was great").
- Reviewers with high Conscientiousness produce more structured, detailed reviews. Low Conscientiousness reviewers write brief, emotional reactions.
- Approximately 15-20% of review content mentions price. Price mentions correlate with lower ratings (Anderson & Simester, "Reviews Without a Purchase," Journal of Marketing Research, 2014).
