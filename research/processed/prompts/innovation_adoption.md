# Innovation Adoption: Calibration Instructions

When simulating customer reactions to new products, features, or technologies, do not model adoption as a simple accept/reject decision. Real adoption involves perceived usefulness, perceived risk, social influence, habit disruption, and network effects that unfold over time. Apply the following research as defaults for all innovation-related persona simulations.

## Technology Acceptance Model (Davis, "Perceived Usefulness, Perceived Ease of Use, and User Acceptance of Information Technology," MIS Quarterly, 1989; Venkatesh et al., "User Acceptance of Information Technology: Toward a Unified View," MIS Quarterly, 2003)

Adoption of new technology is driven primarily by two factors: perceived usefulness (will this help me?) and perceived ease of use (can I figure this out?). Davis's TAM is one of the most cited papers in social science with over 20,000 citations.
- Perceived usefulness consistently explains 40-50% of variance in adoption intention across studies. Perceived ease of use explains an additional 10-20%, and its effect is partly mediated through usefulness -- if something is easy, people assume it must be useful.
- Venkatesh et al.'s UTAUT model added social influence and facilitating conditions, explaining up to 70% of adoption variance. Social influence matters most for mandatory adoption contexts and diminishes as experience increases.
- The intention-behavior gap is substantial: 30-40% of people who express intent to adopt a new technology never actually do so (Venkatesh & Davis, 2000).

When simulating: personas should evaluate innovations on usefulness first, ease of use second. Personas with low tech literacy should weight ease of use more heavily (up to 40% of their evaluation). Always apply a 30-40% discount from stated adoption intent to predicted actual adoption. Social influence should be strongest for personas in the early majority segment.

## Diffusion of Innovations (Rogers, "Diffusion of Innovations," 5th edition, Free Press, 2003; Bass, "A New Product Growth Model for Consumer Durables," Management Science, 1969)

Adoption follows a predictable S-curve driven by two forces: innovation (external influence like marketing) and imitation (internal influence like word of mouth).
- Rogers's adopter categories: innovators (2.5%), early adopters (13.5%), early majority (34%), late majority (34%), laggards (16%). Each segment has fundamentally different motivations and risk tolerances.
- Bass's model quantifies the innovation coefficient (p, typically 0.01-0.03) and imitation coefficient (q, typically 0.3-0.5). Imitation is 10-50x more powerful than innovation in driving adoption, meaning word of mouth dominates marketing.
- Moore's "Crossing the Chasm" theory identifies a critical gap between early adopters and the early majority. Early adopters buy vision; the early majority buys proven solutions. The messaging that works for the first group actively repels the second.
- Time to mainstream adoption (16% penetration) ranges from 2-8 years for most consumer technologies, but can compress to 6-18 months for network-effect products.

When simulating: distribute personas across Rogers's segments using the standard proportions. Innovator and early adopter personas should respond to novelty and vision. Early and late majority personas should require social proof and reliability evidence. Laggard personas should resist adoption unless forced by necessity or social pressure. Never model more than 16% of personas as immediate adopters of any genuinely new offering.

## Feature Adoption and Usage (Jain, Aagja & Bagdare, "Customer Experience -- A Review and Research Agenda," Journal of Service Theory and Practice, 2017; Nambisan & Baron, "Interactions in Virtual Customer Environments," Journal of Interactive Marketing, 2007)

Customers use only a fraction of available product features, and usage patterns follow a power law distribution.
- Industry data consistently shows that users engage with only 20-30% of a typical software product's features regularly. The remaining 70-80% are used rarely or never (Standish Group data, widely cited in product management literature).
- Nambisan & Baron found that customer participation in new feature adoption is driven by cognitive benefits (learning), social benefits (community), personal integrative benefits (status), and hedonic benefits (enjoyment). Features that satisfy only utilitarian needs see 40-50% lower voluntary adoption than those with social or hedonic components.
- Feature discovery is a major barrier: 50-60% of non-adoption is attributable to customers simply not knowing the feature exists rather than evaluating and rejecting it.

When simulating: personas should be aware of and actively use only 20-30% of product features. When asked about a new feature, 30-40% of personas should respond with "I didn't know that existed" for features launched in the past 6 months. Personas should show strong preference for familiar features and resist workflow changes unless the new feature solves an active pain point.

## Resistance to Innovation (Ram, "A Model of Innovation Resistance," Advances in Consumer Research, 1987; Heidenreich & Handrich, "What About Passive Innovation Resistance? Investigating Adoption-Related Behavior from a Resistance Perspective," Journal of Product Innovation Management, 2015; Claudy, Garcia & O'Driscoll, "Consumer Resistance to Innovation -- A Behavioral Reasoning Theory Perspective," Journal of the Academy of Marketing Science, 2015)

Innovation resistance is not the absence of adoption -- it is an active psychological force that must be overcome. Most resistance is passive (dispositional) rather than active (evaluation-based).
- Ram's model identifies five barriers: usage (incompatible with existing workflows), value (unclear ROI), risk (fear of negative consequences), tradition (preference for status quo), and image (social identity conflict).
- Heidenreich & Handrich found that 55-65% of innovation resistance is passive -- people reject new things simply because they are new, before any rational evaluation occurs. This dispositional resistance is strongest in older demographics and those with low openness-to-experience personality traits.
- Claudy et al. showed that "reasons against" adoption are psychologically distinct from "reasons for" adoption and are 1.5-2x more influential in the final decision. Removing barriers is more effective than adding benefits.

When simulating: at least 50% of personas should exhibit some form of innovation resistance by default. Passive resistance (dismissing without evaluation) should be more common than active resistance (evaluating and rejecting). Personas with low openness-to-experience should default to resistance. When modeling adoption campaigns, removing barriers should shift more personas than adding features or benefits.

## Network Effects and Critical Mass (Katz & Shapiro, "Network Externalities, Competition, and Compatibility," American Economic Review, 1985; Shapiro & Varian, "Information Rules: A Strategic Guide to the Network Economy," Harvard Business School Press, 1999)

Products with network effects become more valuable as more people use them, creating positive feedback loops that accelerate adoption past a critical mass threshold.
- Katz & Shapiro's framework distinguishes direct network effects (each user benefits from more users, e.g., messaging apps) from indirect network effects (more users attract more complementary products, e.g., app stores).
- Critical mass for network-effect products typically occurs at 10-25% market penetration, after which adoption becomes self-sustaining. Below this threshold, adoption is fragile and can collapse.
- Shapiro & Varian documented that in network-effect markets, customer expectations about future adoption are as important as current adoption levels. If customers believe a product will become dominant, they adopt preemptively.

When simulating: for products with network effects, personas should factor in how many people they know who use the product. Below 15-20% perceived adoption in the persona's social circle, network-effect products should face a "chicken and egg" credibility penalty of 30-50% on adoption intent. Above that threshold, social proof should accelerate adoption by 20-40%. Personas should articulate concerns about "betting on the wrong platform."

## Platform Switching Costs (Zhu & Iansiti, "Entry into Platform-Based Markets," Strategic Management Journal, 2012; Eisenmann, Parker & Van Alstyne, "Strategies for Two-Sided Markets," Harvard Business Review, 2006)

Platform lock-in operates through data, integrations, social connections, and learned behaviors that accumulate over time and create progressively higher exit barriers.
- Zhu & Iansiti found that platform incumbents retain 75-85% of users even when a superior entrant appears, because switching requires rebuilding data, customizations, and workflows. The "good enough" incumbent beats the "better" newcomer in most cases.
- Eisenmann et al. documented that multi-homing costs (using multiple platforms simultaneously) determine competitive dynamics. When multi-homing is cheap, platform loyalty is low and users maintain 2-3 active alternatives.
- Switching costs accumulate nonlinearly: after 6 months of use, switching cost is moderate; after 18 months, it approximately doubles; after 36 months, it plateaus at roughly 3x the 6-month level due to accumulated data, integrations, and habit formation.

When simulating: personas using a platform for less than 6 months should be relatively open to switching (25-35% would consider it). Personas at 12-18 months should show significant lock-in (only 10-20% would consider switching). Personas beyond 24 months should be deeply locked in (fewer than 10% would switch without a major catalyst). Data portability and integration compatibility should be top concerns for personas evaluating platform switches.
