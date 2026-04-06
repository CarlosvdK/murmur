"use client";

const STATS = [
  { value: "10+", label: "Business types tested" },
  { value: "70%", label: "Backtest accuracy" },
  { value: "60s", label: "Average simulation" },
];

export default function StatsBar() {
  return (
    <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
      {STATS.map((stat) => (
        <div key={stat.label} className="text-center">
          <p className="text-gradient text-5xl font-bold tracking-tight">
            {stat.value}
          </p>
          <p className="mt-2 text-xs font-medium uppercase tracking-widest text-gray-400">
            {stat.label}
          </p>
        </div>
      ))}
    </div>
  );
}
