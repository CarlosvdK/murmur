-- Migration 007: simulation_accuracy
--
-- Structured calibration record, written whenever a user submits what
-- actually happened via POST /simulations/{id}/outcome. Complements
-- real_outcomes (which is free-text) with queryable fields so we can
-- track accuracy over time per business type, confidence band, scenario.

CREATE TABLE IF NOT EXISTS simulation_accuracy (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    real_outcome_id UUID REFERENCES real_outcomes(id) ON DELETE CASCADE,
    predicted_winner TEXT,
    predicted_confidence TEXT,
    predicted_summary TEXT,
    actual_matched BOOLEAN,
    accuracy_pct NUMERIC(5,2),
    match_details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_simulation_accuracy_simulation_id
    ON simulation_accuracy(simulation_id);
CREATE INDEX IF NOT EXISTS idx_simulation_accuracy_created_at
    ON simulation_accuracy(created_at);

ALTER TABLE simulation_accuracy ENABLE ROW LEVEL SECURITY;

-- Users can read/write rows whose simulation belongs to their business.
CREATE POLICY simulation_accuracy_user_read ON simulation_accuracy
    FOR SELECT USING (
        simulation_id IN (
            SELECT s.id FROM simulations s
            JOIN businesses b ON b.id = s.business_id
            WHERE b.user_id = auth.uid()
        )
    );

CREATE POLICY simulation_accuracy_user_insert ON simulation_accuracy
    FOR INSERT WITH CHECK (
        simulation_id IN (
            SELECT s.id FROM simulations s
            JOIN businesses b ON b.id = s.business_id
            WHERE b.user_id = auth.uid()
        )
    );
