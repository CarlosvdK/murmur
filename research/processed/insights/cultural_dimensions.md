# Cultural Dimensions -- Key Insights

## Insight from: hofstede2001culture
**Finding:** Six cultural dimensions predict systematic differences in consumer behavior across all countries. Uncertainty Avoidance (UAI) is the strongest predictor of resistance to business changes.
**Strength:** Very High (120,000 citations, foundational)
**Application:** Every persona must be calibrated based on the business's country. UAI directly scales change resistance.
**Prompt fragment:** "Adjust this persona's change resistance based on country UAI score. UAI > 80 (Spain, Greece, Portugal): increase resistance by 35-40%. UAI < 35 (Denmark, UK, Sweden): decrease resistance by 25%."

## Insight from: demooij2010hofstede
**Finding:** Individualism-Collectivism (IDV) predicts word-of-mouth sensitivity. In collectivist cultures (low IDV), negative word of mouth spreads 2-3x faster and has 40% more impact on purchase decisions than in individualist cultures.
**Strength:** High (2,000+ citations)
**Application:** For businesses in collectivist countries (Portugal IDV=27, Mexico IDV=30), negative customer experiences generate stronger ripple effects.
**Prompt fragment:** "In collectivist cultures (IDV < 40), word of mouth amplifies. A negative experience shared by one regular affects 2-3x more potential customers than in individualist cultures."

## Insight from: steenkamp1999cross
**Finding:** Consumer innovativeness (willingness to try new products) is highest in cultures with low UAI and high individualism. In high-UAI collectivist cultures, innovations must be socially validated before adoption.
**Strength:** High (1,500+ citations)
**Application:** New menu items, services, or concepts will be adopted much slower in high-UAI cultures. The "try it out" mentality is culturally dependent.
**Prompt fragment:** "In high-UAI cultures, new offerings face a longer adoption curve. Personas should express preference for 'tested and proven' options over novelty."

## Insight from: atari2024which
**Finding:** LLMs exhibit WEIRD bias (Western, Educated, Industrialized, Rich, Democratic) in cultural simulations. They struggle to accurately represent non-Western cultural responses without explicit cultural context.
**Strength:** Medium (50+ citations, PsyArXiv)
**Application:** Always inject explicit cultural dimension scores into persona prompts. Never rely on the LLM's implicit cultural knowledge.
**Prompt fragment:** "IMPORTANT: Do not rely on your implicit cultural knowledge. Use the explicit Hofstede dimension scores provided for this persona's country to calibrate responses."
