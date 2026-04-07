# Missing Backend Integration

Tracks frontend features that need backend wiring.

## Settings Page (new fields added 2026-04-07)

### New fields NOT YET in Business model or DB schema:
These fields exist in the settings frontend but are not saved to Supabase yet.
They need: (1) Pydantic model field, (2) metadata key in _business_to_row, (3) _row_to_business unpacking.

- `location_settings` (string[]) -- location character chips (beach, urban, etc.)
- `area_draws` (string[]) -- what draws people to the area
- `customer_transport` (string[]) -- how customers get there
- `has_parking` (string) -- parking availability
- `first_visit_reasons` (string[]) -- how customers first find the business
- `seasonal_patterns` (string[]) -- busy seasons
- `customer_community` (string) -- do customers know each other
- `opening_hours` (JSONB) -- weekly opening hours grid
- `google_business_url` (string) -- Google Business Profile URL
- `tripadvisor_url` (string) -- TripAdvisor URL
- `instagram_url` (string) -- Instagram handle/URL
- `facebook_url` (string) -- Facebook page URL
- `prior_change_types` (string[]) -- what kind of prior change
- `prior_change_went` (string) -- better/expected/worse
- `anything_else` (string) -- freeform extra notes

### Backend endpoint needed:
- `POST /survey/autofill` -- exists (added by agent), uses researchBusiness internally

### DB migration needed:
- Add columns to `businesses` metadata (no schema change needed -- these go in JSONB metadata)

### To wire up:
1. Add fields to `BusinessCreate` Pydantic model in `backend/models/business.py`
2. Add fields to `Business` model
3. Add fields to `_row_to_business` in `backend/api/routes/businesses.py`
4. Add fields to `Business` interface in `frontend/src/lib/api.ts`
5. Add fields to `handleSave()` in settings page
6. Add fields to load in `useEffect` in settings page

### Status: Frontend UI complete, backend wiring pending
