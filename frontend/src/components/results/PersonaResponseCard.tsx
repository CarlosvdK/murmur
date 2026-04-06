"use client";

/**
 * PersonaResponseCard — shows a single persona's response to the question.
 *
 * Inspired by MiroFish's chat message bubbles and timeline entries.
 * Shows the persona's avatar, name, their in-character reaction,
 * reasoning, and sentiment indicator.
 */

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

export default function PersonaResponseCard({ response }: Props) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-4 transition-shadow hover:shadow-sm animate-fade-in-up">
      {/* Header row */}
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold text-white ${avatarColor(response.persona_name)}`}
          >
            {response.persona_name[0]}
          </div>
          <span className="font-medium text-gray-900">
            {response.persona_name}
          </span>
        </div>
        <SentimentDot sentiment={response.sentiment} />
      </div>

      {/* Reaction — the main quote */}
      <p className="mb-2 text-sm text-gray-700">{response.reaction}</p>

      {/* Reasoning — lighter, italic */}
      {response.reasoning && (
        <p className="mb-2 text-xs italic text-gray-400">
          {response.reasoning}
        </p>
      )}

      {/* A/B preference pill */}
      {response.preference && (
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
              response.preference === "A"
                ? "bg-blue-50 text-blue-700"
                : response.preference === "B"
                  ? "bg-purple-50 text-purple-700"
                  : "bg-gray-100 text-gray-500"
            }`}
          >
            Prefers: {response.preference}
          </span>
          {response.preference_strength && (
            <span className="text-xs text-gray-400">
              ({response.preference_strength})
            </span>
          )}
        </div>
      )}
    </div>
  );
}
