-- Migration 002: Full persistence
-- Adds remaining JSONB columns to simulations + CRM tables
-- Run this in Supabase SQL Editor after schema.sql

-- ============================================================
-- SIMULATION EXTRAS
-- Store context, caveats, reviewer intel, and impact inline
-- ============================================================
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS context_data JSONB;
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS caveats JSONB;
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS reviewer_intel JSONB;
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS impact_data JSONB;

-- ============================================================
-- CRM: CONTACTS
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT,
    full_name TEXT NOT NULL,
    job_title TEXT,
    department TEXT,
    seniority_level TEXT,
    email TEXT,
    phone TEXT,
    linkedin_url TEXT,
    city TEXT,
    country TEXT,
    contact_type TEXT NOT NULL DEFAULT 'contact',
    relationship_strength INT NOT NULL DEFAULT 0,
    communication_style TEXT,
    last_contact_date TIMESTAMPTZ,
    has_twin BOOLEAN NOT NULL DEFAULT FALSE,
    twin_type TEXT,
    twin_confidence TEXT,
    twin_corpus_size INT NOT NULL DEFAULT 0,
    current_sentiment TEXT,
    sentiment_trend TEXT,
    notes TEXT,
    tags JSONB DEFAULT '[]',
    organisation_id UUID,  -- FK added after crm_organisations exists
    organisation_name TEXT,
    role_label TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_contacts_user_id ON crm_contacts(user_id);

-- ============================================================
-- CRM: ORGANISATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_organisations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    domain TEXT,
    organisation_type TEXT NOT NULL DEFAULT 'customer',
    industry TEXT,
    size_category TEXT,
    country TEXT,
    city TEXT,
    relationship_status TEXT NOT NULL DEFAULT 'active',
    relationship_since DATE,
    contract_value_annual NUMERIC(12, 2),
    currency TEXT NOT NULL DEFAULT 'EUR',
    health_score INT,
    health_trend TEXT,
    last_contact_date TIMESTAMPTZ,
    has_twin BOOLEAN NOT NULL DEFAULT FALSE,
    website_url TEXT,
    description TEXT,
    tags JSONB DEFAULT '[]',
    contacts_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_organisations_user_id ON crm_organisations(user_id);

-- Now add the FK from contacts -> organisations
ALTER TABLE crm_contacts
    ADD CONSTRAINT fk_crm_contacts_organisation
    FOREIGN KEY (organisation_id) REFERENCES crm_organisations(id) ON DELETE SET NULL;

-- ============================================================
-- CRM: CORRESPONDENCE
-- Stores processing metadata only -- never raw content
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_correspondence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID NOT NULL REFERENCES crm_contacts(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    message_count INT,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    extracted_signals JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_correspondence_contact_id ON crm_correspondence(contact_id);

-- ============================================================
-- CRM: TWIN QUERIES
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_twin_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID REFERENCES crm_contacts(id) ON DELETE CASCADE,
    organisation_id UUID REFERENCES crm_organisations(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    confidence TEXT NOT NULL,
    key_signals JSONB DEFAULT '[]',
    preparation_tips JSONB DEFAULT '[]',
    caveats JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_twin_queries_contact_id ON crm_twin_queries(contact_id);

-- ============================================================
-- CRM: SIGNAL ALERTS
-- Detected relationship signals per contact
-- ============================================================
CREATE TABLE IF NOT EXISTS crm_signal_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID NOT NULL REFERENCES crm_contacts(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    recommendation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crm_signal_alerts_contact_id ON crm_signal_alerts(contact_id);

-- ============================================================
-- ROW LEVEL SECURITY for CRM tables
-- ============================================================
ALTER TABLE crm_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE crm_organisations ENABLE ROW LEVEL SECURITY;
ALTER TABLE crm_correspondence ENABLE ROW LEVEL SECURITY;
ALTER TABLE crm_twin_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE crm_signal_alerts ENABLE ROW LEVEL SECURITY;

-- Direct user ownership
CREATE POLICY crm_contacts_user_policy ON crm_contacts
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY crm_organisations_user_policy ON crm_organisations
    FOR ALL USING (user_id = auth.uid());

-- Child tables: access through contact/org ownership
CREATE POLICY crm_correspondence_user_policy ON crm_correspondence
    FOR ALL USING (contact_id IN (SELECT id FROM crm_contacts WHERE user_id = auth.uid()));

CREATE POLICY crm_twin_queries_user_policy ON crm_twin_queries
    FOR ALL USING (
        contact_id IN (SELECT id FROM crm_contacts WHERE user_id = auth.uid())
        OR organisation_id IN (SELECT id FROM crm_organisations WHERE user_id = auth.uid())
    );

CREATE POLICY crm_signal_alerts_user_policy ON crm_signal_alerts
    FOR ALL USING (contact_id IN (SELECT id FROM crm_contacts WHERE user_id = auth.uid()));

-- ============================================================
-- UPDATED_AT TRIGGERS for CRM tables
-- ============================================================
CREATE TRIGGER crm_contacts_updated_at
    BEFORE UPDATE ON crm_contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER crm_organisations_updated_at
    BEFORE UPDATE ON crm_organisations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
