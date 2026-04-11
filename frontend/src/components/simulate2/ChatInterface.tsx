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
  clarifyingQuestions?: ClarifyingQuestion[];
  clarifyingAnswers?: string[];
  originalQuestion?: string;
}

interface Props {
  businessId: string | null;
  personaCount?: number;
  onSimulationComplete?: (sim: { id: string; question: string; verdict: string }) => void;
}

const VERDICT_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  proceed: { bg: "bg-green-50", text: "text-green-700", label: "Looks good to proceed" },
  caution: { bg: "bg-amber-50", text: "text-amber-700", label: "Proceed with caution" },
  avoid: { bg: "bg-red-50", text: "text-red-700", label: "Evidence suggests avoid" },
  test_first: { bg: "bg-blue-50", text: "text-blue-700", label: "Test with a small group first" },
};

/**
 * Generate clarifying questions based on the user's question.
 *
 * Research-backed design principles:
 * - Anchoring (Tversky & Kahneman 1974): Ask for concrete numbers/baselines to
 *   prevent the simulation from defaulting to optimistic assumptions.
 * - Base rate neglect (Bar-Hillel 1980): Ask about prior change outcomes to ground
 *   predictions in what actually happened, not what might happen.
 * - Reference class forecasting (Kahneman & Lovallo 1993): Ask about competitors
 *   and industry norms to calibrate against external reference classes.
 * - Stated vs revealed preference gap (NeurIPS 2025 synthetic user findings):
 *   Ask about observed behaviour, not just intentions, to reduce optimistic skew.
 */
function generateClarifyingQuestions(question: string): ClarifyingQuestion[] {
  const q = question.toLowerCase();
  const questions: ClarifyingQuestion[] = [];

  // Always start with the baseline anchor -- grounds the simulation in reality
  if (q.includes("price") || q.includes("cost") || q.includes("charge") || q.includes("fee")) {
    questions.push(
      { question: "What is your current pricing, and what would the new pricing be?", hint: "Concrete numbers help -- e.g. 'Coffee is 3.50 EUR, thinking of 4.00 EUR'" },
      { question: "Have you made a similar change before? What actually happened?", hint: "Real outcomes from past changes are the strongest signal we can use" },
      { question: "What do your nearest competitors charge for similar products?", hint: "e.g. 'The cafe two doors down charges 3.80 EUR for a similar coffee'" },
    );
  } else if (q.includes("open") || q.includes("hour") || q.includes("close") || q.includes("sunday") || q.includes("weekend")) {
    questions.push(
      { question: "What are your current opening hours and what change are you considering?", hint: "e.g. 'Currently Mon-Sat 8-6, thinking about adding Sundays 10-4'" },
      { question: "Have customers actually asked for this, or is it a hunch?", hint: "Observed demand (messages, complaints, queues) is stronger than assumed demand" },
      { question: "What would the additional staffing cost be?", hint: "Even a rough estimate helps us weigh customer benefit vs. cost" },
    );
  } else if (q.includes("menu") || q.includes("product") || q.includes("service") || q.includes("offering") || q.includes("add")) {
    questions.push(
      { question: "Describe the specific product or service you would add.", hint: "The more specific the better -- 'oat milk smoothies' not just 'new drinks'" },
      { question: "What evidence do you have that customers want this?", hint: "Requests, social media mentions, what competitors sell that you don't" },
      { question: "What would you need to stop or reduce to make room for this?", hint: "Trade-offs matter -- every addition has a cost (time, space, focus)" },
    );
  } else if (q.includes("loyalty") || q.includes("card") || q.includes("reward") || q.includes("membership")) {
    questions.push(
      { question: "What specific programme are you considering?", hint: "e.g. 'Buy 10 get 1 free', 'points per euro', 'paid membership'" },
      { question: "What percentage of your customers are regulars vs. one-time visitors?", hint: "Loyalty programmes mainly affect regulars -- knowing the split matters" },
      { question: "Have you tried any form of customer retention before?", hint: "Past attempts (even informal ones like discounts) give us calibration data" },
    );
  } else if (q.includes("location") || q.includes("move") || q.includes("expand") || q.includes("second")) {
    questions.push(
      { question: "Where would the new location be, and how far is it from your current one?", hint: "Distance affects whether you split your customer base or reach new ones" },
      { question: "What is your current customer catchment area?", hint: "e.g. 'Most customers live within 10 minutes walking distance'" },
      { question: "Would you keep the original location running as-is?", hint: "Cannibalization risk is real if both locations serve the same area" },
    );
  } else if (q.includes("rebrand") || q.includes("rename") || q.includes("redesign") || q.includes("renovate")) {
    questions.push(
      { question: "What specifically would change, and what would stay the same?", hint: "e.g. 'New logo and interior, same menu and staff'" },
      { question: "Why are you considering this change now?", hint: "Understanding the trigger helps us simulate customer reactions more accurately" },
      { question: "How long have your regular customers been coming?", hint: "Long-time regulars may react very differently to change than newer customers" },
    );
  } else {
    questions.push(
      { question: "Can you describe the specific change you are considering?", hint: "The more detail you give, the more realistic the simulation will be" },
      { question: "What triggered this idea -- a problem you are solving or an opportunity you spotted?", hint: "This helps us frame the simulation around the right customer concerns" },
      { question: "Do you have any data that might be relevant? Sales numbers, customer complaints, competitor moves?", hint: "Even rough numbers significantly improve simulation accuracy" },
    );
  }

  return questions;
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
    const clarifyingQuestions = generateClarifyingQuestions(question);
    const entry: SimEntry = {
      id: entryId,
      question,
      originalQuestion: question,
      status: "clarifying",
      clarifyingQuestions,
      clarifyingAnswers: [],
    };
    setThread((prev) => [...prev, entry]);
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
            const [result, responses, caveats] = await Promise.all([
              getSimulationResult(simId),
              getSimulationResponses(simId).catch(() => []),
              getSimulationCaveats(simId).catch(() => []),
            ]);

            setThread((prev) =>
              prev.map((e) =>
                e.id === simId
                  ? { ...e, status: "done", result, responses, caveats }
                  : e
              )
            );

            if (onSimulationComplete) {
              const impact = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api"}/simulations/${simId}/impact`
              ).then((r) => r.json()).catch(() => null);

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
                  <div className="space-y-4">
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
                    {entry.caveats && entry.caveats.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                          Important caveats
                        </h4>
                        {entry.caveats.slice(0, 3).map((c, i) => (
                          <div key={i} className={`rounded-xl border p-4 ${
                            c.severity === "warning" ? "border-amber-200 bg-amber-50" : "border-[#E5E2DC] bg-gray-50"
                          }`}>
                            <p className={`text-xs font-medium ${c.severity === "warning" ? "text-amber-700" : "text-gray-600"}`}>{c.title}</p>
                            <p className={`mt-1 text-sm ${c.severity === "warning" ? "text-amber-600" : "text-gray-500"}`}>{c.message}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {!entry.caveats?.length && entry.result.confidence_reasoning && (
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
