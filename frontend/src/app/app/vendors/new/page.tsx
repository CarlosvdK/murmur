"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import FormField from "@/components/forms/FormField";
import FormSection from "@/components/forms/FormSection";
import AccuracyBar from "@/components/forms/AccuracyBar";
import FileUploadZone from "@/components/forms/FileUploadZone";
import { createContact } from "@/lib/api";
import { computeCompleteness, VENDOR_FIELD_WEIGHTS } from "@/lib/completeness";

export default function NewVendorPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [savedId, setSavedId] = useState<string | null>(null);
  const [form, setForm] = useState<Record<string, unknown>>({});
  const set = (field: string, value: unknown) => setForm((prev) => ({ ...prev, [field]: value }));

  const { score, milestoneMessage, nextImprovement } = useMemo(
    () => computeCompleteness(form, VENDOR_FIELD_WEIGHTS), [form]
  );

  const handleSave = async () => {
    setSaving(true);
    try {
      const f = form as Record<string, unknown>;
      const contact = await createContact({
        first_name: (f.first_name as string) || "Unnamed",
        last_name: f.last_name,
        email: f.email,
        phone: f.phone,
        linkedin_url: f.linkedin_url,
        contact_type: "vendor",
        notes: f.vendor_relationship_notes,
        extra_data: f,
      });
      setSavedId(contact.id);
    } catch { alert("Failed to save"); }
    setSaving(false);
  };

  return (
    <div className="overflow-y-auto p-8 lg:p-12" style={{ background: "#F5F3EF" }}>
      <div className="mx-auto max-w-3xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <button onClick={() => router.back()} className="mb-2 text-xs text-gray-400 hover:text-black">&larr; Back to vendors</button>
            <h1 className="text-2xl font-bold text-black">Create Vendor Twin</h1>
          </div>
          <button onClick={handleSave} disabled={saving}
            className="rounded-lg bg-black px-6 py-2.5 text-sm font-medium text-white hover:opacity-80 disabled:opacity-50">
            {saving ? "Saving..." : "Generate Twin"}
          </button>
        </div>

        <div className="mb-4 rounded-xl border border-brand-orange/15 bg-brand-orange/5 p-4">
          <p className="text-sm text-gray-600">The more you share about this vendor, the better Murmur can predict how they&apos;ll respond to any request or conversation.</p>
          <p className="mt-2 text-xs italic text-gray-400">
            These fields power predictions for any vendor question -- discounts, delivery terms, exclusivity, switching, capacity increases, contract renewals, and more.
          </p>
        </div>

        <div className="mb-6"><AccuracyBar score={score} milestoneMessage={milestoneMessage} nextImprovement={nextImprovement} /></div>

        <div className="space-y-3">
          {/* SECTION 1: Basic contact */}
          <FormSection title="Who are they?" defaultOpen>
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="First name" name="first_name" placeholder="e.g. Jan" value={form.first_name} onChange={(v) => set("first_name", v)} />
              <FormField label="Last name" name="last_name" placeholder="e.g. De Vries" value={form.last_name} onChange={(v) => set("last_name", v)} />
              <FormField label="Email" name="email" placeholder="email@domain.com" value={form.email} onChange={(v) => set("email", v)} />
              <FormField label="Phone / WhatsApp" name="phone" placeholder="+31 6 1234 5678" value={form.phone} onChange={(v) => set("phone", v)} />
              <FormField label="LinkedIn" name="linkedin_url" placeholder="linkedin.com/in/username" whyItMatters="Helps us understand their professional background and communication style" value={form.linkedin_url} onChange={(v) => set("linkedin_url", v)} />
              <FormField label="Company name" name="company" placeholder="e.g. Fresh Foods Ltd" value={form.company} onChange={(v) => set("company", v)} />
              <FormField label="Company website" name="company_website" placeholder="company.com" value={form.company_website} onChange={(v) => set("company_website", v)} />
              <FormField label="Company LinkedIn" name="company_linkedin" placeholder="linkedin.com/company/name" value={form.company_linkedin} onChange={(v) => set("company_linkedin", v)} />
            </div>
          </FormSection>

          {/* SECTION 2: The vendor company */}
          <FormSection title="About their business" whyItMatters="Vendor category affects typical negotiation room and market dynamics">
            <FormField label="What category of vendor?" name="vendor_category" type="chips" options={[
              { value: "food_drink", label: "Food & drink" }, { value: "ingredients", label: "Ingredients / raw materials" },
              { value: "packaging", label: "Packaging" }, { value: "equipment", label: "Equipment & machinery" },
              { value: "technology", label: "Technology & software" }, { value: "cleaning", label: "Cleaning & maintenance" },
              { value: "staffing", label: "Staffing & HR" }, { value: "marketing", label: "Marketing & design" },
              { value: "logistics", label: "Logistics & delivery" }, { value: "utilities", label: "Utilities" },
              { value: "professional", label: "Professional services" }, { value: "other", label: "Other" },
            ]} value={form.vendor_category} onChange={(v) => set("vendor_category", v)} />
            <FormField label="Main product or service they supply" name="main_supply" type="textarea" rows={2}
              placeholder='e.g. "Weekly vegetable and fruit delivery"' value={form.main_supply} onChange={(v) => set("main_supply", v)} />
            <FormField label="Company size" name="vendor_company_size" type="select" options={[
              { value: "solo", label: "Solo / freelancer" }, { value: "small", label: "Small (2-10)" },
              { value: "medium", label: "Medium (11-100)" }, { value: "large", label: "Large (100+)" },
              { value: "group", label: "Part of a bigger group" }, { value: "unsure", label: "Not sure" },
            ]} whyItMatters="Smaller vendors often have more negotiation flexibility but more supply risk" value={form.vendor_company_size} onChange={(v) => set("vendor_company_size", v)} />
            <FormField label="Client importance" name="client_importance" type="select" options={[
              { value: "biggest", label: "We're their biggest client" },
              { value: "one_of_several", label: "One of several similar clients" },
              { value: "small", label: "We're a small client for them" },
              { value: "unsure", label: "Not sure" },
            ]} whyItMatters="If you're their biggest client you have more leverage" value={form.client_importance} onChange={(v) => set("client_importance", v)} />
          </FormSection>

          {/* SECTION 3: Commercial relationship */}
          <FormSection title="Contract and relationship details" subtitle="shapes predictions for any question you ask about this vendor" whyItMatters="Commercial context affects how this vendor would respond to any request -- not just price, but delivery, exclusivity, capacity, and terms">
            <FormField label="How long have you worked together?" name="tenure_vendor" type="select" options={[
              { value: "<6m", label: "Less than 6 months" }, { value: "6-12m", label: "6-12 months" },
              { value: "1-3y", label: "1-3 years" }, { value: "3-10y", label: "3-10 years" },
              { value: "10y+", label: "More than 10 years" },
            ]} whyItMatters="Longer relationships have different negotiation dynamics" value={form.tenure_vendor} onChange={(v) => set("tenure_vendor", v)} />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="Annual spend (approximate)" name="annual_spend_vendor" type="number" placeholder="e.g. 24000"
                whyItMatters="Affects how much flexibility this vendor is likely to show on any request -- not just price, but delivery terms, lead times, exclusivity, and prioritisation" value={form.annual_spend_vendor} onChange={(v) => set("annual_spend_vendor", v)} />
              <FormField label="Payment terms" name="payment_terms" type="select" options={[
                { value: "net7", label: "Net 7" }, { value: "net14", label: "Net 14" }, { value: "net30", label: "Net 30" },
                { value: "net60", label: "Net 60" }, { value: "delivery", label: "On delivery" },
                { value: "advance", label: "In advance" },
              ]} whyItMatters="Vendors balance multiple factors when responding to requests. Current terms give context for what they might offer in return for different asks -- price, speed, priority, exclusivity." value={form.payment_terms} onChange={(v) => set("payment_terms", v)} />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="Contract type" name="contract_type" type="select" options={[
                { value: "none", label: "No formal contract" }, { value: "monthly", label: "Rolling month-to-month" },
                { value: "fixed", label: "Fixed term" }, { value: "annual", label: "Annual" }, { value: "multi_year", label: "Multi-year" },
              ]} value={form.contract_type} onChange={(v) => set("contract_type", v)} />
              <FormField label="Contract renewal date" name="contract_renewal_date" type="date"
                whyItMatters="Renewal windows are when leverage is highest" value={form.contract_renewal_date} onChange={(v) => set("contract_renewal_date", v)} />
            </div>
            <FormField label="Alternative vendors available?" name="has_alternatives" type="select" options={[
              { value: "several", label: "Yes -- several ready" }, { value: "disruptive", label: "Yes -- but switching would be disruptive" },
              { value: "sole", label: "No -- essentially sole supplier" }, { value: "not_looked", label: "Haven't looked yet" },
            ]} whyItMatters="Alternatives affect how much flexibility a vendor shows on any request -- the more options you have, the more willing they are to accommodate" value={form.has_alternatives} onChange={(v) => set("has_alternatives", v)} />
            <FormField label="How critical are they?" name="criticality_score" type="slider"
              options={{ left: "Not critical -- easy to replace", right: "Mission critical" }}
              whyItMatters="How critical a vendor is affects how you'd both approach any difficult conversation -- whether it's about delivery speed, quality issues, exclusivity, or costs"
              value={form.criticality_score} onChange={(v) => set("criticality_score", v)} />
          </FormSection>

          {/* SECTION 4: Performance */}
          <FormSection title="Performance and reliability" whyItMatters="Performance history shapes trust and risk predictions">
            <div className="grid gap-4 sm:grid-cols-3">
              <FormField label="Quality" name="quality_rating" type="stars" value={form.quality_rating} onChange={(v) => set("quality_rating", v)} />
              <FormField label="Reliability" name="reliability_rating" type="stars" value={form.reliability_rating} onChange={(v) => set("reliability_rating", v)} />
              <FormField label="Communication" name="communication_rating" type="stars" value={form.communication_rating} onChange={(v) => set("communication_rating", v)} />
            </div>
            <FormField label="Have they made significant changes to your terms or conditions?" name="has_raised_prices" type="chips" multi={false}
              formatHint="e.g. price increases, payment term changes, reduced service levels, new minimums"
              options={[
              { value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" },
            ]} whyItMatters="Past behaviour is the strongest predictor of how they'll handle future conversations and requests for change" value={form.has_raised_prices} onChange={(v) => set("has_raised_prices", v)} />
            {form.has_raised_prices === "yes" && (
              <div className="space-y-3 rounded-lg border border-[#E5E2DC] bg-gray-50 p-4">
                <FormField label="How much did they raise by?" name="price_raise_amount" placeholder="e.g. 8% or 2 EUR per unit" value={form.price_raise_amount} onChange={(v) => set("price_raise_amount", v)} />
                <FormField label="How much warning?" name="price_raise_warning" placeholder="e.g. 2 weeks notice" value={form.price_raise_warning} onChange={(v) => set("price_raise_warning", v)} />
                <FormField label="How did they justify it?" name="price_raise_justification" type="textarea" rows={2} value={form.price_raise_justification} onChange={(v) => set("price_raise_justification", v)} />
              </div>
            )}
            <FormField label="Have you ever successfully asked for something and got it?" name="has_negotiated" type="chips" multi={false}
              formatHint="Better pricing, faster delivery, more flexibility, priority treatment, extended terms -- anything"
              whyItMatters="Knowing they've said yes before -- and in what circumstances -- predicts what they're likely to agree to next time"
              options={[
              { value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "never_tried", label: "Never tried" },
            ]} value={form.has_negotiated} onChange={(v) => set("has_negotiated", v)} />
            {form.has_negotiated === "yes" && (
              <FormField label="How did the negotiation go?" name="negotiation_description" type="textarea" rows={2}
                placeholder='e.g. "They pushed back initially but agreed after we mentioned a competitor quote"'
                value={form.negotiation_description} onChange={(v) => set("negotiation_description", v)} />
            )}
            <FormField label="Overall satisfaction" name="overall_satisfaction" type="slider"
              options={{ left: "Very unsatisfied", right: "Very satisfied" }}
              value={form.overall_satisfaction} onChange={(v) => set("overall_satisfaction", v)} />
          </FormSection>

          {/* SECTION 5: Relationship dynamics */}
          <FormSection title="Relationship dynamics" subtitle="most directly powers the digital twin" whyItMatters="This section shapes predictions for any request you make of this vendor -- not just negotiations. It affects how they'd respond to any conversation.">{/* Description */}
            <p className="text-xs text-gray-400 -mt-2 mb-3">This is the section that most directly powers the digital twin. It&apos;s not just about negotiations -- it shapes predictions for any request you make of this vendor.</p>
            <FormField label="Their communication style" name="communication_style" type="chips" whyItMatters="Critical for predicting how they'll respond to any request -- not just price. Someone who goes quiet under pressure will react differently to a delivery complaint than someone who's direct." options={[
              { value: "responsive", label: "Very responsive" }, { value: "slow", label: "Slow to respond" },
              { value: "direct", label: "Direct" }, { value: "formal", label: "Formal" },
              { value: "casual", label: "Casual and friendly" }, { value: "hard_reach", label: "Hard to get hold of" },
              { value: "negotiates_hard", label: "Negotiates hard" }, { value: "flexible", label: "Usually flexible" },
              { value: "quiet_pressure", label: "Goes quiet when under pressure" },
            ]} value={form.communication_style} onChange={(v) => set("communication_style", v)} />
            <FormField label="How do they handle difficult conversations or requests?" name="price_discussion_style" type="textarea" rows={2}
              placeholder='e.g. "Usually says no at first then comes around after a second conversation" or "Very direct -- gives a clear answer fast" or "Avoids the conversation and goes quiet"' value={form.price_discussion_style} onChange={(v) => set("price_discussion_style", v)} />
            <FormField label="What motivates them to keep your business?" name="vendor_motivation" type="chips" whyItMatters="What they value shapes how they respond to everything -- a vendor who values long relationships will respond differently to a difficult conversation than one who's purely transactional" options={[
              { value: "volume", label: "Volume" }, { value: "prompt_payment", label: "Prompt payment" },
              { value: "long_relationship", label: "Long relationship" }, { value: "referrals", label: "Referrals" },
              { value: "prestige", label: "Prestige" }, { value: "not_sure", label: "Not sure" },
            ]} value={form.vendor_motivation} onChange={(v) => set("vendor_motivation", v)} />
            <FormField label="Relationship notes" name="vendor_relationship_notes" type="textarea" rows={3}
              placeholder='e.g. "Jan is very relationship-focused -- always calls before price changes"'
              value={form.vendor_relationship_notes} onChange={(v) => set("vendor_relationship_notes", v)} />
          </FormSection>

          {/* SECTION 6: Market context */}
          <FormSection title="Market and risk context" whyItMatters="Market context shapes what requests are realistic -- if the whole sector is under pressure, asking for a discount lands differently than in a stable market">
            <FormField label="Market competitiveness" name="market_competitiveness" type="select" whyItMatters="Competition affects how easily you could switch vendors, which shapes how much flexibility they'll show on any request -- pricing, delivery, exclusivity, or terms" options={[
              { value: "very_competitive", label: "Very competitive -- many alternatives" },
              { value: "moderate", label: "Moderately competitive" },
              { value: "few", label: "Few alternatives -- niche market" },
              { value: "monopoly", label: "Near monopoly" },
            ]} value={form.market_competitiveness} onChange={(v) => set("market_competitiveness", v)} />
            <FormField label="Market-wide pressures in this category" name="price_trend" type="select" whyItMatters="Market context shapes what requests are realistic -- cost increases, supply shortages, new regulations, labour issues all affect what a vendor can offer" options={[
              { value: "rising_significant", label: "Significant increases" }, { value: "rising_slight", label: "Slight increases" },
              { value: "stable", label: "Stable" }, { value: "falling", label: "Prices falling" }, { value: "unsure", label: "Not sure" },
            ]} value={form.price_trend} onChange={(v) => set("price_trend", v)} />
            <FormField label="Supply chain concerns" name="supply_concerns" type="textarea" rows={2}
              placeholder='e.g. "Coffee prices globally very volatile"' value={form.supply_concerns} onChange={(v) => set("supply_concerns", v)} />
          </FormSection>

          {/* SECTION 7: File upload */}
          <FormSection title="Upload files to activate vendor twin" whyItMatters="Upload conversations, contracts, and invoices to build a predictive twin of this vendor">
            {savedId ? (
              <FileUploadZone contactId={savedId} contactType="vendor" contactName={(form.first_name as string) || "this vendor"} />
            ) : (
              <div className="rounded-lg border border-[#E5E2DC] bg-gray-50 p-6 text-center">
                <p className="text-sm text-gray-400">Save the vendor first, then upload files here.</p>
              </div>
            )}
          </FormSection>
        </div>

        <div className="mt-6 flex items-center justify-between">
          <button onClick={() => router.back()} className="text-sm text-gray-400 hover:text-black">Cancel</button>
          <button onClick={handleSave} disabled={saving}
            className="rounded-lg bg-black px-8 py-2.5 text-sm font-medium text-white hover:opacity-80 disabled:opacity-50">
            {saving ? "Saving..." : "Generate Twin"}
          </button>
        </div>
      </div>
    </div>
  );
}
