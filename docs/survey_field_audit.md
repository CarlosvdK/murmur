# Survey Field Audit -- 2026-04-08

## Summary
- **40 survey fields** identified across the codebase
- **7 stored as DB columns** (name, type, description, customer_description, location, created_at, updated_at)
- **33 stored in metadata JSONB**
- **6 fields used in persona prompts** (name, type, description, customer_description, location, visit_frequency)
- **~15 fields used in context engine** (business_role, visit_frequency, value_drivers, area_demographics, etc.)
- **~20 fields NOT wired to RAG or persona prompts** (address components, social URLs, prior change data, etc.)

## Field Matrix

| field_id | frontend | api_model | db | rag | persona | ml | notes |
|----------|----------|-----------|-----|-----|---------|-----|-------|
| name | Y | Y | column | Y | Y | N | Template var: {{business_name}} |
| type | Y | Y | column | Y | Y | N | Template var: {{business_type}} |
| description | Y | Y | column | Y | Y | N | Template var: {{business_description}} |
| customer_description | Y | Y | column | Y | Y | N | Template var: {{customer_description}} |
| location | Y | Y | column | Y | Y | N | Template var: {{location}} |
| location_street | Y | Y | jsonb | N | N | N | Address component |
| location_number | Y | Y | jsonb | N | N | N | Address component |
| location_postcode | Y | Y | jsonb | N | N | N | Address component |
| location_city | Y | Y | jsonb | N | N | N | Address component |
| location_neighbourhood | Y | Y | jsonb | N | N | N | Address component |
| location_country | Y | Y | jsonb | N | N | N | KEY: triggers Hofstede |
| years_open | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| business_role | Y | Y | jsonb | Y | N | N | Gap: not in persona |
| visit_frequency | Y | Y | jsonb | Y | Y | N | In persona_interview |
| busy_days | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| busy_times | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| customer_value_drivers | Y | Y | jsonb | Y | N | N | Gap: not in persona |
| customer_social_context | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| regular_proportion | Y | Y | jsonb | Y | N | N | Used in reviewer_intelligence |
| area_demographics | Y | Y | jsonb | Y | N | N | Context engine triggers |
| competitor_count | Y | Y | jsonb | Y | N | N | Context for generation |
| area_feel | Y | Y | jsonb | Y | N | N | Context for personas |
| website_url | Y | Y | jsonb | Y | N | N | Context engine: web_search |
| google_place_id | Y | Y | jsonb | Y | N | N | Context engine: google_places |
| additional_customer_notes | Y | Y | jsonb | Y | N | N | Free-form context |
| has_prior_change | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| prior_change_description | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| prior_change_outcome | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| location_settings | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| area_draws | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| customer_transport | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| has_parking | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| first_visit_reasons | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| seasonal_patterns | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| customer_community | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| opening_hours | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| google_business_url | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| tripadvisor_url | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| instagram_url | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| facebook_url | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| prior_change_types | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| prior_change_went | Y | Y | jsonb | N | N | N | Gap: not in RAG |
| anything_else | Y | Y | jsonb | N | N | N | Gap: not in RAG |

## Key Gaps
- **20+ fields** collected but never used in simulations
- **location_country** is the most critical unwired field (should trigger Hofstede calibration)
- **years_open, busy_days, busy_times** are useful context never passed to personas
- **prior_change data** is valuable backtesting signal never used
- **opening_hours** critical for hour-change simulations, not in RAG
