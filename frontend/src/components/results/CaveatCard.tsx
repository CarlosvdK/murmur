"use client";

/**
 * CaveatCard -- displays contextual caveats about the simulation results.
 *
 * Core principle #3: "Always show confidence caveats -- we reduce risk,
 * we don't replace judgment. Every output includes honesty about uncertainty."
 *
 * Caveats come from backend/swarm/caveats.py which generates them based on
 * the question content, business profile quality, and simulation health.
 */

import { useEffect, useState } from "react";
import { CaveatData, getSimulationCaveats } from "@/lib/api";
import { AlertTriangle, Info, ShieldAlert } from "lucide-react";

interface Props {
  simulationId: string;
}

const SEVERITY_CONFIG: Record<
  string,
  { icon: typeof Info; border: string; bg: string; text: string }
> = {
  info: {
    icon: Info,
    border: "border-gray-200",
    bg: "bg-gray-50",
    text: "text-gray-600",
  },
  warning: {
    icon: AlertTriangle,
    border: "border-yellow-200",
    bg: "bg-yellow-50",
    text: "text-yellow-800",
  },
  critical: {
    icon: ShieldAlert,
    border: "border-legacy-red/30",
    bg: "bg-legacy-red/5",
    text: "text-legacy-red",
  },
};

export default function CaveatCard({ simulationId }: Props) {
  const [caveats, setCaveats] = useState<CaveatData[]>([]);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    getSimulationCaveats(simulationId)
      .then(setCaveats)
      .catch(() => {});
  }, [simulationId]);

  if (caveats.length === 0) return null;

  // Show warnings and critical first, then info
  const sorted = [...caveats].sort((a, b) => {
    const order = { critical: 0, warning: 1, info: 2 };
    return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
  });

  const warnings = sorted.filter((c) => c.severity !== "info");
  const infos = sorted.filter((c) => c.severity === "info");
  const visible = expanded ? sorted : warnings.length > 0 ? warnings : sorted.slice(0, 2);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">
          Things to keep in mind
        </h3>
        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
          {caveats.length} {caveats.length === 1 ? "caveat" : "caveats"}
        </span>
      </div>

      <div className="space-y-2">
        {visible.map((caveat, i) => {
          const config = SEVERITY_CONFIG[caveat.severity] || SEVERITY_CONFIG.info;
          const Icon = config.icon;

          return (
            <div
              key={i}
              className={`rounded-lg border ${config.border} ${config.bg} p-3`}
            >
              <div className="flex gap-2.5">
                <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${config.text}`} />
                <div>
                  <p className={`text-sm font-medium ${config.text}`}>
                    {caveat.title}
                  </p>
                  <p className="mt-0.5 text-xs text-gray-500">
                    {caveat.message}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {!expanded && (warnings.length > 0 ? infos.length > 0 : sorted.length > 2) && (
        <button
          onClick={() => setExpanded(true)}
          className="mt-2 text-xs text-gray-400 transition-colors hover:text-gray-600"
        >
          Show {expanded ? "fewer" : `${sorted.length - visible.length} more`}
        </button>
      )}
      {expanded && (
        <button
          onClick={() => setExpanded(false)}
          className="mt-2 text-xs text-gray-400 transition-colors hover:text-gray-600"
        >
          Show fewer
        </button>
      )}
    </div>
  );
}
