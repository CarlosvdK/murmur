# Carlos — manual actions before production launch

These are things I (Claude) cannot do for you. Check them off as you go.

## Must do before first real user

- [ ] **Rotate disposable API keys.** You confirmed these were dev-only but the
      new prod keys should replace them in Railway + Vercel env:
  - `ANTHROPIC_API_KEY`
  - `FRED_API_KEY`
  - `ALPHA_VANTAGE_API_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `BRAVE_SEARCH_API_KEY`
  - `GOOGLE_PLACES_API_KEY`

- [ ] **Set production env vars on Railway (backend):**
  - `SENTRY_DSN=<from Sentry project settings>`
  - `SENTRY_TRACES_SAMPLE_RATE=0.1`
  - `ENVIRONMENT=production`
  - `GIT_SHA=$RAILWAY_GIT_COMMIT_SHA`
  - `RATE_LIMIT_DEFAULT=120/minute`
  - `RATE_LIMIT_SIMULATIONS_CREATE=20/minute`

- [ ] **Run migration 007** in the Supabase SQL editor:
      `backend/db/migration_007_simulation_accuracy.sql`
      (Adds `simulation_accuracy` table. Without it, the outcome-submit
      endpoint silently skips the accuracy write.)

- [ ] **Enable the `exec_sql` RPC in Supabase** (only if you want
      `python -m backend.db.migrate` to run migrations automatically).
      Otherwise keep running SQL files by hand.

      ```sql
      CREATE OR REPLACE FUNCTION exec_sql(sql TEXT)
      RETURNS VOID LANGUAGE plpgsql SECURITY DEFINER AS $$
      BEGIN EXECUTE sql; END;
      $$;
      REVOKE EXECUTE ON FUNCTION exec_sql(TEXT) FROM PUBLIC;
      GRANT EXECUTE ON FUNCTION exec_sql(TEXT) TO service_role;
      ```

- [ ] **Install pre-commit hooks locally** so secret-hygiene tests run
      before every commit:

      ```bash
      pip install pre-commit && pre-commit install
      ```

- [ ] **Create a Sentry project** (FastAPI + Next.js), copy both DSNs.
      (Frontend Sentry wiring is a future item — backend is done.)

- [ ] **Enable GitHub Actions on the repo** if not already on — the
      `.github/workflows/test.yml` workflow is there and will run on push.

## Nice to have

- [ ] Wire Sentry on the frontend (Next.js SDK). Parity with backend.
- [ ] Set `FRONTEND_URL` env var on Railway so CORS allows your prod domain.
- [ ] Provision a managed Redis on Railway (you're using in-process
      asyncio.create_task right now; arq/Redis queue should come later
      for scale — but not needed for launch).
- [ ] Set up an uptime probe hitting `/api/health` (UptimeRobot, Railway
      native, whatever). 503 response is now meaningful — DB down will
      trip it.

## Known pre-existing issues (not mine to fix, flagged for you)

- `backend/tests/test_simulation_pipeline_e2e.py::test_context_engine_provides_data_to_personas`
  constructs `Business(...)` with invalid UUIDs and missing `created_at` /
  `updated_at`. Pydantic rejects it. Test-data bug, not a code bug. Fix
  when you next touch that file.

- There are `.py.bak` files scattered in `backend/tests/`. Safe to delete
  once you're sure you don't need them.

## What's deferred but now on the roadmap (Claude is handling these next session)

All items shipped on 2026-04-21:

- [x] ContextTool wrappers for `EconomicDataTool` / `MarketDataTool`
      ([backend/context/tools/economic_data_tool.py](backend/context/tools/economic_data_tool.py),
      [market_data_tool.py](backend/context/tools/market_data_tool.py))
- [x] Shared `retry_get_json` helper ([backend/context/tools/retry.py](backend/context/tools/retry.py));
      `price_index` migrated as proof. Others can migrate as touched.
- [x] Overall pipeline hard-timeout wrapper (`run_pipeline_with_timeout`
      in [simulations.py](backend/api/routes/simulations.py);
      `SIMULATION_PIPELINE_TIMEOUT` env, default 480s)
- [x] Component tests for `CIChart` / `EvidenceTab` / `ImpactPanel` / `CaveatCard`
- [x] Profile completeness meter surfaced in the results view
      ([ProfileQualityNote.tsx](frontend/src/components/results/ProfileQualityNote.tsx))
- [x] Standalone `<DecisionCard />` component
      ([DecisionCard.tsx](frontend/src/components/results/DecisionCard.tsx))

**New env var you may want to set:** `SIMULATION_PIPELINE_TIMEOUT=480` on Railway.

**Parent page rewiring needed (optional):** `ResultsReport` now accepts
`profileCompleteness` and `profileNextImprovement` props. Whatever page
renders results can compute these (the `computeCompleteness` helper in
[frontend/src/lib/completeness.ts](frontend/src/lib/completeness.ts)
already exists) and pass them in. Without them, `<ProfileQualityNote>`
silently renders nothing — safe default.
