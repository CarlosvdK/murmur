"use client";

/**
 * BusinessProfileForm — step-by-step business profiler.
 *
 * Inspired by MiroFish's Step1 questionnaire flow: progressive disclosure,
 * one field group at a time, with clear progress indication.
 *
 * This is the critical onboarding component — the quality of the business
 * profile directly determines the quality of the persona swarm.
 */

import { useState } from "react";
import { BusinessCreate } from "@/lib/api";
import { ChevronRight, ChevronLeft, Store, MapPin, Users, FileText } from "lucide-react";

interface Props {
  onSubmit: (data: BusinessCreate) => void;
  loading?: boolean;
}

const STEPS = [
  { icon: Store, label: "Your Business", description: "Tell us about your business" },
  { icon: Users, label: "Your Customers", description: "Describe who your customers are" },
  { icon: MapPin, label: "Location", description: "Where is your business?" },
  { icon: FileText, label: "Review", description: "Check everything looks right" },
];

const BUSINESS_TYPES = [
  "Restaurant",
  "Cafe / Coffee Shop",
  "Bar / Pub",
  "Barbershop / Salon",
  "Grocery Store",
  "Retail Shop",
  "Gym / Fitness",
  "Auto Shop",
  "Bakery",
  "Other",
];

export default function BusinessProfileForm({ onSubmit, loading }: Props) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<BusinessCreate>({
    name: "",
    type: "",
    description: "",
    customer_description: "",
    location: "",
  });

  const update = (field: keyof BusinessCreate, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const canNext =
    step === 0
      ? form.name && form.type && form.description
      : step === 1
        ? true // customer_description is optional
        : step === 2
          ? true // location is optional
          : true;

  return (
    <div className="mx-auto max-w-2xl">
      {/* Step indicator — MiroFish numbered steps with status */}
      <div className="mb-8 flex items-center justify-center gap-2">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <button
              onClick={() => i < step && setStep(i)}
              className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-colors ${
                i < step
                  ? "bg-legacy-teal text-white"
                  : i === step
                    ? "bg-legacy-navy text-white"
                    : "bg-gray-100 text-gray-400"
              }`}
            >
              {i + 1}
            </button>
            {i < STEPS.length - 1 && (
              <div
                className={`h-0.5 w-8 ${
                  i < step ? "bg-legacy-teal" : "bg-gray-200"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step header */}
      <div className="mb-6 text-center">
        <h2 className="text-lg font-semibold text-gray-900">
          {STEPS[step].label}
        </h2>
        <p className="text-sm text-gray-500">{STEPS[step].description}</p>
      </div>

      {/* Step content */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        {step === 0 && (
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Business Name *
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => update("name", e.target.value)}
                placeholder="e.g., Tony's Taco Truck"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-legacy-navy focus:outline-none focus:ring-1 focus:ring-legacy-navy"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Business Type *
              </label>
              <div className="grid grid-cols-2 gap-2">
                {BUSINESS_TYPES.map((type) => (
                  <button
                    key={type}
                    onClick={() => update("type", type.toLowerCase())}
                    className={`rounded-lg border px-3 py-2 text-sm transition-colors ${
                      form.type === type.toLowerCase()
                        ? "border-legacy-navy bg-legacy-navy/5 text-legacy-navy"
                        : "border-gray-200 text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Describe Your Business *
              </label>
              <textarea
                value={form.description}
                onChange={(e) => update("description", e.target.value)}
                placeholder="Tell us what makes your business special. What do you serve/sell? What's the vibe? What do people come for?"
                rows={4}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-legacy-navy focus:outline-none focus:ring-1 focus:ring-legacy-navy"
              />
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Describe Your Customers
              </label>
              <p className="mb-2 text-xs text-gray-400">
                Who comes in? Office workers? Families? Students? What are they
                like? The more detail you give, the more realistic our
                simulation will be.
              </p>
              <textarea
                value={form.customer_description || ""}
                onChange={(e) => update("customer_description", e.target.value)}
                placeholder="e.g., Mix of construction workers grabbing lunch, office people on break, and families on weekends. Regulars know us by name. Price-sensitive crowd — they come for value."
                rows={6}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-legacy-navy focus:outline-none focus:ring-1 focus:ring-legacy-navy"
              />
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Location
              </label>
              <p className="mb-2 text-xs text-gray-400">
                City and neighborhood help us create culturally appropriate
                customer personas.
              </p>
              <input
                type="text"
                value={form.location || ""}
                onChange={(e) => update("location", e.target.value)}
                placeholder="e.g., East Austin, Texas"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-legacy-navy focus:outline-none focus:ring-1 focus:ring-legacy-navy"
              />
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div className="rounded-lg bg-gray-50 p-4">
              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="font-medium text-gray-500">Business</dt>
                  <dd className="text-gray-900">
                    {form.name} ({form.type})
                  </dd>
                </div>
                <div>
                  <dt className="font-medium text-gray-500">Description</dt>
                  <dd className="text-gray-900">{form.description}</dd>
                </div>
                {form.customer_description && (
                  <div>
                    <dt className="font-medium text-gray-500">Customers</dt>
                    <dd className="text-gray-900">
                      {form.customer_description}
                    </dd>
                  </div>
                )}
                {form.location && (
                  <div>
                    <dt className="font-medium text-gray-500">Location</dt>
                    <dd className="text-gray-900">{form.location}</dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
        )}
      </div>

      {/* Navigation buttons */}
      <div className="mt-6 flex justify-between">
        <button
          onClick={() => setStep((s) => s - 1)}
          disabled={step === 0}
          className="flex items-center gap-1 rounded-lg px-4 py-2 text-sm text-gray-500 transition-colors hover:text-gray-700 disabled:invisible"
        >
          <ChevronLeft className="h-4 w-4" /> Back
        </button>

        {step < STEPS.length - 1 ? (
          <button
            onClick={() => setStep((s) => s + 1)}
            disabled={!canNext}
            className="flex items-center gap-1 rounded-lg bg-legacy-navy px-6 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            Next <ChevronRight className="h-4 w-4" />
          </button>
        ) : (
          <button
            onClick={() => onSubmit(form)}
            disabled={loading}
            className="flex items-center gap-1 rounded-lg bg-legacy-teal px-6 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {loading ? "Creating..." : "Create Business Profile"}
          </button>
        )}
      </div>
    </div>
  );
}
