"use client";

import { useState } from "react";
import { submitRealOutcome } from "@/lib/api";

interface OutcomeFormProps {
  simulationId: string;
  existingOutcome?: { id: string } | null;
  onSubmitted?: () => void;
}

type UiState = "idle" | "editing" | "submitting" | "logged" | "error";

export default function OutcomeForm({
  simulationId,
  existingOutcome,
  onSubmitted,
}: OutcomeFormProps) {
  const [state, setState] = useState<UiState>(
    existingOutcome ? "logged" : "idle"
  );
  const [happened, setHappened] = useState("");
  const [matched, setMatched] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (state === "logged") {
    return (
      <div className="inline-flex items-center gap-2 rounded-full bg-green-50 px-3 py-1.5 text-xs font-medium text-green-700">
        <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
        Outcome logged
      </div>
    );
  }

  if (state === "idle") {
    return (
      <button
        type="button"
        onClick={() => setState("editing")}
        className="rounded-lg border border-[#E5E2DC] bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
      >
        What happened?
      </button>
    );
  }

  const canSubmit = happened.trim().length > 0 && state !== "submitting";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    setState("submitting");
    setError(null);
    try {
      const payload: {
        what_actually_happened: string;
        outcome_matched?: boolean;
      } = { what_actually_happened: happened.trim() };
      if (matched !== null) payload.outcome_matched = matched;
      await submitRealOutcome(simulationId, payload);
      setState("logged");
      onSubmitted?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setState("error");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-[#E5E2DC] bg-white p-4">
      <label className="mb-2 block text-sm font-medium text-black" htmlFor="what-happened">
        What actually happened?
      </label>
      <textarea
        id="what-happened"
        value={happened}
        onChange={(e) => setHappened(e.target.value)}
        placeholder="e.g. Raised prices 10%, revenue up 6%, three regulars complained"
        className="mb-3 w-full rounded-lg border border-[#E5E2DC] bg-white p-2 text-sm focus:border-brand-orange focus:outline-none"
        rows={3}
      />

      <fieldset className="mb-3">
        <legend className="mb-1 text-xs font-medium text-gray-500">Did it match the prediction?</legend>
        <div className="flex gap-3 text-sm">
          <label className="flex items-center gap-1.5">
            <input
              type="radio"
              name="matched"
              checked={matched === true}
              onChange={() => setMatched(true)}
              aria-label="matched prediction"
            />
            Yes
          </label>
          <label className="flex items-center gap-1.5">
            <input
              type="radio"
              name="matched"
              checked={matched === false}
              onChange={() => setMatched(false)}
              aria-label="did not match prediction"
            />
            No
          </label>
          <label className="flex items-center gap-1.5 text-gray-500">
            <input
              type="radio"
              name="matched"
              checked={matched === null}
              onChange={() => setMatched(null)}
            />
            Not sure
          </label>
        </div>
      </fieldset>

      {error && (
        <p role="alert" className="mb-2 text-xs text-red-600">
          Couldn't save outcome: {error}
        </p>
      )}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={!canSubmit}
          className="rounded-lg bg-brand-orange px-4 py-1.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {state === "submitting" ? "Saving..." : "Submit"}
        </button>
        <button
          type="button"
          onClick={() => setState("idle")}
          className="rounded-lg border border-[#E5E2DC] px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
