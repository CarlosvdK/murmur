"use client";

/**
 * ProgressTimeline — MiroFish-inspired step progress with live status.
 *
 * Modeled after MiroFish's Step3Simulation timeline and platform status cards.
 * Shows: step indicators with status badges, current persona being interviewed,
 * elapsed time, and action count.
 */

import { SimulationProgress, SimulationStatus } from "@/lib/api";
import { Clock, Users, MessageSquare, CheckCircle2, Loader2, AlertCircle } from "lucide-react";

interface Props {
  progress: SimulationProgress;
}

const STEPS: { key: SimulationStatus; label: string }[] = [
  { key: "pending", label: "Queued" },
  { key: "gathering_context", label: "Researching Market Context" },
  { key: "generating_personas", label: "Generating Personas" },
  { key: "simulating", label: "Interviewing Customers" },
  { key: "aggregating", label: "Synthesising Feedback" },
  { key: "completed", label: "Complete" },
];

function stepIndex(status: SimulationStatus): number {
  if (status === "failed") return -1;
  return STEPS.findIndex((s) => s.key === status);
}

function StatusBadge({ status }: { status: "done" | "active" | "pending" | "failed" }) {
  if (status === "done")
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-legacy-teal/10 px-2 py-0.5 text-xs font-medium text-legacy-teal">
        <CheckCircle2 className="h-3 w-3" /> Done
      </span>
    );
  if (status === "active")
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-brand-orange/10 px-2 py-0.5 text-xs font-medium text-brand-orange">
        <Loader2 className="h-3 w-3 animate-spin" /> Running
      </span>
    );
  if (status === "failed")
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-legacy-red/10 px-2 py-0.5 text-xs font-medium text-legacy-red">
        <AlertCircle className="h-3 w-3" /> Failed
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-400">
      Pending
    </span>
  );
}

export default function ProgressTimeline({ progress }: Props) {
  const current = stepIndex(progress.status);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      {/* Stats bar — inspired by MiroFish platform status cards */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-gray-50 p-3 text-center">
          <Users className="mx-auto mb-1 h-4 w-4 text-legacy-navy" />
          <p className="font-mono text-lg font-bold text-gray-900">
            {progress.personas_interviewed}/{progress.personas_total}
          </p>
          <p className="text-xs text-gray-500">Interviewed</p>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-center">
          <Clock className="mx-auto mb-1 h-4 w-4 text-legacy-purple" />
          <p className="font-mono text-lg font-bold text-gray-900">
            {progress.elapsed_seconds.toFixed(1)}s
          </p>
          <p className="text-xs text-gray-500">Elapsed</p>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-center">
          <MessageSquare className="mx-auto mb-1 h-4 w-4 text-legacy-teal" />
          <p className="font-mono text-lg font-bold text-gray-900">
            {progress.personas_generated}
          </p>
          <p className="text-xs text-gray-500">Personas</p>
        </div>
      </div>

      {/* Step timeline — MiroFish vertical timeline with dots + connecting lines */}
      <div className="space-y-0">
        {STEPS.map((step, i) => {
          const state =
            progress.status === "failed" && i === current
              ? "failed"
              : i < current
                ? "done"
                : i === current
                  ? "active"
                  : "pending";

          return (
            <div key={step.key} className="flex items-start gap-3">
              {/* Connector line + dot */}
              <div className="flex flex-col items-center">
                <div
                  className={`h-3 w-3 rounded-full border-2 ${
                    state === "done"
                      ? "border-legacy-teal bg-legacy-teal"
                      : state === "active"
                        ? "border-brand-orange bg-brand-orange animate-breathe"
                        : state === "failed"
                          ? "border-legacy-red bg-legacy-red"
                          : "border-gray-300 bg-white"
                  }`}
                />
                {i < STEPS.length - 1 && (
                  <div
                    className={`h-8 w-0.5 ${
                      i < current ? "bg-legacy-teal" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>

              {/* Step content */}
              <div className="flex-1 pb-4">
                <div className="flex items-center justify-between">
                  <span
                    className={`text-sm font-medium ${
                      state === "active"
                        ? "text-gray-900"
                        : state === "done"
                          ? "text-gray-600"
                          : "text-gray-400"
                    }`}
                  >
                    {step.label}
                  </span>
                  <StatusBadge status={state} />
                </div>
                {state === "active" && progress.current_persona && (
                  <p className="mt-1 text-xs text-brand-orange animate-fade-in-up">
                    Talking to {progress.current_persona}...
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
