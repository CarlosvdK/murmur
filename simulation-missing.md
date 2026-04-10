# Simulation Pipeline -- Missing Components

Everything we need to add, fix, or acquire to make the simulation pipeline work end-to-end.

---

## Missing Survey Fields

~~All critical fields added in Phase 1 (2026-04-10):~~
- ~~customer_age_distribution~~ DONE
- ~~customer_income_bracket~~ DONE
- ~~average_transaction_value~~ DONE
- ~~customer_gender_split~~ DONE
- ~~local_vs_visitor_ratio~~ DONE
- ~~digital_savviness~~ DONE
- ~~price_range~~ DONE

Still missing (lower priority):

| Field | Why it matters | Type | Priority |
|-------|---------------|------|----------|
| `customer_language` | Multicultural neighborhoods need culturally diverse personas. | chips (primary language(s)) | MEDIUM |
| `customer_loyalty_behavior` | Do customers actively choose this business or default to it? | select (destination/default/convenience/habit) | LOW (covered by business_role) |

---

## Missing Research / RAG Articles

### By Business Type (none exist yet)
- Restaurant/hospitality consumer psychology
- Retail consumer psychology
- Service business (barbershop, salon, gym) consumer psychology
- Cafe/coffee shop loyalty patterns
- Food truck / market stall consumer behavior

### By Customer Demographic (none exist yet)
- Generational consumer behavior (Gen Z, Millennial, Gen X, Boomer)
- Income-bracket spending psychology
- Gender differences in consumer behavior
- Family vs individual consumer decision-making

### By Question Type (none exist yet)
- Price elasticity research by industry
- Loyalty program effectiveness meta-analyses
- Menu/product change consumer reaction research
- Operating hours change impact studies
- Renovation/rebrand consumer reaction research

### Existing but Incomplete
- `behavioral_economics` -- has prompt file but no insight file
- `decision_making` -- has prompt file but no insight file
- `personality_models` -- has prompt file but no insight file
- `simulation_methodology` -- has prompt file but no insight file

---

## Missing API Integrations

| API / Source | What it would add | Priority |
|-------------|------------------|----------|
| Yelp Fusion API | Reviews from a different platform (bias diversity) | MEDIUM |
| TripAdvisor API | Tourist-heavy business reviews | LOW |
| Google Trends | Search interest trends for the area/industry | MEDIUM |
| Glassdoor / Indeed | Local wage data (income proxy for customer base) | LOW |
| Census / ONS / INE | Actual demographic data for the neighborhood | HIGH |
| Foursquare Places | Foot traffic patterns, peak hours validation | MEDIUM |

---

## Missing Frontend Components

| Component | What it does | Priority |
|-----------|-------------|----------|
| CI visualization chart | Confidence interval bar with prediction dot and labeled zones | CRITICAL |
| Decision card (go/no-go) | Clear binary recommendation with confidence level | CRITICAL |
| Evidence tab | Individual persona responses with demographic grouping | HIGH |
| Demographic breakdown view | "Younger customers say X, older customers say Y" | HIGH |
| A/B variant input | The chat UI doesn't collect variant_a/variant_b | HIGH |
| Profile completeness meter | Shows which survey fields are filled and their impact on accuracy | MEDIUM |
| Research sources panel | Shows which RAG articles and APIs informed this simulation | MEDIUM |

---

## Missing Backend Logic

| Module | What it does | Priority |
|--------|-------------|----------|
| Targeted RAG selector | Given a profile, select the most relevant research articles (by business type, customer demographics, question type) instead of dumping everything | CRITICAL |
| Profile enrichment pipeline | Structured psychological profile builder that layers cultural + demographic + industry research | CRITICAL |
| Multi-turn interview engine | Focus-group-style interviews (warm-up, core, probing) instead of single-shot | HIGH |
| Hypothesis framing | Detect the null hypothesis from the question and frame the output as go/no-go | HIGH |
| Demographic response grouping | Group persona responses by age bracket, segment type, price sensitivity | HIGH |
| Research-backed feature weights | Replace the current synthetic-data ML weights with literature-backed weights for persona generation | MEDIUM |

---

## Missing Data / Content

| Item | Status | Priority |
|------|--------|----------|
| Industry-specific calibration data | 0 articles | HIGH |
| Generational psychology research | 0 articles | HIGH |
| Price elasticity by industry | 0 articles | HIGH |
| Real user outcomes for ML retraining | 0 records (need 50+) | FUTURE |
| Backtest cases beyond 10 | Currently 10, need 50+ | MEDIUM |
| Census/demographic data by neighborhood | Not integrated | MEDIUM |
