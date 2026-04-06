# Murmur — Customer Simulation Platform

## What Is This?

Murmur is a customer simulation platform for small businesses. A business owner describes their business and customers, asks a question ("What if I raised prices 15%?"), and we generate a swarm of synthetic customer personas tailored to that specific business, run the question through them, and return plain-English feedback that feels like hearing from real customers.

**Target user**: Small business owners (restaurants, barbers, grocery stores) with no data science background and no budget for market research.

**This is NOT** a traditional A/B testing tool. It is a customer insight engine that happens to support A/B-style comparison questions.

## Core Principles

These are non-negotiable. Every feature, prompt, and UI decision must respect them:

1. **Swarm is built fresh per business** — Personas are not generic. They are derived from what the business tells us about their customers. A taco truck's personas are completely different from a hair salon's.
2. **Output must feel human** — "Maria, 34, Friday regular, says she'd accept the price increase but would complain about it" — NOT "67% acceptance rate". Individual voices first, aggregation second.
3. **Always show confidence caveats** — We reduce risk, we don't replace judgment. Every output includes honesty about uncertainty.
4. **Small business owners are the user** — No jargon, no stats, no complexity. If a user needs to Google something to understand the output, we failed.
5. **Logging is non-negotiable from day one** — Every swarm run stores: inputs, persona reasoning, outputs, and eventually real outcomes for backtesting. No exceptions.

## Tech Stack

| Layer | Technology | Version/Notes |
|-------|-----------|---------------|
| Frontend | Next.js (App Router) | 14.x, TypeScript, Tailwind CSS |
| Backend | FastAPI | Python 3.11, async |
| Database | PostgreSQL via Supabase | Auth + DB + Storage |
| Queue | Redis + BullMQ | Async swarm job processing |
| AI | Anthropic Claude API | claude-sonnet-4-20250514 |
| Agent Framework | TBD | CAMEL-AI or direct Anthropic API |
| File Uploads | Supabase Storage | CSV, basic data files |
| Deploy (FE) | Vercel | |
| Deploy (BE) | Railway or Render | |

## Directory Structure

```
/
├── CLAUDE.md                  # This file — project context for Claude Code
├── ARCHITECTURE.md            # System design decisions and rationale
├── PROMPTS.md                 # All AI prompts, versioned
├── BACKTEST.md                # Backtesting strategy and methodology
├── frontend/
│   ├── app/
│   │   ├── (auth)/            # Login/signup (Supabase Auth)
│   │   ├── onboarding/        # Business setup questionnaire
│   │   ├── dashboard/         # Past simulations list
│   │   └── simulate/          # Main simulation interface
│   └── components/
│       ├── questionnaire/     # Step-by-step business profiler
│       ├── simulation/        # Live swarm progress UI
│       └── results/           # Output cards with persona voices
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── businesses.py  # Business profile CRUD
│   │   │   ├── simulations.py # Trigger + poll simulation jobs
│   │   │   └── uploads.py     # CSV/data file handling
│   │   └── main.py            # FastAPI app entry point
│   ├── swarm/
│   │   ├── persona_generator.py  # Build N personas from business profile
│   │   ├── simulator.py          # Run question through all personas
│   │   ├── aggregator.py         # Synthesise responses into output
│   │   └── prompts/              # Prompt template files
│   │       ├── persona_base.txt
│   │       ├── persona_interview.txt
│   │       └── aggregation.txt
│   ├── models/
│   │   ├── business.py
│   │   ├── simulation.py
│   │   └── persona.py
│   └── db/
│       └── schema.sql         # Full Postgres schema
└── docs/
    └── known_ab_tests.md      # Published A/B test results for backtesting
```

## How the Swarm Engine Works

### Step 1: Persona Generation
User provides: business description, customer description, location, optional data (CSV uploads).
System generates N personas (default 12-20) that represent the business's customer base.
Each persona has: name, age, visit frequency, spending habits, personality traits, relationship to the business.
Personas are diverse — not all happy, not all regulars, includes edge cases.

### Step 2: Simulation
The user's question is presented to each persona independently (no cross-contamination).
Each persona responds in character with: their reaction, reasoning, and a sentiment score.
Responses are generated in parallel via async API calls.

### Step 3: Aggregation
A separate aggregation prompt reads all persona responses and produces:
- A plain-English summary of the overall sentiment
- Key themes grouped by reaction type
- Notable outlier voices (the personas who had the strongest/most unusual reactions)
- A confidence assessment
- A recommendation with caveats

### Database Schema
See `backend/db/schema.sql` for the full schema. Key tables:
- `businesses` — Business profiles
- `simulations` — Each question asked
- `personas` — Generated personas per simulation
- `persona_responses` — Individual persona answers with reasoning
- `simulation_results` — Aggregated output
- `real_outcomes` — What actually happened (for backtesting)

## Reference Repos

These repos inform our architecture and approach:

1. **camel-ai/oasis** — Agent initialization patterns, Interview Action, parallel simulation
2. **camel-ai/camel** — ChatAgent class, RolePlaying, persona/system message construction, memory
3. **vincentkoc/synthetic-user-research** — Persona prompting, OCEAN personality model, summary aggregation
4. **666ghj/MiroFish** — Frontend UX flow inspiration only (questionnaire → simulation → report → chat). Do NOT copy their backend.

## Reviewer Intelligence System

Runs AFTER context gathering but BEFORE persona generation. Calibrates the swarm based on real review data + bias corrections + silent majority modelling.

### Research Constraints (non-negotiable)
1. Reviews represent <1% of customers (Alchemer). Treat as vocal minority signal.
2. Reviews are bimodally extreme (Karaman 2021). Compress tails, weight moderate centre.
3. Google underrepresents negative (Han & Anderson 2026). Apply upward correction.
4. Freeform LLM personas skew optimistic (NeurIPS 2025). Structured anchoring FIRST.
5. NEVER store individual reviewer profiles (GDPR). Aggregate patterns only.
6. Silent majority (55-70% of swarm) is most consequential (Gao et al. 2015).

### Pipeline
```
build_reviewer_intelligence(business, persona_count)
  1. extract_review_signals: Google Places aggregate patterns (no individual data stored)
  2. apply_bias_corrections: extremity + platform + silent majority corrections
  3. estimate_silent_majority: model who ISN'T in the reviews
  4. build_segments: 6 customer segments with calibrated proportions
  5. calibrate_personas: PersonaGenerationManifest with structured PersonaSpecs
```

### Customer Segments (always present)
- Silent Regulars (~28%): Come often, never review, most price-sensitive
- Silent Occasionals (~35%): Visit rarely, high switching risk
- Loyal Fans (~5%): Enthusiastic reviewers, overrepresented in perception
- Frustrated Customers (~3%): Bad experience reviewers, included for balance
- Tourists (~14%): Will not return regardless of pricing
- Value Seekers (~9%): Come specifically for affordability

### Persona Generation
When a manifest is available, persona_generator.py uses the constrained path:
- Each PersonaSpec has FIXED structured fields (age, income, visit_frequency, price_sensitivity)
- The LLM adds narrative detail WITHIN those constraints (name, backstory, habits)
- Anti-bias instructions prevent optimistic skew
- Silent majority personas (55-70%) have never written a review in their lives

### Modules (all in `backend/reviewer_intelligence/`)
| File | Purpose |
|------|---------|
| review_signal_extractor.py | Google Places aggregate pattern extraction |
| bias_corrector.py | Extremity + platform + silent majority corrections |
| silent_majority_estimator.py | Models who ISN'T in the reviews |
| customer_segment_builder.py | Builds 6 segments with proportions |
| persona_calibrator.py | Converts segments to PersonaGenerationManifest |
| __init__.py | Entry point: build_reviewer_intelligence() |

## Context Enrichment Engine

The context engine runs BEFORE persona generation. It gathers real-world intelligence to ground the swarm in reality.

### Pipeline
```
gather_context(business, question)
  1. Orchestrator: Claude decides which tools to run (1 API call)
  2. Agent Runner: runs tools in parallel (30s each, 90s total hard timeout)
  3. Relevance Filter: Claude distils results into narrative (skipped if <=3 tools)
  -> Returns BusinessContext with filtered_narrative string
```

### Tools (8 total, all in `backend/context/tools/`)
| Tool | API | Key Required? |
|------|-----|--------------|
| web_search | Brave Search | Yes (BRAVE_SEARCH_API_KEY) |
| google_places | Google Places (New) | Yes (GOOGLE_PLACES_API_KEY) |
| news_search | Brave News | Yes (BRAVE_SEARCH_API_KEY) |
| price_index | Eurostat / World Bank | No (free) |
| weather_trends | Open-Meteo | No (free) |
| demographic | World Bank | No (free) |
| review_analyzer | Google Places + Claude | Yes (GOOGLE_PLACES_API_KEY) |
| social_sentiment | Reddit | Yes (REDDIT_CLIENT_ID/SECRET) |

### Key Design Decisions
- **filtered_narrative is a plain text paragraph**, not structured JSON. Injected via `{{context_narrative}}` template variable.
- **Context flows into all 3 phases**: persona generation, persona interviews, and aggregation.
- **Orchestrator is intelligent**: it reasons about what matters for THIS business and THIS question. It selects 2-5 tools max.
- **Graceful degradation**: gather_context() NEVER raises. If everything fails, returns empty BusinessContext and the swarm proceeds with just the business profile.
- **SSE streaming**: real-time progress via `/simulations/{id}/stream` endpoint.
- **No emojis**: all progress messages are plain text.

## Architecture Patterns (from reference repos)

### From OASIS (camel-ai/oasis)
- **Semaphore pattern**: `asyncio.Semaphore(CONCURRENCY_LIMIT)` limits parallel Claude API calls. Used in `backend/swarm/simulator.py`.
- **Interview Action**: Each persona is interviewed independently via `asyncio.gather(*tasks, return_exceptions=True)`. Failures don't kill the whole simulation.
- **60% minimum threshold**: If fewer than 60% of personas succeed, the simulation fails rather than producing unreliable results.

### From CAMEL (camel-ai/camel)
- **System message construction**: Each persona gets a unique system message built from their profile (like CAMEL's ChatAgent). Template variables are injected from PersonaProfile.
- **Direct Anthropic API**: We chose raw `anthropic.AsyncAnthropic` over CAMEL's framework for simplicity and control. No dependency on CAMEL.

### From Synthetic-User-Research (vincentkoc)
- **OCEAN personality model**: Persona prompts use OCEAN-inspired plain-language traits for personality diversity.
- **Summary agent pattern**: Full transcript of persona responses fed to aggregation prompt (like their SummaryAgent).
- **Anti-bias**: Explicit instructions in persona prompts to avoid people-pleasing and herd mentality.

### From MiroFish (666ghj/MiroFish)
- **Step-by-step UI flow**: Onboarding → Simulation → Report (like their 5-step workflow).
- **Split panel layout**: Left panel shows progress timeline + persona grid, right panel shows responses and final report.
- **Status badges**: Color-coded (orange=running, green=done, red=failed) with animated dots.
- **Avatar circles**: First letter of persona name in colored circle (palette: orange, navy, purple, teal, red, coral).
- **Timeline with connecting lines**: Vertical dots + lines for progress steps.
- **Report sections**: Numbered (01, 02, 03) with collapsible content.
- **2-second polling**: Frontend polls `/simulations/{id}/progress` every 2s for live updates.

## Current Build Status

### Done
- [x] Project scaffolded with directory structure
- [x] CLAUDE.md, ARCHITECTURE.md, PROMPTS.md, BACKTEST.md created
- [x] Database schema designed with RLS policies
- [x] Known A/B tests collected for backtesting (10 cases)
- [x] FastAPI backend with API routes (businesses, simulations, uploads)
- [x] Swarm engine core: persona_generator.py, simulator.py, aggregator.py
- [x] Pydantic models for all entities
- [x] Next.js 14 frontend initialized with Tailwind + custom brand colors
- [x] MiroFish-style UI components: ProgressTimeline, PersonaCard, PersonaResponseCard, ResultsReport, BusinessProfileForm, SimulationPanel
- [x] Frontend pages: home, onboarding, simulate, dashboard
- [x] Frontend builds clean
- [x] A/B testing theory reference docs (6 topics from Uri Simonsohn lectures)
- [x] Caveat system (caveats.py) with 8 caveat types from A/B testing theory
- [x] Research scraper (391 papers across 5 categories)
- [x] Context enrichment engine with 8 tools (web_search, google_places, news_search, price_index, weather_trends, demographic, review_analyzer, social_sentiment)
- [x] Intelligent orchestrator (Claude-powered research planning)
- [x] Relevance filter (Claude-powered narrative synthesis, skips for small result sets)
- [x] SSE streaming endpoint for real-time progress
- [x] Context flows into all 3 swarm phases (generation, interview, aggregation)
- [x] Caveats wired into simulation pipeline and stored per simulation
- [x] Reviewer Intelligence System (6 modules: signal extractor, bias corrector, silent majority estimator, segment builder, persona calibrator, __init__)
- [x] Structured persona anchoring: manifest-constrained generation path in persona_generator.py
- [x] Reviewer-specific caveats (silent_majority_note, review_data_sparse, tourist_heavy, price_change_history)
- [x] Constrained persona prompt template (persona_from_spec.txt)

### Next
- [ ] Set up Supabase project (auth + db) and run schema.sql
- [ ] Replace in-memory stores with Supabase client in backend routes
- [ ] Add Supabase Auth to frontend
- [ ] Run backtesting eval against known A/B tests
- [ ] Add file upload parsing (CSV → business context)
- [ ] Add real_outcomes tracking in the dashboard

## Known Risks and Open Questions

1. **DECIDED — Agent framework**: Using direct Anthropic API with asyncio (not CAMEL-AI). Simpler, full control over prompts, no heavy dependency.
2. **DECIDED — Queue**: Using `arq` (Python async Redis queue) instead of BullMQ. Currently using `asyncio.create_task()` for dev; will migrate to arq for production.
3. **Persona count**: Starting with 15. Need to test accuracy vs cost tradeoff.
4. **Positive bias**: Research shows synthetic users tend to be overly positive and herd-like. Prompts include anti-bias instructions but untested.
5. **Rate limiting**: Semaphore set to 5 concurrent calls. May need adjustment based on API tier.
6. **Backtesting validity**: Our backtest cases are from large companies but our users are small businesses.

## A/B Testing Theory Reference

We have a comprehensive theory reference in `docs/ab-testing-theory/` distilled from Prof. Uri Simonsohn's "Thinking with Data" course. **Claude Code must consult these when writing prompts, caveats, or confidence logic.**

Key lessons that directly shape our product:

### From Topic 1 (How Wrong Can We Be)
- Every estimate = truth + error. Our simulation IS an estimate.
- Use the three-outcome decision framework: "do it", "don't", or "we can't tell"
- Never confuse statistical significance with practical significance

### From Topic 3 (P-Hacking)
- Don't cherry-pick dramatic persona responses — that's our version of p-hacking
- Standout voices are for illustration, not proof
- If a user runs the same question twice and gets different results, that's noise, not signal

### From Topic 4 (A/B Test Challenges) — CRITICAL FOR CAVEATS
- **Novelty effects**: Personas can't simulate the gap between stated preference and actual behavior
- **Self-selection**: Real customers choose to engage; our personas are forced to answer
- **Adherence gap**: "I'd use a loyalty card" ≠ actually using it
- **Sample dependence**: All personas share the same business profile — one biased input biases everything

### From Topic 5 (Regression to the Mean)
- Users often ask questions BECAUSE things are extreme ("sales are down, should I...")
- Even without changes, extreme performance naturally reverts to the mean
- We must warn users about this when we detect their question is triggered by extremes

### From Topic 6 (Causation vs Correlation)
- **Murmur CANNOT claim causation.** We simulate intentions, not causal effects.
- We must never say "this change WILL cause X" — only "customers like yours MIGHT react this way"
- The Facebook ad lesson: correlation between targeting and outcomes ≠ causation

## Confidence & Caveat System

Every simulation result MUST include contextual caveats drawn from the theory. The `backend/swarm/caveats.py` module generates these. Categories:

| Caveat Type | When to Surface | Source |
|-------------|----------------|--------|
| RTM warning | User's question implies extreme recent performance | Topic 5 |
| Novelty effect | Question about new feature/product | Topic 4 |
| Adherence gap | Question about loyalty programs, apps, opt-in features | Topic 4 |
| Self-selection | Any simulation (always applicable) | Topic 4 |
| Small sample | Persona count < 12 or high persona failure rate | Topic 2 |
| Cherry-pick warning | Standout voices section | Topic 3 |
| Not causation | Every result (always applicable) | Topic 6 |
| Profile quality | Business description is short or vague | Topic 4 (dependence) |

## Prompt Engineering Notes

_This section will be filled in as we iterate on prompts. Track all changes in PROMPTS.md._

- v0.1 drafts created — untested placeholder prompts
- Key concern: avoiding positive bias in persona responses
- Key concern: ensuring personas feel distinct, not templated
- OCEAN personality model (from synthetic-user-research) is a promising diversity mechanism
- Anti-p-hacking: aggregator must not cherry-pick extreme responses as representative
- RTM awareness: detect "things are bad lately" framing and add caveat
- Causation disclaimer: never use causal language ("will cause", "will lead to")

## Scientific Reference Corpus

The `backend/scraper/` module collects peer-reviewed research on:
- Synthetic user simulation accuracy and biases
- Persona-based research methodology
- A/B testing methodology and common pitfalls
- Customer behavior prediction validity
- LLM-as-judge and LLM-as-participant research

Scraped articles are stored in `docs/research/` as structured JSON with metadata. These inform our prompt design and accuracy claims.

## Rules for Claude Code Sessions

1. **Read CLAUDE.md first** before starting any work
2. **Never skip the logging layer** — every simulation must be stored to the database
3. **Never output raw statistics to users** — always translate to plain English with persona voices
4. **Version all prompt changes** in PROMPTS.md with a changelog entry
5. **Keep this file updated** as decisions are made and features are built
6. **Always include caveats** — consult `docs/ab-testing-theory/` and `backend/swarm/caveats.py`
7. **Never claim causation** — use language like "might", "could", "customers like yours may"
8. **Check for RTM** — if the user's question implies extreme recent performance, add a regression-to-the-mean warning
