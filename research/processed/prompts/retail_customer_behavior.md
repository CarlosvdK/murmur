# Retail Customer Behavior: Calibration Instructions

When simulating customer behavior in retail and service contexts, apply the following empirically-grounded patterns. These represent robust findings replicated across multiple studies and real-world settings.

## In-Store Decision Making (Inman, Winer & Ferraro, "The Interplay Among Category Characteristics, Customer Characteristics, and Customer Activities on In-Store Decision Making," Journal of Marketing, 2009; Chandon, Hutchinson, Bradlow & Young, "Does In-Store Marketing Work? Effects of the Number and Position of Shelf Facings on Brand Attention and Evaluation at the Point of Purchase," Journal of Marketing, 2009)

Inman et al. found that 55-62% of purchase decisions are made in-store rather than planned before entry. Unplanned purchases are highest in categories with high visual appeal (70%+) and lowest for staples (30-40%). Chandon et al. showed that doubling shelf facings increased visual attention by 29% and brand consideration by 18%. When simulating:
- The majority of persona purchase decisions should NOT be fully pre-determined. Only 38-45% of purchases reflect a specific pre-store plan.
- Impulse purchases increase with longer time in store. Personas spending 30+ minutes make 1.5-2x more unplanned purchases than those on quick trips.
- Point-of-purchase displays and signage shift purchase probability by 15-25% for undecided personas. High-Openness and high-Extraversion personas are 20-30% more susceptible to in-store stimuli.
- Personas with strict budgets or shopping lists exhibit 40-50% less in-store decision flexibility than casual browsers.

## Store Atmosphere Effects (Turley & Milliman, "Atmospheric Effects on Shopping Behavior: A Review of the Experimental Evidence," Journal of Business Research, 2000; Mattila & Wirtz, "Congruency of Scent and Music as a Driver of In-Store Evaluations and Behavior," Journal of Retailing, 2001; Spangenberg, Crowley & Henderson, "Improving the Store Environment: Do Olfactory Cues Affect Evaluations and Behaviors?," Journal of Marketing, 1996)

Turley & Milliman's review of 60+ studies found that atmospheric variables influence shopping duration by 15-25% and spending by 10-20%. Mattila & Wirtz demonstrated that congruent scent-music combinations increased impulse purchasing by 36% compared to incongruent conditions. Spangenberg et al. found that pleasant ambient scent improved store evaluations by 15-20% and time perception (shoppers underestimated time spent by 10-15%). When simulating:
- Pleasant atmosphere increases dwell time by 15-25%, which compounds with in-store decision making to increase total spending by 12-20%.
- Crowding has a nonlinear effect: moderate foot traffic signals popularity and increases purchase confidence, but high crowding reduces shopping time by 20-30% and triggers avoidance in 35-45% of personas.
- Music tempo affects pace: slow music increases dwell time by 15-20% and spending by 10-15% compared to fast music (Milliman 1982). Personas do not consciously notice this effect.
- Atmospheric effects are strongest for hedonic purchases (clothing, dining, gifts) and weakest for utilitarian purchases (hardware, office supplies).

## Wait Time Psychology (Maister, "The Psychology of Waiting Lines," 1985; Hui & Tse, "What to Tell Consumers in Waits of Different Lengths," Journal of Marketing, 1996)

Maister established that perceived wait time matters more than actual wait time, and that occupied time feels 30-40% shorter than unoccupied time. Hui & Tse found that providing wait duration information reduced perceived wait time by 20-25% and increased satisfaction by 15-20%, but ONLY when the provided estimate was accurate. Overestimating (and then beating the estimate) increased satisfaction by an additional 10%. When simulating:
- Unexplained waits feel 1.5-2x longer than explained waits. A persona waiting 10 minutes without knowing why perceives it as 15-20 minutes.
- Pre-process waits (before service begins) feel longer than in-process waits (during service). A 5-minute wait to be seated feels worse than a 5-minute wait for food.
- Solo waiters perceive time as 20-30% longer than those waiting in groups. Apply this modifier based on the persona's visit context.
- A wait that exceeds the persona's expectation by more than 50% triggers a sharp satisfaction drop. A wait that comes in under expectation produces a satisfaction bonus, but the bonus is smaller than the penalty (asymmetric, roughly 1:2 ratio).

## Product Assortment and Choice Overload (Iyengar & Lepper, "When Choice Is Demotivating: Can One Desire Too Much of a Good Thing?," Journal of Personality and Social Psychology, 2000; Scheibehenne, Greifeneder & Todd, "Can There Ever Be Too Many Options? A Meta-Analytic Review of Choice Overload," Journal of Consumer Research, 2010; Boatwright & Nunes, "Reducing Assortment: An Attribute-Based Approach," Journal of Marketing, 2001)

Iyengar & Lepper's famous jam study found that 30% of shoppers purchased from a 6-option display vs only 3% from a 24-option display -- a 10x difference in conversion. However, Scheibehenne et al.'s meta-analysis of 63 studies found an average effect size near zero (d=0.02), indicating the effect is highly context-dependent. Boatwright & Nunes found that reducing assortment by 25-50% in specific categories increased sales by 5-10% when low-share items were removed. When simulating:
- Choice overload is most likely when: options are hard to compare, the persona has no strong prior preference, and the decision feels consequential. Under these conditions, reduce purchase probability by 20-40% when options exceed 15-20.
- When options are easy to compare or the persona has expertise, more choice increases satisfaction. Expert personas benefit from assortment up to 30+ options.
- Overwhelmed personas default to: (a) choosing the most popular option, (b) choosing the cheapest option, or (c) deferring the decision entirely. The split is roughly 30/25/45%.
- Reducing a menu or product line triggers backlash from the 5-15% of personas whose preferred item was removed. These personas react disproportionately loudly.

## Customer Switching Behavior (Keaveney, "Customer Switching Behavior in Service Industries," Journal of Marketing, 1995; Bansal & Taylor, "The Service Provider Switching Model," Journal of Service Research, 1999)

Keaveney's study of 526 critical incidents identified 8 switching triggers: pricing (30%), core service failures (25%), service encounter failures (20%), inconvenience (10%), response to failed service (8%), competition (4%), ethical problems (2%), involuntary switching (1%). Bansal & Taylor confirmed that switching intent is predicted by a combination of push factors (dissatisfaction), pull factors (attractiveness of alternatives), and mooring factors (switching costs, habits). When simulating:
- No single bad experience causes most switching. Keaveney found that 70% of switchers cited 2+ concurrent reasons. A persona needs multiple push factors or one severe failure combined with low switching costs.
- Price is the most common trigger but rarely acts alone. Apply a 30% probability that a price increase is the "last straw" that activates dormant dissatisfaction.
- Switching costs are psychological as much as financial. A persona's accumulated familiarity, relationships with staff, and routine all create inertia. Weight these at 1.5-2x their objective magnitude.
- High-Conscientiousness personas exhibit more deliberate switching (research alternatives thoroughly). High-Agreeableness personas tolerate more dissatisfaction before switching but switch more permanently when they do.

## Word-of-Mouth and Referral Behavior (Anderson, "Customer Satisfaction and Word of Mouth," Journal of Service Research, 1998; East, Hammond & Lomax, "Measuring the Impact of Positive and Negative Word of Mouth on Brand Purchase Probability," International Journal of Research in Marketing, 2008; Berger & Schwartz, "What Drives Immediate and Ongoing Word of Mouth?," Journal of Marketing Research, 2011)

Anderson found that dissatisfied customers tell 9-15 people on average while satisfied customers tell only 4-6 -- a 2-3x asymmetry. East et al. found that positive WOM has a stronger impact on purchase probability per exposure (+25-30%) than negative WOM (-15-20%), but negative WOM spreads more widely. Berger & Schwartz showed that products that are interesting (unusual, surprising) generate 1.5-2x more immediate WOM, but products that are publicly visible or cued by the environment generate more sustained, ongoing WOM. When simulating:
- Dissatisfied personas should produce 2-3x the volume of word-of-mouth as satisfied personas.
- Most WOM is driven by extreme experiences (very positive or very negative). Moderately satisfied personas rarely mention the business unprompted. Only 10-15% of satisfied personas actively recommend.
- High-Extraversion personas generate 2-3x more WOM across all satisfaction levels. Low-Extraversion personas share primarily with close contacts (1-3 people) and only when strongly motivated.
- A remarkable or unusual element of the experience (positive or negative) is the single strongest driver of WOM, more than overall satisfaction. Personas latch onto concrete, specific, story-worthy moments.

## Service Recovery Paradox (McCollough & Bharadwaj, "The Recovery Paradox: An Examination of Consumer Satisfaction in Relation to Disconfirmation, Service Quality, and Attribution Based Theories," Marketing Science Institute, 1992; Tax, Brown & Chandrashekaran, "Customer Evaluations of Service Complaint Experiences: Implications for Relationship Marketing," Journal of Marketing, 1998)

The service recovery paradox posits that a customer who experiences a failure followed by excellent recovery may become MORE satisfied and loyal than one who experienced no failure at all. McCollough & Bharadwaj found this effect in approximately 40-50% of recovery scenarios, but only when the failure was perceived as rare and the recovery was perceived as exceptional. Tax et al. found that recovery satisfaction is driven by three justice dimensions: distributive (what compensation was offered), procedural (how fast and easy the process was), and interactional (how the customer was treated personally). When simulating:
- The paradox only holds when: (a) the failure is a one-time event, not a pattern, (b) the recovery exceeds expectations (not just matches them), and (c) the persona attributes the failure to circumstances rather than incompetence.
- If a failure is the second or third incident, recovery has diminishing returns. Post-recovery satisfaction drops 30-40% for each repeat failure. By the third failure, even excellent recovery cannot restore pre-failure loyalty levels.
- Speed matters more than compensation magnitude. A same-day resolution with modest compensation outperforms a week-long resolution with generous compensation for 60-70% of personas.
- Interactional justice (genuine apology, empathy, personal attention) is weighted as heavily as distributive justice (refunds, discounts) by most personas. A sincere apology with no refund often outperforms a refund with no apology.
- High-Agreeableness personas are more likely to experience the paradox (55-65%). Low-Agreeableness personas are more likely to view recovery as "expected" and remain at or below pre-failure satisfaction (paradox rate: 20-30%).
