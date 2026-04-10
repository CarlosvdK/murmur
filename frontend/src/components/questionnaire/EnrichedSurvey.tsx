"use client";

import { useState, useEffect } from "react";
import {
  BusinessCreate,
  researchBusiness,
  generateDescription,
  generateCustomerDescription,
} from "@/lib/api";

interface Props {
  onSubmit: (data: BusinessCreate) => void;
  loading?: boolean;
}

const BUSINESS_TYPES = [
  "Restaurant", "Cafe / Coffee Shop", "Bar / Pub", "Barbershop / Salon",
  "Grocery Store", "Retail Shop", "Gym / Fitness", "Bakery",
  "SaaS / Software", "E-commerce", "Consulting", "B2B Services",
  "Logistics / Shipping", "Healthcare Clinic", "Dental Practice",
  "Education / Training", "Freelance / Agency", "Hotel / Hospitality",
  "Auto Shop", "Other",
];

const TYPE_MAP: Record<string, string> = {
  "Restaurant": "restaurant", "Cafe / Coffee Shop": "cafe",
  "Bar / Pub": "bar", "Barbershop / Salon": "barbershop",
  "Grocery Store": "grocery", "Retail Shop": "clothing",
  "Gym / Fitness": "gym", "Bakery": "bakery",
  "SaaS / Software": "saas", "E-commerce": "ecommerce",
  "Consulting": "consulting", "B2B Services": "b2b_services",
  "Logistics / Shipping": "logistics", "Healthcare Clinic": "healthcare_clinic",
  "Dental Practice": "dental", "Education / Training": "education",
  "Freelance / Agency": "freelance", "Hotel / Hospitality": "hotel",
  "Auto Shop": "auto", "Other": "other",
};

const BUSINESS_ROLES = [
  { value: "habit", label: "A habit or routine", desc: "They come regularly because it's part of their week -- not because they thought about it", example: "Like the coffee shop someone stops at every morning without thinking twice." },
  { value: "daily_need", label: "A daily need", desc: "They need what you offer -- it's practical and functional", example: "Like the lunch spot near the office that saves them cooking." },
  { value: "treat", label: "A treat or reward", desc: "Coming here feels like a small luxury or something they look forward to", example: "Like the brunch place someone visits when they want to do something nice for themselves." },
  { value: "social", label: "A social spot", desc: "They come to be around people, meet friends, or feel part of something", example: "Like the local pub where everyone knows your name." },
  { value: "convenience", label: "Pure convenience", desc: "You're close, easy, or the fastest option -- that's mainly why they come", example: "Like the nearest petrol station or corner shop." },
  { value: "destination", label: "A destination", desc: "They make a specific effort to come -- it's worth the journey", example: "Like the restaurant people drive 30 minutes to visit." },
];

const VALUE_DRIVERS = [
  { value: "specific_product", label: "A specific product or dish", desc: "There's one thing you do that they can't get elsewhere" },
  { value: "atmosphere", label: "The atmosphere or vibe", desc: "How the place feels -- cosy, buzzy, calm, welcoming" },
  { value: "personal_touch", label: "The personal touch", desc: "The staff know them, remember their order, make them feel like a regular" },
  { value: "location", label: "Location and convenience", desc: "You're simply the most practical option for them" },
  { value: "value", label: "Value for money", desc: "They feel they get more than they paid for" },
  { value: "quality", label: "Quality above everything", desc: "You're simply the best option available to them" },
  { value: "social", label: "The social experience", desc: "It's where they meet people, catch up, feel part of something" },
  { value: "consistency", label: "Consistency and reliability", desc: "They know exactly what they're getting every time" },
];

const AREA_TYPES = [
  { value: "residential", label: "Residential -- mostly local residents" },
  { value: "business", label: "Business district -- lots of office workers" },
  { value: "student", label: "Student area -- near schools or universities" },
  { value: "tourist", label: "Tourist area -- visitors and sightseers" },
  { value: "shopping", label: "Shopping area -- high street or retail zone" },
  { value: "mixed", label: "Mixed -- a real variety" },
];

const AREA_FEELS = [
  { value: "community", label: "Community area", desc: "People know each other -- it has a local feel" },
  { value: "transactional", label: "Transactional area", desc: "Busy, practical, people in and out quickly" },
  { value: "destination", label: "Destination area", desc: "People make a trip to come here specifically" },
  { value: "passing_trade", label: "Passing trade area", desc: "A lot of people just happen to be passing" },
];

export default function EnrichedSurvey({ onSubmit, loading }: Props) {
  const [phase, setPhase] = useState<"lookup" | "survey">("lookup");
  const [step, setStep] = useState(0);
  const [lookupInput, setLookupInput] = useState("");
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupResult, setLookupResult] = useState<Record<string, unknown> | null>(null);
  const [genLoading, setGenLoading] = useState<string | null>(null);
  const [aiOfferDismissed, setAiOfferDismissed] = useState(false);
  const [aiAutocompleting, setAiAutocompleting] = useState(false);

  const [form, setForm] = useState<BusinessCreate>({
    name: "", type: "", description: "", customer_description: "",
    location: "", years_open: "", business_role: "", visit_frequency: "",
    busy_days: [], busy_times: [], customer_value_drivers: [],
    customer_social_context: [], regular_proportion: "",
    area_demographics: [], competitor_count: "", area_feel: "",
    website_url: "", additional_customer_notes: "",
    has_prior_change: false, prior_change_description: "", prior_change_outcome: "",
    location_street: "", location_number: "", location_postcode: "",
    location_city: "", location_neighbourhood: "", location_country: "",
    customer_age_distribution: [], customer_income_bracket: "",
    average_transaction_value: undefined, customer_gender_split: "",
    local_vs_visitor_ratio: "", digital_savviness: "", price_range: "",
  });

  // Save to localStorage
  useEffect(() => {
    const saved = localStorage.getItem("murmur_survey");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setForm((prev) => ({ ...prev, ...parsed }));
        if (parsed.name) setPhase("survey");
      } catch { /* ignore */ }
    }
  }, []);

  useEffect(() => {
    if (form.name) {
      localStorage.setItem("murmur_survey", JSON.stringify(form));
    }
  }, [form]);

  const update = (field: string, value: unknown) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const toggleMulti = (field: string, value: string) => {
    const current = ((form as unknown as Record<string, unknown>)[field] as string[]) || [];
    const next = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    update(field, next);
  };

  // Phase 0: Lookup
  const handleLookup = async () => {
    if (!lookupInput.trim()) return;
    setLookupLoading(true);
    try {
      const result = await researchBusiness(lookupInput.trim());
      setLookupResult(result);
    } catch {
      setPhase("survey");
    } finally {
      setLookupLoading(false);
    }
  };

  const acceptLookup = () => {
    if (!lookupResult) return;
    const r = lookupResult;
    setForm((prev) => ({
      ...prev,
      name: (r.name as string) || prev.name,
      type: (r.type as string) || prev.type,
      description: (r.description as string) || prev.description,
      location: (r.formatted_address as string) || prev.location,
      google_place_id: (r.google_place_id as string) || prev.google_place_id,
      website_url: (r.website as string) || prev.website_url,
      years_open: (r.years_open_estimate as string) || prev.years_open,
    }));
    setPhase("survey");
  };

  // AI generators
  const handleGenerateDescription = async () => {
    setGenLoading("description");
    try {
      const result = await generateDescription({
        name: form.name, type: form.type,
        location: form.location, years_open: form.years_open,
      });
      update("description", result.description);
    } catch { /* ignore */ }
    setGenLoading(null);
  };

  const handleGenerateCustomerDesc = async () => {
    setGenLoading("customer");
    try {
      const result = await generateCustomerDescription({
        business_name: form.name, business_type: form.type,
        location: form.location, business_description: form.description,
      });
      update("customer_description", result.description);
    } catch { /* ignore */ }
    setGenLoading(null);
  };

  const canNext = (() => {
    if (step === 0) return form.name && form.type && form.description && form.location_city;
    if (step === 1) return form.business_role;
    if (step === 2) return form.area_demographics && (form.area_demographics as string[]).length > 0;
    return true;
  })();

  const handleSubmit = () => {
    localStorage.removeItem("murmur_survey");
    // Compose location string from structured fields
    const locationParts = [
      form.location_street,
      form.location_number,
      form.location_postcode,
      form.location_city,
      form.location_country,
    ].filter(Boolean);
    const composedLocation = locationParts.join(", ");
    onSubmit({ ...form, location: composedLocation || form.location });
  };

  const totalSteps = 4;

  // ============================================================
  // PHASE 0: QUICK START
  // ============================================================
  if (phase === "lookup") {
    return (
      <div className="mx-auto max-w-xl py-16">
        <h1 className="mb-2 text-center text-2xl font-bold text-gray-900">
          Let&apos;s find your business
        </h1>
        <p className="mb-8 text-center text-sm text-gray-500">
          Paste your website, Google Business link, or just type your business name and city
        </p>

        {lookupResult ? (
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-lg font-semibold text-gray-900">
              {lookupResult.name as string}
            </p>
            <p className="text-sm text-gray-500">
              {lookupResult.type as string} -- {lookupResult.formatted_address as string}
            </p>
            {lookupResult.rating ? (
              <p className="mt-1 text-sm text-gray-400">
                {String(lookupResult.rating)} stars -- {String(lookupResult.review_count)} reviews
              </p>
            ) : null}
            <p className="mt-4 text-sm text-gray-600">
              We found your business -- does this look right?
            </p>
            <div className="mt-4 flex gap-3">
              <button
                onClick={acceptLookup}
                className="flex-1 rounded-xl bg-murmur-amber py-3 text-sm font-semibold text-white transition-colors hover:bg-murmur-amber/90"
              >
                Yes, that&apos;s me
              </button>
              <button
                onClick={() => { setLookupResult(null); setPhase("survey"); }}
                className="rounded-xl border border-gray-200 px-6 py-3 text-sm text-gray-500 transition-colors hover:bg-gray-50"
              >
                Not quite
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <input
              value={lookupInput}
              onChange={(e) => setLookupInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleLookup()}
              placeholder="e.g. Rosa's Cafe Hackney or paste a Google Maps link"
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
            />
            <div className="flex gap-3">
              <button
                onClick={handleLookup}
                disabled={lookupLoading || !lookupInput.trim()}
                className="flex-1 rounded-xl bg-murmur-amber py-3 text-sm font-semibold text-white transition-colors hover:bg-murmur-amber/90 disabled:opacity-50"
              >
                {lookupLoading ? "Searching..." : "Find my business"}
              </button>
              <button
                onClick={() => setPhase("survey")}
                className="px-4 text-sm text-gray-400 underline"
              >
                Skip, I&apos;ll fill it in
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  const handleAiAutocomplete = async () => {
    if (!form.name) return;
    setAiAutocompleting(true);
    try {
      const result = await researchBusiness(form.name + (form.location_city ? " " + form.location_city : ""));
      if (result) {
        const r = result;
        setForm((prev) => ({
          ...prev,
          description: (r.description as string) || prev.description,
          location: (r.formatted_address as string) || prev.location,
          google_place_id: (r.google_place_id as string) || prev.google_place_id,
          website_url: (r.website as string) || prev.website_url,
          years_open: (r.years_open_estimate as string) || prev.years_open,
          type: (r.type as string) || prev.type,
        }));
      }
    } catch { /* ignore */ }
    setAiAutocompleting(false);
    setAiOfferDismissed(true);
  };

  // ============================================================
  // SURVEY STEPS
  // ============================================================
  return (
    <div className="mx-auto max-w-2xl py-8">
      {/* AI autocomplete offer */}
      {step === 0 && form.name && !aiOfferDismissed && (
        <div className="mb-6 flex items-center gap-4 rounded-xl border border-brand-blue/20 bg-brand-blue/5 p-4">
          <div className="flex-1">
            <p className="text-sm font-medium text-black">Want us to fill in some fields automatically?</p>
            <p className="text-xs text-gray-500">We can look up your business and pre-fill details like description, location, and type.</p>
          </div>
          <button
            onClick={handleAiAutocomplete}
            disabled={aiAutocompleting}
            className="shrink-0 rounded-lg bg-brand-blue px-4 py-2 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50"
          >
            {aiAutocompleting ? "Looking up..." : "Autocomplete"}
          </button>
          <button onClick={() => setAiOfferDismissed(true)} className="shrink-0 text-xs text-gray-400 hover:text-gray-600">Dismiss</button>
        </div>
      )}

      {/* Step indicator */}
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs text-gray-400">Step {step + 1} of {totalSteps}</p>
        {step === 3 && (
          <button onClick={handleSubmit} className="text-xs text-gray-400 hover:text-gray-600">
            Skip optional fields
          </button>
        )}
      </div>
      <div className="mb-8 flex gap-1.5">
        {Array.from({ length: totalSteps }).map((_, i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-colors ${
              i < step ? "bg-murmur-amber" : i === step ? "bg-murmur-amber/60" : "bg-gray-200"
            }`}
          />
        ))}
      </div>

      {/* ====== STEP 1: YOUR BUSINESS ====== */}
      {step === 0 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Your Business</h2>
            <p className="mt-1 text-sm text-gray-500">Tell us the basics -- we&apos;ll do the rest.</p>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Business Name *</label>
            <input
              value={form.name}
              onChange={(e) => update("name", e.target.value)}
              placeholder="e.g. Tony's Taco Truck"
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Business Type *</label>
            <div className="grid grid-cols-2 gap-2">
              {BUSINESS_TYPES.map((t) => (
                <button
                  key={t}
                  onClick={() => update("type", TYPE_MAP[t])}
                  className={`rounded-xl border px-3 py-2.5 text-sm transition-all ${
                    form.type === TYPE_MAP[t]
                      ? "border-murmur-amber bg-murmur-amber-light/30 text-gray-900 font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Where are you? *</label>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2 sm:col-span-1">
                <input
                  value={form.location_street || ""}
                  onChange={(e) => update("location_street", e.target.value)}
                  placeholder="Street name"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
              <div>
                <input
                  value={form.location_number || ""}
                  onChange={(e) => update("location_number", e.target.value)}
                  placeholder="Number"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
              <div>
                <input
                  value={form.location_postcode || ""}
                  onChange={(e) => update("location_postcode", e.target.value)}
                  placeholder="Postcode"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
              <div>
                <input
                  value={form.location_city || ""}
                  onChange={(e) => update("location_city", e.target.value)}
                  placeholder="City *"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
              <div>
                <input
                  value={form.location_neighbourhood || ""}
                  onChange={(e) => update("location_neighbourhood", e.target.value)}
                  placeholder="Neighbourhood / Area"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
              <div>
                <input
                  value={form.location_country || ""}
                  onChange={(e) => update("location_country", e.target.value)}
                  placeholder="Country *"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">How long have you been open? *</label>
            <div className="flex gap-2">
              {["< 1 year", "1-3 years", "3-10 years", "10+ years"].map((opt) => {
                const val = opt.replace(/\s/g, "").replace("years", "").replace("year", "");
                return (
                  <button
                    key={opt}
                    onClick={() => update("years_open", val)}
                    className={`flex-1 rounded-xl border py-2.5 text-sm transition-all ${
                      form.years_open === val
                        ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                        : "border-gray-200 text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Describe your business *</label>
            <p className="mb-2 text-xs text-gray-400">What kind of place is it? What do you sell? What&apos;s the vibe?</p>
            <textarea
              value={form.description}
              onChange={(e) => update("description", e.target.value)}
              placeholder="e.g. Family-run Italian restaurant known for fresh pasta..."
              rows={4}
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
            />
            {form.name && form.type && (
              <button
                onClick={handleGenerateDescription}
                disabled={genLoading === "description"}
                className="mt-2 rounded-lg border border-murmur-amber/30 px-3 py-1.5 text-xs font-medium text-murmur-amber transition-colors hover:bg-murmur-amber-light/20"
              >
                {genLoading === "description" ? "Researching..." : "Write this for me"}
              </button>
            )}
          </div>
        </div>
      )}

      {/* ====== STEP 2: YOUR CUSTOMERS ====== */}
      {step === 1 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Your Customers</h2>
            <p className="mt-1 text-sm text-gray-500">This is what makes your simulation specific to you -- the more honest, the more accurate.</p>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Describe your typical customer</label>
            <p className="mb-2 text-xs text-gray-400">Think about the person who comes most often. What are they like?</p>
            <textarea
              value={form.customer_description || ""}
              onChange={(e) => update("customer_description", e.target.value)}
              placeholder="e.g. Mostly office workers grabbing lunch, families on weekends..."
              rows={3}
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
            />
            <button
              onClick={handleGenerateCustomerDesc}
              disabled={genLoading === "customer"}
              className="mt-2 rounded-lg border border-murmur-amber/30 px-3 py-1.5 text-xs font-medium text-murmur-amber transition-colors hover:bg-murmur-amber-light/20"
            >
              {genLoading === "customer" ? "Researching..." : "Help me describe them"}
            </button>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">What role does your business play in their life? *</label>
            <p className="mb-3 text-xs text-gray-400">Pick the one that fits best</p>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {BUSINESS_ROLES.map((role) => (
                <button
                  key={role.value}
                  onClick={() => update("business_role", role.value)}
                  className={`rounded-xl border p-4 text-left transition-all ${
                    form.business_role === role.value
                      ? "border-murmur-amber bg-murmur-amber-light/20"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <p className="text-sm font-medium text-gray-900">{role.label}</p>
                  <p className="mt-0.5 text-xs text-gray-500">{role.desc}</p>
                </button>
              ))}
            </div>
            {form.business_role && (
              <p className="mt-3 text-xs italic text-murmur-amber">
                {BUSINESS_ROLES.find((r) => r.value === form.business_role)?.example}
              </p>
            )}
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Typical visit frequency</label>
            <div className="flex flex-wrap gap-2">
              {[
                { v: "daily", l: "Almost every day" }, { v: "weekly", l: "Most weeks" },
                { v: "monthly", l: "Once or twice a month" }, { v: "occasional", l: "A few times a year" },
                { v: "mixed", l: "Very mixed" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("visit_frequency", opt.v)}
                  className={`rounded-xl border px-4 py-2 text-sm transition-all ${
                    form.visit_frequency === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Busiest days and times</label>
            <div className="mb-2 flex flex-wrap gap-1.5">
              {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d) => (
                <button
                  key={d}
                  onClick={() => toggleMulti("busy_days", d.toLowerCase())}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                    (form.busy_days || []).includes(d.toLowerCase())
                      ? "border-murmur-amber bg-murmur-amber text-white"
                      : "border-gray-200 text-gray-500 hover:bg-gray-50"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap gap-1.5">
              {["Morning", "Lunchtime", "Afternoon", "Evening", "Late night"].map((t) => (
                <button
                  key={t}
                  onClick={() => toggleMulti("busy_times", t.toLowerCase())}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                    (form.busy_times || []).includes(t.toLowerCase())
                      ? "border-murmur-amber bg-murmur-amber text-white"
                      : "border-gray-200 text-gray-500 hover:bg-gray-50"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">What do they value most about you? *</label>
            <p className="mb-3 text-xs text-gray-400">Pick up to 3</p>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {VALUE_DRIVERS.map((vd) => {
                const selected = (form.customer_value_drivers || []).includes(vd.value);
                const atMax = (form.customer_value_drivers || []).length >= 3 && !selected;
                return (
                  <button
                    key={vd.value}
                    onClick={() => !atMax && toggleMulti("customer_value_drivers", vd.value)}
                    disabled={atMax}
                    className={`rounded-xl border p-3 text-left transition-all ${
                      selected
                        ? "border-murmur-amber bg-murmur-amber-light/20"
                        : atMax
                          ? "border-gray-100 text-gray-300"
                          : "border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    <p className="text-sm font-medium text-gray-900">{vd.label}</p>
                    <p className="mt-0.5 text-xs text-gray-500">{vd.desc}</p>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">What&apos;s the usual social setup?</label>
            <div className="flex flex-wrap gap-2">
              {[
                "On their own", "With a partner", "With family / kids",
                "With friends", "With work colleagues", "Changes a lot",
              ].map((opt) => {
                const val = opt.toLowerCase().replace(/ \/ /g, "_").replace(/ /g, "_");
                return (
                  <button
                    key={opt}
                    onClick={() => toggleMulti("customer_social_context", val)}
                    className={`rounded-xl border px-3 py-2 text-sm transition-all ${
                      (form.customer_social_context || []).includes(val)
                        ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                        : "border-gray-200 text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">How many regulars would you say you have?</label>
            <div className="flex flex-wrap gap-2">
              {[
                { v: "almost_none", l: "Almost no one" },
                { v: "handful", l: "A handful (10-20)" },
                { v: "solid_base", l: "A solid base (50+)" },
                { v: "mostly_regulars", l: "Mostly regulars" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("regular_proportion", opt.v)}
                  className={`rounded-xl border px-4 py-2 text-sm transition-all ${
                    form.regular_proportion === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Customer age range (select all that apply)</label>
            <p className="mb-2 text-xs text-gray-400">Which age groups make up most of your customers?</p>
            <div className="flex flex-wrap gap-1.5">
              {["18-24", "25-34", "35-44", "45-54", "55-64", "65+"].map((bracket) => (
                <button
                  key={bracket}
                  onClick={() => toggleMulti("customer_age_distribution", bracket)}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                    (form.customer_age_distribution || []).includes(bracket)
                      ? "border-murmur-amber bg-murmur-amber text-white"
                      : "border-gray-200 text-gray-500 hover:bg-gray-50"
                  }`}
                >
                  {bracket}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Customer income level</label>
            <div className="flex flex-wrap gap-2">
              {[
                { v: "budget", l: "Budget-conscious" },
                { v: "lower_middle", l: "Lower-middle" },
                { v: "middle", l: "Middle income" },
                { v: "upper_middle", l: "Upper-middle" },
                { v: "affluent", l: "Affluent" },
                { v: "mixed", l: "Mixed / Varies" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("customer_income_bracket", opt.v)}
                  className={`rounded-xl border px-4 py-2 text-sm transition-all ${
                    form.customer_income_bracket === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Average transaction value</label>
            <p className="mb-2 text-xs text-gray-400">How much does a typical customer spend per transaction?</p>
            <input
              type="number"
              value={form.average_transaction_value || ""}
              onChange={(e) => update("average_transaction_value", e.target.value ? parseFloat(e.target.value) : undefined)}
              placeholder="e.g. 25"
              className="w-48 rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Customer gender split</label>
            <div className="flex flex-wrap gap-2">
              {[
                { v: "mostly_male", l: "Mostly male" },
                { v: "mostly_female", l: "Mostly female" },
                { v: "balanced", l: "Balanced" },
                { v: "unknown", l: "Not sure" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("customer_gender_split", opt.v)}
                  className={`rounded-xl border px-4 py-2 text-sm transition-all ${
                    form.customer_gender_split === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Customer base type</label>
            <div className="flex flex-wrap gap-2">
              {[
                { v: "mostly_local", l: "Mostly local / repeat" },
                { v: "mixed", l: "Mix of local and new" },
                { v: "mostly_visitors", l: "Mostly new / one-time" },
                { v: "all_online", l: "All online" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("local_vs_visitor_ratio", opt.v)}
                  className={`rounded-xl border px-4 py-2 text-sm transition-all ${
                    form.local_vs_visitor_ratio === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">How tech-savvy are your customers?</label>
            <div className="flex flex-wrap gap-2">
              {[
                { v: "low", l: "Low (prefer in-person)" },
                { v: "moderate", l: "Moderate" },
                { v: "high", l: "High (apps & online)" },
                { v: "very_high", l: "Very high (digital-native)" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("digital_savviness", opt.v)}
                  className={`rounded-xl border px-4 py-2 text-sm transition-all ${
                    form.digital_savviness === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Your price positioning</label>
            <div className="flex flex-wrap gap-2">
              {[
                { v: "budget", l: "Budget / Economy" },
                { v: "mid_range", l: "Mid-range" },
                { v: "premium", l: "Premium" },
                { v: "luxury", l: "Luxury / High-end" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("price_range", opt.v)}
                  className={`rounded-xl border px-4 py-2 text-sm transition-all ${
                    form.price_range === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ====== STEP 3: YOUR NEIGHBOURHOOD ====== */}
      {step === 2 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Your Local Area</h2>
            <p className="mt-1 text-sm text-gray-500">Where you are shapes who your customers are -- help us understand your patch.</p>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">What kind of area is it? *</label>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {AREA_TYPES.map((at) => (
                <button
                  key={at.value}
                  onClick={() => toggleMulti("area_demographics", at.value)}
                  className={`rounded-xl border p-3 text-left text-sm transition-all ${
                    (form.area_demographics || []).includes(at.value)
                      ? "border-murmur-amber bg-murmur-amber-light/20 font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {at.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">How much local competition is there?</label>
            <div className="flex flex-wrap gap-2">
              {[
                { v: "only_one", l: "We're the only one" },
                { v: "one_two", l: "1-2 others" },
                { v: "three_five", l: "3-5 alternatives" },
                { v: "six_plus", l: "6 or more" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("competitor_count", opt.v)}
                  className={`rounded-xl border px-4 py-2 text-sm transition-all ${
                    form.competitor_count === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">How would you describe the feel of where you are?</label>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {AREA_FEELS.map((af) => (
                <button
                  key={af.value}
                  onClick={() => update("area_feel", af.value)}
                  className={`rounded-xl border p-3 text-left transition-all ${
                    form.area_feel === af.value
                      ? "border-murmur-amber bg-murmur-amber-light/20"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <p className="text-sm font-medium text-gray-900">{af.label}</p>
                  <p className="mt-0.5 text-xs text-gray-500">{af.desc}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ====== STEP 4: OPTIONAL ====== */}
      {step === 3 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">A few more things</h2>
            <p className="mt-1 text-sm text-gray-500">All optional -- but every detail makes your simulation more accurate.</p>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Your website</label>
            <input
              value={form.website_url || ""}
              onChange={(e) => update("website_url", e.target.value)}
              placeholder="https://..."
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none"
            />
            <p className="mt-1 text-xs text-gray-400">We use this to understand your brand and what makes you unique</p>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Tell us anything else about your customers</label>
            <textarea
              value={form.additional_customer_notes || ""}
              onChange={(e) => update("additional_customer_notes", e.target.value)}
              placeholder="Are they mostly one age group? Anything unusual about your customer base?"
              rows={3}
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Have you ever changed something big and seen how customers reacted?</label>
            <div className="flex gap-2">
              {[
                { v: true, l: "Yes" },
                { v: false, l: "No / Not really" },
              ].map((opt) => (
                <button
                  key={String(opt.v)}
                  onClick={() => update("has_prior_change", opt.v)}
                  className={`rounded-xl border px-6 py-2 text-sm transition-all ${
                    form.has_prior_change === opt.v
                      ? "border-murmur-amber bg-murmur-amber text-white font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
            {form.has_prior_change && (
              <div className="mt-4 space-y-3 rounded-xl border border-gray-100 bg-gray-50 p-4">
                <input
                  value={form.prior_change_description || ""}
                  onChange={(e) => update("prior_change_description", e.target.value)}
                  placeholder="What did you change?"
                  className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm"
                />
                <input
                  value={form.prior_change_outcome || ""}
                  onChange={(e) => update("prior_change_outcome", e.target.value)}
                  placeholder="What happened? (optional)"
                  className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm"
                />
                <p className="text-xs text-gray-400">
                  This helps us test our prediction against your own experience.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="mt-8 flex justify-between">
        <button
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={step === 0}
          className="text-sm text-gray-400 transition-colors hover:text-gray-600 disabled:invisible"
        >
          Back
        </button>

        {step < totalSteps - 1 ? (
          <button
            onClick={() => setStep((s) => s + 1)}
            disabled={!canNext}
            className="rounded-xl bg-black px-8 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-80 disabled:opacity-30"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="rounded-xl bg-murmur-amber px-8 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create my profile"}
          </button>
        )}
      </div>
    </div>
  );
}
