-- Migration 004: Experiment corpus and research findings tables
-- Run in Supabase SQL Editor

-- Experiment corpus: structured database of real business experiments
CREATE TABLE IF NOT EXISTS experiment_corpus (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_name TEXT NOT NULL,
  source_url TEXT,\
  source_type TEXT NOT NULL,
  publication_name TEXT,
  authors TEXT[],
  published_year INT,
  doi TEXT,
  citation_count INT,
  peer_reviewed BOOLEAN DEFAULT FALSE,
  business_type TEXT,
  business_size TEXT,
  business_name TEXT,
  country TEXT,
  experiment_type TEXT NOT NULL,
  change_description TEXT NOT NULL,
  change_magnitude TEXT,
  had_control_group BOOLEAN,
  sample_size INT,
  duration_days INT,
  was_randomised BOOLEAN,
  primary_metric TEXT,
  direction TEXT,
  effect_size_raw TEXT,
  effect_size_numeric FLOAT,
  statistical_significance TEXT,
  p_value FLOAT,
  confidence_interval TEXT,
  customer_acceptance_rate FLOAT,
  customer_switch_rate FLOAT,
  customer_complaint_rate FLOAT,
  economic_conditions TEXT,
  competitive_context TEXT,
  cultural_context TEXT,
  murmur_simulation_type TEXT[],
  applicable_survey_fields TEXT[],
  quality_score FLOAT,
  abstract TEXT,
  full_text TEXT,
  key_quotes TEXT[],
  processed BOOLEAN DEFAULT FALSE,
  findings_extracted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_corpus_type ON experiment_corpus(experiment_type);
CREATE INDEX IF NOT EXISTS idx_corpus_business ON experiment_corpus(business_type);
CREATE INDEX IF NOT EXISTS idx_corpus_quality ON experiment_corpus(quality_score);
CREATE INDEX IF NOT EXISTS idx_corpus_direction ON experiment_corpus(direction);

-- Research findings: documented calibration values with provenance
CREATE TABLE IF NOT EXISTS research_findings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  finding_id TEXT UNIQUE NOT NULL,
  domain TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  value_type TEXT NOT NULL,
  value_float FLOAT,
  value_range_low FLOAT,
  value_range_high FLOAT,
  value_categorical TEXT,
  value_boolean BOOLEAN,
  applicable_conditions TEXT,
  not_applicable_when TEXT,
  primary_source TEXT NOT NULL,
  supporting_sources TEXT[],
  contradicting_sources TEXT[],
  confidence_level TEXT NOT NULL,
  last_updated_by_study INT,
  previous_values JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
