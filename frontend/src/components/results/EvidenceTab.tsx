"use client";

/**
 * EvidenceTab -- shows persona responses grouped by demographic segment.
 *
 * Displays:
 * - Group headers with segment name and persona count
 * - Average sentiment per group
 * - Expandable persona cards with 3-turn data
 * - Filter chips for segment filtering
 */

import { useState } from "react";
import { PersonaResponseData } from "@/lib/api";
import PersonaResponseCard from "./PersonaResponseCard";

interface DemographicGroup {
  group: string;
  count: number;
  avg_sentiment: number;
  personas: string[];
  members: { persona_name: string; age?: number; sentiment: number }[];
}

interface Props {
  responses: PersonaResponseData[];
  demographicGroups?: DemographicGroup[];
  statedVsActualGap?: string;
  baselineSummary?: string;
  behavioralPrediction?: {
    engagement_change?: string;
    spend_change?: string;
    adaptation_speed?: string;
    word_of_mouth?: string;
  };
}

function SentimentBar({ value }: { value: number }) {
  // Map -1..1 to 0..100
  const pct = ((value + 1) / 2) * 100;
  const color =
    value > 0.3 ? "bg-legacy-teal" : value < -0.3 ? "bg-legacy-red" : "bg-yellow-400";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-gray-100">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] text-gray-400">{value > 0 ? "+" : ""}{value.toFixed(1)}</span>
    </div>
  );
}

export default function EvidenceTab({
  responses,
  demographicGroups,
  statedVsActualGap,
  baselineSummary,
  behavioralPrediction,
}: Props) {
  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  const groups = demographicGroups || [];
  const allSegments = groups.map((g) => g.group);

  // Filter responses by segment if active
  const filteredResponses = activeFilter
    ? responses.filter((r) => {
        const group = groups.find((g) => g.group === activeFilter);
        return group?.personas.includes(r.persona_name);
      })
    : responses;

  return (
    <div className="space-y-5">
      {/* Baseline summary */}
      {baselineSummary && (
        <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Current Customer Base
          </h4>
          <p className="text-sm text-gray-700">{baselineSummary}</p>
        </div>
      )}

      {/* Say-do gap highlight */}
      {statedVsActualGap && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-amber-600">
            Say-Do Gap
          </h4>
          <p className="text-sm text-amber-800">{statedVsActualGap}</p>
        </div>
      )}

      {/* Behavioral prediction */}
      {behavioralPrediction && (
        <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Predicted Behavior
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {behavioralPrediction.engagement_change && (
              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-[10px] font-medium uppercase text-gray-400">Engagement</p>
                <p className="mt-0.5 text-sm text-gray-700">{behavioralPrediction.engagement_change}</p>
              </div>
            )}
            {behavioralPrediction.spend_change && (
              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-[10px] font-medium uppercase text-gray-400">Spending</p>
                <p className="mt-0.5 text-sm text-gray-700">{behavioralPrediction.spend_change}</p>
              </div>
            )}
            {behavioralPrediction.adaptation_speed && (
              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-[10px] font-medium uppercase text-gray-400">Adaptation</p>
                <p className="mt-0.5 text-sm text-gray-700">{behavioralPrediction.adaptation_speed}</p>
              </div>
            )}
            {behavioralPrediction.word_of_mouth && (
              <div className="rounded-lg bg-gray-50 p-3">
                <p className="text-[10px] font-medium uppercase text-gray-400">Word of Mouth</p>
                <p className="mt-0.5 text-sm text-gray-700">{behavioralPrediction.word_of_mouth}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Demographic groups */}
      {groups.length > 0 && (
        <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
            By Customer Segment
          </h4>

          {/* Filter chips */}
          <div className="mb-4 flex flex-wrap gap-1.5">
            <button
              onClick={() => setActiveFilter(null)}
              className={`rounded-full border px-3 py-1 text-xs transition-all ${
                !activeFilter
                  ? "border-brand-orange bg-brand-orange text-white"
                  : "border-gray-200 text-gray-500 hover:bg-gray-50"
              }`}
            >
              All ({responses.length})
            </button>
            {allSegments.map((seg) => {
              const group = groups.find((g) => g.group === seg);
              return (
                <button
                  key={seg}
                  onClick={() => setActiveFilter(activeFilter === seg ? null : seg)}
                  className={`rounded-full border px-3 py-1 text-xs transition-all ${
                    activeFilter === seg
                      ? "border-brand-orange bg-brand-orange text-white"
                      : "border-gray-200 text-gray-500 hover:bg-gray-50"
                  }`}
                >
                  {seg} ({group?.count || 0})
                </button>
              );
            })}
          </div>

          {/* Group summary cards */}
          <div className="space-y-2">
            {groups.map((group) => (
              <div
                key={group.group}
                className={`flex items-center justify-between rounded-lg border p-3 transition-all ${
                  activeFilter === group.group
                    ? "border-brand-orange bg-brand-orange/5"
                    : "border-gray-100"
                }`}
              >
                <div>
                  <p className="text-sm font-medium text-gray-900">{group.group}</p>
                  <p className="text-[10px] text-gray-400">
                    {group.count} {group.count === 1 ? "person" : "people"}
                  </p>
                </div>
                <SentimentBar value={group.avg_sentiment} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Individual responses */}
      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
          Individual Responses{activeFilter ? ` -- ${activeFilter}` : ""}
          <span className="ml-2 text-gray-300">({filteredResponses.length})</span>
        </h4>
        {filteredResponses.map((resp, i) => (
          <PersonaResponseCard key={i} response={resp} />
        ))}
      </div>
    </div>
  );
}
