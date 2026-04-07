-- Migration 003: Extended contact fields for customer and vendor profiles
-- Run in Supabase SQL Editor

-- Customer-specific fields
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS age_range TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS gender TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS occupation TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS industry TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS income_level TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS lifestyle_description TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS languages JSONB DEFAULT '[]';
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS household_size INT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS location_customer TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS instagram_url TEXT;

-- Relationship fields
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS tenure TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS visit_frequency_contact TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS spend_per_visit NUMERIC(10, 2);
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS estimated_annual_spend NUMERIC(12, 2);
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'EUR';
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS main_purchases TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS why_they_come JSONB DEFAULT '[]';
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS loyalty_level TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS has_complained TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS complaint_description TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS refers_customers TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS customer_segment TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS contact_channels JSONB DEFAULT '[]';

-- Personality fields
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS personality_traits JSONB DEFAULT '[]';
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS decision_style TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS price_sensitivity INT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS what_would_make_leave TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS what_would_make_loyal TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS life_context TEXT;

-- Contact/professional
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS company_website TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS company_linkedin TEXT;

-- History
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS relationship_notes_ext TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS memorable_interactions TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS last_interaction_date DATE;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS how_met TEXT;

-- Vendor-specific fields
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS vendor_category JSONB DEFAULT '[]';
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS main_supply TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS vendor_company_size TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS vendor_location TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS client_importance TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS vendor_staff_count INT;

-- Commercial
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS tenure_vendor TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS annual_spend_vendor NUMERIC(12, 2);
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS payment_terms TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS contract_type TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS contract_renewal_date DATE;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS notice_period TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS has_alternatives TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS delivery_frequency TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS criticality_score INT;

-- Performance
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS quality_rating INT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS reliability_rating INT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS communication_rating INT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS has_let_down BOOLEAN;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS letdown_description TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS has_raised_prices TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS price_raise_amount TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS price_raise_warning TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS price_raise_justification TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS has_negotiated TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS negotiation_outcome TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS negotiation_description TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS has_ongoing_issues BOOLEAN;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS issues_description TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS overall_satisfaction INT;

-- Relationship dynamics
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS vendor_main_contact TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS price_discussion_style TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS vendor_motivation JSONB DEFAULT '[]';
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS client_importance_feeling TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS threatened_to_switch TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS vendor_relationship_notes TEXT;

-- Market context
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS market_competitiveness TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS price_trend TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS supply_concerns TEXT;
ALTER TABLE crm_contacts ADD COLUMN IF NOT EXISTS compliance_concerns TEXT;
