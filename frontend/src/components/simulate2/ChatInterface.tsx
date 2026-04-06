"use client";

import { useState, useRef, useEffect } from "react";
import {
  createSimulation,
  getSimulationProgress,
  getSimulationResult,
  getSimulationResponses,
  SimulationResult,
  PersonaResponseData,
} from "@/lib/api";

const EXAMPLES = [
  "What if I raised prices by 15%?",
  "Should I open on Sundays?",
  "Would my customers use a loyalty card?",
  "What if I changed my opening hours?",
  "Would a new menu item sell well?",
];

interface SimEntry {
  id: string;
  question: string;
  status: "running" | "done" | "failed";
  progress?: string;
  result?: SimulationResult;
  responses?: PersonaResponseData[];
}

interface Props {
  businessId: string | null;
  onSimulationComplete?: (sim: { id: string; question: string; verdict: string }) => void;
}

const VERDICT_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  proceed: { bg: "bg-green-50", text: "text-green-700", label: "Looks good to proceed" },
  caution: { bg: "bg-amber-50", text: "text-amber-700", label: "Proceed with caution" },
  avoid: { bg: "bg-red-50", text: "text-red-700", label: "Evidence suggests avoid" },
  test_first: { bg: "bg-blue-50", text: "text-blue-700", label: "Test with a small group first" },
};

export default function ChatInterface({ businessId, onSimulationComplete }: Props) {
  const [input, setInput] = useState("");
  const [thread, setThread] = useState<SimEntry[]>([]);
  const [running, setRunning] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [thread]);

  const handleSubmit = async () => {
    if (!input.trim() || running) return;
    const question = input.trim();
    setInput("");
    setRunning(true);

    const entryId = Date.now().toString();
    const entry: SimEntry = { id: entryId, question, status: "running", progress: "Starting simulation..." };
    setThread((prev) => [...prev, entry]);

    try {
      // Use a default business if none selected
      let bId = businessId;
      if (!bId) {
        // Create a quick business from the workspace context
        const resp = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api"}/businesses/`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              name: "My Business",
              type: "restaurant",
              description: "A local business",
              location: "Unknown",
            }),
          }
        );
        const biz = await resp.json();
        bId = biz.id;
      }

      const sim = await createSimulation({
        business_id: bId!,
        question,
        persona_count: 12,
      });

      // Update entry with real sim ID
      setThread((prev) =>
        prev.map((e) => (e.id === entryId ? { ...e, id: sim.id } : e))
      );

      // Poll for progress
      const poll = async () => {
        while (true) {
          await new Promise((r) => setTimeout(r, 3000));
          try {
            const prog = await getSimulationProgress(sim.id);
            setThread((prev) =>
              prev.map((e) =>
                e.id === sim.id ? { ...e, progress: prog.step } : e
              )
            );

            if (prog.status === "completed") {
              const result = await getSimulationResult(sim.id);
              let responses: PersonaResponseData[] = [];
              try {
                responses = await getSimulationResponses(sim.id);
              } catch {}

              setThread((prev) =>
                prev.map((e) =>
                  e.id === sim.id
                    ? { ...e, status: "done", result, responses }
                    : e
                )
              );

              if (onSimulationComplete) {
                const impact = await fetch(
                  `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api"}/simulations/${sim.id}/impact`
                ).then((r) => r.json()).catch(() => null);

                onSimulationComplete({
                  id: sim.id,
                  question,
                  verdict: impact?.decision || "caution",
                });
              }
              break;
            }

            if (prog.status === "failed") {
              setThread((prev) =>
                prev.map((e) =>
                  e.id === sim.id ? { ...e, status: "failed", progress: prog.step } : e
                )
              );
              break;
            }
          } catch {
            break;
          }
        }
      };

      await poll();
    } catch {
      setThread((prev) =>
        prev.map((e) =>
          e.id === entryId ? { ...e, status: "failed", progress: "Failed to start simulation" } : e
        )
      );
    } finally {
      setRunning(false);
    }
  };

  const isEmpty = thread.length === 0;

  return (
    <div className="flex h-full flex-col">
      {/* Scrollable thread */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-6">
        {isEmpty ? (
          /* Empty state */
          <div className="flex h-full flex-col items-center justify-center">
            <h2 className="mb-2 text-2xl font-bold text-black">
              What do you want to simulate?
            </h2>
            <p className="mb-8 max-w-md text-center text-gray-400">
              Describe a decision you are considering and we will show you how
              your customers or vendors would react.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setInput(ex)}
                  className="rounded-xl border border-[#E5E2DC] bg-white px-4 py-2.5 text-sm text-gray-600 transition-colors hover:border-gray-400 hover:text-black"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Thread */
          <div className="mx-auto max-w-3xl space-y-6">
            {thread.map((entry) => (
              <div key={entry.id}>
                {/* Question */}
                <div className="mb-4 flex justify-end">
                  <div className="rounded-2xl rounded-br-md bg-black px-5 py-3 text-sm text-white">
                    {entry.question}
                  </div>
                </div>

                {/* Response */}
                {entry.status === "running" && (
                  <div className="rounded-2xl border border-[#E5E2DC] bg-white p-5">
                    <div className="flex items-center gap-3">
                      <div className="h-2 w-2 animate-pulse rounded-full bg-brand-orange" />
                      <p className="text-sm text-gray-500">{entry.progress}</p>
                    </div>
                  </div>
                )}

                {entry.status === "failed" && (
                  <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
                    <p className="text-sm text-red-600">{entry.progress || "Simulation failed"}</p>
                  </div>
                )}

                {entry.status === "done" && entry.result && (
                  <div className="space-y-4">
                    {/* Verdict */}
                    <div className="rounded-2xl border border-[#E5E2DC] bg-white p-6">
                      <div className="mb-4">
                        <span className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${
                          VERDICT_CONFIG[entry.result.confidence_score]?.bg || "bg-gray-100"
                        } ${VERDICT_CONFIG[entry.result.confidence_score]?.text || "text-gray-600"}`}>
                          {VERDICT_CONFIG[entry.result.confidence_score]?.label || entry.result.confidence_score}
                        </span>
                      </div>
                      <p className="text-lg font-semibold text-black">{entry.result.summary}</p>
                      {entry.result.recommendation && (
                        <p className="mt-3 text-sm leading-relaxed text-gray-500">
                          {entry.result.recommendation}
                        </p>
                      )}
                    </div>

                    {/* Persona voices */}
                    {entry.responses && entry.responses.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                          Customer voices
                        </h4>
                        {entry.responses.slice(0, 4).map((r, i) => (
                          <div
                            key={i}
                            className={`rounded-xl border bg-white p-4 ${
                              r.sentiment > 0.3
                                ? "border-l-4 border-l-green-400 border-[#E5E2DC]"
                                : r.sentiment < -0.3
                                  ? "border-l-4 border-l-red-400 border-[#E5E2DC]"
                                  : "border-l-4 border-l-amber-400 border-[#E5E2DC]"
                            }`}
                          >
                            <div className="mb-1 flex items-center gap-2">
                              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-blue text-[10px] font-bold text-white">
                                {r.persona_name[0]}
                              </div>
                              <span className="text-sm font-medium text-black">{r.persona_name}</span>
                            </div>
                            <p className="text-sm italic text-gray-600">
                              &ldquo;{r.reaction.slice(0, 200)}&rdquo;
                            </p>
                          </div>
                        ))}
                        {entry.responses.length > 4 && (
                          <p className="text-xs text-gray-400">
                            + {entry.responses.length - 4} more responses
                          </p>
                        )}
                      </div>
                    )}

                    {/* Caveats */}
                    {entry.result.confidence_reasoning && (
                      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
                        <p className="text-xs font-medium text-amber-700">Note</p>
                        <p className="mt-1 text-sm text-amber-600">
                          {entry.result.confidence_reasoning}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input bar */}
      <div className="border-t border-[#E5E2DC] bg-white p-4">
        <div className="mx-auto flex max-w-3xl gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSubmit()}
            placeholder="What would happen if..."
            disabled={running}
            className="flex-1 rounded-xl border border-[#E5E2DC] bg-[#F5F3EF] px-4 py-3 text-sm text-black placeholder:text-gray-400 focus:border-brand-blue focus:outline-none disabled:opacity-50"
          />
          <button
            onClick={handleSubmit}
            disabled={running || !input.trim()}
            className="rounded-xl bg-black px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-80 disabled:opacity-30"
          >
            {running ? "Running..." : "Run"}
          </button>
        </div>
      </div>
    </div>
  );
}
