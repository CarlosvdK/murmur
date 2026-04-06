"use client";

/**
 * SimulationPanel -- split panel layout with SSE-based live progress.
 *
 * Left panel: progress timeline + persona grid
 * Right panel: live step messages, then persona responses, then final report
 *
 * Uses SSE as primary progress mechanism, falls back to polling if SSE fails.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import {
  SimulationProgress,
  SimulationResult,
  PersonaProfile,
  PersonaResponseData,
  SSEEvent,
  getSimulationProgress,
  getSimulationPersonas,
  getSimulationResponses,
  getSimulationResult,
  createSimulationStream,
} from "@/lib/api";
import ProgressTimeline from "./ProgressTimeline";
import PersonaCard from "./PersonaCard";
import ResultsReport from "../results/ResultsReport";
import PersonaResponseCard from "../results/PersonaResponseCard";
import CaveatCard from "../results/CaveatCard";
import ImpactPanel from "../results/ImpactPanel";
import { Loader2 } from "lucide-react";

interface Props {
  simulationId: string;
  variantA?: string | null;
  variantB?: string | null;
}

export default function SimulationPanel({
  simulationId,
  variantA,
  variantB,
}: Props) {
  const [progress, setProgress] = useState<SimulationProgress | null>(null);
  const [personas, setPersonas] = useState<PersonaProfile[]>([]);
  const [responses, setResponses] = useState<PersonaResponseData[]>([]);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [sseSteps, setSSESteps] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"progress" | "personas" | "responses" | "impact" | "report">("progress");
  const [done, setDone] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Polling fallback + data fetching
  const fetchData = useCallback(async () => {
    try {
      const prog = await getSimulationProgress(simulationId);
      setProgress(prog);

      if (prog.personas_generated > 0 && personas.length === 0) {
        const p = await getSimulationPersonas(simulationId);
        setPersonas(p);
      }

      if (
        (prog.status === "aggregating" || prog.status === "completed") &&
        responses.length === 0
      ) {
        try {
          const r = await getSimulationResponses(simulationId);
          setResponses(r);
        } catch {
          // Not ready yet
        }
      }

      if (prog.status === "completed" && !result) {
        const res = await getSimulationResult(simulationId);
        setResult(res);
        setActiveTab("impact");
        setDone(true);
      }

      if (prog.status === "failed") {
        setDone(true);
      }
    } catch {
      // Ignore fetch errors during polling
    }
  }, [simulationId, personas.length, responses.length, result]);

  const startPolling = useCallback(() => {
    if (pollRef.current) return;
    pollRef.current = setInterval(fetchData, 2000);
  }, [fetchData]);

  // SSE stream for live progress
  useEffect(() => {
    const es = createSimulationStream(
      simulationId,
      (event: SSEEvent) => {
        setSSESteps((prev) => {
          if (prev.length > 0 && prev[prev.length - 1] === event.step) return prev;
          return [...prev, event.step];
        });
      },
      () => {
        setDone(true);
      },
      () => {
        startPolling();
      },
    );

    return () => es.close();
  }, [simulationId, startPolling]);

  // Always poll for data (personas, responses, result) alongside SSE
  useEffect(() => {
    const interval = setInterval(fetchData, 2500);
    fetchData();
    return () => clearInterval(interval);
  }, [fetchData, done]);

  // Stop polling when done
  useEffect(() => {
    if (done && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, [done]);

  const isRunning = progress && progress.status !== "completed" && progress.status !== "failed";

  return (
    <div className="grid min-h-[600px] grid-cols-1 gap-6 lg:grid-cols-5">
      {/* Left panel -- progress + personas (2/5 width) */}
      <div className="space-y-4 lg:col-span-2">
        {progress && <ProgressTimeline progress={progress} />}

        {/* Live step log from SSE */}
        {sseSteps.length > 0 && (
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-gray-700">
              Activity Log
            </h3>
            <div className="max-h-48 space-y-1 overflow-y-auto">
              {sseSteps.map((step, i) => (
                <p
                  key={i}
                  className={`text-xs ${
                    i === sseSteps.length - 1
                      ? "font-medium text-gray-700"
                      : "text-gray-400"
                  }`}
                >
                  {step}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Persona grid -- compact cards */}
        {personas.length > 0 && (
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-gray-700">
              Generated Personas ({personas.length})
            </h3>
            <div className="space-y-2">
              {personas.map((p, i) => (
                <PersonaCard key={i} persona={p} compact />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Right panel -- responses and report (3/5 width) */}
      <div className="lg:col-span-3">
        {/* Tab bar */}
        <div className="mb-4 flex gap-2">
          {(["progress", "personas", "responses", "impact", "report"] as const).map((tab) => {
            const disabled =
              (tab === "personas" && personas.length === 0) ||
              (tab === "responses" && responses.length === 0) ||
              (tab === "impact" && !result) ||
              (tab === "report" && !result);
            return (
              <button
                key={tab}
                onClick={() => !disabled && setActiveTab(tab)}
                disabled={disabled}
                className={`rounded-lg px-4 py-1.5 text-sm font-medium transition-colors ${
                  activeTab === tab
                    ? "bg-legacy-navy text-white"
                    : disabled
                      ? "text-gray-300"
                      : "text-gray-500 hover:bg-gray-100"
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            );
          })}
        </div>

        {/* Tab content */}
        {activeTab === "progress" && (
          <div className="flex flex-col items-center justify-center rounded-xl border border-gray-200 bg-white p-12 text-center shadow-sm">
            {isRunning ? (
              <>
                <Loader2 className="mb-4 h-8 w-8 animate-spin text-brand-orange" />
                <p className="text-sm font-medium text-gray-700">
                  {progress?.step || "Starting simulation..."}
                </p>
                {progress?.current_persona && (
                  <p className="mt-1 text-xs text-gray-400">
                    Currently interviewing {progress.current_persona}
                  </p>
                )}
              </>
            ) : progress?.status === "completed" ? (
              <p className="text-sm text-gray-500">
                Simulation complete. View the report tab.
              </p>
            ) : progress?.status === "failed" ? (
              <p className="text-sm text-legacy-red">
                Simulation failed. Please try again.
              </p>
            ) : (
              <Loader2 className="h-6 w-6 animate-spin text-gray-300" />
            )}
          </div>
        )}

        {activeTab === "personas" && (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {personas.map((p, i) => (
              <PersonaCard key={i} persona={p} />
            ))}
          </div>
        )}

        {activeTab === "responses" && (
          <div className="space-y-3">
            {responses.map((r, i) => (
              <PersonaResponseCard key={i} response={r} />
            ))}
          </div>
        )}

        {activeTab === "impact" && result && (
          <ImpactPanel simulationId={simulationId} />
        )}

        {activeTab === "report" && result && (
          <div className="space-y-4">
            <ResultsReport
              result={result}
              variantA={variantA}
              variantB={variantB}
            />
            <CaveatCard simulationId={simulationId} />
          </div>
        )}
      </div>
    </div>
  );
}
