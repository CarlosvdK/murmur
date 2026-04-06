"use client";

export default function HealthBadge({
  sentiment,
  hasTwin,
}: {
  sentiment: string | null;
  hasTwin: boolean;
}) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    very_positive: { bg: "bg-green-100", text: "text-green-700", label: "Strong" },
    positive: { bg: "bg-green-50", text: "text-green-600", label: "Strong" },
    neutral: { bg: "bg-gray-100", text: "text-gray-600", label: "Neutral" },
    negative: { bg: "bg-amber-50", text: "text-amber-700", label: "Watch" },
    very_negative: { bg: "bg-red-50", text: "text-red-700", label: "At risk" },
    unknown: { bg: "bg-gray-50", text: "text-gray-400", label: "No data" },
  };

  const c = config[sentiment || "unknown"] || config.unknown;

  return (
    <div className="flex items-center gap-2">
      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${c.bg} ${c.text}`}>
        {c.label}
      </span>
      {hasTwin && (
        <span className="rounded bg-brand-blue/10 px-1.5 py-0.5 text-[10px] font-medium text-brand-blue">
          Twin
        </span>
      )}
    </div>
  );
}
