-- Murmur Database Schema
-- PostgreSQL via Supabase
-- Created: 2026-04-05

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- BUSINESSES
-- The core entity: a small business using Murmur
-- ============================================================
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL,                    -- e.g., "restaurant", "barbershop", "grocery store"
    description TEXT NOT NULL,             -- free-text business description
    customer_description TEXT,             -- how the owner describes their customers
    location TEXT,                         -- city/neighborhood for cultural context
    metadata JSONB DEFAULT '{}',          -- flexible extra fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_businesses_user_id ON businesses(user_id);

-- ============================================================
-- BUSINESS UPLOADS
-- CSV or data files uploaded by the business owner
-- ============================================================
CREATE TABLE business_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,                -- Supabase Storage URL
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,               -- "csv", "xlsx", etc.
    parsed_data JSONB,                     -- structured data extracted from file
    parse_status TEXT NOT NULL DEFAULT 'pending',  -- pending, parsed, failed
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_business_uploads_business_id ON business_uploads(business_id);

-- ============================================================
-- SIMULATIONS
-- Each question a business owner asks
-- ============================================================
CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    question TEXT NOT NULL,                -- the user's question
    variant_a TEXT,                        -- for A/B questions: first option
    variant_b TEXT,                        -- for A/B questions: second option
    status TEXT NOT NULL DEFAULT 'pending', -- pending, generating_personas, simulating, aggregating, completed, failed
    persona_count INT NOT NULL DEFAULT 15,
    prompt_version TEXT NOT NULL DEFAULT 'v0.1',  -- which prompt version was used
    business_snapshot JSONB,              -- snapshot of business profile at time of simulation
    error_message TEXT,                    -- if status=failed, why
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_simulations_business_id ON simulations(business_id);
CREATE INDEX idx_simulations_status ON simulations(status);

-- ============================================================
-- PERSONAS
-- Synthetic customer personas generated per simulation
-- ============================================================
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    age INT NOT NULL,
    occupation TEXT,
    visit_frequency TEXT,                  -- e.g., "3x per week"
    avg_spend NUMERIC(10, 2),             -- dollars per visit
    personality TEXT,                      -- plain-language personality description
    relationship_to_business TEXT,         -- their specific connection
    quirk TEXT,                            -- memorable behavioral detail
    profile JSONB NOT NULL DEFAULT '{}',  -- full persona object from generation
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_personas_simulation_id ON personas(simulation_id);

-- ============================================================
-- PERSONA RESPONSES
-- Each persona's individual response to the simulation question
-- ============================================================
CREATE TABLE persona_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    persona_id UUID NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    response TEXT NOT NULL,                -- in-character reaction
    reasoning TEXT,                        -- why they feel this way
    sentiment NUMERIC(3, 2),              -- -1.00 to 1.00
    preference TEXT,                       -- for A/B: "A", "B", or "neither"
    preference_strength TEXT,              -- "strong", "slight", "indifferent"
    raw_output JSONB,                     -- full API response for debugging
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_persona_responses_simulation_id ON persona_responses(simulation_id);
CREATE INDEX idx_persona_responses_persona_id ON persona_responses(persona_id);

-- ============================================================
-- SIMULATION RESULTS
-- Aggregated output shown to the user
-- ============================================================
CREATE TABLE simulation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,                 -- plain-English headline + themes
    recommendation TEXT,                   -- what we suggest
    confidence_score TEXT NOT NULL,        -- "high", "medium", "low"
    confidence_reasoning TEXT,             -- why this confidence level
    winner TEXT,                           -- for A/B: "A", "B", "tie", "depends"
    winner_reasoning TEXT,                 -- for A/B: why
    themes JSONB,                          -- structured theme groups
    standout_voices JSONB,                -- notable persona quotes
    raw_output JSONB NOT NULL,            -- full aggregator response
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_simulation_results_simulation_id ON simulation_results(simulation_id);

-- ============================================================
-- REAL OUTCOMES (BACKTESTING)
-- What actually happened after the business made a decision
-- This is the critical feedback loop table
-- ============================================================
CREATE TABLE real_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    what_actually_happened TEXT NOT NULL,  -- free-text description of the real outcome
    outcome_matched BOOLEAN,               -- did our prediction match reality?
    match_details TEXT,                     -- how well it matched (nuance beyond boolean)
    reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT                              -- any additional context
);

CREATE INDEX idx_real_outcomes_simulation_id ON real_outcomes(simulation_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- Users can only access their own data
-- ============================================================
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE personas ENABLE ROW LEVEL SECURITY;
ALTER TABLE persona_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE real_outcomes ENABLE ROW LEVEL SECURITY;

-- Businesses: users see only their own
CREATE POLICY businesses_user_policy ON businesses
    FOR ALL USING (user_id = auth.uid());

-- All child tables: access through business ownership
CREATE POLICY uploads_user_policy ON business_uploads
    FOR ALL USING (business_id IN (SELECT id FROM businesses WHERE user_id = auth.uid()));

CREATE POLICY simulations_user_policy ON simulations
    FOR ALL USING (business_id IN (SELECT id FROM businesses WHERE user_id = auth.uid()));

CREATE POLICY personas_user_policy ON personas
    FOR ALL USING (simulation_id IN (
        SELECT s.id FROM simulations s
        JOIN businesses b ON s.business_id = b.id
        WHERE b.user_id = auth.uid()
    ));

CREATE POLICY persona_responses_user_policy ON persona_responses
    FOR ALL USING (simulation_id IN (
        SELECT s.id FROM simulations s
        JOIN businesses b ON s.business_id = b.id
        WHERE b.user_id = auth.uid()
    ));

CREATE POLICY simulation_results_user_policy ON simulation_results
    FOR ALL USING (simulation_id IN (
        SELECT s.id FROM simulations s
        JOIN businesses b ON s.business_id = b.id
        WHERE b.user_id = auth.uid()
    ));

CREATE POLICY real_outcomes_user_policy ON real_outcomes
    FOR ALL USING (simulation_id IN (
        SELECT s.id FROM simulations s
        JOIN businesses b ON s.business_id = b.id
        WHERE b.user_id = auth.uid()
    ));

-- ============================================================
-- UPDATED_AT TRIGGER
-- Auto-update the updated_at column on businesses
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER businesses_updated_at
    BEFORE UPDATE ON businesses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
