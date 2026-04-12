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
  {
    label: "Directional",
    count: 15,
    desc: "15 personas -- fast, ~2 min",
    detail: "Good for a quick gut check. Shows general direction (positive/negative) and key themes. Not enough for statistical confidence or segment breakdowns. Based on qualitative research thresholds (Bonabeau 2002).",
  },
  {
    label: "Statistical",
    count: 35,
    desc: "35 personas -- thorough, ~5 min",
    detail: "Exceeds the Central Limit Theorem threshold (n=30) for statistical inference. Produces reliable confidence intervals, percentages, and probability estimates. The minimum for serious decision-making (Rand & Rust 2011).",
  },
  {
    label: "Segmented",
    count: 75,
    desc: "75 personas -- deep, ~10 min",
    detail: "Enables subgroup analysis -- compare reactions by age, income, customer type, and loyalty level. Each segment gets 10+ personas for directional reliability. Use for high-stakes decisions (Rand & Rust 2011).",
  },
];

export default function RightSidebar({ history, onSelect, personaCount, onPersonaCountChange }: Props) {
  return (
    <aside className="flex h-full w-[420px] shrink-0 flex-col border-l border-[#E5E2DC] bg-white">
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
            <p className="text-xs text-gray-500">Simulation depth</p>
            <div className="mt-2 space-y-1.5">
              {SWARM_OPTIONS.map((opt) => (
                <div key={opt.count} className="group relative">
                  <button
                    onClick={() => onPersonaCountChange(opt.count)}
                    className={`w-full rounded-lg border px-3 py-2 text-left transition-all ${
                      personaCount === opt.count
                        ? "border-brand-orange bg-brand-orange/5"
                        : "border-[#E5E2DC] hover:border-gray-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className={`text-xs font-medium ${
                        personaCount === opt.count ? "text-brand-orange" : "text-gray-600"
                      }`}>
                        {opt.label}
                      </span>
                      <span className="text-[10px] text-gray-400">{opt.count}</span>
                    </div>
                    <p className="mt-0.5 text-[10px] text-gray-400">{opt.desc}</p>
                  </button>
                  {/* Hover tooltip */}
                  <div className="pointer-events-none absolute bottom-full left-0 right-0 z-20 mb-2 hidden rounded-lg border border-[#E5E2DC] bg-white p-3 shadow-lg group-hover:block">
                    <p className="text-[10px] leading-relaxed text-gray-600">{opt.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
