"use client";

/**
 * Dashboard — list of past simulations.
 *
 * Inspired by MiroFish's main view: shows all past simulation runs
 * with status badges, timestamps, and quick access to results.
 */

import { useEffect, useState } from "react";
import { listSimulations, Simulation, SimulationStatus } from "@/lib/api";
import { Clock, MessageSquare, ChevronRight } from "lucide-react";

function StatusBadge({ status }: { status: SimulationStatus }) {
  const config: Record<SimulationStatus, { bg: string; text: string }> = {
    pending: { bg: "bg-gray-100", text: "text-gray-500" },
    gathering_context: { bg: "bg-legacy-navy/10", text: "text-legacy-navy" },
    generating_personas: { bg: "bg-brand-orange/10", text: "text-brand-orange" },
    simulating: { bg: "bg-brand-orange/10", text: "text-brand-orange" },
    aggregating: { bg: "bg-legacy-purple/10", text: "text-legacy-purple" },
    completed: { bg: "bg-legacy-teal/10", text: "text-legacy-teal" },
    failed: { bg: "bg-legacy-red/10", text: "text-legacy-red" },
  };
  const c = config[status];
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${c.bg} ${c.text}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

export default function DashboardPage() {
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listSimulations()
      .then(setSimulations)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Your Simulations
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Past questions and their results.
          </p>
        </div>
        <a
          href="/app/simulate"
          className="rounded-lg bg-legacy-navy px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          New Simulation
        </a>
      </div>

      {loading ? (
        <div className="py-16 text-center text-gray-400">Loading...</div>
      ) : simulations.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 py-16 text-center">
          <MessageSquare className="mx-auto mb-3 h-8 w-8 text-gray-300" />
          <p className="text-sm text-gray-500">
            No simulations yet.{" "}
            <a href="/app/simulate" className="text-legacy-navy underline">
              Run your first one.
            </a>
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {simulations.map((sim) => (
            <a
              key={sim.id}
              href={`/simulate?businessId=${sim.business_id}&simulationId=${sim.id}`}
              className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-gray-900">
                  &ldquo;{sim.question}&rdquo;
                </p>
                <div className="mt-1 flex items-center gap-3 text-xs text-gray-400">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(sim.created_at).toLocaleDateString()}
                  </span>
                  <span>{sim.persona_count} personas</span>
                  {sim.variant_a && (
                    <span className="rounded bg-legacy-purple/10 px-1.5 py-0.5 text-legacy-purple">
                      A/B
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={sim.status} />
                <ChevronRight className="h-4 w-4 text-gray-300" />
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
