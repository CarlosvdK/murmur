"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import FormField from "@/components/forms/FormField";
import FormSection from "@/components/forms/FormSection";
import AccuracyBar from "@/components/forms/AccuracyBar";
import FileUploadZone from "@/components/forms/FileUploadZone";
import { createContact } from "@/lib/api";
import { computeCompleteness, CUSTOMER_FIELD_WEIGHTS } from "@/lib/completeness";

export default function NewCustomerPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [savedId, setSavedId] = useState<string | null>(null);

  const [form, setForm] = useState<Record<string, unknown>>({});

  const set = (field: string, value: unknown) => setForm((prev) => ({ ...prev, [field]: value }));

  const { score, milestoneMessage, nextImprovement } = useMemo(
    () => computeCompleteness(form, CUSTOMER_FIELD_WEIGHTS), [form]
  );

  const handleSave = async () => {
    setSaving(true);
    try {
      const f = form as Record<string, unknown>;
      const contact = await createContact({
        first_name: (f.first_name as string) || "Unnamed",
        last_name: f.last_name,
        job_title: f.occupation || f.job_title,
        email: f.email,
        phone: f.phone,
        linkedin_url: f.linkedin_url,
        city: f.city,
        country: f.country,
        contact_type: "customer",
        notes: f.relationship_notes,
        extra_data: f,
      });
      setSavedId(contact.id);
    } catch {
      alert("Failed to save");
    }
    setSaving(false);
  };

  return (
    <div className="overflow-y-auto p-8 lg:p-12" style={{ background: "#F5F3EF" }}>
      <div className="mx-auto max-w-3xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <button onClick={() => router.back()} className="mb-2 text-xs text-gray-400 hover:text-black">&larr; Back to customers</button>
            <h1 className="text-2xl font-bold text-black">Create Customer Twin</h1>
          </div>
          <button onClick={handleSave} disabled={saving}
            className="rounded-lg bg-black px-6 py-2.5 text-sm font-medium text-white hover:opacity-80 disabled:opacity-50">
            {saving ? "Saving..." : "Generate Twin"}
          </button>
        </div>

        {/* Motivation banner */}
        <div className="mb-4 rounded-xl border border-brand-blue/15 bg-brand-blue/5 p-4">
          <p className="text-sm text-gray-600">
            The more you share, the more accurate your simulation will be. Every field helps -- but nothing is required.
          </p>
          <p className="mt-2 text-xs italic text-gray-400">
            These fields power predictions for any question -- not just pricing. Opening hours, menu changes, new services, staff decisions, renovations -- every field helps Murmur understand how this person would react to anything you&apos;re considering.
          </p>
        </div>

        {/* Accuracy bar */}
        <div className="mb-6">
          <AccuracyBar score={score} milestoneMessage={milestoneMessage} nextImprovement={nextImprovement} />
        </div>

        <div className="space-y-3">
          {/* SECTION 1: Basic info */}
          <FormSection title="Who are they?" defaultOpen>
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="First name" name="first_name" placeholder="e.g. Maria" value={form.first_name} onChange={(v) => set("first_name", v)} />
              <FormField label="Last name" name="last_name" placeholder="e.g. Garcia" value={form.last_name} onChange={(v) => set("last_name", v)} />
              <FormField label="Email address" name="email" placeholder="email@domain.com" formatHint="Format: email@domain.com" value={form.email} onChange={(v) => set("email", v)} />
              <FormField label="Phone / WhatsApp" name="phone" placeholder="+34 612 345 678" formatHint="Include country code" value={form.phone} onChange={(v) => set("phone", v)} />
              <FormField label="LinkedIn profile" name="linkedin_url" placeholder="linkedin.com/in/username" formatHint="Format: linkedin.com/in/username" whyItMatters="We use this to understand their professional background and infer decision-making style" value={form.linkedin_url} onChange={(v) => set("linkedin_url", v)} />
              <FormField label="Instagram or other social" name="instagram_url" placeholder="@username or full URL" formatHint="Helps us understand lifestyle and values" value={form.instagram_url} onChange={(v) => set("instagram_url", v)} />
            </div>
          </FormSection>

          {/* SECTION 2: Who they are */}
          <FormSection title="Their background" subtitle="helps us build a realistic persona" whyItMatters="Demographics and lifestyle significantly affect how people respond to business changes">
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="Age or age range" name="age_range" placeholder='e.g. "34" or "30-40"' whyItMatters="Age affects how people respond to changes -- younger customers adapt faster to new services, older ones value consistency more" value={form.age_range} onChange={(v) => set("age_range", v)} />
              <FormField label="Gender" name="gender" type="chips" multi={false} options={[
                { value: "man", label: "Man" }, { value: "woman", label: "Woman" },
                { value: "non-binary", label: "Non-binary" }, { value: "prefer-not", label: "Prefer not to say" },
              ]} value={form.gender} onChange={(v) => set("gender", v)} />
              <FormField label="Location" name="location_customer" placeholder="City, Country" formatHint="Where does this customer live or work?" value={form.location_customer} onChange={(v) => set("location_customer", v)} />
              <FormField label="Occupation / industry" name="occupation" placeholder='e.g. "nurse", "teacher", "self-employed"' whyItMatters="Occupation strongly predicts income level, schedule, and spending priorities" value={form.occupation} onChange={(v) => set("occupation", v)} />
            </div>
            <FormField label="Income level (estimate)" name="income_level" type="chips" multi={false} options={[
              { value: "budget", label: "Budget conscious" }, { value: "middle", label: "Middle income" },
              { value: "comfortable", label: "Comfortable" }, { value: "high", label: "High income" },
              { value: "unsure", label: "Not sure" },
            ]} whyItMatters="Affects how they respond to price changes, new services, added fees, and any decision that involves perceived value or cost" value={form.income_level} onChange={(v) => set("income_level", v)} />
            <FormField label="Lifestyle description" name="lifestyle_description" type="textarea" rows={2} placeholder='e.g. "Young professional, works long hours, values convenience, eats out 3-4x per week"' value={form.lifestyle_description} onChange={(v) => set("lifestyle_description", v)} />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="Languages they speak" name="languages" placeholder="e.g. Spanish, English" value={form.languages} onChange={(v) => set("languages", v)} />
              <FormField label="Household size" name="household_size" type="number" placeholder="e.g. 2" whyItMatters="Household size affects priorities -- a family of 4 reacts differently to schedule changes, menu options, and costs than a solo professional" value={form.household_size} onChange={(v) => set("household_size", v)} />
            </div>
          </FormSection>

          {/* SECTION 3: Relationship with your business */}
          <FormSection title="Their relationship with your business" subtitle="the most important section -- shapes how they'd react to any change you make" whyItMatters="These fields have the highest impact on simulation accuracy for any question you ask">
            <FormField label="How long have they been a customer?" name="tenure" type="select" options={[
              { value: "<3m", label: "Less than 3 months" }, { value: "3-12m", label: "3-12 months" },
              { value: "1-3y", label: "1-3 years" }, { value: "3-10y", label: "3-10 years" },
              { value: "10y+", label: "More than 10 years" },
            ]} whyItMatters="Loyalty duration is the strongest predictor of whether someone accepts change or churns" value={form.tenure} onChange={(v) => set("tenure", v)} />
            <FormField label="How often do they visit or buy?" name="visit_frequency" type="select" whyItMatters="Frequent visitors notice every change -- hours, decor, staff, menu. Occasional visitors are less sensitive to most changes but more sensitive to price." options={[
              { value: "daily", label: "Daily" }, { value: "several_weekly", label: "Several times a week" },
              { value: "weekly", label: "Weekly" }, { value: "fortnightly", label: "Fortnightly" },
              { value: "monthly", label: "Monthly" }, { value: "few_yearly", label: "A few times a year" },
              { value: "yearly", label: "Once a year or less" },
            ]} value={form.visit_frequency} onChange={(v) => set("visit_frequency", v)} />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="Typical spend per visit" name="spend_per_visit" type="number" placeholder="e.g. 25" formatHint="In your local currency" whyItMatters="Anchors the simulation to realistic spending behaviour for this person" value={form.spend_per_visit} onChange={(v) => set("spend_per_visit", v)} />
              <FormField label="Estimated annual spend" name="estimated_annual_spend" type="number" placeholder="e.g. 1200" formatHint="Leave blank if unknown -- we can estimate" value={form.estimated_annual_spend} onChange={(v) => set("estimated_annual_spend", v)} />
            </div>
            <FormField label="What do they mainly buy from you?" name="main_purchases" type="textarea" rows={2} placeholder='e.g. "weekly coffee, occasional pastries, Friday lunch with colleagues"' whyItMatters="Critical for predicting reactions to menu changes, product removals, or service adjustments -- not just pricing decisions" value={form.main_purchases} onChange={(v) => set("main_purchases", v)} />
            <FormField label="Why do they come to you?" name="why_they_come" type="chips" whyItMatters="If someone comes for the atmosphere, they'll react differently to a renovation vs a price change. If they come for a specific dish, a menu change affects them more than anything else. This shapes every simulation." options={[
              { value: "habit", label: "Habit / routine" }, { value: "specific_product", label: "Specific product they love" },
              { value: "closest", label: "Closest option" }, { value: "best_quality", label: "Best quality" },
              { value: "best_value", label: "Best value" }, { value: "social", label: "Social / atmosphere" },
              { value: "staff", label: "Staff / personal service" }, { value: "recommended", label: "Recommended by someone" },
            ]} value={form.why_they_come} onChange={(v) => set("why_they_come", v)} />
            <FormField label="How loyal are they?" name="loyalty_level" type="chips" multi={false} whyItMatters="Loyal customers absorb change better. Transactional customers react more strongly to any disruption -- not just price changes." options={[
              { value: "very_loyal", label: "Very loyal -- would follow us anywhere" },
              { value: "loyal_limits", label: "Loyal but has limits" },
              { value: "occasional", label: "Occasional -- shops around" },
              { value: "transactional", label: "Transactional -- goes wherever is best value" },
            ]} value={form.loyalty_level} onChange={(v) => set("loyalty_level", v)} />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="Have they ever complained?" name="has_complained" type="chips" multi={false} options={[
                { value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" },
              ]} whyItMatters="Complaint history predicts how they'd respond to negative changes" value={form.has_complained} onChange={(v) => set("has_complained", v)} />
              <FormField label="Do they refer others?" name="refers_customers" type="chips" multi={false} options={[
                { value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" },
              ]} whyItMatters="Referrers are typically more embedded and less likely to churn" value={form.refers_customers} onChange={(v) => set("refers_customers", v)} />
            </div>
            <FormField label="Customer segment" name="customer_segment" type="select" options={[
              { value: "vip", label: "VIP -- top 10% by value" }, { value: "regular", label: "Regular -- consistent visitor" },
              { value: "occasional", label: "Occasional -- infrequent" }, { value: "new", label: "New -- joined recently" },
              { value: "lapsed", label: "Lapsed -- used to come more" }, { value: "at_risk", label: "At risk -- signs of disengagement" },
            ]} value={form.customer_segment} onChange={(v) => set("customer_segment", v)} />
            <FormField label="How do they typically contact you?" name="contact_channels" type="chips" options={[
              { value: "in_person", label: "In person" }, { value: "phone", label: "Phone" },
              { value: "whatsapp", label: "WhatsApp" }, { value: "email", label: "Email" },
              { value: "social", label: "Instagram / social" }, { value: "website", label: "Through your website" },
            ]} value={form.contact_channels} onChange={(v) => set("contact_channels", v)} />
          </FormSection>

          {/* SECTION 4: Personality */}
          <FormSection title="How they think and behave" subtitle="helps us give them a realistic voice" whyItMatters="Personality affects how someone responds to any change -- a renovation, new staff, changed hours, a menu update, or a price adjustment. Some people hate any disruption to routine. Others welcome variety.">
            <FormField label="How would you describe their personality?" name="personality_traits" type="chips" options={[
              { value: "friendly", label: "Friendly and chatty" }, { value: "quiet", label: "Quiet and reserved" },
              { value: "direct", label: "Direct and businesslike" }, { value: "price_focused", label: "Price-focused" },
              { value: "quality_focused", label: "Quality-focused" }, { value: "experience_focused", label: "Experience-focused" },
              { value: "spontaneous", label: "Spontaneous" }, { value: "creature_habit", label: "Creature of habit" },
              { value: "detail_oriented", label: "Detail-oriented" }, { value: "goes_with_flow", label: "Goes with the flow" },
            ]} value={form.personality_traits} onChange={(v) => set("personality_traits", v)} />
            <FormField label="How do they make decisions?" name="decision_style" type="chips" multi={false} whyItMatters="Helps predict how quickly they'd adapt to changes you make -- or whether they need time and reassurance before accepting something new" options={[
              { value: "instinct", label: "Quickly -- acts on instinct" }, { value: "takes_time", label: "Takes their time" },
              { value: "compares", label: "Compares all options" }, { value: "recommendations", label: "Follows recommendations" },
              { value: "mood", label: "Depends on their mood" },
            ]} value={form.decision_style} onChange={(v) => set("decision_style", v)} />
            <FormField label="How sensitive are they to changes in cost or value?" name="price_sensitivity" type="slider"
              options={{ left: "Very sensitive to cost", right: "Cost rarely matters" }}
              whyItMatters="Useful for price questions but also for predicting reactions to added fees, removed discounts, new charges, or premium service tiers"
              value={form.price_sensitivity} onChange={(v) => set("price_sensitivity", v)} />
            <FormField label="What would most likely cause them to go elsewhere or stop coming?" name="what_would_make_leave" type="textarea" rows={2}
              placeholder='e.g. "A bad experience with a new staff member" or "If we changed the specific dish they always order" or "Probably nothing -- they have been coming for years"' value={form.what_would_make_leave} onChange={(v) => set("what_would_make_leave", v)} />
            <FormField label="What would deepen their relationship with you?" name="what_would_make_loyal" type="textarea" rows={2}
              placeholder='e.g. "Being recognised by name when they come in" or "A loyalty card" or "Sunday opening so they can come with family"' value={form.what_would_make_loyal} onChange={(v) => set("what_would_make_loyal", v)} />
            <FormField label="Any life context that affects how they spend?" name="life_context" type="textarea" rows={2}
              placeholder='e.g. "Recently had a baby so less disposable income"' value={form.life_context} onChange={(v) => set("life_context", v)} />
          </FormSection>

          {/* SECTION 5: Contact & Professional */}
          <FormSection title="Contact and professional details">
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="Company name" name="company" placeholder="e.g. Acme Corp" value={form.company} onChange={(v) => set("company", v)} />
              <FormField label="Job title" name="job_title" placeholder="e.g. Purchasing Manager" value={form.job_title} onChange={(v) => set("job_title", v)} />
              <FormField label="City" name="city" placeholder="e.g. Barcelona" value={form.city} onChange={(v) => set("city", v)} />
              <FormField label="Country" name="country" placeholder="e.g. Spain" value={form.country} onChange={(v) => set("country", v)} />
            </div>
            <FormField label="Tags" name="tags" placeholder='e.g. "VIP, foodie, referrer, summer regular"' formatHint="Comma separated" value={form.tags} onChange={(v) => set("tags", v)} />
          </FormSection>

          {/* SECTION 6: Notes & History */}
          <FormSection title="Your knowledge about this person">
            <FormField label="Relationship notes" name="relationship_notes" type="textarea" rows={3}
              placeholder='e.g. "Comes every Friday with her husband. Knows all the staff by name. Very loyal but budget conscious."' value={form.relationship_notes} onChange={(v) => set("relationship_notes", v)} />
            <FormField label="Memorable interactions" name="memorable_interactions" type="textarea" rows={2}
              placeholder='e.g. "Complained about the new menu in January but came back."' value={form.memorable_interactions} onChange={(v) => set("memorable_interactions", v)} />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField label="Last interaction" name="last_interaction_date" type="date" value={form.last_interaction_date} onChange={(v) => set("last_interaction_date", v)} />
              <FormField label="How did you first meet them?" name="how_met" type="select" options={[
                { value: "walk_in", label: "Walk-in" }, { value: "referral", label: "Referral" },
                { value: "online", label: "Online" }, { value: "event", label: "Event" }, { value: "other", label: "Other" },
              ]} value={form.how_met} onChange={(v) => set("how_met", v)} />
            </div>
          </FormSection>

          {/* SECTION 7: File Upload */}
          <FormSection title="Upload files to activate their digital twin" whyItMatters="Upload real conversations and we'll build a digital twin of this customer">
            {savedId ? (
              <FileUploadZone contactId={savedId} contactType="customer" contactName={(form.first_name as string) || "this customer"} />
            ) : (
              <div className="rounded-lg border border-[#E5E2DC] bg-gray-50 p-6 text-center">
                <p className="text-sm text-gray-400">Save the customer first, then you can upload files here.</p>
              </div>
            )}
          </FormSection>
        </div>

        {/* Bottom save */}
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
