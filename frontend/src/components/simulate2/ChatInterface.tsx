"use client";

import { useState, useRef, useEffect } from "react";
import {
  createSimulation,
  getSimulationProgress,
  getSimulationResult,
  getSimulationResponses,
  getSimulationCaveats,
  SimulationResult,
  PersonaResponseData,
  CaveatData,
} from "@/lib/api";
import ResultsReport from "@/components/results/ResultsReport";

const EXAMPLES = [
  "What if I raised prices by 15%?",
  "Should I change my operating hours?",
  "Would my customers use a rewards program?",
  "What if I added a new product or service?",
  "How would customers react to a rebrand?",
];

interface ClarifyingQuestion {
  question: string;
  hint: string;
}

interface SimEntry {
  id: string;
  question: string;
  status: "clarifying" | "running" | "done" | "failed";
  progress?: string;
  result?: SimulationResult;
  responses?: PersonaResponseData[];
  caveats?: CaveatData[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  impact?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  demographics?: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ragSelection?: any;
  clarifyingQuestions?: ClarifyingQuestion[];
  clarifyingAnswers?: string[];
  originalQuestion?: string;
}

interface Props {
  businessId: string | null;
  personaCount?: number;
  onSimulationComplete?: (sim: { id: string; question: string; verdict: string }) => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api";

async function fetchClarifyingQuestions(businessId: string, question: string): Promise<ClarifyingQuestion[]> {
  try {
    const { createClient } = await import("@/lib/supabase/client");
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (session?.access_token) {
      headers["Authorization"] = `Bearer ${session.access_token}`;
    }

    const resp = await fetch(`${API_BASE}/simulations/clarifying-questions`, {
      method: "POST",
      headers,
      body: JSON.stringify({ business_id: businessId, question }),
    });
    if (!resp.ok) throw new Error("Failed");
    const data = await resp.json();
    return data.questions || [];
  } catch {
    // Fallback if API fails
    return [
      { question: "Can you describe the specific change you are considering?", hint: "The more detail, the better the simulation" },
      { question: "What triggered this idea?", hint: "Understanding the motivation helps frame the simulation" },
      { question: "Do you have any relevant data?", hint: "Even rough numbers improve accuracy" },
    ];
  }
}

export default function ChatInterface({ businessId, personaCount = 12, onSimulationComplete }: Props) {
  const [input, setInput] = useState("");
  const [thread, setThread] = useState<SimEntry[]>([]);
  const [running, setRunning] = useState(false);
  const [clarifyingIdx, setClarifyingIdx] = useState(0);
  const [clarifyingInput, setClarifyingInput] = useState("");
  const [activeClarifyId, setActiveClarifyId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [thread, clarifyingIdx]);

  const handleSubmit = async () => {
    if (!input.trim() || running) return;
    const question = input.trim();
    setInput("");

    const entryId = Date.now().toString();
    // Show the question immediately with a loading state
    const entry: SimEntry = {
      id: entryId,
      question,
      originalQuestion: question,
      status: "clarifying",
      clarifyingQuestions: [],
      clarifyingAnswers: [],
    };
    setThread((prev) => [...prev, entry]);

    // Fetch AI-generated clarifying questions from the backend
    const clarifyingQuestions = await fetchClarifyingQuestions(businessId!, question);
    setThread((prev) =>
      prev.map((e) => e.id === entryId ? { ...e, clarifyingQuestions } : e)
    );
    setActiveClarifyId(entryId);
    setClarifyingIdx(0);
    setClarifyingInput("");
  };

  const handleClarifyAnswer = () => {
    if (!activeClarifyId) return;
    const answer = clarifyingInput.trim();
    setClarifyingInput("");

    setThread((prev) =>
      prev.map((e) => {
        if (e.id !== activeClarifyId) return e;
        const answers = [...(e.clarifyingAnswers || []), answer];
        return { ...e, clarifyingAnswers: answers };
      })
    );

    const entry = thread.find((e) => e.id === activeClarifyId);
    if (!entry?.clarifyingQuestions) return;
    const nextIdx = clarifyingIdx + 1;

    if (nextIdx >= entry.clarifyingQuestions.length) {
      // All questions answered -- run the simulation
      setClarifyingIdx(0);
      setActiveClarifyId(null);

      const updatedEntry = {
        ...entry,
        clarifyingAnswers: [...(entry.clarifyingAnswers || []), answer],
      };
      runSimulation(updatedEntry);
    } else {
      setClarifyingIdx(nextIdx);
    }
  };

  const handleSkipClarifying = () => {
    if (!activeClarifyId) return;
    const entry = thread.find((e) => e.id === activeClarifyId);
    if (!entry) return;

    setActiveClarifyId(null);
    setClarifyingIdx(0);
    runSimulation(entry);
  };

  const runSimulation = async (entry: SimEntry) => {
    setRunning(true);

    // Build enriched question from clarifying answers
    let enrichedQuestion = entry.originalQuestion || entry.question;
    if (entry.clarifyingAnswers && entry.clarifyingAnswers.length > 0 && entry.clarifyingQuestions) {
      const context = entry.clarifyingQuestions
        .map((q, i) => {
          const a = entry.clarifyingAnswers?.[i];
          return a ? `${q.question} ${a}` : null;
        })
        .filter(Boolean)
        .join("\n");
      if (context) {
        enrichedQuestion = `${entry.originalQuestion}\n\nAdditional context:\n${context}`;
      }
    }

    setThread((prev) =>
      prev.map((e) =>
        e.id === entry.id ? { ...e, status: "running", progress: "Starting simulation..." } : e
      )
    );

    try {
      const sim = await createSimulation({
        business_id: businessId!,
        question: enrichedQuestion,
        persona_count: personaCount,
      });

      setThread((prev) =>
        prev.map((e) => (e.id === entry.id ? { ...e, id: sim.id } : e))
      );

      // Poll for progress
      const simId = sim.id;
      while (true) {
        await new Promise((r) => setTimeout(r, 3000));
        try {
          const prog = await getSimulationProgress(simId);
          setThread((prev) =>
            prev.map((e) =>
              e.id === simId ? { ...e, progress: prog.step } : e
            )
          );

          if (prog.status === "completed") {
            const [result, responses, caveats, impact, demographics] = await Promise.all([
              getSimulationResult(simId),
              getSimulationResponses(simId).catch(() => []),
              getSimulationCaveats(simId).catch(() => []),
              fetch(`${API_BASE}/simulations/${simId}/impact`).then(r => r.ok ? r.json() : null).catch(() => null),
              fetch(`${API_BASE}/simulations/${simId}/demographics`).then(r => r.ok ? r.json() : null).catch(() => null),
            ]);

            setThread((prev) =>
              prev.map((e) =>
                e.id === simId
                  ? { ...e, status: "done", result, responses, caveats, impact, demographics }
                  : e
              )
            );

            if (onSimulationComplete) {
              onSimulationComplete({
                id: simId,
                question: entry.originalQuestion || entry.question,
                verdict: impact?.decision || "caution",
              });
            }
            break;
          }

          if (prog.status === "failed") {
            setThread((prev) =>
              prev.map((e) =>
                e.id === simId ? { ...e, status: "failed", progress: prog.step } : e
              )
            );
            break;
          }
        } catch {
          break;
        }
      }
    } catch {
      setThread((prev) =>
        prev.map((e) =>
          e.id === entry.id ? { ...e, status: "failed", progress: "Failed to start simulation" } : e
        )
      );
    } finally {
      setRunning(false);
    }
  };

  const isEmpty = thread.length === 0;
  const isInClarifying = activeClarifyId !== null;

  return (
    <div className="flex h-full flex-1 flex-col">
      {/* Scrollable thread */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-6">
        {isEmpty ? (
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
          <div className="mx-auto max-w-3xl space-y-6">
            {thread.map((entry) => (
              <div key={entry.id}>
                {/* User question */}
                <div className="mb-4 flex justify-end">
                  <div className="max-w-[70%] rounded-2xl rounded-br-md bg-black px-5 py-3 text-sm text-white">
                    {entry.originalQuestion || entry.question}
                  </div>
                </div>

                {/* Clarifying questions */}
                {entry.status === "clarifying" && entry.clarifyingQuestions && (
                  <div className="space-y-3">
                    {entry.clarifyingQuestions.map((cq, i) => {
                      const answered = (entry.clarifyingAnswers?.length || 0) > i;
                      const isCurrent = entry.id === activeClarifyId && i === clarifyingIdx;
                      if (!answered && !isCurrent) return null;

                      return (
                        <div key={i}>
                          {/* Bot question */}
                          <div className="mb-2 flex items-start gap-3">
                            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-orange text-[10px] font-bold text-white">M</div>
                            <div className="rounded-2xl rounded-bl-md border border-[#E5E2DC] bg-white px-4 py-3 text-sm text-gray-700">
                              <p>{cq.question}</p>
                              {isCurrent && <p className="mt-1 text-xs text-gray-400">{cq.hint}</p>}
                            </div>
                          </div>
                          {/* User answer */}
                          {answered && entry.clarifyingAnswers?.[i] && (
                            <div className="mb-2 flex justify-end">
                              <div className="max-w-[70%] rounded-2xl rounded-br-md bg-gray-100 px-4 py-2.5 text-sm text-black">
                                {entry.clarifyingAnswers[i]}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Running state */}
                {entry.status === "running" && (
                  <div className="rounded-2xl border border-[#E5E2DC] bg-white p-5">
                    <div className="flex items-center gap-3">
                      <div className="h-2 w-2 animate-pulse rounded-full bg-brand-orange" />
                      <p className="text-sm text-gray-500">{entry.progress}</p>
                    </div>
                  </div>
                )}

                {/* Failed state */}
                {entry.status === "failed" && (
                  <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
                    <p className="text-sm text-red-600">{entry.progress || "Simulation failed"}</p>
                  </div>
                )}

                {/* Results */}
                {entry.status === "done" && entry.result && (
                  <div className="max-w-3xl">
                    <ResultsReport
                      result={entry.result}
                      impactData={entry.impact}
                      responses={entry.responses}
                      demographicGroups={entry.demographics}
                      ragSelection={entry.ragSelection}
                    />
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
          {isInClarifying ? (
            <>
              <input
                value={clarifyingInput}
                onChange={(e) => setClarifyingInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleClarifyAnswer()}
                placeholder="Type your answer..."
                autoFocus
                className="flex-1 rounded-xl border border-[#E5E2DC] bg-[#F5F3EF] px-4 py-3 text-sm text-black placeholder:text-gray-400 focus:border-brand-blue focus:outline-none"
              />
              <button
                onClick={handleClarifyAnswer}
                disabled={!clarifyingInput.trim()}
                className="rounded-xl bg-black px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-80 disabled:opacity-30"
              >
                Answer
              </button>
              <button
                onClick={handleSkipClarifying}
                className="rounded-xl border border-[#E5E2DC] px-4 py-3 text-sm text-gray-500 hover:bg-gray-50"
              >
                Skip all
              </button>
            </>
          ) : (
            <>
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
