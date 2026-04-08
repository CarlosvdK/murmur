# Murmur Research Library

Academic knowledge that powers every simulation, persona, and digital twin.

## What This Is

A curated collection of research findings from consumer psychology, behavioral economics, cultural studies, and simulation methodology. Every prompt fragment in this library is grounded in peer-reviewed research and designed to be injected directly into Claude API calls.

## How It Works

1. **Persona generation** -- Cultural dimensions (Hofstede) calibrate how each persona responds to change based on their country
2. **Simulation interviews** -- Consumer psychology and behavioral economics insights shape realistic reactions
3. **Twin queries** -- Negotiation psychology informs vendor twin predictions
4. **Review intelligence** -- Review bias research corrects for silent majority vs vocal minority
5. **Aggregation** -- Simulation methodology rules calibrate confidence and uncertainty language

## Directory Structure

```
research/
  library/          -- Raw papers by domain (PDFs, abstracts)
  processed/
    summaries/      -- One .md per paper with key findings
    insights/       -- Extracted rules per domain
    prompts/        -- Ready-to-inject prompt fragments (MOST IMPORTANT)
    hofstede_scores.json  -- Country cultural dimension scores
  index.json        -- Master index of all papers
  rag_library.py    -- Python integration module
```

## Using the Library in Code

```python
from research.rag_library import get_simulation_context, get_country_profile

# Get full research context for a simulation
context = get_simulation_context("ES", "consumer")
# Returns: cultural profile + consumer psychology + review bias + methodology

# Get just the cultural modifier
profile = get_country_profile("ES")
# Returns: Hofstede scores + simulation_profile adjustments
```

## How to Add a New Paper

1. Check quality filters:
   - Pre-2022: minimum 100 citations (500 for foundational)
   - 2022-2023: minimum 50 citations
   - 2024-2025: minimum 15 citations (5 from top labs)
   - Must be from peer-reviewed journal, named conference, or credentialed arXiv

2. Save to `library/[domain]/[slug].pdf`
3. Create summary at `processed/summaries/[slug].md`
4. Append insights to `processed/insights/[domain].md`
5. If significant: add prompt fragment to `processed/prompts/[domain].md`
6. Add entry to `index.json`

## Top 10 Most Critical Papers

1. **Kahneman & Tversky 1979** -- Prospect Theory (85,000 citations). Loss aversion = 2x. Foundation for all price reaction simulations.
2. **Hofstede 2001** -- Culture's Consequences (120,000 citations). Six cultural dimensions. Foundation for all cross-cultural persona calibration.
3. **Rogers 2003** -- Diffusion of Innovations (130,000 citations). Adoption curve. Maps customer segments to innovation acceptance.
4. **Park et al. 2023** -- Generative Agents (3,500 citations). Validates LLM agent simulation approach.
5. **Gao et al. 2015** -- Vocal Minority (850 citations). Proves reviews are not representative. Foundation for silent majority modeling.
6. **Park et al. 2024** -- 1000 People simulation (85 citations). Shows 85% accuracy with rich demographic data.
7. **Gui & Toubia 2023** -- LLM simulation challenges (45 citations). Identifies positive bias (~20-30%) in LLM personas.
8. **Thaler 1985** -- Mental Accounting (9,500 citations). Explains why identical price changes feel different in context.
9. **Fisher & Ury 1981** -- Getting to Yes (15,000 citations). BATNA and principled negotiation for vendor twins.
10. **Cialdini 1984** -- Influence (20,000+ citations). Six principles of persuasion that shape consumer behavior.

## Hofstede Scores

30 countries indexed. Priority countries for Murmur (serving European SMBs):
- Very High Uncertainty Avoidance: Spain (86), France (86), Greece (100), Portugal (99), Poland (93), Belgium (94)
- High: Italy (75), Germany (65), Brazil (76), Mexico (82)
- Moderate: Netherlands (53), Finland (59), Switzerland (58)
- Low: Denmark (23), Sweden (29), UK (35), Ireland (35), US (46)

These scores directly affect persona change resistance, loyalty patterns, and social proof sensitivity.

## Citation Counts

All citation counts recorded as of April 2026. Re-check annually to detect if newer papers supersede older findings.
