# Digital Experience: Calibration Instructions

When simulating customer reactions to digital touchpoints, apply the following empirically-grounded effects. These are not optional flavor -- they are systematic patterns that real users exhibit consistently across studies.

## Page Load Speed and Conversion (Brutlag, "Speed Matters," Google/Bing Velocity Conference, 2009; Akamai, "The State of Online Retail Performance," 2017; Google, "Mobile Speed Benchmarks," 2018)

Every 100ms of added latency costs measurable conversion. Brutlag's Bing study found that a 200ms slowdown reduced revenue per user by 4.3%. Akamai's 2017 data shows a 100ms delay in load time drops conversion rates by 7%. Google's 2018 mobile benchmarks found 53% of mobile visitors abandon a site that takes longer than 3 seconds to load. When simulating:
- If a persona encounters a slow page (3+ seconds), apply a 53% probability of immediate abandonment for mobile users, ~30% for desktop.
- Each additional 100ms of perceived delay reduces the persona's likelihood of completing a purchase by 5-7%.
- Impatient personas (younger, mobile-first, high time-pressure) should be 1.5-2x more sensitive to speed than patient personas.
- Speed frustration compounds across pages. A persona tolerates one slow page; two slow pages in a funnel trigger exit.

## Mobile vs Desktop Behavior (Ghose, Goldfarb & Park, "Examining the Dark Side of Mobile Internet," Management Science, 2012; Wang, Malthouse & Krishnamurthi, "On the Go: How Mobile Shopping Affects Customer Purchase Behavior," Journal of Retailing, 2015)

Mobile users behave fundamentally differently from desktop users. Ghose et al. found mobile sessions are 60-70% shorter and mobile users search fewer options before deciding. Wang et al. showed mobile conversion rates are roughly 50-65% lower than desktop, but mobile users make more frequent, smaller purchases. When simulating:
- A mobile persona should browse fewer options (3-5 vs 8-12 on desktop) and decide faster.
- Mobile conversion rate should be set at roughly 1.5-2.5% vs 3-5% on desktop for e-commerce.
- Mobile personas are more likely to abandon complex tasks (multi-step forms, detailed comparisons) -- apply a 40-50% higher abandonment rate on mobile for tasks requiring 3+ steps.
- Mobile personas favor simplicity and speed over comprehensiveness. They satisfice more aggressively.

## Form Friction and Abandonment (Baymard Institute, "Checkout Usability," 2012-2023; Imagescape, "Reducing Form Fields," 2008)

Each additional form field measurably reduces completion rates. Baymard Institute's longitudinal checkout studies show the average large e-commerce site has 23 form elements but could reduce to 12-14 without losing necessary data, with each unnecessary field costing ~3-5% completion. Imagescape's study found that reducing form fields from 11 to 4 increased conversions by 160%. When simulating:
- For every form field beyond 4, reduce the persona's completion probability by 3-5% per field.
- Required fields that feel unnecessary (phone number for a digital product, company name for a personal purchase) trigger a 10-15% abandonment spike per irrelevant field.
- Privacy-sensitive personas (older, lower trust, past data breach experience) are 2-3x more likely to abandon when asked for sensitive information without clear justification.

## Social Proof and Online Reviews (Chevalier & Mayzlin, "The Effect of Word of Mouth on Sales," Journal of Marketing Research, 2006; Luca, "Reviews, Reputation, and Revenue," American Economic Review, 2016; Mudambi & Schuff, "What Makes a Helpful Online Review?", MIS Quarterly, 2010)

Reviews are the dominant purchase signal online. Chevalier & Mayzlin found a one-star increase in average book rating on Amazon increased sales by approximately 5-10%. Luca showed a one-star increase on Yelp leads to a 5-9% revenue increase for independent restaurants. Mudambi & Schuff found moderate reviews (3-4 stars) are perceived as most helpful for experience goods, while extreme reviews are more helpful for search goods. When simulating:
- A product with fewer than 10 reviews should trigger uncertainty -- the persona discounts ratings by 30-40% when review count is low.
- Review recency matters: reviews older than 6 months are weighted ~50% less by personas than recent reviews.
- A 4.0-4.5 star rating is the credibility sweet spot. Perfect 5.0 ratings trigger suspicion in 20-30% of personas.
- High-Neuroticism personas weight negative reviews 2-3x more heavily than positive ones.

## Email Marketing Effectiveness (Sahni, Wheeler & Chintagunta, "Personalization in Email Marketing," Journal of Marketing Research, 2018; Goldstein, Suri & McAfee, "The Costs of Annoying," Journal of Economic Behavior and Organization, 2014)

Personalization and frequency strongly affect email engagement. Sahni et al. found that adding the recipient's name to an email subject line increased open rates by 20% and purchase likelihood by 31%, with stronger effects for infrequent buyers. Goldstein et al. demonstrated that excessive email frequency decreases engagement and increases unsubscribe rates -- a doubling of frequency produces a 15-25% increase in unsubscribes. When simulating:
- Personalized subject lines increase a persona's open probability by 15-25%.
- Beyond 2-3 emails per week, each additional email increases the persona's unsubscribe probability by 10-15%.
- Personas who have not purchased recently are more responsive to personalization but also more likely to unsubscribe from high-frequency sends.
- Discount-driven emails produce 2-3x higher click rates but train personas to wait for deals, reducing full-price purchase probability by 15-20% over time.

## Cart Abandonment Psychology (Kukar-Kinney & Close, "The Determinants of Consumers' Online Shopping Cart Abandonment," Journal of the Academy of Marketing Science, 2010; Cho, Kang & Cheon, "Online Shopping Hesitation," CyberPsychology and Behavior, 2006)

Cart abandonment rates average 65-75% across e-commerce. Kukar-Kinney & Close found that entertainment shoppers (browsing for fun) abandon at 75-85%, while need-driven shoppers abandon at 45-55%. Cho et al. identified unexpected costs (shipping, taxes, fees) as the #1 abandonment trigger, causing 55-60% of all abandonments. When simulating:
- When a persona discovers unexpected costs at checkout, apply a 55-60% abandonment probability.
- Requiring account creation increases abandonment by 25-35%. Guest checkout reduces this friction.
- Abandonment recovery emails sent within 1 hour recover 5-10% of carts; after 24 hours, recovery drops to 2-3%.
- Price-sensitive personas use carts as wishlists -- they add items with no intent to buy immediately. Apply a 70-80% abandonment rate for these personas.

## Trust Signals Online (Kim, Ferrin & Rao, "A Trust-Based Consumer Decision-Making Model in Electronic Commerce," Information Systems Research, 2008; Gefen, Karahanna & Straub, "Trust and TAM in Online Shopping," MIS Quarterly, 2003)

Trust is the primary barrier to online purchase from unfamiliar sellers. Gefen et al. found that perceived trustworthiness explains 30-40% of variance in online purchase intention -- more than perceived usefulness or ease of use. Kim et al. showed that trust-reducing factors (poor design, no return policy, missing contact info) have 2-3x the impact of trust-building factors. When simulating:
- Missing trust signals (no SSL, no return policy, no contact information) should reduce purchase probability by 40-60% for first-time visitors.
- Professional design quality acts as a trust proxy -- amateurish design reduces trust by 30-45% even if the product is good.
- Return policies and guarantees increase purchase probability by 15-25%, with stronger effects for higher-priced items.
- Older personas and lower-income personas are more sensitive to trust signals. Apply a 1.5x trust-sensitivity multiplier for these groups.

## Notification and Re-engagement (Sahami Shirazi, Henze, Dingler, Pielot, Weber & Schmidt, "Large-scale Assessment of Mobile Notifications," CHI, 2014; Pielot, Church & de Oliveira, "An In-situ Study of Mobile Phone Notifications," MobileHCI, 2014)

Push notifications follow a sharp diminishing-returns curve. Sahami Shirazi et al. analyzed 200 million notifications and found that users dismiss 65% of notifications, with response rates dropping sharply after 3-5 daily notifications. Pielot et al. found that users attend to notifications within 6 minutes on average, but notification fatigue sets in when frequency exceeds user-perceived relevance. When simulating:
- The first 1-2 daily notifications from a brand are tolerated. Beyond 3 per day, each additional notification increases opt-out probability by 15-20%.
- Personalized, actionable notifications (order updates, price drops on watched items) have 3-5x higher engagement than generic promotional pushes.
- After opt-out, re-engagement requires significant effort -- only 5-10% of users re-enable notifications once disabled.
- Younger personas (18-30) tolerate 2-3x more notifications than older personas (50+) before fatigue sets in.
