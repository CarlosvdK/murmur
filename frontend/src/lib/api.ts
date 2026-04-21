import { createClient } from "@/lib/supabase/client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api";

async function getAuthHeaders(): Promise<Record<string, string>> {
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (session?.access_token) {
    headers["Authorization"] = `Bearer ${session.access_token}`;
  }
  return headers;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

// --- Businesses ---

export interface Business {
  id: string;
  user_id: string;
  name: string;
  type: string;
  description: string;
  customer_description: string | null;
  location: string | null;
  years_open: string | null;
  is_online_only: boolean | null;
  business_role: string[] | string | null;
  business_not_role: string[] | null;
  visit_frequency: string | null;
  busy_days: string[] | null;
  busy_times: string[] | null;
  customer_value_drivers: string[] | null;
  customer_social_context: string[] | null;
  regular_proportion: string | null;
  area_demographics: string[] | null;
  competitor_count: string | null;
  area_feel: string | null;
  website_url: string | null;
  google_place_id: string | null;
  additional_customer_notes: string | null;
  has_prior_change: boolean | null;
  prior_change_description: string | null;
  prior_change_outcome: string | null;
  location_street: string | null;
  location_number: string | null;
  location_postcode: string | null;
  location_city: string | null;
  location_neighbourhood: string | null;
  location_country: string | null;
  location_settings: string[] | null;
  area_draws: string[] | null;
  customer_transport: string[] | null;
  has_parking: string | null;
  first_visit_reasons: string[] | null;
  seasonal_patterns: string[] | null;
  customer_community: string | null;
  customer_discovery: string[] | null;
  nearby_anchors: string[] | null;
  competitor_advantage: string[] | null;
  location_advantage: string | null;
  opening_hours: Record<string, { open: boolean; opens: string; closes: string }> | null;
  google_business_url: string | null;
  tripadvisor_url: string | null;
  instagram_url: string | null;
  facebook_url: string | null;
  prior_change_types: string[] | null;
  prior_change_went: string | null;
  prior_changes: { change: string; year: string; outcome: string; metrics: string }[] | null;
  anything_else: string | null;
  customer_age_distribution: Record<string, number> | string[] | null;
  customer_income_bracket: string | null;
  average_transaction_value: number | null;
  customer_gender_split: string | null;
  local_vs_visitor_ratio: Record<string, number> | string | null;
  digital_savviness: string | null;
  price_range: string | null;
  created_at: string;
  updated_at: string;
}

export interface BusinessCreate {
  name: string;
  type: string;
  description: string;
  customer_description?: string;
  location?: string;
  years_open?: string;
  is_online_only?: boolean;
  business_role?: string[] | string;
  business_not_role?: string[];
  visit_frequency?: string;
  busy_days?: string[];
  busy_times?: string[];
  customer_value_drivers?: string[];
  customer_social_context?: string[];
  regular_proportion?: string;
  area_demographics?: string[];
  competitor_count?: string;
  area_feel?: string;
  website_url?: string;
  google_place_id?: string;
  additional_customer_notes?: string;
  has_prior_change?: boolean;
  prior_change_description?: string;
  prior_change_outcome?: string;
  location_street?: string;
  location_number?: string;
  location_postcode?: string;
  location_city?: string;
  location_neighbourhood?: string;
  location_country?: string;
  location_lat?: number;
  location_lng?: number;
  location_settings?: string[];
  area_draws?: string[];
  customer_transport?: string[];
  has_parking?: string;
  first_visit_reasons?: string[];
  seasonal_patterns?: string[];
  customer_community?: string;
  customer_discovery?: string[];
  nearby_anchors?: string[];
  competitor_advantage?: string[];
  location_advantage?: string;
  opening_hours?: Record<string, { open: boolean; opens: string; closes: string }>;
  google_business_url?: string;
  tripadvisor_url?: string;
  instagram_url?: string;
  facebook_url?: string;
  prior_change_types?: string[];
  prior_change_went?: string;
  prior_changes?: { change: string; year: string; outcome: string; metrics: string }[];
  anything_else?: string;
  customer_age_distribution?: Record<string, number> | string[];
  customer_income_bracket?: string;
  average_transaction_value?: number;
  customer_gender_split?: string;
  local_vs_visitor_ratio?: Record<string, number> | string;
  digital_savviness?: string;
  price_range?: string;
}

// Survey helper API calls
export const researchBusiness = (input: string) =>
  request<Record<string, unknown>>("/survey/research-business", {
    method: "POST",
    body: JSON.stringify({ input }),
  });

export const generateDescription = (data: {
  name: string;
  type: string;
  location?: string;
  years_open?: string;
}) =>
  request<{ description: string }>("/survey/generate-description", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const generateCustomerDescription = (data: {
  business_name: string;
  business_type: string;
  location?: string;
  business_description?: string;
}) =>
  request<{ description: string }>("/survey/generate-customer-description", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const placeAutocomplete = (query: string) =>
  request<{ predictions: { description: string; place_id: string }[] }>("/survey/place-autocomplete", {
    method: "POST", body: JSON.stringify({ query }),
  });

export const placeDetails = (placeId: string) =>
  request<Record<string, string | number | null>>("/survey/place-details", {
    method: "POST", body: JSON.stringify({ place_id: placeId }),
  });

export const createBusiness = (data: BusinessCreate) =>
  request<Business>("/businesses/", { method: "POST", body: JSON.stringify(data) });

export const getBusiness = (id: string) =>
  request<Business>(`/businesses/${id}`);

export const listBusinesses = () =>
  request<Business[]>("/businesses/");

export const deleteAccount = () =>
  request<{ deleted: boolean }>("/businesses/account", { method: "DELETE" });

export const updateBusiness = (id: string, data: BusinessCreate) =>
  request<Business>(`/businesses/${id}`, { method: "PUT", body: JSON.stringify(data) });

// --- Simulations ---

export type SimulationStatus =
  | "pending"
  | "gathering_context"
  | "generating_personas"
  | "simulating"
  | "aggregating"
  | "completed"
  | "failed";

export interface SimulationCreate {
  business_id: string;
  question: string;
  variant_a?: string;
  variant_b?: string;
  persona_count?: number;
}

export interface Simulation {
  id: string;
  business_id: string;
  question: string;
  variant_a: string | null;
  variant_b: string | null;
  status: SimulationStatus;
  persona_count: number;
  prompt_version: string;
  created_at: string;
  completed_at: string | null;
}

export interface SimulationProgress {
  simulation_id: string;
  status: SimulationStatus;
  step: string;
  personas_generated: number;
  personas_interviewed: number;
  personas_total: number;
  current_persona: string | null;
  elapsed_seconds: number;
}

export interface Theme {
  label: string;
  summary: string;
  count: number;
}

export interface StandoutVoice {
  persona_name: string;
  quote: string;
}

export interface PersonaProfile {
  name: string;
  age: number;
  occupation: string;
  engagement_pattern: string;
  spend_model: string;
  personality: string;
  relationship_to_business: string;
  quirk: string;
  segment?: string;
  income_tier?: string;
  price_sensitivity?: string;
  is_silent_majority?: boolean;
  digital_behavior?: string;
  decision_style?: string;
  // Backward-compatible aliases (old DB records)
  visit_frequency?: string;
  avg_spend?: number;
}

export interface PersonaResponseData {
  persona_name: string;
  // Backward-compatible single-shot fields
  reaction: string;
  reasoning: string;
  sentiment: number;
  preference?: string;
  preference_strength?: string;
  // Focus group 3-turn data (Phase 5)
  warmup?: {
    current_engagement: string;
    current_satisfaction: number;
    what_you_value: string;
    alternatives_aware_of: string;
    switching_ease: string;
  };
  core?: {
    reaction: string;
    reasoning: string;
    sentiment: number;
    gut_instinct: string;
    stated_action: string;
    predicted_actual_action: string;
    preference?: string;
    preference_strength?: string;
  };
  depth?: {
    next_3_interactions: { interaction_1: string; interaction_2: string; interaction_3: string };
    net_behavior_change: string;
    spend_change: string;
    would_tell_others: string;
    stated_vs_actual_gap: string;
    single_biggest_factor: string;
    what_would_change_your_mind: string;
  };
}

export interface SimulationResult {
  id: string;
  simulation_id: string;
  summary: string;
  recommendation?: string;
  confidence_score: string;
  confidence_reasoning?: string;
  winner?: string;
  winner_reasoning?: string;
  themes?: { label: string; summary: string; count: number }[];
  standout_voices?: { persona_name: string; quote: string }[];
  baseline_summary?: string;
  behavioral_prediction?: {
    engagement_change?: string;
    spend_change?: string;
    adaptation_speed?: string;
    word_of_mouth?: string;
  };
  stated_vs_actual_gap?: string;
  demographic_breakdown?: { group: string; personas: string[]; avg_sentiment: number }[];
  citations?: { domain: string; title: string; similarity: number }[];
  raw_output?: Record<string, unknown>;
  created_at: string;
}

export const createSimulation = (data: SimulationCreate) =>
  request<Simulation>("/simulations/", { method: "POST", body: JSON.stringify(data) });

export const getSimulation = (id: string) =>
  request<Simulation>(`/simulations/${id}`);

export const getSimulationProgress = (id: string) =>
  request<SimulationProgress>(`/simulations/${id}/progress`);

export const getSimulationPersonas = (id: string) =>
  request<PersonaProfile[]>(`/simulations/${id}/personas`);

export const getSimulationResponses = (id: string) =>
  request<PersonaResponseData[]>(`/simulations/${id}/responses`);

export const getSimulationResult = (id: string) =>
  request<SimulationResult>(`/simulations/${id}/result`);

export interface DemographicGroup {
  group: string;
  count: number;
  avg_sentiment: number;
  personas: string[];
  members: { persona_name: string; age?: number; sentiment: number }[];
}

export const getSimulationDemographics = (id: string) =>
  request<DemographicGroup[]>(`/simulations/${id}/demographics`);

export const listSimulations = () =>
  request<Simulation[]>("/simulations/");

// --- Caveats ---

export interface CaveatData {
  type: string;
  title: string;
  message: string;
  severity: "info" | "warning" | "critical";
  source: string;
}

export const getSimulationCaveats = (id: string) =>
  request<CaveatData[]>(`/simulations/${id}/caveats`);

export const getAccuracyStats = () =>
  request<{ total_outcomes: number; matched: number; accuracy_pct: number | null }>("/simulations/accuracy-stats");

export const submitRealOutcome = (simId: string, data: {
  what_actually_happened: string;
  outcome_matched?: boolean;
  match_details?: string;
  notes?: string;
}) =>
  request<Record<string, unknown>>(`/simulations/${simId}/outcome`, {
    method: "POST",
    body: JSON.stringify({ simulation_id: simId, ...data }),
  });

// --- SSE ---

export interface SSEEvent {
  phase: string;
  step: string;
  timestamp: string;
  simulation_id: string;
  metadata?: Record<string, unknown>;
}

export function createSimulationStream(
  simulationId: string,
  onProgress: (event: SSEEvent) => void,
  onDone: () => void,
  onError?: () => void,
): EventSource {
  const es = new EventSource(`${API_BASE}/simulations/${simulationId}/stream`);

  es.addEventListener("progress", (e) => {
    try {
      const data: SSEEvent = JSON.parse((e as MessageEvent).data);
      onProgress(data);
    } catch {
      // Ignore parse errors
    }
  });

  es.addEventListener("done", () => {
    es.close();
    onDone();
  });

  es.addEventListener("timeout", () => {
    es.close();
    onDone();
  });

  es.onerror = () => {
    es.close();
    if (onError) onError();
  };

  return es;
}

// ============================================================
// CRM API
// ============================================================

export interface CRMContact {
  id: string;
  first_name: string;
  last_name: string | null;
  full_name: string;
  job_title: string | null;
  department: string | null;
  seniority_level: string | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  city: string | null;
  country: string | null;
  contact_type: string;
  relationship_strength: number;
  communication_style: string | null;
  last_contact_date: string | null;
  has_twin: boolean;
  twin_type: string | null;
  twin_confidence: string | null;
  twin_corpus_size: number;
  current_sentiment: string | null;
  sentiment_trend: string | null;
  notes: string | null;
  tags: string[] | null;
  organisation_id: string | null;
  organisation_name: string | null;
  role_label: string | null;
  created_at: string;
  updated_at: string;
}

export interface CRMOrganisation {
  id: string;
  name: string;
  organisation_type: string;
  industry: string | null;
  size_category: string | null;
  country: string | null;
  city: string | null;
  relationship_status: string;
  health_score: number | null;
  contacts_count: number;
  created_at: string;
  updated_at: string;
}

export interface TwinQuery {
  id: string;
  contact_id: string | null;
  question: string;
  answer: string;
  confidence: string;
  key_signals: string[];
  preparation_tips: string[];
  caveats: string[];
  created_at: string;
}

export interface SignalAlert {
  type: string;
  severity: string;
  title: string;
  message: string;
  recommendation: string;
}

// Contacts
export const createContact = (data: Record<string, unknown>) =>
  request<CRMContact>("/crm/contacts/", { method: "POST", body: JSON.stringify(data) });

export const listContacts = (params?: { contact_type?: string; has_twin?: boolean }) => {
  const search = new URLSearchParams();
  if (params?.contact_type) search.set("contact_type", params.contact_type);
  if (params?.has_twin !== undefined) search.set("has_twin", String(params.has_twin));
  const qs = search.toString();
  return request<CRMContact[]>(`/crm/contacts/${qs ? "?" + qs : ""}`);
};

export const getContact = (id: string) =>
  request<CRMContact>(`/crm/contacts/${id}`);

export const deleteContact = (id: string) =>
  request<{ deleted: boolean }>(`/crm/contacts/${id}`, { method: "DELETE" });

// Organisations
export const createOrganisation = (data: Record<string, unknown>) =>
  request<CRMOrganisation>("/crm/organisations/", { method: "POST", body: JSON.stringify(data) });

export const listOrganisations = () =>
  request<CRMOrganisation[]>("/crm/organisations/");

export const getOrganisation = (id: string) =>
  request<CRMOrganisation>(`/crm/organisations/${id}`);

// Twin
export const askTwin = (contactId: string, question: string) =>
  request<TwinQuery>("/crm/twin/query", {
    method: "POST",
    body: JSON.stringify({ contact_id: contactId, question }),
  });

export const getTwinQueries = (contactId: string) =>
  request<TwinQuery[]>(`/crm/twin/queries/${contactId}`);

export const getContactSignals = (contactId: string) =>
  request<{ signals: SignalAlert[] }>(`/crm/twin/signals/${contactId}`);
