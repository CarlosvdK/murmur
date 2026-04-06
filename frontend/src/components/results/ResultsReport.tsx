"use client";

/**
 * ResultsReport — the main simulation output display.
 *
 * Inspired by MiroFish's Step4Report:
 * - Report header block with tag + title
 * - Numbered sections (themes, standout voices, recommendation)
 * - Confidence badge
 * - A/B winner card
 *
 * Key difference: MiroFish shows a full research document. We show
 * plain-English customer feedback that feels like real conversations,
 * not a statistics report. This is core principle #2 and #4.
 */

import { SimulationResult, Theme, StandoutVoice } from "@/lib/api";
import {
  MessageSquare,
  TrendingUp,
  Shield,
  Award,
} from "lucide-react";

interface Props {
  result: SimulationResult;
  variantA?: string | null;
  variantB?: string | null;
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

export default function ResultsReport({ result, variantA, variantB }: Props) {
  return (
    <div className="space-y-6">
      {/* Report header — MiroFish style with tag + title */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-3">
          <span className="rounded-md bg-legacy-navy px-2.5 py-1 text-xs font-medium text-white">
            Simulation Report
          </span>
          <ConfidenceBadge level={result.confidence_score} />
        </div>

        {/* Headline — the key finding */}
        <h2 className="mb-2 text-xl font-semibold text-gray-900">
          {result.summary}
        </h2>

        {result.confidence_reasoning && (
          <p className="text-sm text-gray-500">{result.confidence_reasoning}</p>
        )}
      </div>

      {/* A/B Winner card */}
      {result.winner && variantA && variantB && (
        <div className="rounded-xl border-2 border-legacy-teal/30 bg-legacy-teal/5 p-6">
          <div className="mb-3 flex items-center gap-2">
            <Award className="h-5 w-5 text-legacy-teal" />
            <h3 className="font-semibold text-gray-900">
              {result.winner === "A"
                ? `Winner: ${variantA}`
                : result.winner === "B"
                  ? `Winner: ${variantB}`
                  : result.winner === "tie"
                    ? "Too close to call"
                    : "It depends on your priorities"}
            </h3>
          </div>
          <div className="mb-4 grid grid-cols-2 gap-3">
            <div
              className={`rounded-lg p-3 text-center ${
                result.winner === "A"
                  ? "border-2 border-legacy-teal bg-white"
                  : "border border-gray-200 bg-white"
              }`}
            >
              <p className="text-xs text-gray-500">Option A</p>
              <p className="text-sm font-medium text-gray-900">{variantA}</p>
            </div>
            <div
              className={`rounded-lg p-3 text-center ${
                result.winner === "B"
                  ? "border-2 border-legacy-teal bg-white"
                  : "border border-gray-200 bg-white"
              }`}
            >
              <p className="text-xs text-gray-500">Option B</p>
              <p className="text-sm font-medium text-gray-900">{variantB}</p>
            </div>
          </div>
          {result.winner_reasoning && (
            <p className="text-sm text-gray-600">{result.winner_reasoning}</p>
          )}
        </div>
      )}

      {/* Section 01: Themes */}
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

      {/* Section 02: Standout Voices */}
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

      {/* Section 03: Recommendation */}
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
    </div>
  );
}
