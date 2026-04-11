"use client";

/**
 * CIChart -- Confidence interval bar visualization with prediction dot.
 *
 * Shows the range of possible outcomes with labeled zones:
 * - Red zone: clearly negative
 * - Amber zone: uncertain / too close to call
 * - Green zone: clearly positive
 *
 * The prediction dot shows our best estimate.
 * The CI bar shows the range of uncertainty.
 * Works for ANY impact type (revenue, satisfaction, adoption, etc.).
 */

interface CIChartProps {
  pointEstimate: number;
  ciLow: number;
  ciHigh: number;
  rejectNull: boolean;
  decision: string;
  impactLabel?: string;
  effectSize?: string;
  nullHypothesis?: string;
}

export default function CIChart({
  pointEstimate,
  ciLow,
  ciHigh,
  rejectNull,
  decision,
  impactLabel = "Estimated impact",
  effectSize,
  nullHypothesis = "No change",
}: CIChartProps) {
  // Calculate positions on the bar
  const barMin = Math.min(ciLow - 3, -5);
  const barMax = Math.max(ciHigh + 3, 5);
  const barRange = barMax - barMin;
  const zeroPct = ((0 - barMin) / barRange) * 100;
  const pointPct = ((pointEstimate - barMin) / barRange) * 100;
  const ciLeftPct = ((ciLow - barMin) / barRange) * 100;
  const ciWidthPct = ((ciHigh - ciLow) / barRange) * 100;

  const isPositive = pointEstimate > 0;

  const decisionConfig: Record<string, { bg: string; text: string; border: string; label: string }> = {
    proceed: { bg: "bg-green-50", text: "text-green-700", border: "border-green-200", label: "Go" },
    caution: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200", label: "Caution" },
    avoid: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", label: "No-go" },
    test_first: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200", label: "Test first" },
  };
  const dc = decisionConfig[decision] || decisionConfig.test_first;

  return (
    <div className="rounded-2xl border border-[#E5E2DC] bg-white p-6">
      {/* Header with go/no-go badge */}
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">{impactLabel}</h3>
        <span className={`rounded-full border px-4 py-1.5 text-sm font-semibold ${dc.bg} ${dc.text} ${dc.border}`}>
          {dc.label}
        </span>
      </div>

      {/* Big number */}
      <div className="mb-6 text-center">
        <p className="text-5xl font-black tracking-tight text-gray-900">
          {pointEstimate >= 0 ? "+" : ""}{pointEstimate}%
        </p>
        <p className="mt-1 text-sm text-gray-500">
          {impactLabel.toLowerCase()}
        </p>
        {effectSize && effectSize !== "unknown" && (
          <p className="mt-0.5 text-[10px] uppercase tracking-wider text-gray-400">
            {effectSize} effect
          </p>
        )}
      </div>

      {/* CI Visualization Bar */}
      <div className="mb-2">
        <div className="relative h-14 rounded-xl bg-gray-100 overflow-hidden">
          {/* Zone gradient background */}
          <div
            className="absolute inset-0"
            style={{
              background: `linear-gradient(90deg,
                rgba(197,40,61,0.08) 0%,
                rgba(197,40,61,0.08) ${Math.max(zeroPct - 5, 0)}%,
                rgba(255,135,32,0.06) ${zeroPct - 5}%,
                rgba(255,135,32,0.06) ${zeroPct + 5}%,
                rgba(26,147,111,0.08) ${Math.min(zeroPct + 5, 100)}%,
                rgba(26,147,111,0.08) 100%)`,
            }}
          />

          {/* Zero / null hypothesis line */}
          <div
            className="absolute top-0 h-full w-px bg-gray-400"
            style={{ left: `${zeroPct}%` }}
          />
          <div
            className="absolute -top-5 text-[9px] text-gray-400 whitespace-nowrap"
            style={{ left: `${zeroPct}%`, transform: "translateX(-50%)" }}
          >
            {nullHypothesis}
          </div>

          {/* CI range bar */}
          <div
            className="absolute top-3 h-8 rounded-lg"
            style={{
              left: `${ciLeftPct}%`,
              width: `${Math.max(ciWidthPct, 1)}%`,
              background: rejectNull
                ? isPositive
                  ? "rgba(26,147,111,0.2)"
                  : "rgba(197,40,61,0.2)"
                : "rgba(255,135,32,0.2)",
              border: `1px solid ${rejectNull
                ? isPositive
                  ? "rgba(26,147,111,0.3)"
                  : "rgba(197,40,61,0.3)"
                : "rgba(255,135,32,0.3)"}`,
            }}
          />

          {/* Point estimate marker */}
          <div
            className="absolute top-2 flex h-10 flex-col items-center"
            style={{ left: `${pointPct}%`, transform: "translateX(-50%)" }}
          >
            <div
              className={`h-10 w-1.5 rounded-full ${isPositive ? "bg-legacy-teal" : "bg-legacy-red"}`}
            />
          </div>
        </div>
      </div>

      {/* Labels under the bar */}
      <div className="relative mt-1 h-5">
        {/* CI low label */}
        <div
          className="absolute text-[10px] font-medium text-legacy-red"
          style={{ left: `${ciLeftPct}%`, transform: "translateX(-30%)" }}
        >
          {ciLow >= 0 ? "+" : ""}{ciLow}%
        </div>

        {/* Point estimate label */}
        <div
          className={`absolute text-xs font-bold ${isPositive ? "text-legacy-teal" : "text-legacy-red"}`}
          style={{ left: `${pointPct}%`, transform: "translateX(-50%)" }}
        >
          {pointEstimate >= 0 ? "+" : ""}{pointEstimate}%
        </div>

        {/* CI high label */}
        <div
          className="absolute text-[10px] font-medium text-legacy-teal"
          style={{ left: `${Math.min(ciLeftPct + ciWidthPct, 95)}%`, transform: "translateX(-70%)" }}
        >
          +{ciHigh}%
        </div>
      </div>

      {/* Zone labels */}
      <div className="mt-4 flex justify-between text-[10px] text-gray-400">
        <span>worst case</span>
        <span>best estimate</span>
        <span>best case</span>
      </div>

      {/* Hypothesis test result */}
      {rejectNull && (
        <div className={`mt-4 rounded-xl px-4 py-2.5 ${isPositive ? "bg-green-50" : "bg-red-50"}`}>
          <p className={`text-xs font-medium ${isPositive ? "text-green-700" : "text-red-700"}`}>
            The confidence interval does not include zero -- this change would likely have a{" "}
            {isPositive ? "positive" : "negative"} effect even in conservative scenarios.
          </p>
        </div>
      )}
      {!rejectNull && (
        <div className="mt-4 rounded-xl bg-amber-50 px-4 py-2.5">
          <p className="text-xs font-medium text-amber-700">
            The confidence interval crosses zero -- we cannot rule out that this change
            has no meaningful effect. Consider testing with a small group first.
          </p>
        </div>
      )}
    </div>
  );
}
