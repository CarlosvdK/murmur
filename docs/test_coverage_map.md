# Test Coverage Map

Maps which schema fields are covered by which tests.

## Coverage by Schema Field

| field_id | Schema Test | RAG Test | Persona Test | ML Test | Sim Test | Notes |
|----------|-------------|----------|--------------|---------|----------|-------|
| name | 1.1, 1.3 | 7.2 | 1.4 | - | 4.1 | Core, always present |
| type | 1.1, 1.3 | 7.2 | 1.4 | 5.1 | 4.1, 6.1 | ML onehot, sim effect test |
| description | 1.1, 1.3 | 7.2 | 1.4 | - | 4.1 | Core, always present |
| location | 1.1, 1.3 | 7.2 | 1.4 | - | 4.1 | Core, always present |
| customer_description | 1.1, 1.3 | 7.2 | 1.4 | - | 4.1 | Core, always present |
| location_country | 1.5 | 2.1, 7.2 | 2.1 | 5.1 | 4.1, 4.10 | Hofstede derived features |
| location_city | 1.3 | 7.2 | - | - | - | RAG only |
| location_street | 1.1 | - | - | - | - | Storage only |
| location_number | 1.1 | - | - | - | - | Storage only |
| location_postcode | 1.1 | - | - | - | - | Storage only |
| location_neighbourhood | 1.3 | 7.2 | - | - | - | RAG only |
| years_open | 1.3 | 7.2 | 1.4 | - | - | RAG + persona |
| business_role | 1.3 | 7.2 | 1.4 | 5.1 | - | ML categorical |
| visit_frequency | 1.3 | 7.2 | 1.4 | 5.1 | 6.2 | ML ordinal, sim effect |
| busy_days | 1.3 | 7.2 | - | - | - | RAG only |
| busy_times | 1.3 | 7.2 | - | - | - | RAG only |
| customer_value_drivers | 1.3, 1.5 | 7.2 | 1.4 | 5.1 | 6.4 | ML onehot, sim effect |
| customer_social_context | 1.3 | 7.2 | - | - | 6.6 | Sim effect test |
| regular_proportion | 1.3 | 7.2 | 1.4 | 5.1 | - | ML ordinal |
| area_demographics | 1.3 | 7.2 | 1.4 | 5.1 | 6.3 | ML categorical, sim effect |
| competitor_count | 1.3 | 7.2 | 1.4 | 5.1 | 6.5 | ML ordinal, sim effect |
| area_feel | 1.3 | 7.2 | 1.4 | - | - | RAG + persona |
| website_url | 1.3 | 7.2 | - | - | - | RAG low weight |
| google_place_id | 1.1 | - | - | - | - | Storage only |
| google_business_url | 1.1 | - | - | - | - | Storage only |
| tripadvisor_url | 1.1 | - | - | - | - | Storage only |
| instagram_url | 1.1 | - | - | - | - | Storage only |
| facebook_url | 1.1 | - | - | - | - | Storage only |
| additional_customer_notes | 1.3 | 7.2 | - | - | - | RAG medium |
| has_prior_change | 1.3 | 7.2 | - | - | - | RAG medium |
| prior_change_description | 1.3 | 7.2 | 1.4 | - | - | RAG + persona |
| prior_change_outcome | 1.3 | 7.2 | 1.4 | - | - | RAG + persona |
| location_settings | 1.3 | 7.2 | - | - | - | RAG medium |
| area_draws | 1.3 | 7.2 | - | - | - | RAG medium |
| customer_transport | 1.3 | 7.2 | - | - | - | RAG low |
| has_parking | 1.3 | 7.2 | - | - | - | RAG low |
| first_visit_reasons | 1.3 | 7.2 | - | - | - | RAG medium |
| seasonal_patterns | 1.3 | 7.2 | - | - | - | RAG medium |
| customer_community | 1.3 | 7.2 | - | - | - | RAG medium |
| opening_hours | 1.3 | 7.2 | 1.4 | - | - | RAG + persona |
| prior_change_types | 1.3 | 7.2 | - | - | - | RAG medium |
| prior_change_went | 1.3 | 7.2 | - | - | - | RAG medium |
| anything_else | 1.3 | 7.2 | - | - | - | RAG low |

## Coverage by Test Section

| Section | Tests | What's Covered |
|---------|-------|----------------|
| 1. Schema Integrity | 8 | YAML loading, field validation, RAG output, persona output, ML features, accuracy scoring |
| 2. Research Injection | 6 | Hofstede calibration, consumer psychology, silent majority, review bias, negotiation, hypothetical bias |
| 3. Statistical Validity | 8 | CI computation, sentiment mapping, decision framework, diversity, anti-optimism, RTM detection |
| 4. Simulation Types | 12 | Standard, cultural comparison, vendor negotiation, twin query, segment, temporal, counterfactual |
| 5. ML Calibration | 6 | Feature vectors, model training, importance, pipeline integration, persistence, retraining |
| 6. Survey Data Utilisation | 7 | Effect of each major field section on simulation output |
| 7. Data Flow | 6 | Survey→DB, DB→RAG, RAG→Sim, Survey→ML, Outcome→Model, Schema auto-update |
| 8. Performance | 5 | Timing for all major operations |
| 9. Regression | Per-sim | Snapshot comparison for stability |

## Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| No existing test files | CRITICAL | Everything must be built from scratch |
| No ML calibration model | HIGH | Must be built as production + test infra |
| No formal statistical tests | MEDIUM | Impact estimator uses informal CI, no Wilson/Cohen/binomial |
| Social URLs not tested in RAG | LOW | instagram_url, facebook_url etc. are storage-only |
| Twin query quality testing | MEDIUM | Depends on corpus data quality |
| Real outcomes UI missing | MEDIUM | Can't test outcome→retraining loop without it |

## Research Library Coverage in Tests

| Domain | Prompt File Exists | Tested in Section | Key Assertion |
|--------|--------------------|-------------------|---------------|
| consumer_psychology | Y | 2.2 | loss aversion, status quo bias cited |
| behavioral_economics | Y | 2.2 | anchoring, framing effects |
| review_bias | Y | 2.4 | vocal minority, silent majority 55-70% |
| personality_models | Y | - | OCEAN mapping (not directly tested) |
| decision_making | Y | - | Rogers adoption curve (not directly tested) |
| country_profiles | Y | 2.1 | Hofstede UA calibration |
| negotiation_psychology | Y | 2.5 | BATNA, anchoring in vendor twin |
| digital_twins | Y | - | Anti-positive-bias (tested indirectly via 3.7) |
| simulation_methodology | Y | 3.8 | Minimum sample size |

## Hofstede Countries Tested

| Country | Code | UA | IDV | Test |
|---------|------|----|-----|------|
| Spain | ES | 86 | 51 | 4.1, 4.10 (SEED_A) |
| UK | GB | 35 | 89 | 4.10 (SEED_B) |
| Netherlands | NL | 53 | 80 | SEED_C (not in sim test) |
| Germany | DE | 65 | 67 | SEED_D (vendor test) |
