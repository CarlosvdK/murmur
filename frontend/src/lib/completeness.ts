export const CUSTOMER_FIELD_WEIGHTS: Record<string, { weight: number; label: string }> = {
  first_name: { weight: 2, label: "first name" },
  email: { weight: 3, label: "email" },
  phone: { weight: 2, label: "phone number" },
  linkedin_url: { weight: 3, label: "LinkedIn profile" },
  age_range: { weight: 3, label: "age range" },
  occupation: { weight: 4, label: "occupation" },
  income_level: { weight: 5, label: "income level" },
  lifestyle_description: { weight: 4, label: "lifestyle description" },
  location_customer: { weight: 4, label: "customer location" },
  tenure: { weight: 5, label: "customer tenure" },
  visit_frequency: { weight: 5, label: "visit frequency" },
  spend_per_visit: { weight: 6, label: "spend per visit" },
  main_purchases: { weight: 4, label: "what they buy" },
  why_they_come: { weight: 5, label: "why they come" },
  loyalty_level: { weight: 5, label: "loyalty level" },
  has_complained: { weight: 2, label: "complaint history" },
  customer_segment: { weight: 3, label: "customer segment" },
  personality_traits: { weight: 5, label: "personality traits" },
  decision_style: { weight: 4, label: "decision style" },
  price_sensitivity: { weight: 6, label: "sensitivity to change" },
  what_would_make_leave: { weight: 5, label: "what would make them leave" },
  company: { weight: 2, label: "company name" },
  city: { weight: 3, label: "city" },
  relationship_notes: { weight: 3, label: "relationship notes" },
  memorable_interactions: { weight: 2, label: "memorable interactions" },
  has_file_upload: { weight: 5, label: "file upload for twin" },
};

export const VENDOR_FIELD_WEIGHTS: Record<string, { weight: number; label: string }> = {
  first_name: { weight: 2, label: "contact name" },
  email: { weight: 2, label: "email" },
  company: { weight: 3, label: "company name" },
  vendor_category: { weight: 4, label: "vendor category" },
  main_supply: { weight: 4, label: "what they supply" },
  vendor_company_size: { weight: 3, label: "company size" },
  tenure_vendor: { weight: 5, label: "relationship length" },
  annual_spend_vendor: { weight: 6, label: "annual spend" },
  payment_terms: { weight: 3, label: "payment terms" },
  contract_type: { weight: 3, label: "contract type" },
  has_alternatives: { weight: 5, label: "alternative vendors" },
  criticality_score: { weight: 5, label: "criticality rating" },
  quality_rating: { weight: 4, label: "quality rating" },
  reliability_rating: { weight: 4, label: "reliability rating" },
  has_raised_prices: { weight: 6, label: "history of changes to terms" },
  has_negotiated: { weight: 5, label: "history of successful requests" },
  communication_style: { weight: 4, label: "communication style" },
  price_discussion_style: { weight: 5, label: "how they handle difficult conversations" },
  vendor_motivation: { weight: 4, label: "vendor motivation" },
  market_competitiveness: { weight: 4, label: "market competitiveness" },
  price_trend: { weight: 3, label: "market pressures" },
  vendor_relationship_notes: { weight: 3, label: "relationship notes" },
  has_file_upload: { weight: 5, label: "file upload for twin" },
};

export function computeCompleteness(
  formData: Record<string, unknown>,
  weights: Record<string, { weight: number; label: string }>,
): { score: number; milestoneMessage: string; nextImprovement: string | null } {
  const maxScore = Object.values(weights).reduce((sum, w) => sum + w.weight, 0);
  let earned = 0;

  for (const [field, { weight }] of Object.entries(weights)) {
    const val = formData[field];
    if (val !== undefined && val !== null && val !== "" && val !== false) {
      if (Array.isArray(val) && val.length === 0) continue;
      earned += weight;
    }
  }

  const score = Math.round((earned / maxScore) * 100);

  const milestoneMessage =
    score < 25 ? "Basic profile -- broad reactions only" :
    score < 50 ? "Good start -- habit and routine predictions unlocked" :
    score < 75 ? "Strong profile -- relationship and loyalty predictions unlocked" :
    score < 90 ? "Excellent -- full simulation accuracy across any question you ask" :
    "Complete -- digital twin ready";

  // Find highest-weight empty field
  let bestField: string | null = null;
  let bestWeight = 0;
  for (const [field, { weight, label }] of Object.entries(weights)) {
    const val = formData[field];
    const isEmpty = val === undefined || val === null || val === "" || val === false || (Array.isArray(val) && val.length === 0);
    if (isEmpty && weight > bestWeight) {
      bestWeight = weight;
      bestField = label;
    }
  }

  return { score, milestoneMessage, nextImprovement: bestField };
}
