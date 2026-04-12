# Complaint and Feedback Behavior: Calibration Instructions

When simulating how customers respond to dissatisfaction -- whether they complain, leave silently, or spread negative word of mouth -- apply the following empirically-grounded patterns. Understanding complaint behavior is critical because what customers say (or don't say) to a business is a systematically distorted signal.

## Customer Complaint Behavior Typology (Singh, "Consumer Complaint Intentions and Behavior: Definitional and Taxonomical Issues," Journal of Marketing, 1988; Richins, "Negative Word-of-Mouth by Dissatisfied Consumers: A Pilot Study," Journal of Marketing, 1983)

Singh identified three distinct complaint responses: voice (complaining to the firm), private (negative word-of-mouth to friends and family), and third-party (formal complaints to external agencies). Richins found that dissatisfied customers engage in negative WOM to an average of 9-10 people, compared to satisfied customers who share positive experiences with only 4-5 people. When simulating:
- Dissatisfied personas should spread negative WOM at roughly 2x the rate of positive WOM from satisfied personas. A persona who had a bad experience should tell 8-12 others; a persona with a good experience should tell 3-5.
- Roughly 30-40% of dissatisfied personas should choose voice (direct complaint). The remainder split between private action (50-60%) and doing nothing or switching silently (10-20%).
- Persona traits moderate complaint type: high Assertiveness and high Conscientiousness predict voice; high Neuroticism and low Assertiveness predict private WOM without direct complaint.

## Why Most Unhappy Customers Don't Complain (Goodman, "Strategic Customer Service," 2009; Stephens & Gwinner, "Why Don't Some People Complain? A Cognitive-Emotive Process Model of Consumer Complaint Behavior," Journal of the Academy of Marketing Science, 1998)

TARP studies (summarized in Goodman) found that only 4-5% of dissatisfied customers complain to the company. The rest leave silently or complain only to friends. Stephens and Gwinner showed that the decision not to complain follows a cognitive appraisal process: customers evaluate (1) whether the problem is serious enough, (2) whether complaining will help, and (3) whether the emotional cost of complaining is worth it. When simulating:
- For every persona who voices a complaint directly, approximately 19-24 other personas should be experiencing the same dissatisfaction silently. The voiced complaint is the tip of the iceberg.
- Personas with low perceived likelihood of redress (past negative complaint experiences, small businesses perceived as unable to fix systemic issues) should suppress complaints at 2-3x the baseline rate.
- Personas with low stakes in the transaction (infrequent visitors, low-spend customers) should almost never complain directly. Their dissatisfaction manifests as quiet defection.
- Higher-income and higher-education personas complain at roughly 1.5-2x the rate of lower-income personas, because they have higher expectations and greater perceived self-efficacy.

## Voice, Exit, and Loyalty (Hirschman, "Exit, Voice, and Loyalty: Responses to Decline in Firms, Organizations, and States," 1970)

Hirschman's foundational framework shows that dissatisfied members of an organization choose between exit (leaving), voice (complaining to improve things), or loyalty (staying despite dissatisfaction). Loyalty moderates the exit-voice tradeoff: high-loyalty individuals choose voice over exit because they believe the organization can improve. When simulating:
- Personas with high brand loyalty (action loyalty per Oliver 1999) should express dissatisfaction through voice rather than exit. They complain BECAUSE they care.
- Low-loyalty personas should skip voice entirely and proceed to exit. They are not worth the effort of complaining.
- When switching costs are high (contracts, learned interfaces, social ties), even low-loyalty personas may remain through loyalty-by-default, but they become vocal detractors who spread negative WOM while staying.
- The presence of competitive alternatives accelerates exit. If the simulation includes a known competitor, dissatisfied low-loyalty personas should exit at roughly 2x the rate they would without an alternative.

## Online vs Offline Complaint Behavior (Mattila & Wirtz, "Consumer Complaining to Firms: The Determinants of Channel Choice," Journal of Services Marketing, 2004; Gregoire, Tripp, & Legoux, "When Customer Love Turns into Lasting Hate: The Effects of Relationship Strength and Time on Customer Revenge and Avoidance," Journal of Marketing, 2009)

Online platforms amplify complaint behavior. Mattila and Wirtz found that the reduced social cost of online complaining increases complaint rates by 30-50% compared to face-to-face contexts. Gregoire et al. documented that online revenge behaviors (public shaming, viral negative reviews) are most intense from previously loyal customers who feel betrayed, peaking 2-4 weeks after the incident. When simulating:
- Personas who are active on social media and review platforms should complain at 1.5-2x the rate of offline-only personas.
- The emotional intensity of online complaints should be higher than equivalent offline complaints. Personas expressing frustration online should use 20-30% stronger language than they would in person.
- Previously loyal personas who experience a perceived betrayal (sudden price increase, service degradation, broken promise) should exhibit the strongest online retaliation. Their complaints carry more weight because they reference their history as loyal customers.

## Complaint Handling and Double Deviation (Bitner, Booms, & Tetreault, "The Service Encounter: Diagnosing Favorable and Unfavorable Incidents," Journal of Marketing, 1990; Johnston & Fern, "Service Recovery Strategies for Single and Double Deviation Scenarios," Journal of Services Marketing, 1999)

Bitner et al. found that how a firm handles a service failure matters more than the failure itself. Effective recovery can produce the "service recovery paradox" -- customers who experience a failure followed by excellent recovery report higher satisfaction than customers who never experienced a failure (observed in roughly 30-40% of cases). However, Johnston and Fern documented "double deviation": when the recovery attempt itself fails, satisfaction drops to levels far below the original failure. When simulating:
- When a business scenario includes complaint handling, personas who receive prompt, empathetic, and fair recovery should increase their loyalty by 15-25% above pre-failure levels (recovery paradox).
- When recovery fails (slow response, dismissive tone, inadequate remedy), persona satisfaction should drop to 40-50% below the post-failure level. Double deviation is catastrophic.
- Personas evaluate recovery on three dimensions: speed (response within hours vs days), empathy (acknowledgment of their frustration), and fairness (remedy proportional to the problem). Missing any one dimension reduces recovery effectiveness by roughly 30-40%.
