# Murmur — Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                       │
│                                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐  │
│  │  Auth     │  │  Onboarding  │  │ Simulate  │  │ Dashboard │  │
│  │  (Supa)  │  │  Questionnaire│  │ Interface │  │ History   │  │
│  └──────────┘  └──────────────┘  └─────┬─────┘  └───────────┘  │
│                                        │                        │
└────────────────────────────────────────┼────────────────────────┘
                                         │ REST API
┌────────────────────────────────────────┼────────────────────────┐
│                      BACKEND (FastAPI)  │                        │
│                                        ▼                        │
│  ┌──────────────┐    ┌──────────────────────────────┐           │
│  │  API Routes   │───▶│       Job Queue (Redis)       │           │
│  │  /businesses  │    │  - Enqueue simulation job     │           │
│  │  /simulations │    │  - Poll status via SSE/poll   │           │
│  │  /uploads     │    └──────────────┬───────────────┘           │
│  └──────────────┘                    │                           │
│                                      ▼                           │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                    SWARM ENGINE                            │   │
│  │                                                           │   │
│  │  1. Persona Generator                                     │   │
│  │     Business profile ──▶ N synthetic customer personas    │   │
│  │                                                           │   │
│  │  2. Simulator                                             │   │
│  │     Question + Personas ──▶ N parallel Claude API calls   │   │
│  │     Each persona responds independently                   │   │
│  │                                                           │   │
│  │  3. Aggregator                                            │   │
│  │     N responses ──▶ Plain-English summary + recommendation│   │
│  └───────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                  PostgreSQL (Supabase)                     │   │
│  │  businesses │ simulations │ personas │ responses │ results │   │
│  │                    + real_outcomes (backtesting)           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Key Architecture Decisions

### Why FastAPI (Python) instead of Node.js backend?

- The swarm engine is the core of the product. It involves heavy prompt engineering, async parallel API calls, and data processing — all of which Python handles better.
- Anthropic's Python SDK is the primary SDK with the best async support.
- CAMEL-AI (if we use it) is Python-only.
- NumPy/pandas may be needed for parsing uploaded CSV data.
- FastAPI's async support is excellent and avoids the need for a separate worker process for simple parallelism.

### Why Redis + BullMQ for the job queue?

A single simulation run involves:
1. Generating 12-20 personas (1 API call, ~3-5 seconds)
2. Running the question through each persona in parallel (12-20 API calls, ~5-10 seconds)
3. Aggregating responses (1 API call, ~3-5 seconds)

Total: ~15-25 seconds. This is too long for a synchronous HTTP request.

The queue solves three problems:
- **User experience**: The frontend can show real-time progress ("Generating personas... Interviewing Maria... Interviewing Carlos...")
- **Reliability**: If an API call fails, the job can retry without restarting from scratch
- **Scaling**: Multiple simulations can run concurrently without blocking the API server

**Note**: BullMQ is Node.js. For Python, we'll use either:
- `arq` (async Redis queue for Python, lightweight) — **preferred**
- `celery` with Redis broker (heavier, more features than we need)
- Direct Redis pub/sub with a custom worker (simplest but no retry logic)

Decision: Start with `arq` for simplicity. Migrate to Celery only if we need advanced features.

### Why Supabase?

For a prototype/MVP, Supabase gives us:
- **Auth**: Email/password + OAuth out of the box. No auth code to write.
- **Database**: Managed Postgres with a good dashboard for debugging.
- **Storage**: File uploads (CSV) with signed URLs, no S3 configuration.
- **Realtime**: Built-in Postgres change notifications (could use for live simulation updates).

This lets us ship faster. If we outgrow Supabase, the migration path is straightforward since it's standard Postgres underneath.

### Why NOT microservices?

The swarm engine, API, and worker all live in one Python codebase. Reasons:
- We are one developer building an MVP
- The swarm engine is tightly coupled to the API (shared models, shared DB)
- Deployment complexity should be minimal at this stage
- We can extract services later if needed

## The Swarm Engine — Detailed Flow

### Persona Generation

Input: Business profile (name, type, description, customer_description, location, uploaded data)

Process:
1. Build a meta-prompt that describes the business and its customer base
2. Ask Claude to generate N diverse personas in a single structured output call
3. Each persona gets: name, age, occupation, visit_frequency, avg_spend, personality_traits (OCEAN-inspired), relationship_to_business, quirks
4. Enforce diversity: at least 1 infrequent visitor, 1 price-sensitive customer, 1 loyal regular, 1 potential churner

Output: Array of persona objects stored in the `personas` table

### Simulation (Interview Phase)

Input: User's question + array of personas

Process:
1. For each persona, construct a prompt: "You are [persona]. [Business] is considering [question]. How would you react?"
2. Fire all N prompts in parallel using `asyncio.gather()` with semaphore for rate limiting
3. Each response includes: reaction (in character), reasoning (why they feel that way), sentiment (-1 to 1)
4. Handle failures gracefully: if 2/15 personas fail, continue with 13. Log the failures.

Output: Array of persona_responses stored in DB

### Aggregation

Input: All persona responses for a simulation

Process:
1. Feed all responses to an aggregation prompt
2. The aggregator produces:
   - **Headline**: One sentence summary ("Most of your regulars would accept the price increase, but you'd lose some weekday-only visitors")
   - **Themes**: Grouped reactions ("The price-sensitive group said...", "Your loyalists said...")
   - **Standout voices**: 2-3 specific personas quoted directly
   - **Confidence**: How reliable is this result, given the input quality
   - **Recommendation**: What we'd suggest, with caveats
3. For A/B questions: compare variant_a vs variant_b reactions separately, then declare a winner with confidence

Output: simulation_results record stored in DB

## Logging Strategy

Every simulation run stores:

| What | Where | Why |
|------|-------|-----|
| Business profile snapshot | `simulations.business_snapshot` (jsonb) | Business may change; we need the profile as-it-was |
| User's question | `simulations.question` | Obvious |
| Generated personas | `personas` table | Audit trail + reuse potential |
| Each persona's raw response | `persona_responses.response` | Full audit trail |
| Each persona's reasoning | `persona_responses.reasoning` | Understanding why, not just what |
| Aggregated summary | `simulation_results.summary` | The output shown to user |
| Raw aggregator output | `simulation_results.raw_output` | Debug + prompt iteration |
| Prompt versions used | `simulations.prompt_version` | Tie results to specific prompt versions |
| Timestamps | All tables | Performance tracking |
| Real outcome (later) | `real_outcomes` | Backtesting — did we predict correctly? |

## Parallel API Call Management

```python
# Pseudocode for parallel persona interviews
import asyncio
from anthropic import AsyncAnthropic

CONCURRENCY_LIMIT = 5  # Max parallel API calls (respect rate limits)

async def run_simulation(personas, question, business):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    client = AsyncAnthropic()

    async def interview_persona(persona):
        async with semaphore:
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                system=build_persona_system_prompt(persona, business),
                messages=[{"role": "user", "content": question}],
            )
            return parse_response(response)

    results = await asyncio.gather(
        *[interview_persona(p) for p in personas],
        return_exceptions=True
    )

    # Filter out failures, log them, continue with successes
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    log_failures(failures)

    return successes
```

Key considerations:
- **Semaphore**: Limits concurrent calls to avoid rate limit errors
- **return_exceptions=True**: One failed persona doesn't kill the whole simulation
- **Retry logic**: Failed calls get 1 retry with exponential backoff before being logged as failures
- **Minimum threshold**: If fewer than 60% of personas succeed, mark the simulation as failed

## Data Flow for A/B Questions

```
User asks: "Which menu item would sell better — a spicy burger or a truffle mac & cheese?"

1. System detects A/B pattern (two variants)
2. Personas are generated once (same personas evaluate both)
3. Each persona is asked about variant_a, then variant_b (separate calls)
4. Aggregator receives both sets of responses
5. Output: "Your regulars prefer the spicy burger (especially the lunch crowd),
   but the truffle mac & cheese would attract new customers on weekends.
   We'd recommend the spicy burger for reliability, mac & cheese if you
   want to grow weekend traffic."
```

## Deployment Architecture

### MVP (current target)

- Frontend: Vercel (automatic deploys from `main` branch)
- Backend: Railway (Dockerfile-based deploy)
- Database: Supabase managed Postgres
- Redis: Railway managed Redis add-on
- Domain: Custom domain on Vercel

### Future scaling considerations

- Backend could move to AWS ECS/Fargate if Railway limits are hit
- Redis could move to AWS ElastiCache
- Consider edge caching for static business profiles
- Consider websockets (via Supabase Realtime) instead of polling for simulation progress
