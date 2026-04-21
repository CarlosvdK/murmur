"use client";

/**
 * ProfileQualityNote — shown at the top of the results view when the
 * business profile was sparse at simulation time. Lets the user know
 * the output's uncertainty is rooted in what we know, not just what
 * the personas said.
 *
 * Renders nothing above ~60% completeness (good profile, no noise).
 */

interface Props {
  completeness?: number | null;
  nextImprovement?: string | null;
}

export default function ProfileQualityNote({ completeness, nextImprovement }: Props) {
  if (completeness == null) return null;
  if (completeness >= 60) return null;

  const sparse = completeness < 40;
  const tone = sparse
    ? {
        border: "border-amber-300",
        bg: "bg-amber-50",
        text: "text-amber-800",
      }
    : {
        border: "border-gray-200",
        bg: "bg-gray-50",
        text: "text-gray-600",
      };

  const headline = sparse
    ? "Heads up: your business profile is sparse"
    : "Your business profile is partially complete";

  return (
    <div className={`rounded-xl border ${tone.border} ${tone.bg} p-4`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className={`text-sm font-medium ${tone.text}`}>{headline}</p>
          <p className="mt-0.5 text-xs text-gray-600">
            The simulation draws on what you've told us. A thinner profile
            means thinner personas -- results should be weighed accordingly.
            {nextImprovement && (
              <>
                {" "}
                Consider adding <span className="font-semibold">{nextImprovement}</span>{" "}
                to sharpen future runs.
              </>
            )}
          </p>
        </div>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${tone.text}`}>
          {completeness}%
        </span>
      </div>
    </div>
  );
}
