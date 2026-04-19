-- Migration 003: Add persona_archetypes table for 1-month TTL caching
-- This allows reusing persona demographics/personality across multiple simulations
-- within a 30-day window, reducing API costs and keeping swarms consistent.

CREATE TABLE IF NOT EXISTS persona_archetypes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    profiles JSONB NOT NULL,
    manifest_hash TEXT,
    persona_count INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 days'),
    CONSTRAINT persona_archetypes_business_unique UNIQUE (business_id)
);

CREATE INDEX IF NOT EXISTS idx_persona_archetypes_business_id
    ON persona_archetypes(business_id);

CREATE INDEX IF NOT EXISTS idx_persona_archetypes_expires_at
    ON persona_archetypes(expires_at);

-- RLS: only the business owner can access their own archetypes
ALTER TABLE persona_archetypes ENABLE ROW LEVEL SECURITY;

CREATE POLICY persona_archetypes_owner_access ON persona_archetypes
    FOR ALL USING (
        business_id IN (
            SELECT id FROM businesses WHERE user_id = auth.uid()
        )
    );
