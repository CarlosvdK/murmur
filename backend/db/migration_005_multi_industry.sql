-- Migration 005: Multi-industry customer demographics
-- Run in Supabase SQL Editor
-- Adds structured customer demographic fields to businesses table.
-- All columns are nullable -- existing businesses are unaffected.

-- Customer demographics
ALTER TABLE businesses ADD COLUMN IF NOT EXISTS customer_age_distribution TEXT[];
ALTER TABLE businesses ADD COLUMN IF NOT EXISTS customer_income_bracket TEXT;
ALTER TABLE businesses ADD COLUMN IF NOT EXISTS average_transaction_value NUMERIC(10,2);
ALTER TABLE businesses ADD COLUMN IF NOT EXISTS customer_gender_split TEXT;
ALTER TABLE businesses ADD COLUMN IF NOT EXISTS local_vs_visitor_ratio TEXT;
ALTER TABLE businesses ADD COLUMN IF NOT EXISTS digital_savviness TEXT;
ALTER TABLE businesses ADD COLUMN IF NOT EXISTS price_range TEXT;

-- Index on price_range for filtering simulations by price tier
CREATE INDEX IF NOT EXISTS idx_businesses_price_range ON businesses(price_range);
