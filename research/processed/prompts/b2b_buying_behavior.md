# B2B Buying Behavior: Calibration Instructions

When simulating business-to-business purchase decisions, do not model organizational buyers as single rational actors. Real B2B buying involves committees, politics, risk aversion, and relationship inertia documented across decades of industrial marketing research. Apply the following dynamics as defaults for all B2B persona simulations.

## Buying Center Dynamics (Webster & Wind, "A General Model for Understanding Organizational Buying Behavior," Journal of Marketing, 1972; Johnston & Lewin, "Organizational Buying Behavior: Toward an Integrative Framework," Journal of Business Research, 1996)

B2B purchases involve 5-7 distinct roles: users, influencers, buyers, deciders, and gatekeepers. Each role has different evaluation criteria and veto power.
- Average B2B purchase involves 6.8 stakeholders (CEB/Gartner research based on Johnston & Lewin's framework). As deal size increases, so does committee size -- enterprise deals often involve 10+ people.
- Gatekeepers (IT, procurement, legal) can kill deals that every other stakeholder supports. In Webster & Wind's model, gatekeepers control information flow and vendor access.
- Users and deciders frequently disagree. The person who uses the product daily has different priorities than the executive who signs the contract.

When simulating: generate at least 3 distinct stakeholder personas per B2B buying decision. Include at least one gatekeeper who evaluates on risk/compliance, one user who evaluates on daily workflow impact, and one decider who evaluates on strategic ROI. Model disagreements between them -- unanimous approval is rare.

## Switching Costs (Burnham, Frels & Mahajan, "Consumer Switching Costs: A Typology, Antecedents, and Consequences," Journal of the Academy of Marketing Science, 2003; Jones, Mothersbaugh & Beatty, "Why Customers Stay: Measuring the Underlying Dimensions of Services Switching Costs," Journal of Business Research, 2002)

B2B switching costs operate across three dimensions: procedural (time, effort, learning), financial (contractual penalties, sunk investments), and relational (personal relationships, trust built over years).
- Burnham et al. found procedural switching costs had the strongest effect on retention, explaining 30-40% of variance in intent to stay.
- Jones et al. documented that relational switching costs create emotional lock-in even when a competitor offers a 15-25% price advantage.
- Contract lock-in periods average 12-36 months in B2B SaaS, and early termination penalties of 50-100% of remaining contract value are standard.

When simulating: B2B personas should exhibit strong status quo bias. A competing offer must clear a threshold of approximately 20-30% improvement in total value before a persona will seriously consider switching. Personas in the first half of a contract term should almost never switch.

## Trust and Relationship Quality (Morgan & Hunt, "The Commitment-Trust Theory of Relationship Marketing," Journal of Marketing, 1994; Doney & Cannon, "An Examination of the Nature of Trust in Buyer-Seller Relationships," Journal of Marketing, 1997)

Trust in B2B relationships develops through credibility (competence belief) and benevolence (belief that the vendor cares about the buyer's interests). Morgan & Hunt's model shows trust and commitment are the two central mediators of all relationship outcomes.
- Doney & Cannon found that trust in the salesperson and trust in the supplier firm are distinct constructs. A trusted salesperson leaving can reduce account retention by 20-30%.
- High-trust relationships tolerate service failures 2-3x better than low-trust ones before triggering vendor review.
- Trust takes 12-18 months of consistent delivery to establish but can be destroyed in a single major failure.

When simulating: personas with vendor relationships longer than 18 months should show strong loyalty bias. Personas should react to vendor failures proportionally to relationship length -- new relationships are fragile, established ones are resilient but not invincible.

## B2B Price Sensitivity (Anderson, Jain & Chintagunta, "Customer Value Assessment in Business Markets," Journal of Business-to-Business Marketing, 1993; Nagle & Holden, "The Strategy and Tactics of Pricing," Prentice Hall, multiple editions)

B2B buyers evaluate total cost of ownership, not sticker price. A cheaper product that requires more integration time, training, or maintenance can be perceived as more expensive.
- Anderson et al.'s value-in-use framework shows B2B buyers calculate ROI over 3-5 year horizons. A 10% price increase is acceptable if it comes with a 15%+ productivity gain.
- Price sensitivity in B2B is 40-60% lower than in B2C for comparable purchase amounts because the buyer is spending organizational money, not personal funds.
- However, procurement departments introduce artificial price sensitivity through competitive bidding requirements and annual cost-reduction targets of 3-5%.

When simulating: B2B personas should evaluate price changes through an ROI lens, not an absolute cost lens. A price increase paired with a credible value story should be accepted by 50-65% of personas. Pure price increases without added value should trigger vendor review in 40-60% of personas.

## Vendor Evaluation and Selection (de Boer, Labro & Morlacchi, "A Review of Methods Supporting Supplier Selection," European Journal of Purchasing & Supply Management, 2001; Kannan & Tan, "Supplier Selection and Assessment: Their Impact on Business Performance," Journal of Supply Chain Management, 2002)

Businesses use multi-criteria evaluation combining quality, reliability, price, delivery, and relationship factors. The process is rarely purely rational.
- de Boer et al.'s review found that despite the availability of quantitative models, 60-70% of supplier selection decisions rely heavily on subjective judgment and prior experience.
- Kannan & Tan showed that supplier quality and reliability consistently outrank price as selection criteria, with quality weighted 25-35% and price weighted 15-25% in typical evaluations.
- Incumbent advantage is substantial: existing vendors win re-evaluation 65-75% of the time due to familiarity bias and switching cost awareness.

When simulating: weight quality, reliability, and relationship factors above price in B2B persona evaluations. Incumbent vendors should receive a 15-20% "familiarity premium" in persona scoring. New vendor personas should face skepticism by default.

## Account-Based Decision Making (Adamson, Dixon & Toman, "The End of Solution Selling," Harvard Business Review, 2012; Lilien, "The B2B Knowledge Gap," International Journal of Research in Marketing, 2016)

Enterprise buying cycles are long (3-18 months), nonlinear, and frequently stall. Lilien's research highlights that B2B marketing and buying behavior remain dramatically understudied compared to B2C.
- Adamson et al. found that B2B buyers complete 57% of their purchase decision before contacting a vendor. Early-stage personas should already have strong preconceptions.
- Consensus-building among stakeholders is the primary bottleneck. Deals stall not because of objections but because internal alignment fails -- 40-60% of qualified B2B deals end in "no decision" rather than a competitor win.
- Risk aversion dominates: "Nobody ever got fired for buying IBM." Personas in risk-averse industries (finance, healthcare, government) should default to the safer, more established option even at higher cost.

When simulating: model B2B buying as a multi-stage process with stall points. At least 30% of simulated deals should result in "no decision" or "defer." Personas should arrive with pre-formed opinions from independent research, not as blank slates waiting to be sold to.
