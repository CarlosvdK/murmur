"use client";

/**
 * ResultsReport -- the main simulation output display.
 *
 * Two-tab layout:
 * - Decision: Go/no-go badge, CI chart, themes, recommendation
 * - Evidence: Demographic breakdown, individual persona responses, say-do gap
 */

import { useState } from "react";
import {
  SimulationResult,
  Theme,
  StandoutVoice,
  PersonaResponseData,
} from "@/lib/api";
import {
  MessageSquare,
  TrendingUp,
  Shield,
  Award,
  BookOpen,
  BarChart3,
  Users,
} from "lucide-react";
import CIChart from "./CIChart";
import DecisionCard from "./DecisionCard";
import EvidenceTab from "./EvidenceTab";
import ProfileQualityNote from "./ProfileQualityNote";

interface Props {
  result: SimulationResult;
  variantA?: string | null;
  variantB?: string | null;
  ragSelection?: {
    domains: string[];
    question_type: string;
    reasoning: string;
  } | null;
  impactData?: {
    revenue: {
      point_estimate_pct: number;
      ci_low_pct: number;
      ci_high_pct: number;
      confidence_level: string;
      impact_type?: string;
      impact_label?: string;
    };
    customers_likely_stay: number;
    customers_likely_reduce: number;
    customers_likely_leave: number;
    total_customers_modelled: number;
    retention_rate_pct: number;
    decision: string;
    decision_reasoning: string;
    decision_framework: string;
    worst_case_summary: string;
    best_case_summary: string;
    most_likely_summary: string;
    null_hypothesis?: string;
    alternative_hypothesis?: string;
    reject_null?: boolean;
    effect_size?: string;
  } | null;
  responses?: PersonaResponseData[];
  demographicGroups?: {
    group: string;
    count: number;
    avg_sentiment: number;
    personas: string[];
    members: { persona_name: string; age?: number; sentiment: number }[];
  }[];
  profileCompleteness?: number | null;
  profileNextImprovement?: string | null;
}

function ConfidenceBadge({ level }: { level: string }) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    high: { bg: "bg-legacy-teal/10", text: "text-legacy-teal", label: "High Confidence" },
    medium: { bg: "bg-yellow-50", text: "text-yellow-700", label: "Medium Confidence" },
    low: { bg: "bg-legacy-red/10", text: "text-legacy-red", label: "Low Confidence" },
  };
  const c = config[level] || config.medium;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${c.bg} ${c.text}`}>
      <Shield className="h-3 w-3" />
      {c.label}
    </span>
  );
}

function ThemeCard({ theme }: { theme: Theme }) {
  return (
    <div className="rounded-lg border border-gray-100 bg-gray-50 p-4 animate-fade-in-up">
      <div className="mb-2 flex items-center justify-between">
        <h4 className="font-medium text-gray-900">{theme.label}</h4>
        <span className="rounded-full bg-legacy-navy/10 px-2 py-0.5 text-xs font-mono text-legacy-navy">
          {theme.count} {theme.count === 1 ? "person" : "people"}
        </span>
      </div>
      <p className="text-sm text-gray-600">{theme.summary}</p>
    </div>
  );
}

function VoiceCard({ voice }: { voice: StandoutVoice }) {
  return (
    <div className="flex gap-3 rounded-lg border-l-4 border-legacy-purple bg-legacy-purple/5 p-4 animate-fade-in-up">
      <MessageSquare className="mt-0.5 h-4 w-4 shrink-0 text-legacy-purple" />
      <div>
        <p className="text-sm font-medium text-gray-900">{voice.persona_name}</p>
        <p className="mt-1 text-sm italic text-gray-600">&ldquo;{voice.quote}&rdquo;</p>
      </div>
    </div>
  );
}

const DOMAIN_LABELS: Record<string, string> = {
  consumer_psychology: "Consumer Psychology",
  behavioral_economics: "Behavioral Economics",
  digital_twins: "Simulation Fidelity",
  country_profiles: "Cultural Dimensions",
  review_bias: "Review Bias Correction",
  personality_models: "Personality Models",
  simulation_methodology: "Methodology Calibration",
  negotiation_psychology: "Negotiation Psychology",
  decision_making: "Decision Making",
  qualitative_interview_methodology: "Interview Methodology",
};

export default function ResultsReport({
  result,
  variantA,
  variantB,
  ragSelection,
  impactData,
  responses,
  demographicGroups,
  profileCompleteness,
  profileNextImprovement,
}: Props) {
  const [activeTab, setActiveTab] = useState<"decision" | "evidence">("decision");

  return (
    <div className="space-y-6">
      {/* Report header */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-3">
          <span className="rounded-md bg-legacy-navy px-2.5 py-1 text-xs font-medium text-white">
            Simulation Report
          </span>
          <ConfidenceBadge level={result.confidence_score} />
        </div>

        <h2 className="mb-2 text-xl font-semibold text-gray-900">
          {result.summary}
        </h2>

        {result.confidence_reasoning && (
          <p className="text-sm text-gray-500">{result.confidence_reasoning}</p>
        )}
      </div>

      {/* Tab navigation */}
      <div className="border-b border-[#E5E2DC]">
        <nav className="flex gap-6">
          <button
            onClick={() => setActiveTab("decision")}
            className={`flex items-center gap-2 border-b-2 pb-3 pt-1 text-sm font-medium transition-colors ${
              activeTab === "decision"
                ? "border-brand-orange text-black"
                : "border-transparent text-gray-400 hover:text-gray-600"
            }`}
          >
            <BarChart3 className="h-4 w-4" />
            Decision
          </button>
          <button
            onClick={() => setActiveTab("evidence")}
            className={`flex items-center gap-2 border-b-2 pb-3 pt-1 text-sm font-medium transition-colors ${
              activeTab === "evidence"
                ? "border-brand-orange text-black"
                : "border-transparent text-gray-400 hover:text-gray-600"
            }`}
          >
            <Users className="h-4 w-4" />
            Evidence
            {responses && (
              <span className="rounded-full bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500">
                {responses.length}
              </span>
            )}
          </button>
        </nav>
      </div>

      {/* ====== DECISION TAB ====== */}
      {activeTab === "decision" && (
        <div className="space-y-5">
          {/* Profile-quality caveat (silent when profile is rich) */}
          <ProfileQualityNote
            completeness={profileCompleteness}
            nextImprovement={profileNextImprovement}
          />

          {/* CI Chart */}
          {impactData && (
            <CIChart
              pointEstimate={impactData.revenue.point_estimate_pct}
              ciLow={impactData.revenue.ci_low_pct}
              ciHigh={impactData.revenue.ci_high_pct}
              rejectNull={impactData.reject_null ?? false}
              decision={impactData.decision}
              impactLabel={impactData.revenue.impact_label || "Estimated impact"}
              effectSize={impactData.effect_size}
              nullHypothesis={impactData.null_hypothesis || "No change"}
              pPositive={(impactData as Record<string, unknown>).p_positive as number | undefined}
              pNegative={(impactData as Record<string, unknown>).p_negative as number | undefined}
              upsideVsDownside={(impactData as Record<string, unknown>).upside_vs_downside as string | undefined}
            />
          )}

          {/* Decision card -- prominent go/no-go for the glance-test */}
          {impactData && (
            <DecisionCard
              decision={impactData.decision}
              reasoning={impactData.decision_reasoning}
              confidence={result.confidence_score as "high" | "medium" | "low" | undefined}
            />
          )}

          {/* Decision framework explanation (the underlying logic) */}
          {impactData && impactData.decision_framework && (
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <p className="text-sm leading-relaxed text-gray-600">
                {impactData.decision_framework}
              </p>
            </div>
          )}

          {/* Customer retention */}
          {impactData && impactData.total_customers_modelled > 0 && (
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 text-sm font-semibold text-gray-900">Customer Impact</h3>
              <div className="mb-4 grid grid-cols-3 gap-3">
                <div className="rounded-xl bg-green-50 p-3 text-center">
                  <p className="text-2xl font-bold text-green-700">{impactData.customers_likely_stay}</p>
                  <p className="text-[10px] text-green-600">would stay</p>
                </div>
                <div className="rounded-xl bg-amber-50 p-3 text-center">
                  <p className="text-2xl font-bold text-amber-700">{impactData.customers_likely_reduce}</p>
                  <p className="text-[10px] text-amber-600">reduce engagement</p>
                </div>
                <div className="rounded-xl bg-red-50 p-3 text-center">
                  <p className="text-2xl font-bold text-red-700">{impactData.customers_likely_leave}</p>
                  <p className="text-[10px] text-red-600">would leave</p>
                </div>
              </div>
              <div className="mb-2 h-3 overflow-hidden rounded-full bg-gray-100">
                <div className="flex h-full">
                  <div className="bg-green-400" style={{ width: `${(impactData.customers_likely_stay / impactData.total_customers_modelled) * 100}%` }} />
                  <div className="bg-amber-400" style={{ width: `${(impactData.customers_likely_reduce / impactData.total_customers_modelled) * 100}%` }} />
                  <div className="bg-red-400" style={{ width: `${(impactData.customers_likely_leave / impactData.total_customers_modelled) * 100}%` }} />
                </div>
              </div>
              <p className="text-xs text-gray-400">
                {impactData.retention_rate_pct}% retention across {impactData.total_customers_modelled} simulated customers
              </p>
            </div>
          )}

          {/* A/B Winner card */}
          {result.winner && variantA && variantB && (
            <div className="rounded-xl border-2 border-legacy-teal/30 bg-legacy-teal/5 p-6">
              <div className="mb-3 flex items-center gap-2">
                <Award className="h-5 w-5 text-legacy-teal" />
                <h3 className="font-semibold text-gray-900">
                  {result.winner === "A" ? `Winner: ${variantA}`
                    : result.winner === "B" ? `Winner: ${variantB}`
                    : result.winner === "tie" ? "Too close to call"
                    : "It depends on your priorities"}
                </h3>
              </div>
              <div className="mb-4 grid grid-cols-2 gap-3">
                <div className={`rounded-lg p-3 text-center ${result.winner === "A" ? "border-2 border-legacy-teal bg-white" : "border border-gray-200 bg-white"}`}>
                  <p className="text-xs text-gray-500">Option A</p>
                  <p className="text-sm font-medium text-gray-900">{variantA}</p>
                </div>
                <div className={`rounded-lg p-3 text-center ${result.winner === "B" ? "border-2 border-legacy-teal bg-white" : "border border-gray-200 bg-white"}`}>
                  <p className="text-xs text-gray-500">Option B</p>
                  <p className="text-sm font-medium text-gray-900">{variantB}</p>
                </div>
              </div>
              {result.winner_reasoning && (
                <p className="text-sm text-gray-600">{result.winner_reasoning}</p>
              )}
            </div>
          )}

          {/* Themes */}
          {result.themes && result.themes.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-3">
                <span className="font-mono text-sm font-bold text-brand-orange">01</span>
                <h3 className="font-semibold text-gray-900">What Your Customers Said</h3>
              </div>
              <div className="space-y-3">
                {result.themes.map((theme, i) => (
                  <ThemeCard key={i} theme={theme} />
                ))}
              </div>
            </div>
          )}

          {/* Standout voices */}
          {result.standout_voices && result.standout_voices.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-3">
                <span className="font-mono text-sm font-bold text-brand-orange">02</span>
                <h3 className="font-semibold text-gray-900">Voices Worth Hearing</h3>
              </div>
              <div className="space-y-3">
                {result.standout_voices.map((voice, i) => (
                  <VoiceCard key={i} voice={voice} />
                ))}
              </div>
            </div>
          )}

          {/* Recommendation */}
          {result.recommendation && (
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-3">
                <span className="font-mono text-sm font-bold text-brand-orange">03</span>
                <h3 className="font-semibold text-gray-900">Our Suggestion</h3>
              </div>
              <div className="flex gap-3 rounded-lg bg-legacy-navy/5 p-4">
                <TrendingUp className="mt-0.5 h-5 w-5 shrink-0 text-legacy-navy" />
                <p className="text-sm text-gray-700">{result.recommendation}</p>
              </div>
              <p className="mt-3 text-xs text-gray-400">
                This is based on simulated customer feedback, not real data. Use it
                as one input to your decision, not the only one.
              </p>
            </div>
          )}

          {/* Scenarios */}
          {impactData && (
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 text-sm font-semibold text-gray-900">Scenario Analysis</h3>
              <div className="space-y-3">
                <div className="rounded-xl bg-green-50 p-3">
                  <p className="text-xs font-medium text-green-700">Best case</p>
                  <p className="mt-1 text-sm text-green-600">{impactData.best_case_summary}</p>
                </div>
                <div className="rounded-xl bg-gray-50 p-3">
                  <p className="text-xs font-medium text-gray-700">Most likely</p>
                  <p className="mt-1 text-sm text-gray-600">{impactData.most_likely_summary}</p>
                </div>
                <div className="rounded-xl bg-red-50 p-3">
                  <p className="text-xs font-medium text-red-700">Worst case</p>
                  <p className="mt-1 text-sm text-red-600">{impactData.worst_case_summary}</p>
                </div>
              </div>
            </div>
          )}

          {/* Research sources: prefer result.citations (new), fall back to ragSelection (legacy) */}
          {(() => {
            const citations = result.citations || [];
            /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
            const ragSections = (ragSelection as any)?.sections as
              | { domain: string; title: string; similarity: number }[]
              | undefined;
            const sections = citations.length > 0 ? citations : ragSections;
            const domains = ragSelection?.domains;
            const hasAnything = (sections && sections.length > 0) || (domains && domains.length > 0);
            if (!hasAnything) return null;
            return (
              <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                <div className="mb-3 flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-gray-400" />
                  <h4 className="text-xs font-medium uppercase tracking-wider text-gray-400">
                    Research Sources
                    {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                    {(ragSelection as any)?.method === "vector_search" && (
                      <span className="ml-2 text-[9px] text-gray-300">semantic match</span>
                    )}
                  </h4>
                </div>
                {sections && sections.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {sections.map((section, i) => (
                      <span
                        key={i}
                        className="rounded-full border border-gray-200 bg-gray-50 px-2.5 py-0.5 text-[10px] text-gray-500"
                      >
                        {section.title}
                        {section.similarity > 0 && (
                          <span className="ml-1 text-gray-300">
                            {Math.round(section.similarity * 100)}%
                          </span>
                        )}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {domains!.map((domain) => (
                      <span
                        key={domain}
                        className="rounded-full border border-gray-200 bg-gray-50 px-2.5 py-0.5 text-[10px] text-gray-500"
                      >
                        {DOMAIN_LABELS[domain] || domain}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}

      {/* ====== EVIDENCE TAB ====== */}
      {activeTab === "evidence" && (
        <EvidenceTab
          responses={responses || []}
          demographicGroups={demographicGroups}
          statedVsActualGap={result.stated_vs_actual_gap || undefined}
          baselineSummary={result.baseline_summary || undefined}
          behavioralPrediction={result.behavioral_prediction || undefined}
        />
      )}
    </div>
  );
}
