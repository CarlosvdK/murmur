# Decision Making: Calibration Instructions

When simulating how personas adopt new products, perceive risk, and make decisions under uncertainty, apply the following frameworks. These determine which customer segments respond first, which resist longest, and how risk perception shapes behavior differently from objective risk.

## Diffusion of Innovations (Rogers, "Diffusion of Innovations," 5th edition, 2003)

All persona cohorts must map to Rogers' adoption curve. The distribution is empirically stable across product categories, industries, and cultures:

- **Innovators (2.5% of population):** Risk-seeking, high income or high willingness to absorb losses, high Openness (8-10). They adopt based on the product's novelty alone. They do not need social proof -- in fact, social proof can reduce their interest ("if everyone has it, it's not interesting"). They tolerate bugs, incomplete features, and poor UX. They are motivated by being first. They provide early feedback but are not representative of the broader market. Do not use their reactions to predict mainstream reception.

- **Early Adopters (13.5% of population):** Opinion leaders. High Openness (6-9), moderate-to-high Extraversion (6-8). They adopt based on perceived strategic advantage, not pure novelty. They need a compelling value proposition but do not need proof that others have adopted. They are the critical bridge to mainstream adoption -- if they endorse, the early majority follows. Their reviews and word-of-mouth carry disproportionate weight. They are willing to pay premium prices for early access.

- **Early Majority (34% of population):** Pragmatists. Moderate Openness (4-6), moderate-to-high Conscientiousness (5-7). They adopt after seeing evidence that the product works for people like them. They need social proof, case studies, and reviews. They are price-sensitive relative to early adopters. They want reliability and support. The transition from early adopters to early majority is the "chasm" (Moore, "Crossing the Chasm," 1991) -- many products fail here because early adopter enthusiasm does not automatically translate to early majority adoption.

- **Late Majority (34% of population):** Skeptics. Low Openness (3-5), high Neuroticism (6-8). They adopt only when the product has become the norm or when not adopting creates social/professional pressure. They are highly price-sensitive. They need extensive proof, risk reduction (guarantees, free trials), and often adopt due to necessity rather than desire. They are the most sensitive to switching costs and prefer products that integrate with what they already use.

- **Laggards (16% of population):** Traditionalists. Very low Openness (1-3), high Conscientiousness about current routines. They adopt only when their current solution is no longer available or when institutional pressure forces adoption. They are suspicious of change. Marketing to laggards directly is usually not cost-effective -- they adopt when they have no alternative. Their reference point is the past: "the old way worked fine."

When simulating a cohort response to a new product or change, stagger adoption across these segments. Do not show all personas responding simultaneously. The timeline depends on product category:
- Digital products / apps: Innovators within days, early adopters within weeks, early majority within 2-6 months, late majority within 6-18 months.
- Physical products / services: Roughly 2x the digital timeline.
- High-cost products: Roughly 3-5x the low-cost timeline for the same category.

## Risk Perception (Slovic, "The Perception of Risk," 1987; Slovic, "Trust, Emotion, Sex, Politics, and Science," Risk Analysis, 1999)

Personas do not perceive risk objectively. Perceived risk diverges from actual risk in systematic ways:

- **Dread risk amplification:** Risks that are perceived as uncontrollable, catastrophic, or involuntary are weighted 5-10x more heavily than equivalent risks that are perceived as controllable, chronic, or voluntary. A data breach (uncontrollable, catastrophic) produces far more customer flight than a slow, steady decline in service quality (controllable, chronic) -- even when the latter costs the customer more.

- **Availability heuristic:** Risks that are easily recalled (recent, vivid, emotionally charged) are perceived as more probable. A persona who recently heard about a competitor's security breach will overweight security concerns by 2-4x when evaluating your product. This decays over time -- roughly halving every 2-3 months without reinforcement.

- **Affect heuristic:** Risk judgments are driven by emotional reactions, not probability calculations. If a persona feels positively about a brand, they perceive its products as lower risk AND higher benefit simultaneously (these should be independent but empirically are not). If they feel negatively, both risk perception and benefit perception worsen.

- **Trust asymmetry:** Trust is slow to build and fast to destroy. A single trust-violating event (perceived dishonesty, hidden fees, data misuse) destroys 6-12 months of trust-building. Slovic's research shows that negative trust events are 2-4x more impactful than positive trust events of equal magnitude. When simulating reactions to business mistakes, apply this asymmetry.

## Ambiguity Aversion (Ellsberg, "Risk, Ambiguity, and the Savage Axioms," Quarterly Journal of Economics, 1961; Fox & Tversky, "Ambiguity Aversion and Comparative Ignorance," Quarterly Journal of Economics, 1995)

Personas prefer known risks over unknown risks, even when the unknown risk has a better expected value:

- A persona will choose a product with a known 20% failure rate over a product with an unknown failure rate, even if available evidence suggests the unknown rate is likely ~10%.
- This means established businesses with known flaws beat new businesses with unknown quality, all else being equal. The incumbent advantage from ambiguity aversion is roughly 15-25% in choice studies (Fox & Tversky, 1995).
- Ambiguity aversion is strongest when the persona feels they know less than others about the domain ("comparative ignorance"). A persona who is a domain expert exhibits less ambiguity aversion in that domain.
- To overcome ambiguity aversion, new products must signal transparency: clear pricing, detailed specs, visible reviews, money-back guarantees. Each transparency signal reduces the ambiguity penalty by roughly 10-15%.

## Choice Overload (Iyengar & Lepper, "When Choice is Demotivating," Journal of Personality and Social Psychology, 2000; Chernev et al., "Choice Overload: A Conceptual Review," Journal of Consumer Psychology, 2015)

More options do not always produce better outcomes for personas:

- In Iyengar's jam study, reducing options from 24 to 6 increased purchase conversion by ~10x (from 3% to 30%). While subsequent meta-analyses (Chernev et al., 2015) show the effect is more conditional than initially reported, choice overload reliably occurs when: (a) the persona lacks strong prior preferences, (b) options are difficult to compare, and (c) the decision feels high-stakes.
- When simulating persona responses to menus, pricing tiers, or product catalogs with more than 5-7 options: increase decision deferral ("I'll decide later" = never) by 20-40%.
- High-Conscientiousness personas are more susceptible to choice overload because they feel compelled to evaluate all options. Low-Conscientiousness personas handle large choice sets better because they satisfice (pick the first acceptable option) rather than maximize.
- The "decoy effect" (Huber, Payne, & Puto, "Adding Asymmetrically Dominated Alternatives," Journal of Consumer Research, 1982): adding a clearly inferior option makes an adjacent option look better, shifting preference by 15-25% in controlled studies. When a business offers three tiers and the middle tier is the target, the top tier often serves as a decoy.

## Satisficing vs. Maximizing (Schwartz, "The Paradox of Choice," 2004; Simon, "A Behavioral Model of Rational Choice," Quarterly Journal of Economics, 1955)

Not all personas optimize. Most satisfice -- they choose the first option that meets their minimum threshold rather than evaluating all options:

- Approximately 60-70% of consumers are satisficers for any given purchase category. They search until they find "good enough" and stop.
- Maximizers (~30-40%) evaluate extensively and are more likely to experience post-purchase regret even when they objectively chose well. High Conscientiousness + High Neuroticism personas are most likely to be maximizers.
- Satisficers are faster to convert but less sensitive to marginal product improvements. Maximizers are slower to convert but more sensitive to competitive positioning.
- When simulating: satisficing personas should stop evaluating alternatives once they find an option that meets their stated requirements, even if a better option exists. They should not exhibit regret about potentially better alternatives they did not evaluate.
