# Murmur -- Full System Audit
# Generated: 2026-04-07
# Read CLAUDE.md and missing.md before starting

## HOW TO RUN THIS AUDIT

Work through each section sequentially. For each check:
- Read the file referenced
- Verify the specific condition
- Mark the result

Markers:
- PASS: Working correctly
- WARN: Works but has issues (fix immediately if small, log to missing.md if large)
- FAIL: Broken or missing (log to missing.md with priority)
- IDEA: Not broken but could be improved (log to missing.md as LOW)

Rules:
1. Never assume -- always trace from frontend button to backend DB write
2. Fix small issues (typos, missing imports, unused vars) immediately
3. Log large issues to missing.md with exact file path and description
4. Test with real API calls where possible (curl the endpoint)
5. Read every file referenced -- do not skip

## MISSING.MD FORMAT

For each issue found, append to missing.md:

```
### [PRIORITY] [Short title]
**File:** [exact path]
**Issue:** [what is wrong]
**Fix:** [what needs to happen]
**Depends on:** [any blockers]
```

---

## SECTION 1: AUTHENTICATION & MIDDLEWARE

### 1.1 Supabase Client Setup
**File:** `frontend/src/lib/supabase/client.ts`
- [ ] File exists and exports `createClient()`
- [ ] Uses `createBrowserClient` from `@supabase/ssr`
- [ ] Reads `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**File:** `frontend/src/lib/supabase/server.ts`
- [ ] File exists and exports `createClient()`
- [ ] Uses `createServerClient` from `@supabase/ssr`
- [ ] Calls `cookies()` (synchronous for Next.js 14 -- NOT `await cookies()`)

**File:** `frontend/src/lib/supabase/middleware.ts`
- [ ] Exports `updateSession(request)`
- [ ] Uses `getSession()` (not `getUser()` -- network call would hang middleware)
- [ ] Public routes list includes: `/`, `/login`, `/signup`, `/auth/*`
- [ ] Unauthenticated users on protected routes redirect to `/login`
- [ ] Authenticated users on `/login` or `/signup` redirect to `/app`

**File:** `frontend/src/middleware.ts`
- [ ] Calls `updateSession(request)`
- [ ] Matcher excludes `_next/static`, `_next/image`, `favicon.ico`, image files

### 1.2 Backend Auth Dependency
**File:** `backend/auth/dependencies.py`
- [ ] `get_current_user_id(request)` extracts Bearer token from Authorization header
- [ ] Calls `db.auth.get_user(token)` to verify
- [ ] Returns UUID on success, raises 401 on failure

### 1.3 Auth Flow Integration
- [ ] `POST /api/businesses/` requires auth (uses `Depends(get_current_user_id)`)
- [ ] `GET /api/businesses/` requires auth and scopes by user_id
- [ ] `POST /api/simulations/` requires auth and verifies business ownership
- [ ] `GET /api/simulations/` requires auth and only returns user's simulations
- [ ] CRM routes require auth
- [ ] Survey routes do NOT require auth (they're used during onboarding)
- [ ] `curl -s http://localhost:8001/api/businesses/` returns 401 without token

---

## SECTION 2: SIGNUP / LOGIN / ONBOARDING FLOW

### 2.1 Signup Page
**File:** `frontend/src/app/signup/page.tsx`
- [ ] Email and password fields present
- [ ] Calls `supabase.auth.signUp({ email, password })`
- [ ] On success shows "Check your email" confirmation
- [ ] Link back to `/login` present
- [ ] Error state displays error message

### 2.2 Auth Callback
**File:** `frontend/src/app/auth/callback/route.ts`
- [ ] Reads `code` from URL search params
- [ ] Calls `supabase.auth.exchangeCodeForSession(code)`
- [ ] Redirects to `/app` on success
- [ ] Redirects to `/login` on failure

### 2.3 Login Page
**File:** `frontend/src/app/login/page.tsx`
- [ ] Email and password fields present
- [ ] Calls `supabase.auth.signInWithPassword({ email, password })`
- [ ] On success calls `listBusinesses()` to check if user has a business
- [ ] If no businesses -> redirects to `/onboarding`
- [ ] If businesses exist -> redirects to `/app`
- [ ] Error state displays error message

### 2.4 Onboarding Page
**File:** `frontend/src/app/onboarding/page.tsx`
- [ ] Renders `EnrichedSurvey` component
- [ ] On submit calls `createBusiness(data)`
- [ ] `createBusiness` sends POST to `/businesses/` with auth token
- [ ] On success redirects to `/app`
- [ ] Error state displays error message

### 2.5 App Home Business Check
**File:** `frontend/src/app/app/page.tsx`
- [ ] On mount calls `listBusinesses()`
- [ ] If no businesses -> redirects to `/onboarding`
- [ ] If businesses exist -> shows dashboard with stats
- [ ] Stats are fetched from `listSimulations()` and `listContacts()` (both types)

---

## SECTION 3: BUSINESS PROFILE (SETTINGS)

### 3.1 Settings Page Load
**File:** `frontend/src/app/app/settings/page.tsx`
- [ ] On mount calls `listBusinesses()` and loads first business
- [ ] All existing fields populate from business object (name, type, description, etc.)
- [ ] New fields populate: opening_hours, social URLs, location_settings, etc.
- [ ] Page scrolls (layout uses `overflow-y-auto`, not `overflow-hidden`)

### 3.2 Settings Page Save
- [ ] "Save all changes" button calls `updateBusiness(business.id, data)`
- [ ] `updateBusiness` sends PUT to `/businesses/{id}` with auth token
- [ ] Backend `_business_to_row` packs extra fields into metadata JSONB
- [ ] Backend `_row_to_business` unpacks all fields from metadata
- [ ] After save, business object updates in state
- [ ] "All changes saved" confirmation appears

### 3.3 URL Autofill
- [ ] "Find & auto-fill" button calls `researchBusiness(url)`
- [ ] Backend `POST /survey/research-business` calls Google Places API
- [ ] Results shown in confirmation card with checkmarks/crosses
- [ ] "Apply these fields" button fills form fields
- [ ] URL-like values are NOT applied as business name (filtered in backend)

### 3.4 Address Autocomplete
- [ ] Address search input calls `placeAutocomplete(query)` on type (3+ chars)
- [ ] Backend `POST /survey/place-autocomplete` calls Google Places autocomplete API
- [ ] Suggestions dropdown appears below input
- [ ] Selecting a suggestion calls `placeDetails(placeId)`
- [ ] Backend `POST /survey/place-details` fetches structured address
- [ ] Address fields auto-fill: street, number, postcode, city, neighbourhood, country

### 3.5 AI Generate Buttons
- [ ] Description "Generate" button calls `generateDescription({name, type, location, years_open})`
- [ ] Backend `POST /survey/generate-description` calls Claude API
- [ ] Generated text appears in textarea
- [ ] Customer description "Generate" button calls `generateCustomerDescription({...})`
- [ ] Backend `POST /survey/generate-customer-description` calls Claude API

### 3.6 Business Type Dropdown
- [ ] Dropdown uses `<optgroup>` elements for categories
- [ ] All categories present: Food & Drink, Health & Wellness, Retail, Services, Hospitality, Other
- [ ] Selected value saves correctly to type field

### 3.7 Opening Hours Grid
- [ ] 7 rows (Mon-Sun) with checkbox, opens time, closes time
- [ ] Time dropdowns show 30-minute increments (00:00 to 23:30)
- [ ] Unchecked days disable time dropdowns
- [ ] "Copy Mon to all weekdays" button copies Mon hours to Tue-Fri

### 3.8 New Fields Backend Wiring
**CRITICAL CHECK -- from missing.md:**
- [ ] `location_settings` field exists in BusinessCreate Pydantic model
- [ ] `area_draws` field exists in BusinessCreate Pydantic model
- [ ] `customer_transport` field exists in BusinessCreate Pydantic model
- [ ] `has_parking` field exists in BusinessCreate Pydantic model
- [ ] `first_visit_reasons` field exists in BusinessCreate Pydantic model
- [ ] `seasonal_patterns` field exists in BusinessCreate Pydantic model
- [ ] `customer_community` field exists in BusinessCreate Pydantic model
- [ ] `opening_hours` field exists in BusinessCreate Pydantic model
- [ ] `google_business_url` field exists in BusinessCreate Pydantic model
- [ ] `tripadvisor_url` field exists in BusinessCreate Pydantic model
- [ ] `instagram_url` field exists in BusinessCreate Pydantic model
- [ ] `facebook_url` field exists in BusinessCreate Pydantic model
- [ ] `prior_change_types` field exists in BusinessCreate Pydantic model
- [ ] `prior_change_went` field exists in BusinessCreate Pydantic model
- [ ] `anything_else` field exists in BusinessCreate Pydantic model
- [ ] All 15 fields appear in `_row_to_business` converter
- [ ] All 15 fields appear in `Business` TypeScript interface
- [ ] All 15 fields appear in `BusinessCreate` TypeScript interface
- [ ] All 15 fields included in `handleSave()` data object
- [ ] All 15 fields loaded in `useEffect` from business object
- [ ] Saving and refreshing preserves values for all 15 fields

---

## SECTION 4: SIMULATION ENGINE

### 4.1 Create Simulation
**File:** `frontend/src/components/simulate2/ChatInterface.tsx`
- [ ] Submitting a question enters clarifying questions phase
- [ ] Clarifying questions are category-aware (price, hours, menu, loyalty, etc.)
- [ ] "Skip all" button skips clarifying and runs simulation immediately
- [ ] Answering all questions appends context to simulation question
- [ ] `createSimulation()` called with business_id, enriched question, persona_count
- [ ] Backend `POST /simulations/` creates simulation row in DB
- [ ] Backend verifies business ownership before creating simulation

### 4.2 Simulation Pipeline
**File:** `backend/api/routes/simulations.py`
- [ ] Pipeline runs as background task via `asyncio.create_task()`
- [ ] Step 0: Context gathering runs if `CONTEXT_ENABLED=true`
- [ ] Step 0.5: Reviewer intelligence runs if `GOOGLE_PLACES_API_KEY` set
- [ ] Step 1: Persona generation via `generate_personas()`
- [ ] Step 2: Persona interviews via `run_simulation()` with semaphore
- [ ] Step 3: Aggregation via `aggregate_responses()`
- [ ] Step 4: Impact estimation via `estimate_impact()`
- [ ] Step 5: Caveat generation via `generate_caveats()`
- [ ] Each step updates simulation status in DB via `_update_sim()`
- [ ] Context, caveats, reviewer_intel, impact_data saved as JSONB columns
- [ ] Personas saved to `personas` table
- [ ] Responses saved to `persona_responses` table
- [ ] Result saved to `simulation_results` table
- [ ] On failure: status set to FAILED, error_message saved

### 4.3 SSE Streaming
**File:** `backend/api/routes/simulations.py`
- [ ] `GET /simulations/{id}/stream` returns SSE stream
- [ ] Events emitted: progress (with phase, step, timestamp)
- [ ] Final event: "done" or "timeout"
- [ ] Queue cleaned up in finally block (`await queue.put(None)`)

### 4.4 Progress Polling
**File:** `frontend/src/components/simulate2/ChatInterface.tsx`
- [ ] Polls `GET /simulations/{id}/progress` every 3 seconds
- [ ] Updates UI with current step text
- [ ] On status "completed": fetches result, responses, caveats
- [ ] On status "failed": shows error message
- [ ] On completion: calls `onSimulationComplete` callback

### 4.5 Results Display
- [ ] Verdict badge renders with correct color (proceed/caution/avoid/test_first)
- [ ] Summary text displays
- [ ] Recommendation text displays
- [ ] Customer voices show up to 4 persona responses with sentiment coloring
- [ ] Caveats section displays if caveats returned from API
- [ ] Confidence reasoning displays as fallback if no caveats

### 4.6 Simulation Read Endpoints
- [ ] `GET /simulations/{id}` returns simulation metadata
- [ ] `GET /simulations/{id}/personas` returns PersonaProfile list from DB
- [ ] `GET /simulations/{id}/responses` returns persona_responses from DB
- [ ] `GET /simulations/{id}/result` returns simulation_results from DB
- [ ] `GET /simulations/{id}/context` returns context_data JSONB from simulations table
- [ ] `GET /simulations/{id}/caveats` returns caveats JSONB from simulations table
- [ ] `GET /simulations/{id}/reviewer-intelligence` returns reviewer_intel JSONB
- [ ] `GET /simulations/{id}/impact` returns impact_data JSONB
- [ ] `GET /simulations/` returns all simulations for user's businesses

---

## SECTION 5: CRM -- CONTACTS

### 5.1 Customer List Page
**File:** `frontend/src/app/app/customers/page.tsx`
- [ ] On mount calls `listContacts({ contact_type: "customer" })`
- [ ] Table renders with Name, Title, Email, Health, Twin columns
- [ ] Search input filters by name (client-side)
- [ ] Filter buttons work: All, Has Twin, No Twin
- [ ] "+ Add customer" button navigates to `/app/customers/new`
- [ ] Empty state shows with link to add first customer
- [ ] Clicking a row opens profile panel on right

### 5.2 Customer Profile Panel
- [ ] Shows contact info: email, phone, LinkedIn, location, type, style
- [ ] Activity tab shows about section and signals
- [ ] Twin tab shows twin status and query interface (if twin active)
- [ ] Twin tab shows "Upload files" prompt (if no twin)
- [ ] Files tab renders FileUploadZone component
- [ ] "Ask Twin" button calls `askTwin(contactId, question)`
- [ ] Backend `POST /crm/twin/query` verifies contact ownership
- [ ] Backend queries latest `crm_correspondence.extracted_signals`
- [ ] Backend calls Claude to generate answer
- [ ] Backend stores query in `crm_twin_queries`
- [ ] Response appears in query list

### 5.3 Add Customer Form
**File:** `frontend/src/app/app/customers/new/page.tsx`
- [ ] AccuracyBar renders and updates live as fields are filled
- [ ] 7 collapsible sections present (Who, Background, Relationship, Personality, Contact, Notes, Files)
- [ ] "Save customer" button calls `createContact()` with contact_type "customer"
- [ ] Backend `POST /crm/contacts/` requires auth
- [ ] Backend checks `crm_access` tier gate (hardcoded to Connect)
- [ ] Contact saved to `crm_contacts` table
- [ ] After save, savedId enables file upload section
- [ ] Completeness score correctly computes from CUSTOMER_FIELD_WEIGHTS

### 5.4 File Upload
**File:** `frontend/src/components/forms/FileUploadZone.tsx`
- [ ] 5 source-specific upload buttons (WhatsApp, Email, Meeting, Notes, Purchase)
- [ ] General drop zone present
- [ ] Upload calls `POST /crm/twin/upload/{contactId}` with multipart form
- [ ] Backend reads file into memory, processes via `process_correspondence()`
- [ ] Backend deletes raw text immediately (`del raw_text`, `del raw_bytes`)
- [ ] Backend updates contact: has_twin=true, twin_confidence, twin_corpus_size
- [ ] Backend stores correspondence record (no raw content)
- [ ] Backend runs signal detection and stores alerts
- [ ] Success message appears with message count and confidence

---

## SECTION 6: CRM -- VENDORS

### 6.1 Vendor List Page
**File:** `frontend/src/app/app/vendors/page.tsx`
- [ ] On mount calls `listContacts({ contact_type: "vendor" })`
- [ ] Same structure as customers but with vendor-specific columns (Company, Role)
- [ ] "+ Add vendor" navigates to `/app/vendors/new`

### 6.2 Add Vendor Form
**File:** `frontend/src/app/app/vendors/new/page.tsx`
- [ ] 7 vendor-specific sections present (Who, Company, Contract, Performance, Dynamics, Market, Files)
- [ ] Vendor-specific fields: category, supply, company size, client importance
- [ ] Commercial fields: tenure, annual spend, payment terms, contract type, alternatives
- [ ] Performance: star ratings, price raise history (conditional), negotiation history (conditional)
- [ ] Relationship: communication style chips, difficult conversation style
- [ ] AccuracyBar uses VENDOR_FIELD_WEIGHTS
- [ ] "Save vendor" calls `createContact()` with contact_type "vendor"

---

## SECTION 7: CRM -- ORGANISATIONS (Legacy /crm pages)

### 7.1 CRM Pages Exist and Load
- [ ] `/crm` page loads without error
- [ ] `/crm/contacts` page loads without error
- [ ] `/crm/contacts/[id]` page loads without error
- [ ] `/crm/organisations` page loads without error
- [ ] `/crm/organisations/[id]` page loads without error

---

## SECTION 8: DASHBOARD & REPORTS

### 8.1 Dashboard
**File:** `frontend/src/app/dashboard/page.tsx`
- [ ] Lists all simulations via `listSimulations()`
- [ ] Status badges render with correct colors
- [ ] Clicking a simulation navigates to `/simulate?businessId=...&simulationId=...`

### 8.2 Reports Page
**File:** `frontend/src/app/app/reports/page.tsx`
- [ ] Simulation History tab shows completed simulations in table
- [ ] Accuracy tab shows backtest stats
- [ ] Usage tab shows real counts (simulations, customers, vendors, twins)

### 8.3 Intelligence Page
**File:** `frontend/src/app/app/intelligence/page.tsx`
- [ ] Loads all contacts and derives customer/vendor/at-risk/strong/neutral counts
- [ ] Portfolio health bars render with correct proportions
- [ ] "Needs attention" section shows at-risk contacts

---

## SECTION 9: LANDING PAGE & NAVIGATION

### 9.1 Landing Page Links
**File:** `frontend/src/app/page.tsx`
- [ ] "Sign in" button links to `/login`
- [ ] "Create an account" button links to `/signup`

**File:** `frontend/src/components/landing2/Navigation.tsx`
- [ ] "Sign in" links to `/login`
- [ ] "Try free" links to `/signup`
- [ ] Mobile menu has same links

**File:** `frontend/src/components/landing2/FinalCTA.tsx`
- [ ] "Create an account" links to `/signup`

### 9.2 App Navigation (TopNav)
**File:** `frontend/src/components/shell/TopNav.tsx`
- [ ] All tab links work: Home, Simulate, Customers, Vendors, Intelligence, Reports
- [ ] Settings gear links to `/app/settings`
- [ ] "Sign out" button calls `supabase.auth.signOut()` and redirects to `/login`

---

## SECTION 10: DATABASE TABLES

### 10.1 Core Tables Exist
- [ ] `businesses` table exists with correct columns
- [ ] `simulations` table exists with context_data, caveats, reviewer_intel, impact_data JSONB columns
- [ ] `personas` table exists
- [ ] `persona_responses` table exists
- [ ] `simulation_results` table exists
- [ ] `business_uploads` table exists
- [ ] `real_outcomes` table exists

### 10.2 CRM Tables Exist
- [ ] `crm_contacts` table exists with all migration_003 columns
- [ ] `crm_organisations` table exists
- [ ] `crm_correspondence` table exists
- [ ] `crm_twin_queries` table exists
- [ ] `crm_signal_alerts` table exists

### 10.3 RLS Enabled
- [ ] `businesses` has RLS enabled with user_id = auth.uid() policy
- [ ] `simulations` has RLS enabled
- [ ] `personas` has RLS enabled
- [ ] `persona_responses` has RLS enabled
- [ ] `simulation_results` has RLS enabled
- [ ] `real_outcomes` has RLS enabled
- [ ] `crm_contacts` has RLS enabled with user_id = auth.uid() policy
- [ ] `crm_organisations` has RLS enabled
- [ ] `crm_correspondence` has RLS enabled
- [ ] `crm_twin_queries` has RLS enabled
- [ ] `crm_signal_alerts` has RLS enabled

### 10.4 Triggers
- [ ] `businesses` has `updated_at` trigger
- [ ] `crm_contacts` has `updated_at` trigger
- [ ] `crm_organisations` has `updated_at` trigger

---

## SECTION 11: ENVIRONMENT VARIABLES

### 11.1 Backend (.env)
- [ ] `ANTHROPIC_API_KEY` is set and non-empty
- [ ] `SUPABASE_URL` is set and starts with `https://`
- [ ] `SUPABASE_KEY` is set (anon key)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` is set
- [ ] `REDIS_URL` is set (default: redis://localhost:6379)
- [ ] `GOOGLE_PLACES_API_KEY` is set (optional but needed for context/survey)
- [ ] `BRAVE_SEARCH_API_KEY` is set (optional)

### 11.2 Frontend (.env.local)
- [ ] `NEXT_PUBLIC_API_URL` is set to `http://localhost:8001/api`
- [ ] `NEXT_PUBLIC_SUPABASE_URL` is set
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` is set

### 11.3 .env.example
- [ ] `backend/.env.example` exists with all required vars documented

---

## LOGIC QUALITY CHECKS

### LQ1: Simulation Accuracy
- [ ] Persona count from request is passed through to `generate_personas()`
- [ ] Context narrative is passed to all 3 phases (generation, interview, aggregation)
- [ ] Caveats are always generated (not_causation and self_selection are always-on)
- [ ] Impact estimator uses confidence intervals, not point estimates alone
- [ ] Decision framework follows 3-outcome logic (proceed/avoid/test_first)

### LQ2: Persona Diversity
- [ ] Manifest path (when review data available) enforces segment distribution
- [ ] Silent majority represents 55-70% of generated personas
- [ ] Persona prompts include anti-bias instructions
- [ ] At least one frustrated/negative persona is always generated

### LQ3: Twin Privacy
- [ ] Raw correspondence text is deleted immediately after processing
- [ ] Only anonymised patterns are stored in `crm_correspondence.extracted_signals`
- [ ] Individual review content is never stored (only aggregate patterns)
- [ ] `confirm_rights` is required for correspondence upload

### LQ4: Error Handling
- [ ] Simulation pipeline catches exceptions and sets status to FAILED
- [ ] Context engine never raises (graceful degradation)
- [ ] Individual context tools have 30s timeouts
- [ ] Total context gathering has 90s hard timeout
- [ ] 60% minimum persona success threshold enforced

### LQ5: Completeness Scoring
- [ ] Customer weights sum approximately to 100
- [ ] Vendor weights sum approximately to 100
- [ ] Milestone messages update correctly at 25%, 50%, 75%, 90% thresholds
- [ ] "Next improvement" points to highest-weight empty field

---

## FINAL OUTPUT FORMAT

After completing every check, update missing.md:

### AUDIT SUMMARY
PASS: [count]
WARN: [count]
FAIL: [count]
IDEA: [count]

### CRITICAL (fix before any user sees this)
[list]

### HIGH PRIORITY (fix this week)
[list]

### MEDIUM (fix before launch)
[list]

### LOW (post-launch)
[list]

### RECOMMENDED NEXT SESSION
[What to tackle next based on audit findings]
