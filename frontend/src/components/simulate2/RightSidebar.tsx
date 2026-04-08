"use client";

interface SimHistory {
  id: string;
  question: string;
  verdict: string;
  date: string;
}

interface Props {
  history: SimHistory[];
  onSelect: (id: string) => void;
  personaCount: number;
  onPersonaCountChange: (count: number) => void;
}

const VERDICT_COLORS: Record<string, string> = {
  proceed: "text-green-600",
  caution: "text-amber-600",
  avoid: "text-red-600",
  test_first: "text-blue-600",
};

const VERDICT_LABELS: Record<string, string> = {
  proceed: "Go",
  caution: "Caution",
  avoid: "Avoid",
  test_first: "Test",
};

const SWARM_OPTIONS = [
  { label: "Quick (15)", count: 15 },
  { label: "Standard (35)", count: 35 },
  { label: "Deep (75)", count: 75 },
];

export default function RightSidebar({ history, onSelect, personaCount, onPersonaCountChange }: Props) {
  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-l border-[#E5E2DC] bg-white">
      {/* Past simulations */}
      <div className="flex-1 overflow-y-auto p-5">
        <h3 className="mb-4 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
          Past simulations
        </h3>

        {history.length === 0 ? (
          <p className="text-sm text-gray-300">
            Your simulation history will appear here.
          </p>
        ) : (
          <div className="space-y-2">
            {history.map((sim) => (
              <button
                key={sim.id}
                onClick={() => onSelect(sim.id)}
                className="w-full rounded-xl border border-[#E5E2DC] p-3 text-left transition-colors hover:bg-gray-50"
              >
                <p className="text-sm text-black line-clamp-2">
                  {sim.question}
                </p>
                <div className="mt-1.5 flex items-center justify-between">
                  <span className={`text-xs font-medium ${VERDICT_COLORS[sim.verdict] || "text-gray-400"}`}>
                    {VERDICT_LABELS[sim.verdict] || sim.verdict}
                  </span>
                  <span className="text-[10px] text-gray-300">{sim.date}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Context files */}
      <div className="border-t border-[#E5E2DC] p-5">
        <h3 className="mb-3 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
          Context files
        </h3>
        <p className="text-xs text-gray-300">
          Drag files here to add context to your next simulation.
        </p>
        <p className="mt-1 text-[10px] text-gray-300">.pdf .docx .txt .csv</p>
      </div>

      {/* Simulation settings */}
      <div className="border-t border-[#E5E2DC] p-5">
        <h3 className="mb-3 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
          Settings
        </h3>
        <div className="space-y-2">
          <div>
            <p className="text-xs text-gray-500">Swarm size</p>
            <div className="mt-1 flex gap-1.5">
              {SWARM_OPTIONS.map((opt) => (
                <button
                  key={opt.count}
                  onClick={() => onPersonaCountChange(opt.count)}
                  className={`rounded-lg border px-2 py-1 text-[10px] transition-all ${
                    personaCount === opt.count
                      ? "border-brand-orange bg-brand-orange/5 text-brand-orange"
                      : "border-[#E5E2DC] text-gray-400 hover:border-gray-300"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
