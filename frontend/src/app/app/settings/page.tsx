"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { listBusinesses, updateBusiness, deleteAccount, researchBusiness, generateDescription, generateCustomerDescription, placeAutocomplete, placeDetails, Business, BusinessCreate } from "@/lib/api";
import { createClient } from "@/lib/supabase/client";

// === EXPANDED BUSINESS TYPES WITH GROUPS ===
const BUSINESS_TYPE_GROUPS = [
  { label: "Food & Drink", options: [
    { value: "restaurant", label: "Restaurant" }, { value: "cafe", label: "Cafe / Coffee shop" },
    { value: "bar", label: "Bar / Pub" }, { value: "bakery", label: "Bakery" },
    { value: "food_truck", label: "Food truck / Market stall" }, { value: "catering", label: "Catering business" },
    { value: "desserts", label: "Ice cream / Desserts" },
  ]},
  { label: "Health & Wellness", options: [
    { value: "gym", label: "Gym / Fitness studio" }, { value: "yoga", label: "Yoga / Pilates studio" },
    { value: "spa", label: "Spa / Massage" }, { value: "barbershop", label: "Barbershop / Barber" },
    { value: "hair_salon", label: "Hair salon / Beauty salon" }, { value: "nail_salon", label: "Nail salon" },
    { value: "tattoo", label: "Tattoo studio" }, { value: "physio", label: "Physiotherapy / Osteopathy" },
  ]},
  { label: "Retail", options: [
    { value: "grocery", label: "Grocery / Supermarket" }, { value: "clothing", label: "Clothing / Fashion" },
    { value: "bookshop", label: "Bookshop" }, { value: "gift_shop", label: "Gift shop / Homeware" },
    { value: "florist", label: "Florist" }, { value: "sports", label: "Sports / Outdoor gear" },
    { value: "electronics", label: "Electronics" }, { value: "toy_shop", label: "Toy shop" },
    { value: "pet_shop", label: "Pet shop" },
  ]},
  { label: "Services", options: [
    { value: "auto", label: "Auto repair / Garage" }, { value: "dry_cleaning", label: "Dry cleaning / Laundry" },
    { value: "photography", label: "Photography studio" }, { value: "printing", label: "Printing / Design" },
    { value: "accountant", label: "Accountant / Financial advisor" }, { value: "legal", label: "Legal services" },
  ]},
  { label: "Hospitality & Tourism", options: [
    { value: "hotel", label: "Hotel / B&B" }, { value: "hostel", label: "Hostel" },
    { value: "campsite", label: "Campsite / Glamping" }, { value: "tour_operator", label: "Tour operator" },
    { value: "activity_centre", label: "Activity centre" },
  ]},
  { label: "Other", options: [
    { value: "other", label: "Other (describe below)" },
  ]},
];

const ALL_TYPE_OPTIONS = BUSINESS_TYPE_GROUPS.flatMap((g) => g.options);

const BUSINESS_ROLES = [
  { value: "habit", label: "A habit or routine" }, { value: "daily_need", label: "A daily need" },
  { value: "treat", label: "A treat or reward" }, { value: "social", label: "A social spot" },
  { value: "convenience", label: "Pure convenience" }, { value: "destination", label: "A destination" },
];
const VALUE_DRIVERS = [
  { value: "specific_product", label: "A specific product or dish" }, { value: "atmosphere", label: "The atmosphere or vibe" },
  { value: "personal_touch", label: "The personal touch" }, { value: "location", label: "Location and convenience" },
  { value: "value", label: "Value for money" }, { value: "quality", label: "Quality above everything" },
  { value: "social", label: "The social experience" }, { value: "consistency", label: "Consistency and reliability" },
];
const AREA_TYPES = [
  { value: "residential", label: "Residential" }, { value: "business", label: "Business district" },
  { value: "student", label: "Student area" }, { value: "tourist", label: "Tourist area" },
  { value: "shopping", label: "Shopping area" }, { value: "mixed", label: "Mixed" },
];
const AREA_FEELS = [
  { value: "community", label: "Community" }, { value: "transactional", label: "Transactional" },
  { value: "destination", label: "Destination" }, { value: "passing_trade", label: "Passing trade" },
];
const AREA_DRAWS = [
  { value: "live_here", label: "People live here" }, { value: "work_here", label: "People work here" },
  { value: "shop_here", label: "People come to shop" }, { value: "nightlife", label: "Nightlife" },
  { value: "tourism", label: "Tourism / sightseeing" }, { value: "nature", label: "Nature / outdoors" },
  { value: "passing_through", label: "People pass through" }, { value: "come_for_us", label: "People come specifically for my business" },
];
const TRANSPORT_MODES = [
  { value: "foot", label: "On foot" }, { value: "car", label: "By car" },
  { value: "bike", label: "By bike / scooter" }, { value: "public_transport", label: "Public transport" },
  { value: "mix", label: "Mix of all" },
];
const FIRST_VISIT_REASONS = [
  { value: "walked_past", label: "Walked past" }, { value: "recommended", label: "Friend / family recommendation" },
  { value: "found_online", label: "Found online" }, { value: "social_media", label: "Social media" },
  { value: "knew_brand", label: "Already knew the brand" }, { value: "moved_area", label: "Moved to the area" },
  { value: "one_off_treat", label: "One-off treat" }, { value: "work_nearby", label: "Work brought them nearby" },
];
const SEASONAL_PATTERNS = [
  { value: "year_round", label: "Consistent year-round" }, { value: "summer", label: "Summer peak" },
  { value: "winter", label: "Winter peak" }, { value: "spring", label: "Spring peak" },
  { value: "autumn", label: "Autumn peak" }, { value: "school_holidays", label: "School holiday peaks" },
  { value: "weekend_heavy", label: "Weekend-heavy" }, { value: "weekday_heavy", label: "Weekday-heavy" },
];
const LOCATION_SETTINGS = [
  { value: "city_centre", label: "City centre / Urban" }, { value: "suburban", label: "Suburban" },
  { value: "rural", label: "Rural town / Village" }, { value: "industrial", label: "Industrial / Business park" },
  { value: "retail_park", label: "Retail park / Shopping centre" }, { value: "transport_hub", label: "Airport / Transport hub" },
  { value: "beach", label: "Near a beach" }, { value: "waterfront", label: "Lakeside / Waterfront" },
  { value: "mountain", label: "Mountain / Countryside" }, { value: "tourist_area", label: "Touristy area" },
  { value: "university", label: "University / Campus area" }, { value: "hospital", label: "Hospital / Medical district" },
];
const PRIOR_CHANGE_TYPES = [
  { value: "price", label: "Price change" }, { value: "menu", label: "Menu / product change" },
  { value: "hours", label: "Hours change" }, { value: "location", label: "Location change" },
  { value: "new_service", label: "New service" }, { value: "staff", label: "Staff change" },
  { value: "renovation", label: "Renovation" }, { value: "other", label: "Other" },
];

function Chip({ label, active, onClick, disabled }: { label: string; active: boolean; onClick: () => void; disabled?: boolean }) {
  return (
    <button onClick={onClick} disabled={disabled} className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${active ? "border-brand-orange bg-brand-orange text-white" : disabled ? "border-gray-100 text-gray-300" : "border-[#E5E2DC] text-gray-500 hover:bg-gray-50"}`}>
      {label}
    </button>
  );
}

function GenButton({ label, loading, onClick }: { label: string; loading: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} disabled={loading} className="flex items-center gap-1.5 rounded-md border border-brand-orange/30 px-2.5 py-1 text-xs text-brand-orange transition-colors hover:bg-brand-orange/10 disabled:opacity-50">
      <span>&#10024;</span><span>{loading ? "Generating..." : label}</span>
    </button>
  );
}

function SectionComp({ title, description, children, defaultOpen = false }: { title: string; description?: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-xl border border-[#E5E2DC] bg-white">
      <button onClick={() => setOpen(!open)} className="flex w-full items-center justify-between p-5 text-left">
        <div>
          <h3 className="font-semibold text-black">{title}</h3>
          {description && <p className="mt-0.5 text-sm text-gray-500">{description}</p>}
        </div>
        <svg className={`h-5 w-5 text-gray-400 transition-transform ${open ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="border-t border-[#E5E2DC] p-5">{children}</div>}
    </div>
  );
}

type SettingsTab = "profile" | "notifications" | "privacy" | "billing";

export default function SettingsPage() {
  const router = useRouter();
  const [tab, setTab] = useState<SettingsTab>("profile");
  const [business, setBusiness] = useState<Business | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [email, setEmail] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [bannerDismissed, setBannerDismissed] = useState(false);

  // Autofill
  const [autofillUrl, setAutofillUrl] = useState("");
  const [autofillLoading, setAutofillLoading] = useState(false);
  const [autofillResult, setAutofillResult] = useState<{ found: Record<string, string>; not_found: string[] } | null>(null);

  // Address search
  const [addressQuery, setAddressQuery] = useState("");
  const [addressSuggestions, setAddressSuggestions] = useState<{ description: string; place_id: string }[]>([]);

  // Generate loading
  const [genLoading, setGenLoading] = useState<string | null>(null);

  // Notification preferences
  const [notifSimComplete, setNotifSimComplete] = useState(true);
  const [notifSignals, setNotifSignals] = useState(true);
  const [notifWeekly, setNotifWeekly] = useState(false);
  const [notifMarketing, setNotifMarketing] = useState(false);

  // All fields
  const [name, setName] = useState("");
  const [type, setType] = useState("");
  const [location, setLocation] = useState("");
  const [locationStreet, setLocationStreet] = useState("");
  const [locationNumber, setLocationNumber] = useState("");
  const [locationPostcode, setLocationPostcode] = useState("");
  const [locationCity, setLocationCity] = useState("");
  const [locationNeighbourhood, setLocationNeighbourhood] = useState("");
  const [locationCountry, setLocationCountry] = useState("");
  const [yearsOpen, setYearsOpen] = useState("");
  const [description, setDescription] = useState("");
  const [customerDescription, setCustomerDescription] = useState("");
  const [businessRole, setBusinessRole] = useState("");
  const [visitFrequency, setVisitFrequency] = useState("");
  const [busyDays, setBusyDays] = useState<string[]>([]);
  const [busyTimes, setBusyTimes] = useState<string[]>([]);
  const [valueDrivers, setValueDrivers] = useState<string[]>([]);
  const [socialContext, setSocialContext] = useState<string[]>([]);
  const [regularProportion, setRegularProportion] = useState("");
  const [areaDemographics, setAreaDemographics] = useState<string[]>([]);
  const [competitorCount, setCompetitorCount] = useState("");
  const [areaFeel, setAreaFeel] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");
  const [hasPriorChange, setHasPriorChange] = useState(false);
  const [priorChangeDesc, setPriorChangeDesc] = useState("");
  const [priorChangeOutcome, setPriorChangeOutcome] = useState("");
  // New fields
  const [areaDraws, setAreaDraws] = useState<string[]>([]);
  const [customerTransport, setCustomerTransport] = useState<string[]>([]);
  const [hasParking, setHasParking] = useState("");
  const [firstVisitReasons, setFirstVisitReasons] = useState<string[]>([]);
  const [seasonalPatterns, setSeasonalPatterns] = useState<string[]>([]);
  const [customerCommunity, setCustomerCommunity] = useState("");
  const [locationSettings, setLocationSettings] = useState<string[]>([]);
  const [priorChangeTypes, setPriorChangeTypes] = useState<string[]>([]);
  const [priorChangeWent, setPriorChangeWent] = useState("");
  const [anythingElse, setAnythingElse] = useState("");
  const [googleBusinessUrl, setGoogleBusinessUrl] = useState("");
  const [tripadvisorUrl, setTripadvisorUrl] = useState("");
  const [instagramUrl, setInstagramUrl] = useState("");
  const [facebookUrl, setFacebookUrl] = useState("");
  const [openingHours, setOpeningHours] = useState<Record<string, { open: boolean; opens: string; closes: string }>>({
    mon: { open: false, opens: "08:00", closes: "18:00" }, tue: { open: false, opens: "08:00", closes: "18:00" },
    wed: { open: false, opens: "08:00", closes: "18:00" }, thu: { open: false, opens: "08:00", closes: "18:00" },
    fri: { open: false, opens: "08:00", closes: "18:00" }, sat: { open: false, opens: "09:00", closes: "18:00" },
    sun: { open: false, opens: "10:00", closes: "16:00" },
  });

  useEffect(() => {
    const dismissed = localStorage.getItem("murmur_settings_banner_dismissed");
    if (dismissed) setBannerDismissed(true);
    async function load() {
      try {
        const supabase = createClient();
        const { data: { user } } = await supabase.auth.getUser();
        if (user?.email) setEmail(user.email);
        const businesses = await listBusinesses();
        if (businesses.length > 0) {
          const b = businesses[0];
          setBusiness(b);
          setName(b.name || ""); setType(b.type || ""); setLocation(b.location || "");
          setLocationStreet(b.location_street || ""); setLocationNumber(b.location_number || "");
          setLocationPostcode(b.location_postcode || ""); setLocationCity(b.location_city || "");
          setLocationNeighbourhood(b.location_neighbourhood || ""); setLocationCountry(b.location_country || "");
          setYearsOpen(b.years_open || ""); setDescription(b.description || "");
          setCustomerDescription(b.customer_description || "");
          setBusinessRole(b.business_role || ""); setVisitFrequency(b.visit_frequency || "");
          setBusyDays(b.busy_days || []); setBusyTimes(b.busy_times || []);
          setValueDrivers(b.customer_value_drivers || []);
          setSocialContext(b.customer_social_context || []);
          setRegularProportion(b.regular_proportion || "");
          setAreaDemographics(b.area_demographics || []); setCompetitorCount(b.competitor_count || "");
          setAreaFeel(b.area_feel || ""); setWebsiteUrl(b.website_url || "");
          setAdditionalNotes(b.additional_customer_notes || "");
          setHasPriorChange(b.has_prior_change || false);
          setPriorChangeDesc(b.prior_change_description || "");
          setPriorChangeOutcome(b.prior_change_outcome || "");
          setLocationSettings(b.location_settings || []);
          setAreaDraws(b.area_draws || []);
          setCustomerTransport(b.customer_transport || []);
          setHasParking(b.has_parking || "");
          setFirstVisitReasons(b.first_visit_reasons || []);
          setSeasonalPatterns(b.seasonal_patterns || []);
          setCustomerCommunity(b.customer_community || "");
          if (b.opening_hours) setOpeningHours(b.opening_hours);
          setGoogleBusinessUrl(b.google_business_url || "");
          setTripadvisorUrl(b.tripadvisor_url || "");
          setInstagramUrl(b.instagram_url || "");
          setFacebookUrl(b.facebook_url || "");
          setPriorChangeTypes(b.prior_change_types || []);
          setPriorChangeWent(b.prior_change_went || "");
          setAnythingElse(b.anything_else || "");
        }
      } catch { /* */ }
      finally { setLoading(false); }
    }
    load();
  }, []);

  const toggleArr = (arr: string[], val: string, setter: (v: string[]) => void) => {
    setter(arr.includes(val) ? arr.filter((v) => v !== val) : [...arr, val]);
  };

  // Autofill handler
  const handleAutofill = async () => {
    if (!autofillUrl.trim()) return;
    setAutofillLoading(true);
    try {
      const result = await researchBusiness(autofillUrl.trim());
      const found: Record<string, string> = {};
      const notFound: string[] = [];
      for (const [k, v] of Object.entries(result)) {
        if (v && String(v).trim() && k !== "confidence") found[k] = String(v);
        else if (k !== "confidence") notFound.push(k);
      }
      setAutofillResult({ found, not_found: notFound });
    } catch {
      setAutofillResult({ found: {}, not_found: ["everything"] });
    }
    setAutofillLoading(false);
  };

  const applyAutofill = () => {
    if (!autofillResult) return;
    const f = autofillResult.found;
    if (f.name) setName(f.name);
    if (f.type) setType(f.type);
    if (f.description) setDescription(f.description);
    if (f.formatted_address) setLocation(f.formatted_address);
    if (f.website) setWebsiteUrl(f.website);
    if (f.years_open_estimate) setYearsOpen(f.years_open_estimate);
    setAutofillResult(null);
    setAutofillUrl("");
  };

  // Address autocomplete
  const handleAddressSearch = async (q: string) => {
    setAddressQuery(q);
    if (q.length < 3) { setAddressSuggestions([]); return; }
    try {
      const result = await placeAutocomplete(q);
      setAddressSuggestions(result.predictions || []);
    } catch { setAddressSuggestions([]); }
  };

  const handleAddressSelect = async (placeId: string) => {
    setAddressSuggestions([]);
    setAddressQuery("");
    try {
      const details = await placeDetails(placeId);
      if (details.street) setLocationStreet(details.street as string);
      if (details.number) setLocationNumber(details.number as string);
      if (details.postcode) setLocationPostcode(details.postcode as string);
      if (details.city) setLocationCity(details.city as string);
      if (details.neighbourhood) setLocationNeighbourhood(details.neighbourhood as string);
      if (details.country) setLocationCountry(details.country as string);
    } catch { /* */ }
  };

  // Generate handlers
  const handleGenDescription = async () => {
    setGenLoading("description");
    try {
      const result = await generateDescription({ name, type, location: locationCity || location, years_open: yearsOpen });
      setDescription(result.description);
    } catch { /* */ }
    setGenLoading(null);
  };

  const handleGenCustomerDesc = async () => {
    setGenLoading("customer");
    try {
      const result = await generateCustomerDescription({ business_name: name, business_type: type, location: locationCity || location, business_description: description });
      setCustomerDescription(result.description);
    } catch { /* */ }
    setGenLoading(null);
  };

  async function handleSave() {
    if (!business) return;
    setSaving(true); setSaved(false);
    try {
      const data: BusinessCreate = {
        name, type, description,
        location: [locationStreet, locationNumber, locationPostcode, locationCity, locationCountry].filter(Boolean).join(", ") || location || undefined,
        location_street: locationStreet || undefined, location_number: locationNumber || undefined,
        location_postcode: locationPostcode || undefined, location_city: locationCity || undefined,
        location_neighbourhood: locationNeighbourhood || undefined, location_country: locationCountry || undefined,
        years_open: yearsOpen || undefined, customer_description: customerDescription || undefined,
        business_role: businessRole || undefined, visit_frequency: visitFrequency || undefined,
        busy_days: busyDays.length ? busyDays : undefined, busy_times: busyTimes.length ? busyTimes : undefined,
        customer_value_drivers: valueDrivers.length ? valueDrivers : undefined,
        customer_social_context: socialContext.length ? socialContext : undefined,
        regular_proportion: regularProportion || undefined,
        area_demographics: areaDemographics.length ? areaDemographics : undefined,
        competitor_count: competitorCount || undefined, area_feel: areaFeel || undefined,
        website_url: websiteUrl || undefined, additional_customer_notes: additionalNotes || undefined,
        has_prior_change: hasPriorChange, prior_change_description: priorChangeDesc || undefined,
        prior_change_outcome: priorChangeOutcome || undefined,
        location_settings: locationSettings.length ? locationSettings : undefined,
        area_draws: areaDraws.length ? areaDraws : undefined,
        customer_transport: customerTransport.length ? customerTransport : undefined,
        has_parking: hasParking || undefined,
        first_visit_reasons: firstVisitReasons.length ? firstVisitReasons : undefined,
        seasonal_patterns: seasonalPatterns.length ? seasonalPatterns : undefined,
        customer_community: customerCommunity || undefined,
        opening_hours: openingHours,
        google_business_url: googleBusinessUrl || undefined,
        tripadvisor_url: tripadvisorUrl || undefined,
        instagram_url: instagramUrl || undefined,
        facebook_url: facebookUrl || undefined,
        prior_change_types: priorChangeTypes.length ? priorChangeTypes : undefined,
        prior_change_went: priorChangeWent || undefined,
        anything_else: anythingElse || undefined,
      };
      const result = await updateBusiness(business.id, data);
      setBusiness(result); setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) { console.error("Save failed", e); }
    finally { setSaving(false); }
  }

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/"); router.refresh();
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-gray-400">Loading...</p></div>;

  const tabs: { key: SettingsTab; label: string }[] = [
    { key: "profile", label: "Profile" }, { key: "notifications", label: "Notifications" },
    { key: "privacy", label: "Privacy & Security" }, { key: "billing", label: "Billing" },
  ];

  const TIMES = Array.from({ length: 48 }, (_, i) => {
    const h = String(Math.floor(i / 2)).padStart(2, "0");
    const m = i % 2 === 0 ? "00" : "30";
    return `${h}:${m}`;
  });

  return (
    <div className="overflow-y-auto p-8 lg:p-12">
      <div className="mx-auto max-w-4xl">
        <h1 className="mb-1 text-2xl font-bold text-black">Settings</h1>
        <p className="mb-6 text-gray-500">Manage your profile, business, and preferences.</p>

        <div className="mb-8 flex gap-1 overflow-x-auto border-b border-[#E5E2DC]">
          {tabs.map((t) => (
            <button key={t.key} onClick={() => setTab(t.key)} className={`whitespace-nowrap px-5 py-2.5 text-sm font-medium ${tab === t.key ? "border-b-2 border-brand-orange text-black" : "text-gray-400"}`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* ====== PROFILE TAB ====== */}
        {tab === "profile" && (
          <div className="space-y-4">
            {/* Change 4: Notification banner */}
            {!bannerDismissed && (
              <div className="relative rounded-xl border-l-4 border-brand-blue bg-brand-blue/5 p-4 pr-10">
                <button onClick={() => { setBannerDismissed(true); localStorage.setItem("murmur_settings_banner_dismissed", "1"); }} className="absolute right-3 top-3 text-gray-400 hover:text-black">x</button>
                <p className="text-sm font-medium text-black">The more you fill in, the more accurate Murmur&apos;s simulations become.</p>
                <div className="mt-2 space-y-1 text-xs text-gray-500">
                  <p>Basic info -- general reactions</p>
                  <p>Customer profile -- specific behaviour patterns</p>
                  <p>Local area + context -- full simulation accuracy</p>
                </div>
              </div>
            )}

            {/* Change 1: URL finder */}
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-1 font-semibold text-black">Find your business online</h3>
              <p className="mb-3 text-xs text-gray-400">Paste your Google Maps link, website, or Google Business URL and we&apos;ll auto-fill your business details.</p>
              <div className="flex gap-2">
                <input value={autofillUrl} onChange={(e) => setAutofillUrl(e.target.value)} placeholder="https://..." className="flex-1 rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                <button onClick={handleAutofill} disabled={autofillLoading || !autofillUrl.trim()} className="shrink-0 rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:opacity-80 disabled:opacity-50">
                  {autofillLoading ? "Researching..." : "Find & auto-fill"}
                </button>
              </div>
              <p className="mt-2 text-[10px] text-gray-300">Accepts: Website URL -- Google Maps link -- Google Business Profile URL</p>

              {/* Autofill confirmation */}
              {autofillResult && (
                <div className="mt-4 rounded-lg border border-[#E5E2DC] bg-gray-50 p-4">
                  {Object.keys(autofillResult.found).length > 0 ? (
                    <>
                      <p className="mb-3 text-sm font-medium text-black">We found your business -- does this look right?</p>
                      <div className="space-y-1.5 text-sm">
                        {Object.entries(autofillResult.found).map(([k, v]) => (
                          <div key={k} className="flex items-start gap-2">
                            <span className="mt-0.5 text-green-500">&#10003;</span>
                            <span className="text-gray-600"><span className="font-medium text-black">{k.replace(/_/g, " ")}:</span> {String(v).slice(0, 100)}</span>
                          </div>
                        ))}
                        {autofillResult.not_found.filter((f) => !["confidence", "error"].includes(f)).map((f) => (
                          <div key={f} className="flex items-start gap-2">
                            <span className="mt-0.5 text-gray-300">&#10007;</span>
                            <span className="text-gray-400">{f.replace(/_/g, " ")}: Couldn&apos;t retrieve</span>
                          </div>
                        ))}
                      </div>
                      <div className="mt-4 flex gap-2">
                        <button onClick={applyAutofill} className="rounded-lg bg-black px-4 py-1.5 text-sm font-medium text-white hover:opacity-80">Apply these fields</button>
                        <button onClick={() => setAutofillResult(null)} className="text-sm text-gray-400">Cancel</button>
                      </div>
                    </>
                  ) : (
                    <p className="text-sm text-gray-500">We couldn&apos;t find that business. Try a different URL or fill in manually.</p>
                  )}
                </div>
              )}
            </div>

            {/* Account info */}
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 font-semibold text-black">Account</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div><label className="mb-1 block text-xs text-gray-500">Email</label>
                  <input value={email} className="w-full rounded-lg border border-[#E5E2DC] bg-gray-50 px-3 py-2 text-sm" disabled /></div>
                <div><label className="mb-1 block text-xs text-gray-500">Password</label>
                  <button className="mt-1 text-sm text-brand-blue hover:underline">Change password</button></div>
              </div>
            </div>

            {/* Business profile summary */}
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <div className="mb-1 flex items-center justify-between">
                <h3 className="font-semibold text-black">Business profile</h3>
                {business && <span className="rounded-full bg-green-50 px-2 py-0.5 text-[10px] font-medium text-green-600">Active</span>}
              </div>
              <p className="mb-4 text-sm text-gray-500">{name || "No business"}{type ? ` -- ${ALL_TYPE_OPTIONS.find((o) => o.value === type)?.label || type}` : ""}{locationCity ? ` in ${locationCity}` : ""}</p>
              <p className="text-xs text-gray-400">Edit the sections below to update your business profile. Changes improve simulation accuracy.</p>
            </div>

            {/* === BUSINESS DETAILS === */}
            <SectionComp title="Business details" description="Name, type, location, and description" defaultOpen>
              <div className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div><label className="mb-1 block text-xs text-gray-500">Business name</label>
                    <input value={name} onChange={(e) => setName(e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                  <div><label className="mb-1 block text-xs text-gray-500">Business type</label>
                    {/* Change 5: Expanded with optgroups */}
                    <select value={type} onChange={(e) => setType(e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none">
                      <option value="">Select...</option>
                      {BUSINESS_TYPE_GROUPS.map((g) => (
                        <optgroup key={g.label} label={g.label}>
                          {g.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                        </optgroup>
                      ))}
                    </select></div>
                  <div><label className="mb-1 block text-xs text-gray-500">Years open</label>
                    <div className="flex gap-1.5">
                      {["<1", "1-3", "3-10", "10+"].map((v) => <Chip key={v} label={v} active={yearsOpen === v} onClick={() => setYearsOpen(v)} />)}
                    </div></div>
                </div>

                {/* Change 2: Address search */}
                <div>
                  <label className="mb-2 block text-xs font-medium text-gray-500">Address</label>
                  <div className="relative mb-3">
                    <input value={addressQuery} onChange={(e) => handleAddressSearch(e.target.value)} placeholder="Search your address..." className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                    {addressSuggestions.length > 0 && (
                      <div className="absolute left-0 right-0 top-full z-10 mt-1 rounded-lg border border-[#E5E2DC] bg-white shadow-lg">
                        {addressSuggestions.map((s) => (
                          <button key={s.place_id} onClick={() => handleAddressSelect(s.place_id)} className="block w-full px-3 py-2 text-left text-sm text-black hover:bg-gray-50">
                            {s.description}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="grid gap-3 sm:grid-cols-4">
                    <div className="sm:col-span-2"><input value={locationStreet} onChange={(e) => setLocationStreet(e.target.value)} placeholder="Street" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                    <div><input value={locationNumber} onChange={(e) => setLocationNumber(e.target.value)} placeholder="Number" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                    <div><input value={locationPostcode} onChange={(e) => setLocationPostcode(e.target.value)} placeholder="Postcode" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                    <div><input value={locationCity} onChange={(e) => setLocationCity(e.target.value)} placeholder="City" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                    <div><input value={locationNeighbourhood} onChange={(e) => setLocationNeighbourhood(e.target.value)} placeholder="Neighbourhood" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                    <div className="sm:col-span-2"><input value={locationCountry} onChange={(e) => setLocationCountry(e.target.value)} placeholder="Country" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                  </div>
                  <p className="mt-1 text-[10px] text-gray-300">Filled automatically from search above -- edit if needed</p>
                </div>

                {/* Change 6: Location setting */}
                <div>
                  <label className="mb-2 block text-xs text-gray-500">What kind of location are you in?</label>
                  <div className="flex flex-wrap gap-1.5">
                    {LOCATION_SETTINGS.map((ls) => <Chip key={ls.value} label={ls.label} active={locationSettings.includes(ls.value)} onClick={() => toggleArr(locationSettings, ls.value, setLocationSettings)} />)}
                  </div>
                  <p className="mt-1 text-[10px] text-gray-300">Helps us understand whether customers have alternatives nearby</p>
                </div>

                {/* Change 3: Description with generate */}
                <div>
                  <div className="mb-1 flex items-center justify-between">
                    <label className="text-xs text-gray-500">Description</label>
                    <GenButton label="Generate from my business details" loading={genLoading === "description"} onClick={handleGenDescription} />
                  </div>
                  <textarea rows={3} value={description} onChange={(e) => setDescription(e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                  {genLoading === null && description && <p className="text-[10px] text-gray-300">AI generated -- edit to make it yours</p>}
                </div>

                <div><label className="mb-1 block text-xs text-gray-500">Website</label>
                  <input value={websiteUrl} onChange={(e) => setWebsiteUrl(e.target.value)} placeholder="https://..." className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>

                {/* Change 11: Opening hours */}
                <div>
                  <label className="mb-2 block text-xs text-gray-500">When are you open?</label>
                  <p className="mb-2 text-[10px] text-gray-300">Critical for simulating reactions to hour changes</p>
                  <div className="space-y-1.5">
                    <div className="grid grid-cols-4 gap-2 text-[10px] font-medium text-gray-400">
                      <span>Day</span><span>Open?</span><span>Opens</span><span>Closes</span>
                    </div>
                    {["mon", "tue", "wed", "thu", "fri", "sat", "sun"].map((day) => (
                      <div key={day} className="grid grid-cols-4 items-center gap-2">
                        <span className="text-xs font-medium text-black">{day.charAt(0).toUpperCase() + day.slice(1)}</span>
                        <input type="checkbox" checked={openingHours[day]?.open || false} onChange={(e) => setOpeningHours((prev) => ({ ...prev, [day]: { ...prev[day], open: e.target.checked } }))} className="h-4 w-4 accent-brand-orange" />
                        <select value={openingHours[day]?.opens || "08:00"} disabled={!openingHours[day]?.open} onChange={(e) => setOpeningHours((prev) => ({ ...prev, [day]: { ...prev[day], opens: e.target.value } }))} className="rounded border border-[#E5E2DC] px-2 py-1 text-xs disabled:opacity-30">
                          {TIMES.map((t) => <option key={t} value={t}>{t}</option>)}
                        </select>
                        <select value={openingHours[day]?.closes || "18:00"} disabled={!openingHours[day]?.open} onChange={(e) => setOpeningHours((prev) => ({ ...prev, [day]: { ...prev[day], closes: e.target.value } }))} className="rounded border border-[#E5E2DC] px-2 py-1 text-xs disabled:opacity-30">
                          {TIMES.map((t) => <option key={t} value={t}>{t}</option>)}
                        </select>
                      </div>
                    ))}
                  </div>
                  <button onClick={() => {
                    const monHours = openingHours.mon;
                    setOpeningHours((prev) => ({
                      ...prev,
                      tue: { ...monHours }, wed: { ...monHours }, thu: { ...monHours }, fri: { ...monHours },
                    }));
                  }} className="mt-2 text-[10px] text-brand-blue hover:underline">Copy Mon to all weekdays</button>
                </div>

                {/* Change 12: Social presence */}
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Where are you online?</label>
                  <p className="mb-2 text-[10px] text-gray-300">We use these to research how your customers already talk about you</p>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div><input value={googleBusinessUrl} onChange={(e) => setGoogleBusinessUrl(e.target.value)} placeholder="Google Business Profile URL" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                    <div><input value={tripadvisorUrl} onChange={(e) => setTripadvisorUrl(e.target.value)} placeholder="TripAdvisor page URL" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                    <div><input value={instagramUrl} onChange={(e) => setInstagramUrl(e.target.value)} placeholder="Instagram @handle or URL" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                    <div><input value={facebookUrl} onChange={(e) => setFacebookUrl(e.target.value)} placeholder="Facebook page URL" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
                  </div>
                </div>
              </div>
            </SectionComp>

            {/* === CUSTOMER PROFILE === */}
            <SectionComp title="Customer profile" description="Who your customers are and what they value">
              <div className="space-y-5">
                <div>
                  <div className="mb-1 flex items-center justify-between">
                    <label className="text-xs text-gray-500">Describe your typical customer</label>
                    <GenButton label="Generate from my business profile" loading={genLoading === "customer"} onClick={handleGenCustomerDesc} />
                  </div>
                  <textarea rows={3} value={customerDescription} onChange={(e) => setCustomerDescription(e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                </div>
                <div><label className="mb-2 block text-xs text-gray-500">Role your business plays in their life</label>
                  <div className="flex flex-wrap gap-1.5">{BUSINESS_ROLES.map((r) => <Chip key={r.value} label={r.label} active={businessRole === r.value} onClick={() => setBusinessRole(r.value)} />)}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">Visit frequency</label>
                  <div className="flex flex-wrap gap-1.5">{[{ v: "daily", l: "Daily" }, { v: "weekly", l: "Weekly" }, { v: "monthly", l: "Monthly" }, { v: "occasional", l: "Occasional" }, { v: "mixed", l: "Mixed" }].map((o) => <Chip key={o.v} label={o.l} active={visitFrequency === o.v} onClick={() => setVisitFrequency(o.v)} />)}</div></div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div><label className="mb-2 block text-xs text-gray-500">Busiest days</label>
                    <div className="flex flex-wrap gap-1.5">{["mon", "tue", "wed", "thu", "fri", "sat", "sun"].map((d) => <Chip key={d} label={d.charAt(0).toUpperCase() + d.slice(1)} active={busyDays.includes(d)} onClick={() => toggleArr(busyDays, d, setBusyDays)} />)}</div></div>
                  <div><label className="mb-2 block text-xs text-gray-500">Busiest times</label>
                    <div className="flex flex-wrap gap-1.5">{["morning", "lunchtime", "afternoon", "evening", "late night"].map((t) => <Chip key={t} label={t.charAt(0).toUpperCase() + t.slice(1)} active={busyTimes.includes(t)} onClick={() => toggleArr(busyTimes, t, setBusyTimes)} />)}</div></div>
                </div>
                <div><label className="mb-2 block text-xs text-gray-500">What do they value most? (up to 3)</label>
                  <div className="flex flex-wrap gap-1.5">{VALUE_DRIVERS.map((vd) => { const a = valueDrivers.includes(vd.value); const m = valueDrivers.length >= 3 && !a; return <Chip key={vd.value} label={vd.label} active={a} disabled={m} onClick={() => !m && toggleArr(valueDrivers, vd.value, setValueDrivers)} />; })}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">Social setup</label>
                  <div className="flex flex-wrap gap-1.5">{["on_their_own", "with_a_partner", "with_family_kids", "with_friends", "with_work_colleagues", "changes_a_lot"].map((v) => <Chip key={v} label={v.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase())} active={socialContext.includes(v)} onClick={() => toggleArr(socialContext, v, setSocialContext)} />)}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">How many regulars?</label>
                  <div className="flex flex-wrap gap-1.5">{[{ v: "almost_none", l: "Almost none" }, { v: "handful", l: "A handful" }, { v: "solid_base", l: "Solid base (50+)" }, { v: "mostly_regulars", l: "Mostly regulars" }].map((o) => <Chip key={o.v} label={o.l} active={regularProportion === o.v} onClick={() => setRegularProportion(o.v)} />)}</div></div>
                {/* Change 8: New customer fields */}
                <div><label className="mb-2 block text-xs text-gray-500">How do people first find you?</label>
                  <p className="mb-1 text-[10px] text-gray-300">Word-of-mouth customers tend to be more loyal than walk-ins</p>
                  <div className="flex flex-wrap gap-1.5">{FIRST_VISIT_REASONS.map((r) => <Chip key={r.value} label={r.label} active={firstVisitReasons.includes(r.value)} onClick={() => toggleArr(firstVisitReasons, r.value, setFirstVisitReasons)} />)}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">Seasonal patterns</label>
                  <div className="flex flex-wrap gap-1.5">{SEASONAL_PATTERNS.map((p) => <Chip key={p.value} label={p.label} active={seasonalPatterns.includes(p.value)} onClick={() => toggleArr(seasonalPatterns, p.value, setSeasonalPatterns)} />)}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">Do most customers know each other?</label>
                  <p className="mb-1 text-[10px] text-gray-300">Community businesses amplify both positive and negative reactions through word of mouth</p>
                  <div className="flex flex-wrap gap-1.5">{[
                    { v: "community", l: "Yes -- real community, regulars interact" },
                    { v: "some", l: "Some do -- small groups" },
                    { v: "not_really", l: "Not really -- mostly strangers" },
                    { v: "anonymous", l: "Completely anonymous" },
                  ].map((o) => <Chip key={o.v} label={o.l} active={customerCommunity === o.v} onClick={() => setCustomerCommunity(o.v)} />)}</div></div>
              </div>
            </SectionComp>

            {/* === LOCAL AREA === */}
            <SectionComp title="Local area" description="Your neighbourhood and competition">
              <div className="space-y-5">
                <div><label className="mb-2 block text-xs text-gray-500">Area type (select all)</label>
                  <div className="flex flex-wrap gap-1.5">{AREA_TYPES.map((at) => <Chip key={at.value} label={at.label} active={areaDemographics.includes(at.value)} onClick={() => toggleArr(areaDemographics, at.value, setAreaDemographics)} />)}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">Competition</label>
                  <div className="flex flex-wrap gap-1.5">{[{ v: "only_one", l: "Only one" }, { v: "one_two", l: "1-2 others" }, { v: "three_five", l: "3-5" }, { v: "six_plus", l: "6+" }].map((o) => <Chip key={o.v} label={o.l} active={competitorCount === o.v} onClick={() => setCompetitorCount(o.v)} />)}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">Area feel</label>
                  <div className="flex flex-wrap gap-1.5">{AREA_FEELS.map((af) => <Chip key={af.value} label={af.label} active={areaFeel === af.value} onClick={() => setAreaFeel(af.value)} />)}</div></div>
                {/* Change 7: New area fields */}
                <div><label className="mb-2 block text-xs text-gray-500">What draws people to your area?</label>
                  <div className="flex flex-wrap gap-1.5">{AREA_DRAWS.map((d) => <Chip key={d.value} label={d.label} active={areaDraws.includes(d.value)} onClick={() => toggleArr(areaDraws, d.value, setAreaDraws)} />)}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">How do most customers get to you?</label>
                  <p className="mb-1 text-[10px] text-gray-300">Affects sensitivity to changes in opening hours, location, or parking</p>
                  <div className="flex flex-wrap gap-1.5">{TRANSPORT_MODES.map((t) => <Chip key={t.value} label={t.label} active={customerTransport.includes(t.value)} onClick={() => toggleArr(customerTransport, t.value, setCustomerTransport)} />)}</div></div>
                <div><label className="mb-2 block text-xs text-gray-500">Parking available nearby?</label>
                  <div className="flex flex-wrap gap-1.5">{[
                    { v: "free", l: "Yes -- free parking" }, { v: "paid", l: "Yes -- paid parking" },
                    { v: "limited", l: "Limited / street only" }, { v: "none", l: "No -- pedestrian/transport only" },
                  ].map((o) => <Chip key={o.v} label={o.l} active={hasParking === o.v} onClick={() => setHasParking(o.v)} />)}</div></div>
              </div>
            </SectionComp>

            {/* === EXTRA CONTEXT === */}
            <SectionComp title="Extra context" description="Notes, prior changes, and additional details">
              <div className="space-y-5">
                <div>
                  <div className="mb-1 flex items-center justify-between">
                    <label className="text-xs text-gray-500">Additional customer notes</label>
                    <GenButton label="Suggest based on my profile" loading={genLoading === "notes"} onClick={async () => {
                      setGenLoading("notes");
                      try {
                        const result = await generateCustomerDescription({ business_name: name, business_type: type, location: locationCity, business_description: description });
                        setAdditionalNotes(result.description);
                      } catch { /* */ }
                      setGenLoading(null);
                    }} />
                  </div>
                  <textarea rows={3} value={additionalNotes} onChange={(e) => setAdditionalNotes(e.target.value)} placeholder="Anything else about your customers..." className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                </div>
                {/* Change 9: Expanded prior change */}
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Have you made a big change before?</label>
                  <div className="flex gap-1.5">
                    <Chip label="Yes" active={hasPriorChange} onClick={() => setHasPriorChange(true)} />
                    <Chip label="No" active={!hasPriorChange} onClick={() => setHasPriorChange(false)} />
                  </div>
                  {hasPriorChange && (
                    <div className="mt-3 space-y-3 rounded-lg border border-[#E5E2DC] bg-gray-50 p-4">
                      <div><label className="mb-1 block text-[10px] text-gray-500">What kind of change?</label>
                        <div className="flex flex-wrap gap-1.5">{PRIOR_CHANGE_TYPES.map((c) => <Chip key={c.value} label={c.label} active={priorChangeTypes.includes(c.value)} onClick={() => toggleArr(priorChangeTypes, c.value, setPriorChangeTypes)} />)}</div></div>
                      <div><label className="mb-1 block text-[10px] text-gray-500">What did you change?</label>
                        <input value={priorChangeDesc} onChange={(e) => setPriorChangeDesc(e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] bg-white px-3 py-2 text-sm" /></div>
                      <div><label className="mb-1 block text-[10px] text-gray-500">What happened?</label>
                        <textarea rows={2} value={priorChangeOutcome} onChange={(e) => setPriorChangeOutcome(e.target.value)} placeholder="Describe customer reaction..." className="w-full rounded-lg border border-[#E5E2DC] bg-white px-3 py-2 text-sm" /></div>
                      <div><label className="mb-1 block text-[10px] text-gray-500">Would you say it went:</label>
                        <div className="flex gap-1.5">
                          {[{ v: "better", l: "Better than expected" }, { v: "expected", l: "About as expected" }, { v: "worse", l: "Worse than expected" }].map((o) => (
                            <Chip key={o.v} label={o.l} active={priorChangeWent === o.v} onClick={() => setPriorChangeWent(o.v)} />
                          ))}
                        </div></div>
                      <p className="text-[10px] text-gray-400">We use this to calibrate future simulations for your business.</p>
                    </div>
                  )}
                </div>
                <div><label className="mb-1 block text-xs text-gray-500">Anything else about your business we should know?</label>
                  <textarea rows={2} value={anythingElse} onChange={(e) => setAnythingElse(e.target.value)} placeholder='e.g. "We cater heavily to the over-60s" or "We are the only option within 5km"' className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" /></div>
              </div>
            </SectionComp>

            {/* Save */}
            <div className="flex items-center gap-3 pt-2">
              <button onClick={handleSave} disabled={saving} className="rounded-lg bg-black px-6 py-2.5 text-sm font-medium text-white hover:opacity-80 disabled:opacity-50">
                {saving ? "Saving..." : "Save all changes"}
              </button>
              {saved && <span className="text-sm text-green-600">All changes saved</span>}
            </div>
          </div>
        )}

        {/* ====== NOTIFICATIONS ====== */}
        {tab === "notifications" && (
          <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
            <h3 className="mb-4 font-semibold text-black">Email notifications</h3>
            <div className="space-y-4">
              {[
                { label: "Simulation complete", desc: "Get notified when a simulation finishes", state: notifSimComplete, setter: setNotifSimComplete },
                { label: "Relationship signals", desc: "Alerts when sentiment changes or signals detected", state: notifSignals, setter: setNotifSignals },
                { label: "Weekly digest", desc: "Summary of simulations, twin activity, and portfolio health", state: notifWeekly, setter: setNotifWeekly },
                { label: "Product updates", desc: "New features, improvements, and tips", state: notifMarketing, setter: setNotifMarketing },
              ].map((n) => (
                <div key={n.label} className="flex items-center justify-between">
                  <div><p className="text-sm font-medium text-black">{n.label}</p><p className="text-xs text-gray-500">{n.desc}</p></div>
                  <button onClick={() => n.setter(!n.state)} className={`relative h-6 w-11 rounded-full transition-colors ${n.state ? "bg-brand-orange" : "bg-gray-200"}`}>
                    <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${n.state ? "left-[22px]" : "left-0.5"}`} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ====== PRIVACY ====== */}
        {tab === "privacy" && (
          <div className="space-y-4">
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 font-semibold text-black">Data & Privacy</h3>
              <div className="space-y-4 text-sm">
                <div className="flex items-center justify-between">
                  <div><p className="font-medium text-black">Export your data</p><p className="text-xs text-gray-500">Download all your data</p></div>
                  <button className="rounded-lg border border-[#E5E2DC] px-4 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50">Export</button>
                </div>
                <div className="border-t border-[#E5E2DC] pt-4"><p className="font-medium text-black">How we handle your data</p>
                  <ul className="mt-2 space-y-1.5 text-xs text-gray-500">
                    <li>-- Your data is stored securely in Supabase (EU region)</li>
                    <li>-- Uploaded correspondence is processed in memory and deleted immediately</li>
                    <li>-- Only anonymised patterns are stored for twins</li>
                    <li>-- We never sell or share your data</li>
                  </ul></div>
              </div>
            </div>
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 font-semibold text-black">Security</h3>
              <div className="space-y-4 text-sm">
                <div className="flex items-center justify-between">
                  <div><p className="font-medium text-black">Change password</p></div>
                  <button className="rounded-lg border border-[#E5E2DC] px-4 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50">Change</button>
                </div>
                <div className="flex items-center justify-between border-t border-[#E5E2DC] pt-4">
                  <div><p className="font-medium text-black">Sign out</p></div>
                  <button onClick={handleSignOut} className="rounded-lg border border-[#E5E2DC] px-4 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50">Sign out</button>
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-red-200 bg-red-50/50 p-5">
              <h3 className="mb-2 font-semibold text-red-700">Danger zone</h3>
              <p className="mb-4 text-sm text-red-600/70">Permanently delete your account and all data. This cannot be undone.</p>
              {showDeleteConfirm ? (
                <div className="flex gap-3"><button onClick={() => setShowDeleteConfirm(false)} className="rounded-lg border border-[#E5E2DC] px-4 py-1.5 text-xs text-gray-600">Cancel</button>
                  <button onClick={async () => {
                    try {
                      await deleteAccount();
                      const supabase = createClient();
                      await supabase.auth.signOut();
                      router.push("/");
                      router.refresh();
                    } catch { alert("Failed to delete account"); }
                  }} className="rounded-lg bg-red-600 px-4 py-1.5 text-xs font-medium text-white">Yes, delete everything</button></div>
              ) : (<button onClick={() => setShowDeleteConfirm(true)} className="rounded-lg border border-red-300 px-4 py-1.5 text-xs font-medium text-red-600 hover:bg-red-100">Delete account</button>)}
            </div>
          </div>
        )}

        {/* ====== BILLING ====== */}
        {tab === "billing" && (
          <div className="space-y-4">
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-2 font-semibold text-black">Current plan</h3>
              <span className="rounded-full bg-brand-blue/10 px-3 py-1 text-sm font-medium text-brand-blue">Simulate (Free)</span>
              <p className="mt-3 text-sm text-gray-500">5 simulations per month. No CRM access.</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border-2 border-brand-orange/30 bg-brand-orange/5 p-6">
                <h4 className="font-semibold text-black">Connect</h4>
                <p className="mt-1 text-2xl font-bold text-black">49 EUR<span className="text-sm font-normal text-gray-500">/month</span></p>
                <ul className="mt-3 space-y-1 text-sm text-gray-600"><li>Unlimited simulations</li><li>50 contacts</li><li>Digital twins</li></ul>
                <button className="mt-4 w-full rounded-lg bg-brand-orange px-4 py-2 text-sm font-medium text-white hover:opacity-90">Upgrade</button>
              </div>
              <div className="rounded-xl border-2 border-brand-pink/30 bg-brand-pink/5 p-6">
                <h4 className="font-semibold text-black">Intelligence</h4>
                <p className="mt-1 text-2xl font-bold text-black">199 EUR<span className="text-sm font-normal text-gray-500">/month</span></p>
                <ul className="mt-3 space-y-1 text-sm text-gray-600"><li>Everything in Connect</li><li>Unlimited contacts</li><li>Organisation intelligence</li></ul>
                <button className="mt-4 w-full rounded-lg bg-brand-pink px-4 py-2 text-sm font-medium text-white hover:opacity-90">Upgrade</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
