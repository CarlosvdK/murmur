"use client";

/**
 * PersonaResponseCard -- shows a single persona's response.
 *
 * Supports both:
 * - Legacy single-shot format (reaction, reasoning, sentiment)
 * - Focus group 3-turn format (warmup, core, depth)
 *
 * When 3-turn data is available, shows expandable sections for each phase.
 */

import { useState } from "react";
import { PersonaResponseData } from "@/lib/api";

interface Props {
  response: PersonaResponseData;
}

const AVATAR_COLORS = [
  "bg-brand-orange",
  "bg-legacy-navy",
  "bg-legacy-purple",
  "bg-legacy-teal",
  "bg-legacy-red",
  "bg-legacy-coral",
];

function avatarColor(name: string): string {
  if (!name) return AVATAR_COLORS[0];
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length];
}

function SentimentDot({ sentiment }: { sentiment: number }) {
  const color =
    sentiment > 0.3
      ? "bg-legacy-teal"
      : sentiment < -0.3
        ? "bg-legacy-red"
        : "bg-yellow-400";
  const label =
    sentiment > 0.3
      ? "Positive"
      : sentiment < -0.3
        ? "Negative"
        : "Neutral";

  return (
    <div className="flex items-center gap-1.5">
      <div className={`h-2 w-2 rounded-full ${color}`} />
      <span className="text-xs text-gray-400">{label}</span>
    </div>
  );
}

function TurnSection({
  title,
  phase,
  children,
  defaultOpen = false,
}: {
  title: string;
  phase: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const phaseColors: Record<string, string> = {
    warmup: "text-brand-blue",
    core: "text-brand-orange",
    depth: "text-legacy-purple",
  };
  return (
    <div className="border-t border-gray-100 pt-2">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between py-1 text-left"
      >
        <span className={`text-[10px] font-semibold uppercase tracking-wider ${phaseColors[phase] || "text-gray-400"}`}>
          {title}
        </span>
        <span className="text-[10px] text-gray-300">{open ? "hide" : "show"}</span>
      </button>
      {open && <div className="pb-2 pt-1">{children}</div>}
    </div>
  );
}

export default function PersonaResponseCard({ response }: Props) {
  const hasFocusGroup = !!(response.warmup || response.core || response.depth);
  const sentiment = response.core?.sentiment ?? response.sentiment;
  const reaction = response.core?.reaction || response.reaction;
  const reasoning = response.core?.reasoning || response.reasoning;

  return (
    <div className="rounded-xl border border-gray-100 bg-white p-4 transition-shadow hover:shadow-sm animate-fade-in-up">
      {/* Header row */}
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold text-white ${avatarColor(response.persona_name || "")}`}
          >
            {(response.persona_name || "?")[0]}
          </div>
          <span className="font-medium text-gray-900">
            {response.persona_name}
          </span>
        </div>
        <SentimentDot sentiment={sentiment} />
      </div>

      {/* Main reaction */}
      <p className="mb-2 text-sm text-gray-700">{reaction}</p>

      {reasoning && (
        <p className="mb-2 text-xs italic text-gray-400">{reasoning}</p>
      )}

      {/* Say-do gap highlight (if available) */}
      {response.core?.stated_action && response.core?.predicted_actual_action &&
        response.core.stated_action !== response.core.predicted_actual_action && (
        <div className="mb-2 rounded-lg bg-amber-50 px-3 py-2">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-600">Say-do gap</p>
          <p className="mt-0.5 text-xs text-amber-700">
            Says: &ldquo;{response.core.stated_action}&rdquo;
          </p>
          <p className="text-xs text-amber-700">
            Would actually: &ldquo;{response.core.predicted_actual_action}&rdquo;
          </p>
        </div>
      )}

      {/* A/B preference pill */}
      {(response.core?.preference || response.preference) && (
        <div className="mb-2 flex items-center gap-2">
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
              (response.core?.preference || response.preference) === "A"
                ? "bg-blue-50 text-blue-700"
                : (response.core?.preference || response.preference) === "B"
                  ? "bg-purple-50 text-purple-700"
                  : "bg-gray-100 text-gray-500"
            }`}
          >
            Prefers: {response.core?.preference || response.preference}
          </span>
          {(response.core?.preference_strength || response.preference_strength) && (
            <span className="text-xs text-gray-400">
              ({response.core?.preference_strength || response.preference_strength})
            </span>
          )}
        </div>
      )}

      {/* Focus group expandable turns */}
      {hasFocusGroup && (
        <div className="mt-3 space-y-1">
          {response.warmup && (
            <TurnSection title="Warmup -- Current Relationship" phase="warmup">
              <div className="space-y-1 text-xs text-gray-600">
                <p><span className="font-medium text-gray-700">Engagement:</span> {response.warmup.current_engagement}</p>
                <p><span className="font-medium text-gray-700">Satisfaction:</span> {response.warmup.current_satisfaction}/10</p>
                <p><span className="font-medium text-gray-700">Values most:</span> {response.warmup.what_you_value}</p>
                <p><span className="font-medium text-gray-700">Alternatives:</span> {response.warmup.alternatives_aware_of}</p>
                <p><span className="font-medium text-gray-700">Switching ease:</span> {response.warmup.switching_ease}</p>
              </div>
            </TurnSection>
          )}

          {response.core && (
            <TurnSection title="Core Reaction" phase="core" defaultOpen={false}>
              <div className="space-y-1 text-xs text-gray-600">
                <p><span className="font-medium text-gray-700">Gut instinct:</span> {response.core.gut_instinct}</p>
                <p><span className="font-medium text-gray-700">Says they would:</span> {response.core.stated_action}</p>
                <p><span className="font-medium text-gray-700">Would actually:</span> {response.core.predicted_actual_action}</p>
              </div>
            </TurnSection>
          )}

          {response.depth && (
            <TurnSection title="Behavioral Prediction" phase="depth">
              <div className="space-y-1 text-xs text-gray-600">
                {response.depth.next_3_interactions && (
                  <>
                    <p><span className="font-medium text-gray-700">1st time:</span> {response.depth.next_3_interactions.interaction_1}</p>
                    <p><span className="font-medium text-gray-700">2nd time:</span> {response.depth.next_3_interactions.interaction_2}</p>
                    <p><span className="font-medium text-gray-700">3rd time:</span> {response.depth.next_3_interactions.interaction_3}</p>
                  </>
                )}
                <p><span className="font-medium text-gray-700">Net change:</span> {response.depth.net_behavior_change}</p>
                <p><span className="font-medium text-gray-700">Spend change:</span> {response.depth.spend_change}</p>
                {response.depth.stated_vs_actual_gap && (
                  <p className="mt-1 rounded bg-amber-50 px-2 py-1 text-amber-700">
                    <span className="font-medium">Gap:</span> {response.depth.stated_vs_actual_gap}
                  </p>
                )}
                <p><span className="font-medium text-gray-700">Biggest factor:</span> {response.depth.single_biggest_factor}</p>
              </div>
            </TurnSection>
          )}
        </div>
      )}
    </div>
  );
}
