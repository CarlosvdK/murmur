"use client";

/**
 * DecisionCard — the go/no-go verdict for a simulation.
 *
 * Previously the decision was inferable only from CIChart's badge or the
 * prose in ImpactPanel. This component surfaces it as a dedicated, prominent
 * card so a small-business owner can glance at the report and see the answer
 * to "should I do this?" without parsing charts.
 */

interface DecisionCardProps {
  decision: string;
  reasoning: string;
  confidence?: "high" | "medium" | "low";
}

const DECISION_CONFIG: Record<
  string,
  { label: string; bg: string; text: string; border: string; chip: string }
> = {
  proceed: {
    label: "Go",
    bg: "bg-green-50",
    text: "text-green-800",
    border: "border-green-200",
    chip: "bg-green-100 text-green-700",
  },
  caution: {
    label: "Caution",
    bg: "bg-amber-50",
    text: "text-amber-800",
    border: "border-amber-200",
    chip: "bg-amber-100 text-amber-700",
  },
  avoid: {
    label: "No-go",
    bg: "bg-red-50",
    text: "text-red-800",
    border: "border-red-200",
    chip: "bg-red-100 text-red-700",
  },
  test_first: {
    label: "Test first",
    bg: "bg-blue-50",
    text: "text-blue-800",
    border: "border-blue-200",
    chip: "bg-blue-100 text-blue-700",
  },
};

export default function DecisionCard({
  decision,
  reasoning,
  confidence,
}: DecisionCardProps) {
  const config = DECISION_CONFIG[decision] || DECISION_CONFIG.test_first;

  return (
    <div
      className={`rounded-2xl border ${config.border} ${config.bg} p-6`}
      role="region"
      aria-label="decision"
    >
      <div className="mb-2 flex items-center gap-3">
        <span
          className={`rounded-full px-4 py-1 text-sm font-bold ${config.text}`}
        >
          {config.label}
        </span>
        {confidence && (
          <span className={`rounded-full px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider ${config.chip}`}>
            {confidence} confidence
          </span>
        )}
      </div>
      <p className={`text-sm ${config.text}`}>{reasoning}</p>
    </div>
  );
}
