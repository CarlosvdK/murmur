"use client";

interface Props {
  score: number;
  milestoneMessage: string;
  nextImprovement?: string | null;
}

export default function AccuracyBar({ score, milestoneMessage, nextImprovement }: Props) {
  return (
    <div className="rounded-xl border border-[#E5E2DC] bg-white p-4">
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-sm text-gray-500">Profile completeness</span>
        <span className="text-sm font-semibold" style={{
          color: score < 25 ? "#FF8720" : score < 60 ? "#FF8DE4" : "#448CFD"
        }}>{score}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-gray-100">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${Math.min(score, 100)}%`,
            background: "linear-gradient(90deg, #448CFD, #FF8DE4)",
          }}
        />
      </div>
      <p className="mt-1.5 text-[11px] text-gray-400">{milestoneMessage}</p>
      {nextImprovement && (
        <p className="mt-0.5 text-[11px] text-brand-orange">
          Add {nextImprovement} to improve accuracy
        </p>
      )}
    </div>
  );
}
