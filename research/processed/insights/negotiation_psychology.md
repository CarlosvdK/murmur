# Negotiation Psychology -- Key Insights

## Insight from: fisher1981getting
**Finding:** BATNA (Best Alternative To Negotiated Agreement) is the single strongest predictor of negotiation outcomes. A party with a strong BATNA concedes ~40% less than one without alternatives.
**Strength:** Very High (15,000 citations)
**Application:** When simulating vendor responses, check if the user has alternative vendors. If they do, the vendor twin should be more flexible. If the user is sole-dependent, the vendor twin should be firmer.
**Prompt fragment:** "Calibrate vendor flexibility based on buyer's BATNA. If buyer has alternatives: vendor concedes ~40% more. If buyer is sole-dependent: vendor holds firm on ~75% of requests."

## Insight from: bazerman1992negotiating
**Finding:** The first offer in a price negotiation anchors 30-50% of the final outcome, even when both parties know the anchor is arbitrary. Extreme first offers extract more value than moderate ones, up to a point.
**Strength:** Very High (8,000+ citations)
**Application:** When simulating price negotiations, the party who frames the discussion first has 30-50% influence on the final outcome.
**Prompt fragment:** "In price discussions, whoever states a number first anchors the negotiation. The anchor influences 30-50% of the final outcome. If the vendor states their price first, the buyer's counter-offer is constrained."

## Insight from: curhan2006what
**Finding:** Negotiators value four outcomes: economic (price/terms), process (fairness of the negotiation), relationship (future dealings), and self (feeling respected). Small business negotiations weight relationship and self outcomes more than corporate ones.
**Strength:** High (800+ citations, JPSP)
**Application:** Vendor twins should value relationship preservation. A request that threatens the relationship will be met with more resistance than one that threatens only economics.
**Prompt fragment:** "This vendor values four outcomes: economic terms, process fairness, relationship preservation, and feeling respected. Weight relationship and respect heavily -- small business vendors prioritize ongoing relationships over single transactions."
