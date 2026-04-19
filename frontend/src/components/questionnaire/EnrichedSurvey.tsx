"use client";

import { useState, useEffect, useRef } from "react";
import {
  BusinessCreate,
  researchBusiness,
  generateDescription,
  generateCustomerDescription,
  placeAutocomplete,
  placeDetails,
} from "@/lib/api";

interface Props {
  onSubmit: (data: BusinessCreate) => void;
  loading?: boolean;
}

const BUSINESS_SECTORS: { value: string; label: string; types: { value: string; label: string }[] }[] = [
  { value: "food_drink", label: "Food & Drink", types: [
    { value: "restaurant", label: "Restaurant" }, { value: "cafe", label: "Cafe / Coffee Shop" },
    { value: "bar", label: "Bar / Pub" }, { value: "bakery", label: "Bakery" },
    { value: "food_truck", label: "Food Truck" }, { value: "catering", label: "Catering" },
    { value: "desserts", label: "Desserts / Ice Cream" }, { value: "pizzeria", label: "Pizzeria" },
    { value: "sushi", label: "Sushi / Japanese" }, { value: "fast_food", label: "Fast Food" },
    { value: "fine_dining", label: "Fine Dining" }, { value: "juice_bar", label: "Juice Bar / Smoothies" },
    { value: "food_delivery", label: "Food Delivery / Ghost Kitchen" }, { value: "brewery", label: "Brewery / Taproom" },
    { value: "winery", label: "Winery / Wine Bar" },
  ]},
  { value: "health_wellness", label: "Health & Wellness", types: [
    { value: "barbershop", label: "Barbershop" }, { value: "hair_salon", label: "Hair Salon" },
    { value: "nail_salon", label: "Nail Salon" }, { value: "spa", label: "Spa / Massage" },
    { value: "tattoo", label: "Tattoo Studio" }, { value: "gym", label: "Gym / Fitness" },
    { value: "yoga", label: "Yoga / Pilates" }, { value: "physio", label: "Physiotherapy" },
    { value: "personal_trainer", label: "Personal Trainer" }, { value: "crossfit", label: "CrossFit" },
    { value: "martial_arts", label: "Martial Arts" }, { value: "dance_studio", label: "Dance Studio" },
    { value: "meditation_studio", label: "Meditation Studio" }, { value: "beauty_salon", label: "Beauty Salon" },
    { value: "tanning", label: "Tanning Salon" },
  ]},
  { value: "retail", label: "Retail", types: [
    { value: "grocery", label: "Grocery Store" }, { value: "clothing", label: "Clothing / Fashion" },
    { value: "bookshop", label: "Bookshop" }, { value: "gift_shop", label: "Gift Shop" },
    { value: "florist", label: "Florist" }, { value: "sports", label: "Sports / Outdoor" },
    { value: "electronics", label: "Electronics" }, { value: "toy_shop", label: "Toy Shop" },
    { value: "pet_shop", label: "Pet Shop" }, { value: "furniture", label: "Furniture" },
    { value: "jewelry", label: "Jewellery" }, { value: "shoe_store", label: "Shoe Store" },
    { value: "thrift_store", label: "Thrift / Vintage" }, { value: "hardware", label: "Hardware Store" },
    { value: "pharmacy", label: "Pharmacy" }, { value: "optical", label: "Optical / Eyewear" },
    { value: "convenience", label: "Convenience Store" }, { value: "liquor_store", label: "Liquor Store" },
    { value: "garden_center", label: "Garden Centre" }, { value: "art_supplies", label: "Art Supplies" },
    { value: "music_store", label: "Music / Instruments" },
  ]},
  { value: "services", label: "Home & Local Services", types: [
    { value: "auto", label: "Auto Services / Mechanic" }, { value: "dry_cleaning", label: "Dry Cleaning / Laundry" },
    { value: "photography", label: "Photography" }, { value: "printing", label: "Printing / Signage" },
    { value: "cleaning", label: "Cleaning Service" }, { value: "plumbing", label: "Plumbing" },
    { value: "electrical", label: "Electrician" }, { value: "landscaping", label: "Landscaping / Garden" },
    { value: "pest_control", label: "Pest Control" }, { value: "moving_company", label: "Moving Company" },
    { value: "locksmith", label: "Locksmith" }, { value: "car_wash", label: "Car Wash / Detailing" },
    { value: "tailor", label: "Tailor / Alterations" }, { value: "pet_grooming", label: "Pet Grooming" },
    { value: "repair_shop", label: "Repair Shop" },
  ]},
  { value: "professional", label: "Professional Services", types: [
    { value: "accountant", label: "Accountant / Bookkeeping" }, { value: "legal", label: "Legal / Law Firm" },
    { value: "consulting", label: "Consulting" }, { value: "freelance", label: "Freelance / Agency" },
    { value: "marketing_agency", label: "Marketing / Advertising" }, { value: "financial_advisor", label: "Financial Advisor" },
    { value: "insurance", label: "Insurance" }, { value: "real_estate", label: "Real Estate" },
    { value: "recruitment", label: "Recruitment / Staffing" }, { value: "architecture", label: "Architecture / Design" },
    { value: "translation", label: "Translation / Interpreting" }, { value: "coaching", label: "Business Coaching" },
  ]},
  { value: "technology", label: "Technology", types: [
    { value: "saas", label: "SaaS / Software" }, { value: "ecommerce", label: "E-commerce" },
    { value: "app", label: "Mobile App" }, { value: "it_services", label: "IT Services / Support" },
    { value: "web_design", label: "Web Design / Development" }, { value: "hosting", label: "Hosting / Cloud" },
    { value: "cybersecurity", label: "Cybersecurity" }, { value: "data_analytics", label: "Data / Analytics" },
    { value: "ai_ml", label: "AI / Machine Learning" }, { value: "devtools", label: "Developer Tools" },
    { value: "marketplace", label: "Online Marketplace" },
  ]},
  { value: "b2b", label: "B2B / Industrial", types: [
    { value: "b2b_services", label: "B2B Services" }, { value: "logistics", label: "Logistics / Shipping" },
    { value: "wholesale", label: "Wholesale / Distribution" }, { value: "manufacturing", label: "Manufacturing" },
    { value: "commercial_cleaning", label: "Commercial Cleaning" }, { value: "fleet_management", label: "Fleet Management" },
    { value: "packaging", label: "Packaging / Labelling" }, { value: "waste_management", label: "Waste Management" },
    { value: "construction", label: "Construction / Contracting" }, { value: "printing_commercial", label: "Commercial Printing" },
  ]},
  { value: "hospitality", label: "Hospitality & Travel", types: [
    { value: "hotel", label: "Hotel" }, { value: "hostel", label: "Hostel" },
    { value: "campsite", label: "Campsite / Glamping" }, { value: "tour_operator", label: "Tour Operator" },
    { value: "activity_centre", label: "Activity Centre" }, { value: "airbnb", label: "Vacation Rental / Airbnb" },
    { value: "event_venue", label: "Event Venue" }, { value: "wedding_venue", label: "Wedding Venue" },
    { value: "travel_agency", label: "Travel Agency" }, { value: "bed_breakfast", label: "B&B / Guest House" },
    { value: "resort", label: "Resort" },
  ]},
  { value: "healthcare", label: "Healthcare", types: [
    { value: "healthcare_clinic", label: "General Practice / Clinic" }, { value: "dental", label: "Dental Practice" },
    { value: "veterinary", label: "Veterinary" }, { value: "mental_health", label: "Therapist / Counsellor" },
    { value: "optometry", label: "Optician / Optometry" }, { value: "dermatology", label: "Dermatology" },
    { value: "chiropractor", label: "Chiropractor" }, { value: "podiatry", label: "Podiatry" },
    { value: "fertility_clinic", label: "Fertility Clinic" }, { value: "urgent_care", label: "Urgent Care" },
  ]},
  { value: "education", label: "Education & Childcare", types: [
    { value: "education", label: "School / Training Centre" }, { value: "childcare", label: "Childcare / Nursery" },
    { value: "driving_school", label: "Driving School" }, { value: "tutoring", label: "Tutoring" },
    { value: "language_school", label: "Language School" }, { value: "music_school", label: "Music School" },
    { value: "coding_bootcamp", label: "Coding Bootcamp" }, { value: "art_school", label: "Art School" },
    { value: "test_prep", label: "Test Prep" }, { value: "online_course", label: "Online Courses" },
  ]},
  { value: "entertainment", label: "Entertainment & Leisure", types: [
    { value: "cinema", label: "Cinema" }, { value: "bowling", label: "Bowling" },
    { value: "arcade", label: "Arcade / Gaming" }, { value: "escape_room", label: "Escape Room" },
    { value: "mini_golf", label: "Mini Golf" }, { value: "theme_park", label: "Theme Park" },
    { value: "museum", label: "Museum / Gallery" }, { value: "nightclub", label: "Nightclub" },
    { value: "comedy_club", label: "Comedy Club" }, { value: "trampoline_park", label: "Trampoline Park" },
    { value: "laser_tag", label: "Laser Tag / Paintball" }, { value: "zoo", label: "Zoo / Aquarium" },
  ]},
  { value: "property", label: "Property & Facilities", types: [
    { value: "coworking", label: "Coworking Space" }, { value: "storage", label: "Storage / Self-storage" },
    { value: "parking", label: "Parking" }, { value: "laundromat", label: "Laundromat" },
    { value: "car_wash", label: "Car Wash" },
  ]},
  { value: "creative", label: "Creative & Media", types: [
    { value: "recording_studio", label: "Recording Studio" }, { value: "film_production", label: "Film / Video Production" },
    { value: "graphic_design", label: "Graphic Design" }, { value: "content_creation", label: "Content Creation" },
    { value: "podcast", label: "Podcast Studio" }, { value: "printing_3d", label: "3D Printing" },
  ]},
  { value: "nonprofit", label: "Community & Nonprofit", types: [
    { value: "charity", label: "Charity / NGO" }, { value: "community_centre", label: "Community Centre" },
    { value: "church", label: "Church / Religious Org" }, { value: "sports_club", label: "Sports Club" },
    { value: "association", label: "Association / Membership Org" },
  ]},
];

// Flat lookup: value -> label and label -> value
const ALL_TYPES_FLAT = BUSINESS_SECTORS.flatMap((s) => s.types);
const TYPE_VALUE_TO_LABEL: Record<string, string> = {};
const TYPE_LABEL_TO_VALUE: Record<string, string> = {};
for (const t of ALL_TYPES_FLAT) {
  TYPE_VALUE_TO_LABEL[t.value] = t.label;
  TYPE_LABEL_TO_VALUE[t.label] = t.value;
  TYPE_LABEL_TO_VALUE[t.label.toLowerCase()] = t.value;
}

const BUSINESS_ROLES: { value: string; label: string; desc: string; examples: Record<string, string> }[] = [
  { value: "habit", label: "A habit or routine", desc: "They come regularly because it's part of their week -- not because they thought about it", examples: {
    default: "Like the coffee shop someone stops at every morning without thinking twice.",
    saas: "Like the project management tool someone opens first thing every morning -- it is just part of how they work.",
    ecommerce: "Like the online store someone checks every week for new arrivals without thinking about it.",
    gym: "Like the gym someone goes to at 6am every day -- it is just what they do.",
    b2b_services: "Like the supplier a business reorders from every month on autopilot.",
  }},
  { value: "daily_need", label: "A daily need", desc: "They need what you offer -- it's practical and functional", examples: {
    default: "Like the lunch spot near the office that saves them cooking.",
    saas: "Like the accounting software a business relies on to send invoices and track payments.",
    healthcare_clinic: "Like the pharmacy people visit because they need their prescription filled.",
    logistics: "Like the shipping provider an e-commerce business uses because orders need to go out every day.",
    childcare: "Like the nursery parents depend on so they can get to work.",
  }},
  { value: "treat", label: "A treat or reward", desc: "Coming here feels like a small luxury or something they look forward to", examples: {
    default: "Like the brunch place someone visits when they want to do something nice for themselves.",
    spa: "Like the spa day someone books after a hard month at work.",
    ecommerce: "Like the online boutique someone browses when they want to treat themselves to something special.",
    fine_dining: "Like the restaurant reserved for anniversaries and celebrations.",
    salon: "Like the salon appointment that makes someone feel put-together again.",
  }},
  { value: "social", label: "A social spot", desc: "They come to be around people, meet friends, or feel part of something", examples: {
    default: "Like the local pub where everyone knows your name.",
    coworking: "Like the coworking space where freelancers go to feel less isolated and bump into familiar faces.",
    gym: "Like the CrossFit box where the community is half the reason people show up.",
    saas: "Like the Slack community or forum where users help each other and feel part of something.",
    bar: "Like the bar where the same group meets every Friday night.",
  }},
  { value: "convenience", label: "Pure convenience", desc: "You're close, easy, or the fastest option -- that's mainly why they come", examples: {
    default: "Like the nearest petrol station or corner shop.",
    saas: "Like the tool someone picked because it was the first Google result and good enough.",
    ecommerce: "Like Amazon -- not because they love it, but because it is the fastest option.",
    pharmacy: "Like the pharmacy on the walk home from work.",
    auto: "Like the mechanic closest to someone's house -- they go because it saves time, not because they love it.",
  }},
  { value: "destination", label: "A destination", desc: "They make a specific effort to come -- it's worth the journey", examples: {
    default: "Like the restaurant people drive 30 minutes to visit.",
    museum: "Like the museum people plan a whole day trip around.",
    saas: "Like the niche tool teams switch to specifically because nothing else does what it does.",
    wedding_venue: "Like the venue couples travel across the country to book.",
    consulting: "Like the specialist consultant companies seek out because of their reputation in the industry.",
  }},
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


export default function EnrichedSurvey({ onSubmit, loading }: Props) {
  const [step, setStep] = useState(0);
  const [lookupInput, setLookupInput] = useState("");
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupResult, setLookupResult] = useState<Record<string, unknown> | null>(null);
  const [genLoading, setGenLoading] = useState<string | null>(null);
  const [infoDismissed, setInfoDismissed] = useState(false);

  // Location autocomplete state
  const [locationQuery, setLocationQuery] = useState("");
  const [locationSuggestions, setLocationSuggestions] = useState<{ description: string; place_id: string }[]>([]);
  const [locationLoading, setLocationLoading] = useState(false);
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);
  const locationDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [form, setForm] = useState<BusinessCreate>({
    name: "", type: "", description: "", customer_description: "",
    is_online_only: false,
    location: "", years_open: "", business_role: [], business_not_role: [], visit_frequency: "",
    busy_days: [], busy_times: [], customer_value_drivers: [],
    customer_social_context: [], regular_proportion: "",
    area_demographics: [], competitor_count: "", area_feel: "",
    customer_discovery: [], nearby_anchors: [],
    competitor_advantage: [], location_advantage: "",
    website_url: "", additional_customer_notes: "",
    has_prior_change: false, prior_change_description: "", prior_change_outcome: "",
    prior_changes: [],
    location_street: "", location_number: "", location_postcode: "",
    location_city: "", location_neighbourhood: "", location_country: "",
    customer_age_distribution: { "18-24": 0, "25-34": 0, "35-44": 0, "45-54": 0, "55-64": 0, "65+": 0 } as Record<string, number>,
    customer_income_bracket: "",
    average_transaction_value: undefined, customer_gender_split: "",
    local_vs_visitor_ratio: {
      loyal_regulars: 0, casual_regulars: 0, occasional: 0,
      first_timers: 0, tourists: 0, one_time_life: 0, referrals: 0, online_only: 0,
    } as Record<string, number>,
    digital_savviness: "", price_range: "",
  });

  // Save to localStorage
  useEffect(() => {
    const saved = localStorage.getItem("murmur_survey");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setForm((prev) => ({ ...prev, ...parsed }));
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

  // Parse a formatted address into component fields
  const parseFormattedAddress = (formatted: string) => {
    if (!formatted || formatted.length < 3) return;
    const parts = formatted.split(",").map((p) => p.trim()).filter(Boolean);
    if (parts.length < 1) return;

    const updates: {
      location: string; location_street?: string; location_number?: string;
      location_postcode?: string; location_city?: string;
      location_neighbourhood?: string; location_country?: string;
    } = { location: formatted };

    // Try to find street+number in the first part (always)
    const firstPart = parts[0];
    const streetNum1 = firstPart.match(/^(.+?)\s+(\d+\S*)$/);  // "Rietpolderweg 13"
    const streetNum2 = firstPart.match(/^(\d+\S*)\s+(.+)$/);    // "13 Rietpolderweg"
    if (streetNum1) {
      updates.location_street = streetNum1[1];
      updates.location_number = streetNum1[2];
    } else if (streetNum2) {
      updates.location_number = streetNum2[1];
      updates.location_street = streetNum2[2];
    }

    // Scan ALL parts for postcode patterns
    for (const part of parts) {
      if (updates.location_postcode) break;
      // Dutch: "2266 BM", UK: "SW1A 1AA", US: "10001", German: "10115"
      const pc = part.match(/\b(\d{4,5}\s*[A-Z]{0,2})\b/) || part.match(/\b([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b/);
      if (pc) updates.location_postcode = pc[1].trim();
    }

    // Scan ALL parts for city: any part that is just a word (no numbers, not street)
    // and is not the first part (which is street) or a known country
    const knownCountries = new Set(["netherlands", "nederland", "germany", "deutschland", "france", "spain", "italy", "united kingdom", "uk", "usa", "united states", "belgium", "austria", "switzerland", "portugal", "ireland", "australia", "canada", "brazil", "japan", "china", "india", "mexico"]);
    for (let i = 1; i < parts.length; i++) {
      const clean = parts[i].replace(/\b\d{4,5}\s*[A-Z]{0,2}\b/g, "").replace(/\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b/g, "").trim();
      if (!clean) continue;
      if (knownCountries.has(clean.toLowerCase())) {
        updates.location_country = clean;
      } else if (!updates.location_city && clean.length > 1 && !/^\d+$/.test(clean)) {
        updates.location_city = clean;
      }
    }

    // If last part looks like a country (2-3 letter code or known name), use it
    if (parts.length >= 2) {
      const last = parts[parts.length - 1];
      if (last.length <= 3 && /^[A-Z]+$/i.test(last)) {
        updates.location_country = last.toUpperCase();
      } else if (knownCountries.has(last.toLowerCase())) {
        updates.location_country = last;
      }
    }

    setForm((prev) => ({
      ...prev,
      location: formatted,
      location_street: updates.location_street || prev.location_street,
      location_number: updates.location_number || prev.location_number,
      location_postcode: updates.location_postcode || prev.location_postcode,
      location_city: updates.location_city || prev.location_city,
      location_neighbourhood: updates.location_neighbourhood || prev.location_neighbourhood,
      location_country: updates.location_country || prev.location_country,
    }));
  };

  // Location autocomplete
  const handleLocationSearch = (query: string) => {
    setLocationQuery(query);
    if (locationDebounceRef.current) clearTimeout(locationDebounceRef.current);
    if (query.length < 3) {
      setLocationSuggestions([]);
      setShowLocationDropdown(false);
      return;
    }
    setLocationLoading(true);
    locationDebounceRef.current = setTimeout(async () => {
      try {
        const result = await placeAutocomplete(query);
        setLocationSuggestions(result.predictions || []);
        setShowLocationDropdown(true);
      } catch {
        setLocationSuggestions([]);
      }
      setLocationLoading(false);
    }, 300);
  };

  const handleLocationSelect = async (placeId: string, description: string) => {
    setShowLocationDropdown(false);
    setLocationQuery(description);
    setLocationLoading(true);
    try {
      const details = await placeDetails(placeId);
      setForm((prev) => ({
        ...prev,
        location: (details.formatted as string) || description,
        location_street: (details.street as string) || "",
        location_number: (details.number as string) || "",
        location_postcode: (details.postcode as string) || "",
        location_city: (details.city as string) || "",
        location_neighbourhood: (details.neighbourhood as string) || "",
        location_country: (details.country as string) || "",
      }));
    } catch {
      // If details API fails, parse the formatted address string locally
      parseFormattedAddress(description);
    }
    setLocationLoading(false);
  };

  // Phase 0: Lookup
  const handleLookup = async () => {
    if (!lookupInput.trim()) return;
    setLookupLoading(true);
    try {
      const result = await researchBusiness(lookupInput.trim());
      // Only show result if something useful came back
      const hasName = result.name && !/^(https?:\/\/|www\.)/i.test((result.name as string).trim());
      const hasDesc = !!result.description;
      const hasType = !!result.type;
      if (hasName || hasDesc || hasType) {
        setLookupResult(result);
      } else {
        setLookupResult(null);
      }
    } catch {
      // lookup failed silently -- user can fill manually
    } finally {
      setLookupLoading(false);
    }
  };

  const isUrl = (s: string) => /^(https?:\/\/|www\.)/i.test(s.trim());

  const acceptLookup = () => {
    if (!lookupResult) return;
    const r = lookupResult;
    const nameVal = (r.name as string) || "";
    setForm((prev) => ({
      ...prev,
      name: (!isUrl(nameVal) && nameVal) ? nameVal : prev.name,
      type: (r.type as string) || prev.type,
      description: (r.description as string) || prev.description,
      location: (r.formatted_address as string) || prev.location,
      google_place_id: (r.google_place_id as string) || prev.google_place_id,
      website_url: (r.website as string) || prev.website_url,
      years_open: (r.years_open_estimate as string) || prev.years_open,
      location_city: (r.location_city as string) || prev.location_city,
      location_country: (r.location_country as string) || prev.location_country,
    }));
    // Parse the formatted address into component fields if they weren't set
    const addr = (r.formatted_address as string) || "";
    if (addr && !r.location_city) {
      parseFormattedAddress(addr);
    }
    setLocationQuery(addr);
    setLookupResult(null);
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
    if (step === 1) return (form.business_role as string[])?.length > 0;
    if (step === 2) return (form.customer_discovery as string[])?.length > 0;
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
  // SURVEY STEPS
  // ============================================================
  return (
    <div className="mx-auto max-w-2xl py-8">
      {/* Accuracy info banner */}
      {!infoDismissed && (
        <div className="mb-6 rounded-xl border border-brand-orange/20 bg-brand-orange/5 p-4">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-orange/10 text-brand-orange text-xs font-bold">i</div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">The more you share, the more accurate your simulation</p>
              <p className="mt-1 text-xs text-gray-500">
                Every field you fill helps us build more realistic customer personas.
                The business description, customer details, and location are the most
                impactful -- but even optional fields like price range, customer age,
                and digital savviness meaningfully improve accuracy. Fields left blank
                will be estimated, but your direct knowledge is always better than our guesses.
              </p>
            </div>
            <button
              onClick={() => setInfoDismissed(true)}
              className="shrink-0 p-1 text-gray-400 hover:text-gray-600"
              aria-label="Dismiss"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
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

          {/* Quick fill: paste a URL or search by name */}
          <div className="rounded-xl border border-brand-blue/20 bg-brand-blue/5 p-4">
            <label className="mb-1 block text-xs font-medium text-brand-blue">Quick fill -- paste your website or type your business name</label>
            <div className="flex gap-2">
              <input
                value={lookupInput}
                onChange={(e) => setLookupInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLookup()}
                placeholder="e.g. www.yourbusiness.com or Rosa's Cafe Hackney"
                className="flex-1 rounded-lg border border-brand-blue/20 bg-white px-3 py-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-2 focus:ring-brand-blue/20"
              />
              <button
                onClick={handleLookup}
                disabled={lookupLoading || !lookupInput.trim()}
                className="shrink-0 rounded-lg bg-brand-blue px-4 py-2.5 text-xs font-medium text-white transition-colors hover:opacity-90 disabled:opacity-50"
              >
                {lookupLoading ? "Searching..." : "Find"}
              </button>
            </div>
            {lookupResult && (
              <div className="mt-3 rounded-lg border border-gray-200 bg-white p-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{(lookupResult.name as string) || (lookupResult.description as string)?.slice(0, 60) || "Business found"}</p>
                    <p className="text-xs text-gray-500">
                      {lookupResult.type as string}{lookupResult.formatted_address ? ` -- ${lookupResult.formatted_address as string}` : ""}
                    </p>
                    {lookupResult.rating ? (
                      <p className="text-xs text-gray-400">{String(lookupResult.rating)} stars -- {String(lookupResult.review_count)} reviews</p>
                    ) : null}
                  </div>
                  <button
                    onClick={acceptLookup}
                    className="shrink-0 rounded-lg bg-murmur-amber px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-murmur-amber/90"
                  >
                    Use this
                  </button>
                </div>
              </div>
            )}
            <p className="mt-2 text-[10px] text-gray-400">
              We&apos;ll scrape your website and look you up on Google to pre-fill as much as possible. Or just fill in the fields below manually.
            </p>
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
            <p className="mb-2 text-xs text-gray-400">Pick a sector, then choose or type your specific business type</p>
            <div className="flex gap-2">
              {/* Sector dropdown */}
              <select
                value={BUSINESS_SECTORS.find((s) => s.types.some((t) => t.value === form.type))?.value || ""}
                onChange={(e) => {
                  const sector = BUSINESS_SECTORS.find((s) => s.value === e.target.value);
                  if (sector && sector.types.length > 0) {
                    update("type", sector.types[0].value);
                  }
                }}
                className="w-48 shrink-0 rounded-xl border border-gray-200 bg-white px-3 py-3 text-sm text-gray-700 focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
              >
                <option value="">Select sector...</option>
                {BUSINESS_SECTORS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
              {/* Type search input with dropdown */}
              <div className="relative flex-1">
                <input
                  value={TYPE_VALUE_TO_LABEL[form.type] || form.type || ""}
                  onChange={(e) => {
                    const typed = e.target.value;
                    // Check if it matches a known type
                    const match = ALL_TYPES_FLAT.find(
                      (t) => t.label.toLowerCase() === typed.toLowerCase() || t.value === typed.toLowerCase()
                    );
                    if (match) {
                      update("type", match.value);
                    } else {
                      // Allow custom type -- store as-is
                      update("type", typed.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, ""));
                    }
                  }}
                  placeholder="e.g. SaaS, Restaurant, Dental..."
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                  list="business-types-list"
                />
                <datalist id="business-types-list">
                  {ALL_TYPES_FLAT.map((t) => (
                    <option key={t.value} value={t.label} />
                  ))}
                </datalist>
              </div>
            </div>
            {/* Show selected type as confirmed chip */}
            {form.type && (
              <div className="mt-2 flex items-center gap-2">
                <span className="rounded-full border border-murmur-amber bg-murmur-amber/10 px-3 py-1 text-xs font-medium text-murmur-amber">
                  {TYPE_VALUE_TO_LABEL[form.type] || form.type}
                </span>
                <button onClick={() => update("type", "")} className="text-xs text-gray-400 hover:text-gray-600">
                  change
                </button>
              </div>
            )}
          </div>

          {/* Online/Physical toggle */}
          <div className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-4">
            <button
              onClick={() => update("is_online_only", !(form.is_online_only as boolean))}
              className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${
                form.is_online_only ? "bg-murmur-amber" : "bg-gray-300"
              }`}
            >
              <span className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                form.is_online_only ? "translate-x-5" : ""
              }`} />
            </button>
            <div>
              <p className="text-sm font-medium text-gray-900">
                {form.is_online_only ? "We are an online-only business" : "We have a physical location"}
              </p>
              <p className="text-xs text-gray-400">
                {form.is_online_only
                  ? "No storefront, office, or venue that customers visit in person"
                  : "Customers can visit you in person (even if you also sell online)"
                }
              </p>
            </div>
          </div>

          {/* Location section -- changes based on online/physical */}
          {form.is_online_only ? (
            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Where are your customers based?</label>
                <p className="mb-2 text-xs text-gray-400">Select all regions where you have significant customers</p>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    "Local city/region", "Nationwide", "Europe", "North America",
                    "UK & Ireland", "Asia Pacific", "Latin America", "Middle East & Africa",
                    "Global / Worldwide",
                  ].map((region) => (
                    <button
                      key={region}
                      onClick={() => toggleMulti("area_demographics", region.toLowerCase().replace(/\s+/g, "_").replace(/[&\/]/g, ""))}
                      className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                        (form.area_demographics || []).includes(region.toLowerCase().replace(/\s+/g, "_").replace(/[&\/]/g, ""))
                          ? "border-murmur-amber bg-murmur-amber text-white"
                          : "border-gray-200 text-gray-500 hover:bg-gray-50"
                      }`}
                    >
                      {region}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Primary country / market</label>
                <input
                  value={form.location_country || ""}
                  onChange={(e) => update("location_country", e.target.value)}
                  placeholder="e.g. US, UK, Netherlands, Global"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Where is the business registered / headquartered?</label>
                <input
                  value={form.location_city || ""}
                  onChange={(e) => update("location_city", e.target.value)}
                  placeholder="e.g. Amsterdam, London, San Francisco"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
            </div>
          ) : (
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Where are you? *</label>
            {/* Location autocomplete search */}
            <div className="relative mb-3">
              <input
                value={locationQuery || form.location || ""}
                onChange={(e) => {
                  handleLocationSearch(e.target.value);
                  update("location", e.target.value);
                }}
                onFocus={() => locationSuggestions.length > 0 && setShowLocationDropdown(true)}
                onBlur={() => {
                  setTimeout(() => setShowLocationDropdown(false), 200);
                  // Parse address when user leaves the field
                  const val = locationQuery || (form.location as string) || "";
                  if (val.includes(",") && !form.location_city) {
                    parseFormattedAddress(val);
                  }
                }}
                placeholder="Start typing your address..."
                className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
              />
              {locationLoading && (
                <div className="absolute right-3 top-3.5">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-murmur-amber" />
                </div>
              )}
              {showLocationDropdown && locationSuggestions.length > 0 && (
                <div className="absolute left-0 right-0 top-full z-10 mt-1 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg">
                  {locationSuggestions.map((suggestion) => (
                    <button
                      key={suggestion.place_id}
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => handleLocationSelect(suggestion.place_id, suggestion.description)}
                      className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      <svg className="h-4 w-4 shrink-0 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {suggestion.description}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {/* Detailed address fields (auto-filled by autocomplete, editable) */}
            {(form.location_city || form.location_street) && (
              <div className="grid grid-cols-2 gap-2">
                <input
                  value={form.location_street || ""}
                  onChange={(e) => update("location_street", e.target.value)}
                  placeholder="Street"
                  className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 text-xs text-gray-600 focus:border-murmur-amber focus:bg-white focus:outline-none"
                />
                <input
                  value={form.location_number || ""}
                  onChange={(e) => update("location_number", e.target.value)}
                  placeholder="Number"
                  className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 text-xs text-gray-600 focus:border-murmur-amber focus:bg-white focus:outline-none"
                />
                <input
                  value={form.location_postcode || ""}
                  onChange={(e) => update("location_postcode", e.target.value)}
                  placeholder="Postcode"
                  className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 text-xs text-gray-600 focus:border-murmur-amber focus:bg-white focus:outline-none"
                />
                <input
                  value={form.location_city || ""}
                  onChange={(e) => update("location_city", e.target.value)}
                  placeholder="City *"
                  className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 text-xs text-gray-600 focus:border-murmur-amber focus:bg-white focus:outline-none"
                />
                <input
                  value={form.location_neighbourhood || ""}
                  onChange={(e) => update("location_neighbourhood", e.target.value)}
                  placeholder="Neighbourhood"
                  className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 text-xs text-gray-600 focus:border-murmur-amber focus:bg-white focus:outline-none"
                />
                <input
                  value={form.location_country || ""}
                  onChange={(e) => update("location_country", e.target.value)}
                  placeholder="Country *"
                  className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 text-xs text-gray-600 focus:border-murmur-amber focus:bg-white focus:outline-none"
                />
              </div>
            )}
            {/* Manual city/country entry if no autocomplete used */}
            {!form.location_city && !form.location_street && (
              <div className="grid grid-cols-2 gap-3">
                <input
                  value={form.location_city || ""}
                  onChange={(e) => update("location_city", e.target.value)}
                  placeholder="City *"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
                <input
                  value={form.location_country || ""}
                  onChange={(e) => update("location_country", e.target.value)}
                  placeholder="Country *"
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm focus:border-murmur-amber focus:outline-none focus:ring-2 focus:ring-murmur-amber-light"
                />
              </div>
            )}
          </div>
          )}

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
            <p className="mb-2 text-xs text-gray-400">
              The more specific you are, the more realistic the simulation. Try to cover:
            </p>
            <ul className="mb-3 space-y-1 text-xs text-gray-400">
              <li><span className="font-medium text-gray-500">Who they are:</span> age range, profession, lifestyle (busy parents, students, office workers on lunch break)</li>
              <li><span className="font-medium text-gray-500">Why they come:</span> what brings them to you specifically (quick lunch, a special day out, they need a reliable supplier)</li>
              <li><span className="font-medium text-gray-500">What they expect:</span> speed, quality, personal touch, low prices, expertise, convenience, a premium experience?</li>
              <li><span className="font-medium text-gray-500">How they behave:</span> do they compare prices? read reviews? come in groups? are they loyal or always shopping around?</li>
            </ul>
            <textarea
              value={form.customer_description || ""}
              onChange={(e) => update("customer_description", e.target.value)}
              placeholder="e.g. Our weekday crowd is mostly office workers from nearby who want a fast, affordable lunch -- they are price-conscious and will switch if we are slow. Weekends bring families who expect a welcoming atmosphere. We also get tourists who found us on Google -- they spend more but never come back."
              rows={5}
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
            <p className="mb-3 text-xs text-gray-400">Pick up to 2 that fit best</p>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {BUSINESS_ROLES.map((role) => {
                const roles = (form.business_role as string[]) || [];
                const selected = roles.includes(role.value);
                const atMax = roles.length >= 2 && !selected;
                return (
                  <button
                    key={role.value}
                    onClick={() => {
                      if (selected) {
                        update("business_role", roles.filter((r) => r !== role.value));
                      } else if (!atMax) {
                        update("business_role", [...roles, role.value]);
                      }
                    }}
                    disabled={atMax}
                    className={`rounded-xl border p-4 text-left transition-all ${
                      selected
                        ? "border-murmur-amber bg-murmur-amber-light/20"
                        : atMax
                          ? "border-gray-100 opacity-40"
                          : "border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    <p className="text-sm font-medium text-gray-900">{role.label}</p>
                    <p className="mt-0.5 text-xs text-gray-500">{role.desc}</p>
                  </button>
                );
              })}
            </div>
            {((form.business_role as string[]) || []).length > 0 && (
              <p className="mt-3 text-xs italic text-murmur-amber">
                {((form.business_role as string[]) || []).map((v) => {
                  const role = BUSINESS_ROLES.find((r) => r.value === v);
                  if (!role) return null;
                  return role.examples[form.type] || role.examples.default;
                }).filter(Boolean).join(" ")}
              </p>
            )}
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">What is your business absolutely NOT?</label>
            <p className="mb-3 text-xs text-gray-400">Pick up to 2 -- this helps us avoid generating the wrong type of customer</p>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {BUSINESS_ROLES.map((role) => {
                const notRoles = (form.business_not_role as string[]) || [];
                const roles = (form.business_role as string[]) || [];
                const selected = notRoles.includes(role.value);
                const atMax = notRoles.length >= 2 && !selected;
                const isPositive = roles.includes(role.value);
                return (
                  <button
                    key={role.value}
                    onClick={() => {
                      if (selected) {
                        update("business_not_role", notRoles.filter((r) => r !== role.value));
                      } else if (!atMax && !isPositive) {
                        update("business_not_role", [...notRoles, role.value]);
                      }
                    }}
                    disabled={atMax || isPositive}
                    className={`rounded-xl border p-3 text-left transition-all ${
                      selected
                        ? "border-legacy-red bg-legacy-red/5"
                        : isPositive
                          ? "border-gray-100 opacity-20"
                          : atMax
                            ? "border-gray-100 opacity-40"
                            : "border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    <p className={`text-sm font-medium ${selected ? "text-legacy-red" : "text-gray-900"}`}>{role.label}</p>
                    <p className="mt-0.5 text-xs text-gray-500">{role.desc}</p>
                  </button>
                );
              })}
            </div>
            {((form.business_not_role as string[]) || []).length > 0 && (
              <p className="mt-2 text-xs text-gray-400">
                Customers who come for these reasons will be excluded or downweighted in the simulation.
              </p>
            )}
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">How often do customers typically engage?</label>
            <div className="flex flex-wrap gap-1.5">
              {[
                { v: "multiple_daily", l: "Multiple times a day" },
                { v: "daily", l: "Daily" },
                { v: "few_per_week", l: "A few times a week" },
                { v: "weekly", l: "Weekly" },
                { v: "fortnightly", l: "Every 2 weeks" },
                { v: "monthly", l: "Monthly" },
                { v: "quarterly", l: "Every few months" },
                { v: "occasional", l: "A few times a year" },
                { v: "annual", l: "Once a year" },
                { v: "one_time", l: "Usually one-time" },
                { v: "project_based", l: "Project-based" },
                { v: "subscription", l: "Ongoing subscription" },
                { v: "mixed", l: "Very mixed" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("visit_frequency", opt.v)}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
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
            <label className="mb-2 block text-sm font-medium text-gray-700">What proportion of your customers are regulars?</label>
            <p className="mb-2 text-xs text-gray-400">People who come back repeatedly, not one-time visitors</p>
            <div className="flex flex-wrap gap-1.5">
              {[
                { v: "almost_none", l: "Almost none (0-5%)" },
                { v: "very_few", l: "Very few (5-15%)" },
                { v: "handful", l: "A handful (15-30%)" },
                { v: "solid_base", l: "Solid base (30-50%)" },
                { v: "majority", l: "Majority (50-70%)" },
                { v: "mostly_regulars", l: "Mostly regulars (70-90%)" },
                { v: "almost_all", l: "Almost all (90%+)" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("regular_proportion", opt.v)}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
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
            <label className="mb-2 block text-sm font-medium text-gray-700">Customer age breakdown</label>
            <p className="mb-3 text-xs text-gray-400">Tap + and - to distribute 100% across age groups</p>
            {(() => {
              const brackets = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"];
              const ageDist = (form.customer_age_distribution || {}) as Record<string, number>;
              const total = brackets.reduce((sum, b) => sum + (ageDist[b] || 0), 0);
              const remaining = 100 - total;
              const step = 5;
              return (
                <div className="space-y-2">
                  {/* Progress bar */}
                  <div className="mb-3">
                    <div className="flex h-3 overflow-hidden rounded-full bg-gray-100">
                      {brackets.map((bracket) => {
                        const val = ageDist[bracket] || 0;
                        if (val === 0) return null;
                        const colors: Record<string, string> = {
                          "18-24": "bg-brand-blue", "25-34": "bg-brand-orange",
                          "35-44": "bg-legacy-teal", "45-54": "bg-legacy-purple",
                          "55-64": "bg-legacy-coral", "65+": "bg-legacy-navy",
                        };
                        return (
                          <div
                            key={bracket}
                            className={`${colors[bracket] || "bg-gray-400"} transition-all duration-200`}
                            style={{ width: `${val}%` }}
                            title={`${bracket}: ${val}%`}
                          />
                        );
                      })}
                    </div>
                  </div>
                  {brackets.map((bracket) => {
                    const val = ageDist[bracket] || 0;
                    const colors: Record<string, string> = {
                      "18-24": "bg-brand-blue", "25-34": "bg-brand-orange",
                      "35-44": "bg-legacy-teal", "45-54": "bg-legacy-purple",
                      "55-64": "bg-legacy-coral", "65+": "bg-legacy-navy",
                    };
                    return (
                      <div key={bracket} className="flex items-center gap-3">
                        <div className={`h-3 w-3 shrink-0 rounded-full ${colors[bracket]}`} />
                        <span className="w-12 shrink-0 text-xs font-medium text-gray-700">{bracket}</span>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => {
                              if (val >= step) update("customer_age_distribution", { ...ageDist, [bracket]: val - step });
                            }}
                            disabled={val === 0}
                            className="flex h-7 w-7 items-center justify-center rounded-lg border border-gray-200 text-sm text-gray-500 transition-colors hover:bg-gray-50 disabled:opacity-30"
                          >
                            -
                          </button>
                          <span className={`w-10 text-center text-sm font-mono ${val > 0 ? "font-semibold text-gray-900" : "text-gray-300"}`}>
                            {val}
                          </span>
                          <button
                            onClick={() => {
                              if (remaining >= step) update("customer_age_distribution", { ...ageDist, [bracket]: val + step });
                            }}
                            disabled={remaining < step}
                            className="flex h-7 w-7 items-center justify-center rounded-lg border border-gray-200 text-sm text-gray-500 transition-colors hover:bg-gray-50 disabled:opacity-30"
                          >
                            +
                          </button>
                        </div>
                        <span className="text-[10px] text-gray-400">%</span>
                      </div>
                    );
                  })}
                  <div className="flex items-center justify-between border-t border-gray-100 pt-2">
                    {total === 100 && <span className="text-xs text-legacy-teal font-medium">100% -- done</span>}
                    {total > 0 && total < 100 && <span className="text-xs text-amber-500">{remaining}% remaining</span>}
                    {total === 0 && <span className="text-xs text-gray-300">Tap + to start</span>}
                    {total > 100 && (
                      <button
                        onClick={() => update("customer_age_distribution", { "18-24": 0, "25-34": 0, "35-44": 0, "45-54": 0, "55-64": 0, "65+": 0 })}
                        className="text-xs text-legacy-red underline"
                      >
                        Reset
                      </button>
                    )}
                  </div>
                </div>
              );
            })()}
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
            <label className="mb-2 block text-sm font-medium text-gray-700">Customer base makeup</label>
            <p className="mb-3 text-xs text-gray-400">Tap + and - to distribute 100% across customer types</p>
            {(() => {
              const segments: { key: string; label: string; desc: string }[] = [
                { key: "loyal_regulars", label: "Loyal regulars", desc: "Come consistently, part of their routine" },
                { key: "casual_regulars", label: "Casual regulars", desc: "Come often but could easily drift" },
                { key: "occasional", label: "Occasional", desc: "A few times a year, seasonal" },
                { key: "first_timers", label: "First-timers", desc: "Trying you for the first time" },
                { key: "tourists", label: "Tourists / passing", desc: "Will likely never return" },
                { key: "one_time_life", label: "Once-in-a-lifetime", desc: "Major purchase or life event" },
                { key: "referrals", label: "Referrals", desc: "Came via recommendation" },
                { key: "online_only", label: "Online only", desc: "Never visit in person" },
              ];
              const custTypes = (form.local_vs_visitor_ratio || {}) as Record<string, number>;
              const total = segments.reduce((sum, s) => sum + (custTypes[s.key] || 0), 0);
              const remaining = 100 - total;
              const step = 5;
              return (
                <div className="space-y-2">
                  {/* Progress bar */}
                  <div className="mb-3">
                    <div className="flex h-3 overflow-hidden rounded-full bg-gray-100">
                      {segments.map(({ key }) => {
                        const val = custTypes[key] || 0;
                        if (val === 0) return null;
                        const colors: Record<string, string> = {
                          loyal_regulars: "bg-legacy-teal", casual_regulars: "bg-brand-blue",
                          occasional: "bg-brand-orange", first_timers: "bg-legacy-purple",
                          tourists: "bg-legacy-coral", one_time_life: "bg-legacy-red",
                          referrals: "bg-legacy-navy", online_only: "bg-yellow-400",
                        };
                        return (
                          <div
                            key={key}
                            className={`${colors[key] || "bg-gray-400"} transition-all duration-200`}
                            style={{ width: `${val}%` }}
                          />
                        );
                      })}
                    </div>
                  </div>
                  {segments.map(({ key, label, desc }) => {
                    const val = custTypes[key] || 0;
                    const colors: Record<string, string> = {
                      loyal_regulars: "bg-legacy-teal", casual_regulars: "bg-brand-blue",
                      occasional: "bg-brand-orange", first_timers: "bg-legacy-purple",
                      tourists: "bg-legacy-coral", one_time_life: "bg-legacy-red",
                      referrals: "bg-legacy-navy", online_only: "bg-yellow-400",
                    };
                    return (
                      <div key={key} className="flex items-center gap-2">
                        <div className={`h-2.5 w-2.5 shrink-0 rounded-full ${colors[key]}`} />
                        <div className="min-w-0 flex-1">
                          <span className="text-xs font-medium text-gray-700">{label}</span>
                          <span className="ml-1.5 text-[10px] text-gray-400">{desc}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => { if (val >= step) update("local_vs_visitor_ratio", { ...custTypes, [key]: val - step }); }}
                            disabled={val === 0}
                            className="flex h-6 w-6 items-center justify-center rounded border border-gray-200 text-xs text-gray-500 hover:bg-gray-50 disabled:opacity-30"
                          >-</button>
                          <span className={`w-8 text-center text-xs font-mono ${val > 0 ? "font-semibold text-gray-900" : "text-gray-300"}`}>{val}</span>
                          <button
                            onClick={() => { if (remaining >= step) update("local_vs_visitor_ratio", { ...custTypes, [key]: val + step }); }}
                            disabled={remaining < step}
                            className="flex h-6 w-6 items-center justify-center rounded border border-gray-200 text-xs text-gray-500 hover:bg-gray-50 disabled:opacity-30"
                          >+</button>
                        </div>
                      </div>
                    );
                  })}
                  <div className="flex items-center justify-between border-t border-gray-100 pt-2">
                    {total === 100 && <span className="text-xs text-legacy-teal font-medium">100% -- done</span>}
                    {total > 0 && total < 100 && <span className="text-xs text-amber-500">{remaining}% remaining</span>}
                    {total === 0 && <span className="text-xs text-gray-300">Tap + to start</span>}
                    {total > 100 && (
                      <button
                        onClick={() => update("local_vs_visitor_ratio", segments.reduce((o, s) => ({ ...o, [s.key]: 0 }), {} as Record<string, number>))}
                        className="text-xs text-legacy-red underline"
                      >Reset</button>
                    )}
                  </div>
                </div>
              );
            })()}
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

      {/* ====== STEP 3: YOUR MARKET ====== */}
      {step === 2 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Your Market</h2>
            <p className="mt-1 text-sm text-gray-500">How customers find you and what you compete against -- this directly shapes the simulation.</p>
          </div>

          {/* Discovery channels -- adapts to online/physical */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">How do customers find you? *</label>
            <p className="mb-2 text-xs text-gray-400">Select all that apply</p>
            <div className="flex flex-wrap gap-1.5">
              {[
                ...(!form.is_online_only ? [
                  { v: "walk_in", l: "Walk past / foot traffic" },
                  { v: "drive", l: "Drive to you" },
                  { v: "public_transport", l: "Public transport" },
                  { v: "local_signage", l: "Signage / billboards" },
                  { v: "flyers_posters", l: "Flyers / posters / leaflets" },
                  { v: "local_events", l: "Local events / markets" },
                  { v: "local_press", l: "Local press / radio" },
                ] : []),
                { v: "google_search", l: "Google / SEO" },
                { v: "google_maps", l: "Google Maps" },
                { v: "social_media", l: "Social media (organic)" },
                { v: "paid_social", l: "Paid social ads" },
                { v: "google_ads", l: "Google / search ads" },
                { v: "word_of_mouth", l: "Word of mouth" },
                { v: "review_sites", l: "Review sites (Yelp, TripAdvisor, G2)" },
                { v: "referral_program", l: "Referral / affiliate program" },
                { v: "marketplace", l: "Marketplace (Amazon, Etsy, Uber Eats)" },
                { v: "email", l: "Email marketing" },
                { v: "content_marketing", l: "Blog / content / SEO articles" },
                { v: "influencers", l: "Influencers / creators" },
                { v: "partnerships", l: "Partnerships / cross-promotions" },
                { v: "app_store", l: "App store" },
                { v: "direct_sales", l: "Direct sales / outbound" },
                { v: "trade_shows", l: "Trade shows / conferences" },
                { v: "pr", l: "PR / media coverage" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => toggleMulti("customer_discovery", opt.v)}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                    ((form.customer_discovery as string[]) || []).includes(opt.v)
                      ? "border-murmur-amber bg-murmur-amber text-white"
                      : "border-gray-200 text-gray-500 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          {/* What drives traffic -- physical vs online */}
          {!form.is_online_only ? (
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">What is nearby that brings people to your area?</label>
              <p className="mb-2 text-xs text-gray-400">Select all that apply</p>
              <div className="flex flex-wrap gap-1.5">
                {[
                  { v: "offices", l: "Offices / workplaces" },
                  { v: "residential", l: "Residential housing" },
                  { v: "schools", l: "Schools / Universities" },
                  { v: "shopping_centre", l: "Shopping centre / Mall" },
                  { v: "high_street", l: "High street / Main road" },
                  { v: "train_station", l: "Train / Metro / Bus station" },
                  { v: "hospital", l: "Hospital / Medical centre" },
                  { v: "tourist_attraction", l: "Tourist attractions" },
                  { v: "hotels", l: "Hotels / Accommodation" },
                  { v: "sports_venue", l: "Sports venue / Stadium" },
                  { v: "beach", l: "Beach / Waterfront" },
                  { v: "park_nature", l: "Park / Nature / Hiking" },
                  { v: "nightlife", l: "Nightlife / Entertainment district" },
                  { v: "market", l: "Market / Food hall" },
                  { v: "cultural", l: "Museum / Gallery / Theatre" },
                  { v: "religious", l: "Church / Mosque / Temple" },
                  { v: "gym_sports", l: "Gym / Sports facilities" },
                  { v: "airport", l: "Airport" },
                  { v: "highway", l: "Major highway / Motorway" },
                  { v: "industrial", l: "Industrial / Business park" },
                  { v: "parking", l: "Free parking available" },
                  { v: "nothing_nearby", l: "Nothing notable -- we are the draw" },
                ].map((opt) => (
                  <button
                    key={opt.v}
                    onClick={() => toggleMulti("nearby_anchors", opt.v)}
                    className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                      ((form.nearby_anchors as string[]) || []).includes(opt.v)
                        ? "border-murmur-amber bg-murmur-amber text-white"
                        : "border-gray-200 text-gray-500 hover:bg-gray-50"
                    }`}
                  >
                    {opt.l}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">What drives traffic to your platform?</label>
              <p className="mb-2 text-xs text-gray-400">Select all that apply</p>
              <div className="flex flex-wrap gap-1.5">
                {[
                  { v: "organic_seo", l: "Organic search / SEO" },
                  { v: "paid_acquisition", l: "Paid acquisition (ads)" },
                  { v: "viral_growth", l: "Viral / product-led growth" },
                  { v: "integrations", l: "Integrations / ecosystem" },
                  { v: "community", l: "Community / forums" },
                  { v: "freemium", l: "Free tier / freemium" },
                  { v: "api_developers", l: "Developer API / documentation" },
                  { v: "enterprise_sales", l: "Enterprise sales team" },
                  { v: "resellers", l: "Resellers / channel partners" },
                  { v: "marketplace_listing", l: "Marketplace / directory listing" },
                  { v: "content", l: "Content / thought leadership" },
                  { v: "webinars", l: "Webinars / demos" },
                  { v: "open_source", l: "Open source / community edition" },
                ].map((opt) => (
                  <button
                    key={opt.v}
                    onClick={() => toggleMulti("nearby_anchors", opt.v)}
                    className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                      ((form.nearby_anchors as string[]) || []).includes(opt.v)
                        ? "border-murmur-amber bg-murmur-amber text-white"
                        : "border-gray-200 text-gray-500 hover:bg-gray-50"
                    }`}
                  >
                    {opt.l}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Competition -- same for both but different framing */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">How crowded is your market?</label>
            <div className="flex flex-wrap gap-1.5">
              {[
                { v: "only_one", l: "We are the only option" },
                { v: "niche", l: "Niche -- few direct competitors" },
                { v: "one_two", l: "1-2 main alternatives" },
                { v: "three_five", l: "3-5 alternatives" },
                { v: "six_plus", l: "6+ alternatives" },
                { v: "saturated", l: "Highly saturated / red ocean" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("competitor_count", opt.v)}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
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
            <label className="mb-2 block text-sm font-medium text-gray-700">What do competitors do better than you?</label>
            <p className="mb-2 text-xs text-gray-400">Be honest -- this shapes how we model switching risk</p>
            <div className="flex flex-wrap gap-1.5">
              {[
                { v: "cheaper", l: "Lower prices" },
                { v: "better_quality", l: "Better quality / product" },
                ...(!form.is_online_only ? [
                  { v: "more_convenient", l: "Better location" },
                  { v: "better_parking", l: "Better parking / access" },
                  { v: "better_ambiance", l: "Better atmosphere / vibe" },
                ] : [
                  { v: "better_ux", l: "Better UX / design" },
                  { v: "more_features", l: "More features" },
                  { v: "better_integrations", l: "Better integrations" },
                ]),
                { v: "better_brand", l: "Stronger brand" },
                { v: "wider_selection", l: "Wider selection / range" },
                { v: "better_service", l: "Better customer service" },
                { v: "faster", l: "Faster / more efficient" },
                { v: "better_tech", l: "Better technology" },
                { v: "bigger_marketing", l: "Bigger marketing budget" },
                { v: "more_trust", l: "More reviews / social proof" },
                { v: "better_content", l: "Better content / education" },
                { v: "nothing", l: "Nothing -- we are the best" },
              ].map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => toggleMulti("competitor_advantage", opt.v)}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                    ((form.competitor_advantage as string[]) || []).includes(opt.v)
                      ? "border-murmur-amber bg-murmur-amber text-white"
                      : "border-gray-200 text-gray-500 hover:bg-gray-50"
                  }`}
                >
                  {opt.l}
                </button>
              ))}
            </div>
          </div>

          {/* Location advantage -- adapts */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              {form.is_online_only ? "Is your market position an advantage?" : "Is your location an advantage?"}
            </label>
            <div className="flex flex-wrap gap-1.5">
              {(form.is_online_only ? [
                { v: "major_advantage", l: "Strong moat -- hard for competitors to replicate" },
                { v: "slight_advantage", l: "Some advantages but not defensible" },
                { v: "neutral", l: "Neutral -- could go either way" },
                { v: "slight_disadvantage", l: "Late to market / playing catch-up" },
                { v: "major_disadvantage", l: "Competing against established giants" },
              ] : [
                { v: "major_advantage", l: "Prime spot -- high visibility, easy access" },
                { v: "slight_advantage", l: "Good location but not perfect" },
                { v: "neutral", l: "Average -- location is not a factor" },
                { v: "slight_disadvantage", l: "Not ideal -- hard to find or park" },
                { v: "major_disadvantage", l: "Poor location -- we survive despite it" },
              ]).map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => update("location_advantage", opt.v)}
                  className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
                    (form.location_advantage as string) === opt.v
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
            <label className="mb-1 block text-sm font-medium text-gray-700">Past changes and how customers reacted</label>
            <p className="mb-3 text-xs text-gray-400">
              If you have ever changed prices, hours, products, branding, or anything else and seen what happened,
              this is the most valuable data you can give us. Real outcomes from YOUR business beat any research paper.
            </p>

            {/* Existing entries */}
            {((form.prior_changes as { change: string; year: string; outcome: string; metrics: string }[]) || []).map((entry, i) => (
              <div key={i} className="mb-3 rounded-xl border border-gray-200 bg-white p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500">Change {i + 1}</span>
                  <button
                    onClick={() => {
                      const updated = [...(form.prior_changes as { change: string; year: string; outcome: string; metrics: string }[])];
                      updated.splice(i, 1);
                      update("prior_changes", updated);
                      if (updated.length === 0) update("has_prior_change", false);
                    }}
                    className="text-[10px] text-gray-400 hover:text-legacy-red"
                  >
                    remove
                  </button>
                </div>
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <input
                      value={entry.change}
                      onChange={(e) => {
                        const updated = [...(form.prior_changes as { change: string; year: string; outcome: string; metrics: string }[])];
                        updated[i] = { ...entry, change: e.target.value };
                        update("prior_changes", updated);
                      }}
                      placeholder="What did you change? (e.g. raised prices 10%, closed Mondays, added delivery)"
                      className="flex-1 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs focus:bg-white focus:outline-none focus:border-murmur-amber"
                    />
                    <input
                      value={entry.year}
                      onChange={(e) => {
                        const updated = [...(form.prior_changes as { change: string; year: string; outcome: string; metrics: string }[])];
                        updated[i] = { ...entry, year: e.target.value };
                        update("prior_changes", updated);
                      }}
                      placeholder="When? (e.g. 2023)"
                      className="w-24 shrink-0 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs focus:bg-white focus:outline-none focus:border-murmur-amber"
                    />
                  </div>
                  <textarea
                    value={entry.outcome}
                    onChange={(e) => {
                      const updated = [...(form.prior_changes as { change: string; year: string; outcome: string; metrics: string }[])];
                      updated[i] = { ...entry, outcome: e.target.value };
                      update("prior_changes", updated);
                    }}
                    placeholder="What actually happened? How did customers react? Did anyone leave? Did new customers come? Be specific."
                    rows={2}
                    className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs focus:bg-white focus:outline-none focus:border-murmur-amber"
                  />
                  <textarea
                    value={entry.metrics}
                    onChange={(e) => {
                      const updated = [...(form.prior_changes as { change: string; year: string; outcome: string; metrics: string }[])];
                      updated[i] = { ...entry, metrics: e.target.value };
                      update("prior_changes", updated);
                    }}
                    placeholder="Any numbers? (e.g. revenue dropped 5% for 2 months then recovered, lost ~10 regulars, gained 20 new customers, reviews went from 4.5 to 4.2)"
                    rows={2}
                    className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs focus:bg-white focus:outline-none focus:border-murmur-amber"
                  />
                </div>
              </div>
            ))}

            {/* Add button */}
            <button
              onClick={() => {
                const current = (form.prior_changes as { change: string; year: string; outcome: string; metrics: string }[]) || [];
                update("prior_changes", [...current, { change: "", year: "", outcome: "", metrics: "" }]);
                update("has_prior_change", true);
              }}
              className="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-gray-200 py-3 text-sm text-gray-400 transition-colors hover:border-murmur-amber hover:text-murmur-amber"
            >
              <span className="text-lg">+</span>
              {((form.prior_changes as unknown[]) || []).length === 0 ? "Add a past change" : "Add another change"}
            </button>
            <p className="mt-2 text-[10px] text-gray-400">
              The more changes you document with real outcomes, the better we can calibrate the simulation to YOUR business -- not just general research.
            </p>
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
