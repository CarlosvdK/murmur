"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { listBusinesses, updateBusiness, Business, BusinessCreate } from "@/lib/api";
import { createClient } from "@/lib/supabase/client";

const BUSINESS_TYPES = [
  "Restaurant", "Cafe / Coffee Shop", "Bar / Pub", "Barbershop / Salon",
  "Grocery Store", "Retail Shop", "Gym / Fitness", "Bakery", "Auto Shop", "Other",
];
const TYPE_MAP: Record<string, string> = {
  "Restaurant": "restaurant", "Cafe / Coffee Shop": "cafe", "Bar / Pub": "bar",
  "Barbershop / Salon": "barbershop", "Grocery Store": "grocery", "Retail Shop": "retail",
  "Gym / Fitness": "gym", "Bakery": "bakery", "Auto Shop": "auto", "Other": "other",
};
const TYPE_REVERSE: Record<string, string> = Object.fromEntries(
  Object.entries(TYPE_MAP).map(([k, v]) => [v, k])
);

const BUSINESS_ROLES = [
  { value: "habit", label: "A habit or routine" },
  { value: "daily_need", label: "A daily need" },
  { value: "treat", label: "A treat or reward" },
  { value: "social", label: "A social spot" },
  { value: "convenience", label: "Pure convenience" },
  { value: "destination", label: "A destination" },
];

const VALUE_DRIVERS = [
  { value: "specific_product", label: "A specific product or dish" },
  { value: "atmosphere", label: "The atmosphere or vibe" },
  { value: "personal_touch", label: "The personal touch" },
  { value: "location", label: "Location and convenience" },
  { value: "value", label: "Value for money" },
  { value: "quality", label: "Quality above everything" },
  { value: "social", label: "The social experience" },
  { value: "consistency", label: "Consistency and reliability" },
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

function Chip({ label, active, onClick, disabled }: { label: string; active: boolean; onClick: () => void; disabled?: boolean }) {
  return (
    <button onClick={onClick} disabled={disabled} className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${active ? "border-brand-orange bg-brand-orange text-white" : disabled ? "border-gray-100 text-gray-300" : "border-[#E5E2DC] text-gray-500 hover:bg-gray-50"}`}>
      {label}
    </button>
  );
}

function Section({ title, description, children, defaultOpen = false }: { title: string; description?: string; children: React.ReactNode; defaultOpen?: boolean }) {
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

  // Notification preferences
  const [notifSimComplete, setNotifSimComplete] = useState(true);
  const [notifSignals, setNotifSignals] = useState(true);
  const [notifWeekly, setNotifWeekly] = useState(false);
  const [notifMarketing, setNotifMarketing] = useState(false);

  // All survey fields
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

  useEffect(() => {
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
          setAreaDemographics(b.area_demographics || []);
          setCompetitorCount(b.competitor_count || ""); setAreaFeel(b.area_feel || "");
          setWebsiteUrl(b.website_url || ""); setAdditionalNotes(b.additional_customer_notes || "");
          setHasPriorChange(b.has_prior_change || false);
          setPriorChangeDesc(b.prior_change_description || "");
          setPriorChangeOutcome(b.prior_change_outcome || "");
        }
      } catch { /* */ }
      finally { setLoading(false); }
    }
    load();
  }, []);

  const toggleArr = (arr: string[], val: string, setter: (v: string[]) => void) => {
    setter(arr.includes(val) ? arr.filter((v) => v !== val) : [...arr, val]);
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
        years_open: yearsOpen || undefined,
        customer_description: customerDescription || undefined,
        business_role: businessRole || undefined, visit_frequency: visitFrequency || undefined,
        busy_days: busyDays.length ? busyDays : undefined,
        busy_times: busyTimes.length ? busyTimes : undefined,
        customer_value_drivers: valueDrivers.length ? valueDrivers : undefined,
        customer_social_context: socialContext.length ? socialContext : undefined,
        regular_proportion: regularProportion || undefined,
        area_demographics: areaDemographics.length ? areaDemographics : undefined,
        competitor_count: competitorCount || undefined, area_feel: areaFeel || undefined,
        website_url: websiteUrl || undefined,
        additional_customer_notes: additionalNotes || undefined,
        has_prior_change: hasPriorChange,
        prior_change_description: priorChangeDesc || undefined,
        prior_change_outcome: priorChangeOutcome || undefined,
      };
      const result = await updateBusiness(business.id, data);
      setBusiness(result);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) { console.error("Save failed", e); }
    finally { setSaving(false); }
  }

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-gray-400">Loading...</p></div>;

  const tabs: { key: SettingsTab; label: string }[] = [
    { key: "profile", label: "Profile" },
    { key: "notifications", label: "Notifications" },
    { key: "privacy", label: "Privacy & Security" },
    { key: "billing", label: "Billing" },
  ];

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
            {/* Account info */}
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 font-semibold text-black">Account</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs text-gray-500">Email</label>
                  <input value={email} className="w-full rounded-lg border border-[#E5E2DC] bg-gray-50 px-3 py-2 text-sm" disabled />
                </div>
                <div>
                  <label className="mb-1 block text-xs text-gray-500">Password</label>
                  <button className="mt-1 text-sm text-brand-blue hover:underline">Change password</button>
                </div>
              </div>
            </div>

            {/* Business profile -- clickable to expand, shows summary when collapsed */}
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <div className="mb-1 flex items-center justify-between">
                <h3 className="font-semibold text-black">Business profile</h3>
                {business && <span className="rounded-full bg-green-50 px-2 py-0.5 text-[10px] font-medium text-green-600">Active</span>}
              </div>
              <p className="mb-4 text-sm text-gray-500">{name || "No business"}{type ? ` -- ${TYPE_REVERSE[type] || type}` : ""}{location ? ` in ${location}` : ""}</p>
              <p className="text-xs text-gray-400">Edit the sections below to update your business profile. Changes improve simulation accuracy.</p>
            </div>

            {/* Collapsible survey sections */}
            <Section title="Business details" description="Name, type, location, and description" defaultOpen>
              <div className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-xs text-gray-500">Business name</label>
                    <input value={name} onChange={(e) => setName(e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-gray-500">Business type</label>
                    <select value={TYPE_REVERSE[type] || ""} onChange={(e) => setType(TYPE_MAP[e.target.value] || e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none">
                      <option value="">Select...</option>
                      {BUSINESS_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-gray-500">Years open</label>
                    <div className="flex gap-1.5">
                      {["<1", "1-3", "3-10", "10+"].map((v) => (
                        <Chip key={v} label={v} active={yearsOpen === v} onClick={() => setYearsOpen(v)} />
                      ))}
                    </div>
                  </div>
                </div>
                <div className="mt-4">
                  <label className="mb-2 block text-xs font-medium text-gray-500">Address</label>
                  <div className="grid gap-3 sm:grid-cols-4">
                    <div className="sm:col-span-2">
                      <input value={locationStreet} onChange={(e) => setLocationStreet(e.target.value)} placeholder="Street" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                    </div>
                    <div>
                      <input value={locationNumber} onChange={(e) => setLocationNumber(e.target.value)} placeholder="Number" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                    </div>
                    <div>
                      <input value={locationPostcode} onChange={(e) => setLocationPostcode(e.target.value)} placeholder="Postcode" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                    </div>
                    <div>
                      <input value={locationCity} onChange={(e) => setLocationCity(e.target.value)} placeholder="City" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                    </div>
                    <div>
                      <input value={locationNeighbourhood} onChange={(e) => setLocationNeighbourhood(e.target.value)} placeholder="Neighbourhood" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                    </div>
                    <div className="sm:col-span-2">
                      <input value={locationCountry} onChange={(e) => setLocationCountry(e.target.value)} placeholder="Country" className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                    </div>
                  </div>
                </div>
                <div>
                  <label className="mb-1 block text-xs text-gray-500">Description</label>
                  <textarea rows={3} value={description} onChange={(e) => setDescription(e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-xs text-gray-500">Website</label>
                  <input value={websiteUrl} onChange={(e) => setWebsiteUrl(e.target.value)} placeholder="https://..." className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                </div>
              </div>
            </Section>

            <Section title="Customer profile" description="Who your customers are and what they value">
              <div className="space-y-5">
                <div>
                  <label className="mb-1 block text-xs text-gray-500">Describe your typical customer</label>
                  <textarea rows={3} value={customerDescription} onChange={(e) => setCustomerDescription(e.target.value)} className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                </div>
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Role your business plays in their life</label>
                  <div className="flex flex-wrap gap-1.5">
                    {BUSINESS_ROLES.map((r) => <Chip key={r.value} label={r.label} active={businessRole === r.value} onClick={() => setBusinessRole(r.value)} />)}
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Visit frequency</label>
                  <div className="flex flex-wrap gap-1.5">
                    {[{ v: "daily", l: "Daily" }, { v: "weekly", l: "Weekly" }, { v: "monthly", l: "Monthly" }, { v: "occasional", l: "Occasional" }, { v: "mixed", l: "Mixed" }].map((o) => (
                      <Chip key={o.v} label={o.l} active={visitFrequency === o.v} onClick={() => setVisitFrequency(o.v)} />
                    ))}
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-xs text-gray-500">Busiest days</label>
                    <div className="flex flex-wrap gap-1.5">
                      {["mon", "tue", "wed", "thu", "fri", "sat", "sun"].map((d) => (
                        <Chip key={d} label={d.charAt(0).toUpperCase() + d.slice(1)} active={busyDays.includes(d)} onClick={() => toggleArr(busyDays, d, setBusyDays)} />
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="mb-2 block text-xs text-gray-500">Busiest times</label>
                    <div className="flex flex-wrap gap-1.5">
                      {["morning", "lunchtime", "afternoon", "evening", "late night"].map((t) => (
                        <Chip key={t} label={t.charAt(0).toUpperCase() + t.slice(1)} active={busyTimes.includes(t)} onClick={() => toggleArr(busyTimes, t, setBusyTimes)} />
                      ))}
                    </div>
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-xs text-gray-500">What do they value most? (up to 3)</label>
                  <div className="flex flex-wrap gap-1.5">
                    {VALUE_DRIVERS.map((vd) => {
                      const active = valueDrivers.includes(vd.value);
                      const atMax = valueDrivers.length >= 3 && !active;
                      return <Chip key={vd.value} label={vd.label} active={active} disabled={atMax} onClick={() => !atMax && toggleArr(valueDrivers, vd.value, setValueDrivers)} />;
                    })}
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Social setup</label>
                  <div className="flex flex-wrap gap-1.5">
                    {["on_their_own", "with_a_partner", "with_family_kids", "with_friends", "with_work_colleagues", "changes_a_lot"].map((v) => (
                      <Chip key={v} label={v.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase())} active={socialContext.includes(v)} onClick={() => toggleArr(socialContext, v, setSocialContext)} />
                    ))}
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-xs text-gray-500">How many regulars?</label>
                  <div className="flex flex-wrap gap-1.5">
                    {[{ v: "almost_none", l: "Almost none" }, { v: "handful", l: "A handful" }, { v: "solid_base", l: "Solid base (50+)" }, { v: "mostly_regulars", l: "Mostly regulars" }].map((o) => (
                      <Chip key={o.v} label={o.l} active={regularProportion === o.v} onClick={() => setRegularProportion(o.v)} />
                    ))}
                  </div>
                </div>
              </div>
            </Section>

            <Section title="Local area" description="Your neighbourhood and competition">
              <div className="space-y-5">
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Area type (select all)</label>
                  <div className="flex flex-wrap gap-1.5">
                    {AREA_TYPES.map((at) => <Chip key={at.value} label={at.label} active={areaDemographics.includes(at.value)} onClick={() => toggleArr(areaDemographics, at.value, setAreaDemographics)} />)}
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Competition</label>
                  <div className="flex flex-wrap gap-1.5">
                    {[{ v: "only_one", l: "Only one" }, { v: "one_two", l: "1-2 others" }, { v: "three_five", l: "3-5" }, { v: "six_plus", l: "6+" }].map((o) => (
                      <Chip key={o.v} label={o.l} active={competitorCount === o.v} onClick={() => setCompetitorCount(o.v)} />
                    ))}
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Area feel</label>
                  <div className="flex flex-wrap gap-1.5">
                    {AREA_FEELS.map((af) => <Chip key={af.value} label={af.label} active={areaFeel === af.value} onClick={() => setAreaFeel(af.value)} />)}
                  </div>
                </div>
              </div>
            </Section>

            <Section title="Extra context" description="Prior changes and additional notes">
              <div className="space-y-5">
                <div>
                  <label className="mb-1 block text-xs text-gray-500">Additional customer notes</label>
                  <textarea rows={3} value={additionalNotes} onChange={(e) => setAdditionalNotes(e.target.value)} placeholder="Anything else about your customers..." className="w-full rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                </div>
                <div>
                  <label className="mb-2 block text-xs text-gray-500">Have you made a big change before?</label>
                  <div className="flex gap-1.5">
                    <Chip label="Yes" active={hasPriorChange} onClick={() => setHasPriorChange(true)} />
                    <Chip label="No" active={!hasPriorChange} onClick={() => setHasPriorChange(false)} />
                  </div>
                  {hasPriorChange && (
                    <div className="mt-3 space-y-3 rounded-lg border border-[#E5E2DC] bg-gray-50 p-4">
                      <input value={priorChangeDesc} onChange={(e) => setPriorChangeDesc(e.target.value)} placeholder="What did you change?" className="w-full rounded-lg border border-[#E5E2DC] bg-white px-3 py-2 text-sm" />
                      <input value={priorChangeOutcome} onChange={(e) => setPriorChangeOutcome(e.target.value)} placeholder="What happened?" className="w-full rounded-lg border border-[#E5E2DC] bg-white px-3 py-2 text-sm" />
                      <p className="text-[11px] text-gray-400">Real outcomes from past changes help calibrate future simulations.</p>
                    </div>
                  )}
                </div>
              </div>
            </Section>

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
          <div className="space-y-4">
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 font-semibold text-black">Email notifications</h3>
              <div className="space-y-4">
                {[
                  { label: "Simulation complete", desc: "Get notified when a simulation finishes running", state: notifSimComplete, setter: setNotifSimComplete },
                  { label: "Relationship signals", desc: "Alerts when a contact's sentiment changes or a signal is detected", state: notifSignals, setter: setNotifSignals },
                  { label: "Weekly digest", desc: "A summary of your simulations, twin activity, and portfolio health", state: notifWeekly, setter: setNotifWeekly },
                  { label: "Product updates", desc: "New features, improvements, and tips", state: notifMarketing, setter: setNotifMarketing },
                ].map((n) => (
                  <div key={n.label} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-black">{n.label}</p>
                      <p className="text-xs text-gray-500">{n.desc}</p>
                    </div>
                    <button
                      onClick={() => n.setter(!n.state)}
                      className={`relative h-6 w-11 rounded-full transition-colors ${n.state ? "bg-brand-orange" : "bg-gray-200"}`}
                    >
                      <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${n.state ? "left-[22px]" : "left-0.5"}`} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ====== PRIVACY & SECURITY ====== */}
        {tab === "privacy" && (
          <div className="space-y-4">
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 font-semibold text-black">Data & Privacy</h3>
              <div className="space-y-4 text-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-black">Export your data</p>
                    <p className="text-xs text-gray-500">Download all your business data, simulations, and contacts</p>
                  </div>
                  <button className="rounded-lg border border-[#E5E2DC] px-4 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50">Export</button>
                </div>
                <div className="border-t border-[#E5E2DC] pt-4">
                  <p className="font-medium text-black">How we handle your data</p>
                  <ul className="mt-2 space-y-1.5 text-xs text-gray-500">
                    <li>-- Your business data is stored securely in Supabase (EU region)</li>
                    <li>-- Uploaded correspondence is processed in memory and deleted immediately</li>
                    <li>-- Only anonymised communication patterns are stored for twins</li>
                    <li>-- Simulation prompts and responses are logged for accuracy improvement</li>
                    <li>-- We never sell or share your data with third parties</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 font-semibold text-black">Security</h3>
              <div className="space-y-4 text-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-black">Change password</p>
                    <p className="text-xs text-gray-500">Update your account password</p>
                  </div>
                  <button className="rounded-lg border border-[#E5E2DC] px-4 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50">Change</button>
                </div>
                <div className="flex items-center justify-between border-t border-[#E5E2DC] pt-4">
                  <div>
                    <p className="font-medium text-black">Sign out</p>
                    <p className="text-xs text-gray-500">Sign out of your account on this device</p>
                  </div>
                  <button onClick={handleSignOut} className="rounded-lg border border-[#E5E2DC] px-4 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50">Sign out</button>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-red-200 bg-red-50/50 p-5">
              <h3 className="mb-2 font-semibold text-red-700">Danger zone</h3>
              <p className="mb-4 text-sm text-red-600/70">Permanently delete your account, business data, contacts, and all simulation history. This cannot be undone.</p>
              {showDeleteConfirm ? (
                <div className="flex items-center gap-3">
                  <button onClick={() => setShowDeleteConfirm(false)} className="rounded-lg border border-[#E5E2DC] px-4 py-1.5 text-xs text-gray-600 hover:bg-white">Cancel</button>
                  <button className="rounded-lg bg-red-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-red-700">Yes, delete everything</button>
                </div>
              ) : (
                <button onClick={() => setShowDeleteConfirm(true)} className="rounded-lg border border-red-300 px-4 py-1.5 text-xs font-medium text-red-600 hover:bg-red-100">Delete account</button>
              )}
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
                <ul className="mt-3 space-y-1 text-sm text-gray-600">
                  <li>Unlimited simulations</li><li>50 contacts, 20 organisations</li>
                  <li>Digital twins</li><li>Correspondence upload</li>
                </ul>
                <button className="mt-4 w-full rounded-lg bg-brand-orange px-4 py-2 text-sm font-medium text-white hover:opacity-90">Upgrade</button>
              </div>
              <div className="rounded-xl border-2 border-brand-pink/30 bg-brand-pink/5 p-6">
                <h4 className="font-semibold text-black">Intelligence</h4>
                <p className="mt-1 text-2xl font-bold text-black">199 EUR<span className="text-sm font-normal text-gray-500">/month</span></p>
                <ul className="mt-3 space-y-1 text-sm text-gray-600">
                  <li>Everything in Connect</li><li>Unlimited contacts</li>
                  <li>Organisation intelligence</li><li>Vendor twin</li>
                </ul>
                <button className="mt-4 w-full rounded-lg bg-brand-pink px-4 py-2 text-sm font-medium text-white hover:opacity-90">Upgrade</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
