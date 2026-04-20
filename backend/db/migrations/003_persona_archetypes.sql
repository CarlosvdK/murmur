-- Migration 003: Add persona_archetypes table for indefinite caching
-- Personas represent customer demographics (static) and are cached indefinitely.
-- Context and responses are always generated fresh per question/date.
-- Personas are invalidated ONLY on significant business profile changes.

CREATE TABLE IF NOT EXISTS persona_archetypes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    profiles JSONB NOT NULL,
    persona_count INT NOT NULL,
    business_snapshot_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT persona_archetypes_business_unique UNIQUE (business_id)
);

CREATE INDEX IF NOT EXISTS idx_persona_archetypes_business_id
    ON persona_archetypes(business_id);

CREATE INDEX IF NOT EXISTS idx_persona_archetypes_created_at
    ON persona_archetypes(created_at);

-- RLS: only the business owner can access their own archetypes
ALTER TABLE persona_archetypes ENABLE ROW LEVEL SECURITY;

CREATE POLICY persona_archetypes_owner_access ON persona_archetypes
    FOR ALL USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()
        )
    );
