# Retroactive Testing Plan — Comprehensive Coverage

**Goal:** Test every single line of existing code before building new features.  
**Rule:** A feature is NOT "done" until tests prove it works end-to-end.

---

## BACKEND: 80+ Python Files

### CRITICAL PATH (Core Business Logic)
These are the heart of the application. Mission-critical.

#### 1. `backend/api/routes/simulations.py` (350+ lines)
**What it does:** Orchestrates the entire simulation flow (_run_pipeline is the entry point)  
**Tests needed:**
- `test_create_simulation()` — POST /simulations creates record in DB
- `test_run_pipeline()` — Full flow: context gathering → persona generation → simulation → aggregation
- `test_run_pipeline_with_uploads()` — CSV data injected into context
- `test_run_pipeline_timeout()` — Handles 5s timeout gracefully
- `test_run_pipeline_partial_failure()` — One tool fails, simulation continues
- `test_stream_progress()` — SSE events emit correctly
- `test_get_simulation()` — Retrieves completed simulation with results
- `test_outcome_submission()` — POST /simulations/{id}/outcome records real outcome
- `test_accuracy_stats()` — GET /simulations/accuracy-stats calculates correctly

**Status:** 🔴 NOT TESTED

#### 2. `backend/swarm/simulator.py` (200+ lines)
**What it does:** Runs interview with each persona in parallel  
**Tests needed:**
- `test_run_interview_success()` — Full persona interview succeeds
- `test_run_interview_with_context()` — Interview uses context data
- `test_run_interview_timeout()` — Individual persona timeout handled
- `test_run_interview_api_error()` — Claude API error gracefully degraded
- `test_run_interview_parallel()` — Multiple personas run in parallel
- `test_minimum_success_rate()` — If <60% succeed, simulation fails
- `test_interview_response_parsing()` — Response parsed into correct schema

**Status:** 🔴 NOT TESTED

#### 3. `backend/swarm/persona_generator.py` (250+ lines)
**What it does:** Generates N personas tailored to business  
**Tests needed:**
- `test_generate_personas_count()` — Returns exactly N personas
- `test_generate_personas_diversity()` — Personas have different traits/ages/habits
- `test_generate_with_manifest()` — Structured manifest respected (age, income, frequency, price_sensitivity)
- `test_generate_with_upload_data()` — CSV data influences persona generation
- `test_generate_timeout()` — Handles Anthropic API timeout
- `test_anti_bias_instructions()` — Personas not overly positive/rational
- `test_persona_cache_reuse()` — Cached archetype reused for same business

**Status:** 🔴 NOT TESTED

#### 4. `backend/swarm/aggregator.py` (150+ lines)
**What it does:** Synthesizes all persona responses into final output  
**Tests needed:**
- `test_aggregate_responses()` — All responses included in aggregation
- `test_aggregate_sentiment_calculation()` — Sentiment score computed correctly
- `test_aggregate_themes()` — Themes grouped properly
- `test_aggregate_outlier_detection()` — Standout voices identified
- `test_aggregate_confidence()` — Confidence score reflects data quality
- `test_aggregate_with_caveats()` — Caveats injected into output
- `test_aggregate_timeout()` — Handles timeout gracefully
- `test_cherry_pick_warning()` — Anti-p-hacking safeguards work

**Status:** 🔴 NOT TESTED

#### 5. `backend/auth/dependencies.py` (80+ lines)
**What it does:** JWT auth, permission checks, user/tier extraction  
**Tests needed:**
- `test_get_current_user_id_valid_token()` — Valid JWT extracts user ID
- `test_get_current_user_id_invalid_token()` — Invalid JWT raises 401
- `test_get_current_user_id_expired_token()` — Expired token raises 401
- `test_get_current_user_tier_standard()` — Standard tier user identified
- `test_get_current_user_tier_premium()` — Premium tier user identified
- `test_require_auth_blocks_unauth()` — Unauthed request blocked
- `test_require_auth_allows_authed()` — Valid auth allowed

**Status:** 🔴 NOT TESTED

#### 6. `backend/api/routes/uploads.py` (100+ lines)
**What it does:** File upload, CSV parsing, storage  
**Tests needed:**
- `test_upload_csv_parsing()` — CSV parsed correctly
- `test_upload_csv_row_count()` — Row count correct
- `test_upload_csv_column_detection()` — Columns extracted
- `test_upload_csv_sample_rows()` — Sample rows returned (≤5)
- `test_upload_unsupported_format()` — .exe rejected with 400
- `test_upload_oversized_file()` — >10MB rejected with 400
- `test_upload_wrong_owner()` — Other user can't access → 404
- `test_upload_utf8_error()` — Binary/encoding error → graceful fallback
- `test_upload_stored_in_db()` — File metadata saved to business_uploads table
- `test_upload_injection_into_context()` — Parsed CSV data in context_narrative

**Status:** 🟡 PARTIAL (CSV parsing works, injection untested)

#### 7. `backend/api/routes/businesses.py` (150+ lines)
**What it does:** CRUD for business profiles  
**Tests needed:**
- `test_create_business()` — POST /businesses creates record
- `test_get_business()` — GET /businesses/{id} returns owned business
- `test_get_business_404()` — GET non-existent → 404
- `test_get_business_forbidden()` — Other user's business → 403
- `test_update_business()` — PATCH /businesses/{id} updates fields
- `test_update_business_forbidden()` — Other user can't update → 403
- `test_delete_business()` — DELETE /businesses/{id} removes record
- `test_delete_business_forbidden()` — Other user can't delete → 403
- `test_list_businesses()` — GET /businesses returns user's businesses only

**Status:** 🔴 NOT TESTED

#### 8. `backend/db/client.py` (50+ lines)
**What it does:** Supabase client initialization  
**Tests needed:**
- `test_get_supabase_returns_client()` — get_supabase() returns Supabase instance
- `test_get_supabase_cached()` — LRU cache works (same instance returned)
- `test_supabase_connection()` — Client can connect (or mock Supabase)

**Status:** 🔴 NOT TESTED

---

### CONTEXT ENGINE (8 Tools + Orchestration)

#### 9. `backend/context/orchestrator.py`
**Tests needed:**
- `test_orchestrator_selects_tools()` — Claude decides which tools matter
- `test_orchestrator_runs_tools_in_parallel()` — Tools run simultaneously
- `test_orchestrator_timeout()` — 30s per tool, 90s total
- `test_orchestrator_graceful_degradation()` — 1 tool fails, others continue
- `test_orchestrator_returns_context()` — Returns BusinessContext

**Status:** 🔴 NOT TESTED

#### 10. `backend/context/filter.py`
**Tests needed:**
- `test_filter_skips_for_few_results()` — <3 tools, no filtering
- `test_filter_summarizes_large_results()` — 4+ tools, Claude summarizes
- `test_filter_preserves_relevance()` — Only relevant content kept
- `test_filter_timeout()` — Handles timeout gracefully

**Status:** 🔴 NOT TESTED

#### 11. `backend/context/tools/web_search.py`
**Tests needed:**
- `test_web_search_returns_results()` — Query returns 5-10 results
- `test_web_search_empty_query()` — Empty query → empty results
- `test_web_search_api_failure()` — API 500 → graceful return
- `test_web_search_retry_on_429()` — Retries on rate limit (with tenacity)
- `test_web_search_retry_on_500()` — Retries on server error
- `test_web_search_no_retry_on_401()` — Auth error fails immediately
- `test_web_search_timeout()` — 20s timeout respected

**Status:** 🔴 NOT TESTED (respx mocks ready)

#### 12. `backend/context/tools/news_search.py`
**Tests needed:**
- Similar to web_search (returns news results)
- `test_news_search_filters_by_date()` — Recent news only
- `test_news_search_retry_logic()`

**Status:** 🔴 NOT TESTED

#### 13. `backend/context/tools/google_places.py`
**Tests needed:**
- `test_google_places_finds_business()` — Searches for business location
- `test_google_places_returns_rating()` — Rating extracted
- `test_google_places_returns_reviews()` — Reviews included
- `test_google_places_api_failure()` — Graceful degradation
- `test_google_places_retry_logic()`

**Status:** 🔴 NOT TESTED

#### 14. `backend/context/tools/review_analyzer.py`
**Tests needed:**
- `test_review_analyzer_summarizes_reviews()` — Multi-review summary
- `test_review_analyzer_extracts_sentiment()` — Sentiment from text
- `test_review_analyzer_identifies_themes()` — Common complaints/praise
- `test_review_analyzer_empty_reviews()` — No reviews → default
- `test_review_analyzer_api_failure()`

**Status:** 🔴 NOT TESTED

#### 15. `backend/context/tools/social_sentiment.py`
**Tests needed:**
- `test_social_sentiment_gathers_reddit()` — Reddit search
- `test_social_sentiment_score_in_range()` — -1 to 1
- `test_social_sentiment_retry_logic()`
- `test_social_sentiment_api_failure()`

**Status:** 🔴 NOT TESTED

#### 16-19. `backend/context/tools/weather_trends.py`, `price_index.py`, `demographic.py`, `google_trends.py`
**Tests needed:** Similar pattern for each tool  
**Status:** 🔴 NOT TESTED

#### 20. `backend/context/realtime_intelligence.py`
**Tests needed:** (Already written in Phase 1)
- `test_payday_week()`, `test_is_holiday()`, etc.
- `test_gather_all()` returns full RealtimeContext

**Status:** 🟡 PARTIAL (Phase 1 tests written, implementation needed)

#### 21. `backend/context/location_profiler.py`
**Tests needed:** (Already written in Phase 1)
- `test_extract_country_code()`, `test_world_bank_api()`, etc.

**Status:** 🟡 PARTIAL (Phase 1 tests written, implementation needed)

---

### REVIEWER INTELLIGENCE (6 Modules)

#### 22-27. `backend/reviewer_intelligence/*.py`
**Tests needed per module:**
- `test_extract_review_signals()` — Google Places data extracted
- `test_apply_bias_corrections()` — Extremity/platform/majority corrections
- `test_estimate_silent_majority()` — Silent majority modeled
- `test_build_customer_segments()` — 6 segments with correct proportions
- `test_calibrate_personas()` — Manifest built from segments
- `test_build_reviewer_intelligence()` — Full pipeline

**Status:** 🔴 NOT TESTED

---

### MODELS (Pydantic Validation)

#### 28-34. `backend/models/*.py` (business.py, persona.py, simulation.py, context.py, etc.)
**Tests needed per file:**
- `test_model_creation()` — Model instantiates with valid data
- `test_model_validation()` — Invalid data raises validation error
- `test_model_serialization()` — .model_dump() works
- `test_model_json_schema()` — Schema generation works

**Status:** 🟡 PARTIAL (test_models.py exists, only covers some models)

---

### OTHER BACKEND (Config, Utils, Research, CRM, Impact, ML)

#### 35-45. Config, research, CRM, impact, ML modules
**Tests needed:** Module-specific functionality  
**Status:** 🔴 MOSTLY NOT TESTED

---

## FRONTEND: 70+ TypeScript/TSX Files

### CRITICAL PATH (Core Pages & Components)

#### 1. `frontend/src/lib/api.ts` (150+ lines)
**What it does:** All API client calls  
**Tests needed:**
- `test_createSimulation()` — POST /simulations works
- `test_getSimulationProgress()` — Polls progress correctly
- `test_getSimulationResult()` — Retrieves completed result
- `test_createBusiness()` — POST /businesses works
- `test_updateBusiness()` — PATCH /businesses works
- `test_uploadFile()` — POST /uploads works
- `test_listSimulations()` — GET /simulations works
- `test_submitRealOutcome()` — POST /simulations/{id}/outcome works
- `test_getAccuracyStats()` — GET /simulations/accuracy-stats works
- `test_error_handling()` — API errors handled gracefully
- `test_auth_token_passed()` — Authorization header set
- `test_retry_on_network_error()` — Network errors retry

**Status:** 🔴 NOT TESTED

#### 2. `frontend/src/components/simulate2/ChatInterface.tsx` (300+ lines)
**What it does:** Main simulation polling loop  
**Tests needed:**
- `test_starts_simulation()` — createSimulation() called
- `test_polls_progress()` — getSimulationProgress() called every 3s
- `test_shows_completion()` — Result shown when done
- `test_shows_error_after_failures()` — 3 network errors → error message
- `test_timeout_after_8_minutes()` — Displays timeout message
- `test_friendly_error_messages()` — Error messages user-friendly
- `test_retry_logic()` — Exponential backoff on failure
- `test_sse_fallback()` — Falls back to polling if SSE unavailable

**Status:** 🔴 NOT TESTED

#### 3. `frontend/src/components/questionnaire/BusinessProfileForm.tsx` (250+ lines)
**What it does:** Multi-step business profile form  
**Tests needed:**
- `test_step_0_validation()` — Next disabled until name/type/description valid
- `test_step_0_char_count()` — Description char count shown
- `test_step_0_min_length()` — Description <50 chars shows error
- `test_step_1_validation()` — customer_description >30 chars required
- `test_step_2_validation()` — All fields filled before submit
- `test_form_submission()` — createBusiness() called with data
- `test_form_validation_errors()` — Errors shown on blur
- `test_discard_warning()` — Warn on unsaved changes

**Status:** 🔴 NOT TESTED

#### 4. `frontend/src/app/app/page.tsx` (200+ lines)
**What it does:** Dashboard with recent simulations  
**Tests needed:**
- `test_loads_simulations_on_mount()` — listSimulations() called
- `test_displays_empty_state()` — No sims → "Create your first" CTA
- `test_displays_recent_simulations()` — Last 5 sims shown
- `test_shows_simulation_status()` — Status badge correct (running/done/failed)
- `test_shows_outcome_button()` — "What happened?" on completed sim
- `test_shows_outcome_logged_badge()` — Green badge if outcome recorded
- `test_outcomes_ui_integration()` — submitRealOutcome() called
- `test_accuracy_stats_displayed()` — Accuracy % shown if outcomes exist

**Status:** 🔴 NOT TESTED (hardcoded placeholder)

#### 5. `frontend/src/components/simulation/SimulationPanel.tsx` (150+ lines)
**What it does:** Real-time simulation progress with SSE  
**Tests needed:**
- `test_opens_event_source()` — EventSource created on start
- `test_receives_progress_updates()` — Progress event updates UI
- `test_receives_done_event()` — Done event triggers result fetch
- `test_sse_error_handled()` — Error event handled gracefully
- `test_timeout_event_shown()` — Timeout event shows message
- `test_closes_connection_on_complete()` — EventSource closed
- `test_persona_grid_updates()` — Persona status badges update

**Status:** 🔴 NOT TESTED

---

### PAGES (10+ page components)

#### 6-15. `frontend/src/app/**/*.tsx` (login, signup, onboarding, simulate, etc.)
**Tests needed:**
- `test_page_loads()` — Component renders without error
- `test_redirect_unauthenticated()` — Unauthed users redirected to login
- `test_navigation_works()` — Links/buttons navigate correctly
- `test_api_calls_on_mount()` — Required data fetched

**Status:** 🔴 MOSTLY NOT TESTED

---

### COMPONENTS (40+ components)

#### 16-55. Component library (forms, results, simulation, etc.)
**Tests needed per component:**
- `test_renders()` — Component renders
- `test_accepts_props()` — Props work correctly
- `test_handles_click()` — Click handlers work
- `test_displays_data()` — Data displayed correctly
- `test_handles_empty_state()` — Empty data handled gracefully

**Status:** 🔴 MOSTLY NOT TESTED

---

## DATABASE (schema.sql)

#### Tests needed:
- `test_tables_exist()` — All 7 tables created
- `test_rls_policies_work()` — Row-level security enforced
- `test_foreign_keys()` — Constraints work
- `test_indexes_exist()` — Performance indexes in place
- `test_migration_applies()` — Schema migrations work

**Status:** 🔴 NOT TESTED

---

## SUMMARY

| Category | Files | Tests Needed | Status |
|----------|-------|-------------|--------|
| Backend Critical Path | 8 | 60+ | 🔴 1% |
| Context Engine (8 tools) | 13 | 80+ | 🔴 5% |
| Reviewer Intelligence | 6 | 30+ | 🔴 0% |
| Models | 7 | 40+ | 🟡 30% |
| Other Backend | 30+ | 50+ | 🔴 5% |
| **Backend Total** | **64** | **260+** | **🔴 8%** |
| Frontend Critical | 5 | 40+ | 🔴 0% |
| Pages | 10 | 50+ | 🔴 0% |
| Components | 40+ | 100+ | 🔴 0% |
| **Frontend Total** | **55** | **190+** | **🔴 0%** |
| Database | 1 | 20+ | 🔴 0% |
| **TOTAL** | **120+** | **470+** | **🔴 3%** |

---

## TESTING PHASES (Sequential)

### Phase A: Backend Critical Path (1-2 days)
Write tests for: simulations.py, simulator.py, persona_generator.py, aggregator.py, auth, uploads, businesses, db/client  
→ Make tests pass → Verify integration

### Phase B: Context Engine (1-2 days)
Write tests for: orchestrator, filter, all 8 tools, realtime_intelligence, location_profiler  
→ Make tests pass → Verify tools wired into _run_pipeline

### Phase C: Reviewer Intelligence + Models (1 day)
Write tests for: all 6 reviewer modules, all Pydantic models  
→ Make tests pass → Verify integration

### Phase D: Frontend Critical (1-2 days)
Write tests for: api.ts, ChatInterface, BusinessProfileForm, Dashboard, SimulationPanel  
→ Make tests pass → Run app, manually verify flows

### Phase E: Frontend Pages + Components (2-3 days)
Write tests for: all page components, all UI components  
→ Make tests pass

### Phase F: Database (0.5 days)
Write tests for: schema, migrations, RLS policies, indexes  
→ Make tests pass

---

## THEN: Production-Ready Implementation (Phases 0-6)

Once retroactive testing complete:
- All existing code has test coverage
- All existing code verified wired correctly
- Missing integration points identified
- Missing implementations identified

THEN: Proceed with the full TDD Plan (Phases 0-6) for all remaining work.

---

## Rule Going Forward

**No feature is "done" without:**
1. ✅ Tests written (happy path + errors + edge cases)
2. ✅ Tests passing (100%)
3. ✅ Integration verified (grep for call sites, manual smoke test)
4. ✅ Documented in BUILD_STATUS.md
5. ✅ Status file reflects actual test results, not opinions
