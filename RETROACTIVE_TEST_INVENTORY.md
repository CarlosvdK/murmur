# Retroactive Test Inventory — Complete Coverage Map

**Status**: Full test suite being written (Path A: Complete all tests before implementation)

## Written ✅ (~300 tests)

- [x] backend/tests/test_realtime_intelligence.py (19 tests)
- [x] backend/tests/test_location_profiler.py (10 tests)
- [x] backend/tests/test_weather_tool.py (10 tests)
- [x] backend/tests/test_auth_dependencies.py (11 tests)
- [x] backend/tests/test_db_client.py (3 tests)
- [x] backend/tests/test_businesses_routes.py (13 tests)
- [x] backend/tests/test_swarm_simulator.py (15 tests)
- [x] backend/tests/test_swarm_persona_generator.py (19 tests)
- [x] backend/tests/test_swarm_aggregator.py (18 tests)
- [x] backend/tests/test_uploads_routes.py (13 tests)
- [x] backend/tests/test_context_tools_comprehensive.py (30+ tests for 7 tools)
- [x] backend/tests/test_reviewer_intelligence_comprehensive.py (20+ tests)
- [x] backend/tests/test_models_comprehensive.py (25+ tests)

**Total written: ~160+ tests covering core functionality**

---

## Remaining to Write (~300+ tests)

### CRITICAL PATH (Must write)

#### Backend Routes (20+ tests)
- `test_simulations_routes.py`
  - POST /simulations → creates simulation
  - GET /simulations/{id} → retrieves simulation  
  - GET /simulations/{id}/stream → SSE stream works
  - POST /simulations/{id}/outcome → records real outcome
  - GET /simulations/accuracy-stats → calculates accuracy %
  
- `test_survey_routes.py`
  - POST /survey/{business_id} → validates survey
  - GET /survey/{business_id} → retrieves survey

- `test_crm_routes.py` (4 route files, 30+ tests)
  - Contact CRUD operations
  - Organisation CRUD operations
  - Twin creation/retrieval
  - Correspondence processing

#### Core Swarm Engine (15+ tests)
- `test_swarm_orchestrator.py`
  - Claude decides which tools to run
  - Tools run in parallel
  - 30s timeout per tool, 90s total
  - Graceful degradation when tools fail

- `test_swarm_filter.py`
  - Skips filter for <3 tools
  - Summarizes for 4+ tools
  - Preserves relevance

- `test_swarm_caveats.py` (10+ tests already exist but need expansion)
  - RTM warning generated for extreme recent performance
  - Novelty effect caveat generated
  - Adherence gap caveat for loyalty programs
  - Self-selection caveat (always present)
  - Small sample caveat when persona count < 12
  - Cherry-pick warning for standout voices
  - Not causation caveat (always present)
  - Profile quality caveat when description vague

- `test_swarm_question_interpreter.py`
  - Extracts entity (product, price, feature, etc.)
  - Identifies if A/B comparison question
  - Detects extreme scenario framing

- `test_swarm_bias_correction.py`
  - Anti-positivity bias applied to persona responses
  - Herd mentality prevention

#### Context Engine (20+ tests)
- `test_context_orchestrator.py`
  - Decides which tools to call based on business/question
  - Runs tools in parallel with semaphore
  - Timeouts handled
  - Returns BusinessContext

- `test_context_filter.py`
  - Result filtering/summarization
  - Relevance preservation

- `test_context_engine.py` (integration)
  - Full gather_context pipeline
  - Tool orchestration
  - Error handling

- `test_context_profile_builder.py`
  - Business profile enrichment

- `test_context_vector_rag.py`
  - Vector search from research corpus
  - Semantic Scholar integration

- `test_context_rag_selector.py`
  - RAG relevance scoring

#### Utilities & Supporting (20+ tests)
- `test_context_progress.py`
  - Progress tracking
  - SSE message formatting

- `test_swarm_research_override.py`
  - Research corpus selection/injection

- `test_swarm_persona_archetype.py` (partial tests exist)
  - Archetype caching
  - Reuse logic

- `test_impact_estimator.py`
  - Impact calculations
  - Confidence scoring

- `test_survey_feature_extractor.py`
  - Feature extraction from survey

- `test_survey_rag_builder.py`
  - RAG building from survey

- `test_research_corpus_loader.py`
  - Paper loading from disk
  - Metadata extraction

- `test_research_quality_scorer.py`
  - Paper quality/relevance scoring

- `test_research_corpus_scraper.py`
  - Paper fetching from sources
  - Metadata parsing

- `test_ml_training_data.py`
  - Training data preparation

- `test_ml_calibration_model.py`
  - Calibration model training/inference

- `test_ml_outcome_learner.py`
  - Learning from real outcomes

- `test_crm_correspondence_processor.py`
  - Email/correspondence parsing
  - Sentiment extraction

- `test_crm_signal_detector.py`
  - Business signal detection from conversations

- `test_crm_twin_engine.py`
  - Digital twin generation
  - Correspondence simulation

---

### FRONTEND TESTS (100+ tests)

#### API Client (20+ tests)
- `frontend/src/lib/api.test.ts`
  - createBusiness()
  - updateBusiness()
  - listBusinesses()
  - createSimulation()
  - getSimulationProgress()
  - getSimulationResult()
  - uploadFile()
  - submitRealOutcome()
  - getAccuracyStats()
  - Error handling
  - Auth token passing
  - Retry logic

#### Pages (30+ tests)
- `frontend/src/app/page.test.tsx` (landing)
- `frontend/src/app/login/page.test.tsx`
- `frontend/src/app/signup/page.test.tsx`
- `frontend/src/app/onboarding/page.test.tsx`
  - Step progression
  - Validation per step
  - Form submission
  - Next/back button logic

- `frontend/src/app/app/page.test.tsx` (dashboard)
  - Loads simulations
  - Empty state
  - Recent activity list
  - Outcome submission UI
  - Accuracy stats display

- `frontend/src/app/app/simulate/page.test.tsx`
  - Question input
  - Simulation start
  - Progress polling
  - Result display

- `frontend/src/app/dashboard/page.test.tsx`
- `frontend/src/app/crm/page.test.tsx` (and subpages)

#### Components (50+ tests)
- `frontend/src/components/questionnaire/BusinessProfileForm.test.tsx` (25+ tests)
  - Step 0: name, type, description validation
  - Step 1: customer_description validation
  - Step 2: all fields validation
  - Min/max length checks
  - Error messages on blur
  - Character count display
  - Form submission
  - Discard warning

- `frontend/src/components/simulate2/ChatInterface.test.tsx` (15+ tests)
  - Starts simulation
  - Polls progress
  - Shows result
  - Shows error after 3 failures
  - Timeout after 8 minutes
  - Friendly error messages
  - Exponential backoff retry
  - SSE fallback

- `frontend/src/components/simulation/SimulationPanel.test.tsx` (10+ tests)
  - Opens EventSource
  - Receives progress
  - Receives done event
  - Handles error
  - Shows timeout message
  - Closes connection
  - Updates persona badges

- `frontend/src/components/results/ResultsReport.test.tsx`
  - Displays summary
  - Shows themes
  - Shows outlier voices
  - Shows confidence
  - Shows caveats
  - Shows recommendation

- `frontend/src/components/results/CaveatCard.test.tsx`
  - Displays caveat text
  - Shows caveat type icon
  - Expandable/collapsible

- `frontend/src/components/simulation/PersonaCard.test.tsx`
  - Shows persona name
  - Shows persona age
  - Shows persona traits
  - Shows status badge

- `frontend/src/components/shell/TopNav.test.tsx`
  - Shows user menu
  - Logout works
  - Navigation links work

- Other component tests (20+):
  - ProgressTimeline
  - FileUploadZone
  - FormField
  - CIChart
  - EvidenceTab
  - ImpactPanel
  - PersonaResponseCard
  - AccuracyBar
  - etc.

---

## Testing Strategy

1. **Write all tests first** (what you see above)
2. **Run all tests** → see baseline: # passed, # failed, # errors
3. **Fix implementations** to make tests pass
4. **Verify all tests green** before shipping

## Test Organization

```
backend/tests/
├── test_realtime_intelligence.py ✅
├── test_location_profiler.py ✅
├── test_weather_tool.py ✅
├── test_auth_dependencies.py ✅
├── test_db_client.py ✅
├── test_businesses_routes.py ✅
├── test_swarm_simulator.py ✅
├── test_swarm_persona_generator.py ✅
├── test_swarm_aggregator.py ✅
├── test_uploads_routes.py ✅
├── test_context_tools_comprehensive.py ✅
├── test_reviewer_intelligence_comprehensive.py ✅
├── test_models_comprehensive.py ✅
├── test_simulations_routes.py  (TO WRITE)
├── test_survey_routes.py  (TO WRITE)
├── test_crm_routes.py  (TO WRITE)
├── test_context_orchestrator.py  (TO WRITE)
├── test_context_filter.py  (TO WRITE)
├── test_swarm_orchestrator.py  (TO WRITE)
├── test_swarm_caveats_comprehensive.py  (TO WRITE)
├── test_swarm_question_interpreter.py  (TO WRITE)
├── ... (20+ more files)

frontend/src/lib/
├── api.test.ts  (TO WRITE)

frontend/src/app/**/
├── *.test.tsx  (TO WRITE - 10+ page tests)

frontend/src/components/*/
├── *.test.tsx  (TO WRITE - 40+ component tests)
```

## Coverage Target

- **Backend**: 300+ tests across 40+ files
- **Frontend**: 100+ tests across 50+ files
- **Total**: 400+ comprehensive tests

## Current Progress

- ✅ Phase 1 context tool tests (19+10+10 = 39 tests)
- ✅ Auth, DB, Business routes (11+3+13 = 27 tests)
- ✅ Core swarm (15+19+18 = 52 tests)
- ✅ Uploads (13 tests)
- ✅ All context tools (30+ tests)
- ✅ Reviewer intelligence (20+ tests)
- ✅ Models (25+ tests)

**Total: ~160+ tests written**

**Remaining: ~240+ tests to write**

---

## Next Steps

1. Continue writing remaining 240+ test files
2. Run full test suite
3. Document all failures/errors
4. Fix implementations to make tests pass
5. Achieve 95%+ test pass rate
6. Then: Implement Phases 1-6 with tests
