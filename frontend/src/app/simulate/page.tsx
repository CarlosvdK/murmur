"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { createSimulation, getSimulation } from "@/lib/api";
import SimulationPanel from "@/components/simulation/SimulationPanel";
import { Suspense } from "react";
import { Send, GitCompare, ArrowLeft } from "lucide-react";

function SimulateContent() {
  const searchParams = useSearchParams();
  const businessId = searchParams.get("businessId");
  const existingSimId = searchParams.get("simulationId");

  const [question, setQuestion] = useState("");
  const [isAB, setIsAB] = useState(false);
  const [variantA, setVariantA] = useState("");
  const [variantB, setVariantB] = useState("");
  const [simulationId, setSimulationId] = useState<string | null>(existingSimId);
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [submittedA, setSubmittedA] = useState<string | null>(null);
  const [submittedB, setSubmittedB] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If navigating from dashboard with an existing simulationId, fetch its details
  useEffect(() => {
    if (existingSimId) {
      getSimulation(existingSimId)
        .then((sim) => {
          setSubmittedQuestion(sim.question);
          setSubmittedA(sim.variant_a);
          setSubmittedB(sim.variant_b);
          setSimulationId(sim.id);
        })
        .catch(() => {
          setError("Could not load simulation. It may have been deleted.");
          setSimulationId(null);
        });
    }
  }, [existingSimId]);

  if (!businessId && !existingSimId) {
    return (
      <div className="py-16 text-center">
        <p className="text-gray-500">
          No business selected.{" "}
          <a href="/onboarding" className="text-legacy-navy underline">
            Create one first.
          </a>
        </p>
      </div>
    );
  }

  const handleSubmit = async () => {
    if (!question.trim() || !businessId) return;
    setLoading(true);
    setError(null);
    try {
      const sim = await createSimulation({
        business_id: businessId,
        question: question.trim(),
        variant_a: isAB && variantA.trim() ? variantA.trim() : undefined,
        variant_b: isAB && variantB.trim() ? variantB.trim() : undefined,
      });
      setSimulationId(sim.id);
      setSubmittedQuestion(question.trim());
      setSubmittedA(isAB ? variantA.trim() : null);
      setSubmittedB(isAB ? variantB.trim() : null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start simulation");
    } finally {
      setLoading(false);
    }
  };

  // If simulation exists (new or from dashboard), show the panel
  if (simulationId) {
    return (
      <div className="py-4">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-500">Question asked:</p>
            <h2 className="text-lg font-semibold text-gray-900">
              &ldquo;{submittedQuestion}&rdquo;
            </h2>
          </div>
          <a
            href="/dashboard"
            className="flex items-center gap-1 rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-gray-500 transition-colors hover:bg-gray-50"
          >
            <ArrowLeft className="h-3 w-3" /> Dashboard
          </a>
        </div>
        <SimulationPanel
          simulationId={simulationId}
          variantA={submittedA}
          variantB={submittedB}
        />
      </div>
    );
  }

  // Question input form
  return (
    <div className="mx-auto max-w-2xl py-8">
      <h1 className="mb-2 text-2xl font-bold text-gray-900">
        Ask Your Customers
      </h1>
      <p className="mb-8 text-sm text-gray-500">
        Type any question about a business decision. We&apos;ll simulate how your
        customers would react.
      </p>

      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Your Question
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What would happen if I raised drink prices by 15%?"
            rows={3}
            className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-legacy-navy focus:outline-none focus:ring-1 focus:ring-legacy-navy"
          />
        </div>

        {/* A/B toggle */}
        <button
          onClick={() => setIsAB(!isAB)}
          className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-sm transition-colors ${
            isAB
              ? "border-legacy-purple bg-legacy-purple/5 text-legacy-purple"
              : "border-gray-200 text-gray-500 hover:bg-gray-50"
          }`}
        >
          <GitCompare className="h-4 w-4" />
          {isAB ? "Comparing two options" : "Compare two options (A/B)"}
        </button>

        {isAB && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Option A
              </label>
              <input
                type="text"
                value={variantA}
                onChange={(e) => setVariantA(e.target.value)}
                placeholder="e.g., Raise prices 15%"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-legacy-navy focus:outline-none focus:ring-1 focus:ring-legacy-navy"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Option B
              </label>
              <input
                type="text"
                value={variantB}
                onChange={(e) => setVariantB(e.target.value)}
                placeholder="e.g., Keep prices the same"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-legacy-navy focus:outline-none focus:ring-1 focus:ring-legacy-navy"
              />
            </div>
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading || !question.trim()}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-legacy-navy py-3 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-40"
        >
          {loading ? "Starting..." : "Run Simulation"}
          <Send className="h-4 w-4" />
        </button>

        {error && (
          <div className="rounded-lg bg-legacy-red/10 p-3 text-center text-sm text-legacy-red">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default function SimulatePage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <Suspense fallback={<div className="py-16 text-center text-gray-400">Loading...</div>}>
        <SimulateContent />
      </Suspense>
    </div>
  );
}
