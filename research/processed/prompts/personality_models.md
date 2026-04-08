# Personality Models: Calibration Instructions

When constructing and simulating personas, assign each a position on the Big Five / OCEAN personality dimensions. These are not decorative labels -- each dimension produces specific, empirically-documented effects on consumer behavior. Use the mappings below to modulate how each persona evaluates products, responds to marketing, complains, reviews, and makes purchase decisions.

The Big Five model is the most empirically validated personality framework in psychology (Costa & McCrae, "Revised NEO Personality Inventory and NEO Five-Factor Inventory Professional Manual," 1992). Each dimension is a continuous spectrum, not a binary. Assign personas a value from 1 (very low) to 10 (very high) on each dimension.

## Openness to Experience

Openness correlates with willingness to try new products, tolerance for unfamiliar experiences, and aesthetic sensitivity.

Consumer behavior effects:
- High Openness (7-10): These personas are early adopters. They actively seek novel products and experiences. They are 2-3x more likely to try a new brand or product than low-Openness personas (Matz et al., "Psychological Targeting as an Effective Approach to Digital Mass Persuasion," PNAS, 2017). They respond strongly to messaging about innovation, uniqueness, and creativity. They get bored with routine purchases and may switch brands purely for variety, even when satisfied.
- Low Openness (1-4): These personas are brand loyal by temperament. They prefer familiar products and established brands. They require stronger evidence or social proof before trying something new. They are skeptical of "revolutionary" claims. They value reliability and consistency in messaging over novelty.
- Moderate Openness (5-6): Default consumer behavior. Will try new things when the switching cost is low or when there is strong social proof, but does not actively seek novelty.

## Conscientiousness

Conscientiousness correlates with planning behavior, price comparison, loyalty program engagement, and long-term value assessment.

Consumer behavior effects:
- High Conscientiousness (7-10): These personas research before purchasing. They compare prices across 3-5 options. They read the fine print. They are more likely to use loyalty programs and track their spending. They exhibit less hyperbolic discounting than average (~30-40% reduction per Frederick et al., 2002). They are more sensitive to perceived dishonesty or hidden fees, which can produce strong negative reactions. They leave detailed, structured reviews when they do review.
- Low Conscientiousness (1-4): These personas are impulse buyers. They respond to immediate emotional appeals and convenience. They are 2-3x more susceptible to upsells and add-ons at checkout. They rarely compare prices. They forget to cancel free trials. They leave short, emotionally-driven reviews. They exhibit stronger hyperbolic discounting.
- Moderate Conscientiousness (5-6): Default research behavior. Will do some comparison shopping for expensive purchases but impulse-buy for low-cost items.

## Extraversion

Extraversion correlates with social proof sensitivity, word-of-mouth behavior, review propensity, and responsiveness to social/community marketing.

Consumer behavior effects:
- High Extraversion (7-10): These personas are strongly influenced by social proof (Cialdini effect amplified ~1.5-2x). They talk about purchases with friends and family -- they are your word-of-mouth vectors. They are ~2x more likely to leave a review than introverts (both positive and negative). They respond to community features, social media marketing, and "join the movement" messaging. They value the social signal of their purchases.
- Low Extraversion (1-4): These personas make decisions more independently. Social proof still works but at reduced intensity (~0.5-0.7x baseline). They rarely leave unsolicited reviews. They are less influenced by brand communities or social features. They prefer self-service over human interaction. They value privacy and dislike being contacted.
- Moderate Extraversion (5-6): Responsive to social proof at baseline rates. Will share strong experiences (positive or negative) but not moderate ones.

## Agreeableness

Agreeableness correlates with complaint behavior, negotiation style, tolerance for poor service, and susceptibility to persuasion.

Consumer behavior effects:
- High Agreeableness (7-10): These personas suppress complaints. They are the silent dissatisfied -- they will stop using a product rather than complain about it. They give higher ratings than their true satisfaction warrants (inflate by roughly 0.5-1.0 stars). They are more susceptible to reciprocity-based sales tactics ("we gave you a free sample, now..."). They avoid conflict with service staff. They are more likely to accept the first offer in a negotiation. They represent the largest gap between expressed satisfaction and true satisfaction -- this is critical for Murmur's value proposition.
- Low Agreeableness (1-4): These personas complain readily and specifically. They negotiate aggressively. They leave detailed negative reviews. They demand to speak to managers. They are resistant to reciprocity tactics. Their expressed satisfaction closely matches their true satisfaction, so their reviews are more calibrated but their tone is harsher than their actual experience warrants.
- Moderate Agreeableness (5-6): Will complain about significant issues but let minor ones slide. Default complaint threshold.

## Neuroticism (Emotional Stability)

Neuroticism correlates with risk aversion, price sensitivity, anxiety about purchases, post-purchase regret, and responsiveness to fear-based messaging.

Consumer behavior effects:
- High Neuroticism (7-10): These personas are anxious buyers. They experience more pre-purchase deliberation and more post-purchase regret. They are ~1.5-2x more sensitive to price increases than emotionally stable personas. They respond strongly to money-back guarantees and risk-reduction messaging. They are more likely to return products. They are more likely to leave a negative review after a bad experience (~1.5x) because the negative emotion is amplified and sustained. They are more susceptible to fear-of-missing-out (FOMO) messaging but also more likely to regret FOMO-driven purchases.
- Low Neuroticism (1-4): These personas are calm, confident buyers. They experience less decision anxiety and less post-purchase regret. They are less price-sensitive in relative terms. They are harder to manipulate with urgency or scarcity tactics. They take longer to react to service failures because their emotional response is muted.
- Moderate Neuroticism (5-6): Default anxiety and price sensitivity levels.

## Trait Interactions

Do not treat the five dimensions independently. Key documented interactions:
- High Openness + High Extraversion = "Enthusiast" archetype. First to adopt, first to evangelize. Overrepresented in online reviews of new products.
- High Conscientiousness + Low Agreeableness = "Demanding Researcher" archetype. Will find every flaw and articulate it precisely. Produces the most useful (and most feared) negative reviews.
- High Neuroticism + High Agreeableness = "Silent Sufferer" archetype. Experiences the most dissatisfaction but expresses the least. This is the persona most invisible to traditional review analysis and the one Murmur most needs to surface.
- Low Openness + High Conscientiousness = "Loyal Pragmatist" archetype. Extremely difficult to acquire but extremely difficult to lose. High lifetime value.
- High Extraversion + Low Conscientiousness = "Impulse Influencer" archetype. Buys impulsively and talks about it widely. High word-of-mouth value but low retention.

## Population Distribution

When generating a representative persona cohort, the Big Five traits are approximately normally distributed in the general population (Costa & McCrae, 1992). Use a mean of 5.5 and standard deviation of ~2 on the 1-10 scale. Do not cluster personas at extremes unless simulating a specific demographic known to skew (e.g., tech early adopters skew high Openness).

Cross-cultural note: trait distributions shift across cultures (Schmitt et al., "Why Can't a Man Be More Like a Woman?", Journal of Personality and Social Psychology, 2008). When simulating specific demographics, adjust means accordingly -- but the consumer behavior mappings above remain directionally consistent across cultures.
