"use client";

/**
 * PersonaCard — displays a synthetic customer persona.
 *
 * Inspired by MiroFish's agent profile cards in Step2EnvSetup:
 * - Avatar circle with first letter
 * - Name, age, occupation
 * - Personality traits as tags
 * - Relationship to business
 * - Quirk detail
 */

import { PersonaProfile } from "@/lib/api";

interface Props {
  persona: PersonaProfile;
  compact?: boolean;
}

// Color palette from MiroFish for avatar circles
const AVATAR_COLORS = [
  "bg-brand-orange",
  "bg-legacy-navy",
  "bg-legacy-purple",
  "bg-legacy-teal",
  "bg-legacy-red",
  "bg-legacy-coral",
];

function avatarColor(name: string): string {
  const idx = name.charCodeAt(0) % AVATAR_COLORS.length;
  return AVATAR_COLORS[idx];
}

export default function PersonaCard({ persona, compact }: Props) {
  if (compact) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-gray-100 bg-white p-3 transition-shadow hover:shadow-sm">
        <div
          className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold text-white ${avatarColor(persona.name)}`}
        >
          {persona.name[0]}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-gray-900">
            {persona.name}, {persona.age}
          </p>
          <p className="truncate text-xs text-gray-500">{persona.occupation}</p>
        </div>
        <span className="font-mono text-xs text-gray-400">
          {persona.spend_model || (persona.avg_spend ? `$${persona.avg_spend}` : "")}
        </span>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md animate-fade-in-up">
      {/* Header */}
      <div className="mb-3 flex items-start gap-3">
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-lg font-bold text-white ${avatarColor(persona.name)}`}
        >
          {persona.name[0]}
        </div>
        <div>
          <p className="font-medium text-gray-900">
            {persona.name}, {persona.age}
          </p>
          <p className="text-sm text-gray-500">{persona.occupation}</p>
        </div>
      </div>

      {/* Stats row */}
      <div className="mb-3 flex flex-wrap gap-3 text-xs text-gray-500">
        <span>{persona.engagement_pattern || persona.visit_frequency}</span>
        {(persona.spend_model || persona.avg_spend) && (
          <span>{persona.spend_model || `$${persona.avg_spend}`}</span>
        )}
        {persona.segment && (
          <span className="rounded-full bg-brand-orange/10 px-2 py-0.5 text-[10px] font-medium text-brand-orange">
            {persona.segment}
          </span>
        )}
      </div>

      {/* Personality traits as tags */}
      <div className="mb-3 flex flex-wrap gap-1.5">
        {persona.personality.split(",").map((trait, i) => (
          <span
            key={i}
            className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
          >
            {trait.trim()}
          </span>
        ))}
      </div>

      {/* Relationship */}
      <p className="mb-2 text-sm text-gray-700">
        {persona.relationship_to_business}
      </p>

      {/* Quirk — italic, smaller */}
      <p className="text-xs italic text-gray-400">{persona.quirk}</p>
    </div>
  );
}
