"use client";

import { useEffect, useState } from "react";

interface ImpactData {
  revenue: {
    point_estimate_pct: number;
    ci_low_pct: number;
    ci_high_pct: number;
    confidence_level: string;
  };
  customers_likely_stay: number;
  customers_likely_reduce: number;
  customers_likely_leave: number;
  total_customers_modelled: number;
  retention_rate_pct: number;
  decision: string;
  decision_reasoning: string;
  decision_framework: string;
  worst_case_summary: string;
  best_case_summary: string;
  most_likely_summary: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function ImpactPanel({ simulationId }: { simulationId: string }) {
  const [data, setData] = useState<ImpactData | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/simulations/${simulationId}/impact`)
      .then((r) => (r.ok ? r.json() : null))
      .then(setData)
      .catch(() => {});
  }, [simulationId]);

  if (!data) return null;

  const { revenue } = data;
  // Position the point estimate and zero line on the CI bar
  const barMin = Math.min(revenue.ci_low_pct, -2);
  const barMax = Math.max(revenue.ci_high_pct, 2);
  const barRange = barMax - barMin;
  const zeroPct = ((0 - barMin) / barRange) * 100;
  const pointPct = ((revenue.point_estimate_pct - barMin) / barRange) * 100;
  const ciLeftPct = ((revenue.ci_low_pct - barMin) / barRange) * 100;
  const ciWidthPct = ((revenue.ci_high_pct - revenue.ci_low_pct) / barRange) * 100;

  const isPositive = revenue.point_estimate_pct > 0;

  const decisionColors: Record<string, { bg: string; text: string; label: string }> = {
    proceed: { bg: "bg-green-50", text: "text-green-700", label: "Likely worth it" },
    caution: { bg: "bg-amber-50", text: "text-amber-700", label: "Proceed with caution" },
    avoid: { bg: "bg-red-50", text: "text-red-700", label: "Probably not worth it" },
    test_first: { bg: "bg-blue-50", text: "text-blue-700", label: "Test first" },
  };
  const dc = decisionColors[data.decision] || decisionColors.test_first;

  return (
    <div className="space-y-5">
      {/* Revenue Impact Card */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Estimated Revenue Impact</h3>
          <span className={`rounded-full px-3 py-1 text-xs font-medium ${dc.bg} ${dc.text}`}>
            {dc.label}
          </span>
        </div>

        {/* Big number */}
        <div className="mb-6 text-center">
          <p className="text-5xl font-black tracking-tight text-gray-900">
            {revenue.point_estimate_pct >= 0 ? "+" : ""}{revenue.point_estimate_pct}%
          </p>
          <p className="mt-1 text-sm text-gray-500">
            estimated revenue change
          </p>
        </div>

        {/* CI Visualization Bar */}
        <div className="mb-2">
          <div className="relative h-12 rounded-xl bg-gray-100">
            {/* Zero line */}
            <div
              className="absolute top-0 h-full w-px bg-gray-400"
              style={{ left: `${zeroPct}%` }}
            />
            <div
              className="absolute -top-5 text-[10px] text-gray-400"
              style={{ left: `${zeroPct}%`, transform: "translateX(-50%)" }}
            >
              0%
            </div>

            {/* CI range bar */}
            <div
              className="absolute top-2 h-8 rounded-lg"
              style={{
                left: `${ciLeftPct}%`,
                width: `${ciWidthPct}%`,
                background: "linear-gradient(90deg, rgba(239,68,68,0.15), rgba(209,213,219,0.2), rgba(34,197,94,0.15))",
                border: "1px solid rgba(0,0,0,0.08)",
              }}
            />

            {/* Point estimate marker */}
            <div
              className="absolute top-1 flex h-10 flex-col items-center"
              style={{ left: `${pointPct}%`, transform: "translateX(-50%)" }}
            >
              <div
                className={`h-8 w-1 rounded-full ${isPositive ? "bg-green-500" : "bg-red-500"}`}
              />
            </div>

            {/* CI low label */}
            <div
              className="absolute top-14 text-[10px] font-medium text-red-400"
              style={{ left: `${ciLeftPct}%`, transform: "translateX(-30%)" }}
            >
              {revenue.ci_low_pct >= 0 ? "+" : ""}{revenue.ci_low_pct}%
            </div>

            {/* Point estimate label */}
            <div
              className={`absolute top-14 text-xs font-bold ${isPositive ? "text-green-600" : "text-red-600"}`}
              style={{ left: `${pointPct}%`, transform: "translateX(-50%)" }}
            >
              {revenue.point_estimate_pct >= 0 ? "+" : ""}{revenue.point_estimate_pct}%
            </div>

            {/* CI high label */}
            <div
              className="absolute top-14 text-[10px] font-medium text-green-400"
              style={{ left: `${ciLeftPct + ciWidthPct}%`, transform: "translateX(-70%)" }}
            >
              +{revenue.ci_high_pct}%
            </div>
          </div>
        </div>

        {/* Labels */}
        <div className="mt-8 flex justify-between text-[10px] text-gray-400">
          <span>worst case</span>
          <span>best estimate</span>
          <span>best case</span>
        </div>

        {/* Decision framework explanation */}
        <div className="mt-5 rounded-xl bg-gray-50 p-4">
          <p className="text-sm leading-relaxed text-gray-600">
            {data.decision_framework}
          </p>
        </div>
      </div>

      {/* Customer Retention Card */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <h3 className="mb-4 text-sm font-semibold text-gray-900">Customer Impact</h3>

        <div className="mb-4 grid grid-cols-3 gap-3">
          <div className="rounded-xl bg-green-50 p-3 text-center">
            <p className="text-2xl font-bold text-green-700">{data.customers_likely_stay}</p>
            <p className="text-[10px] text-green-600">would stay</p>
          </div>
          <div className="rounded-xl bg-amber-50 p-3 text-center">
            <p className="text-2xl font-bold text-amber-700">{data.customers_likely_reduce}</p>
            <p className="text-[10px] text-amber-600">reduce visits</p>
          </div>
          <div className="rounded-xl bg-red-50 p-3 text-center">
            <p className="text-2xl font-bold text-red-700">{data.customers_likely_leave}</p>
            <p className="text-[10px] text-red-600">would leave</p>
          </div>
        </div>

        {/* Retention bar */}
        <div className="mb-2 h-3 overflow-hidden rounded-full bg-gray-100">
          <div className="flex h-full">
            <div
              className="bg-green-400"
              style={{ width: `${(data.customers_likely_stay / data.total_customers_modelled) * 100}%` }}
            />
            <div
              className="bg-amber-400"
              style={{ width: `${(data.customers_likely_reduce / data.total_customers_modelled) * 100}%` }}
            />
            <div
              className="bg-red-400"
              style={{ width: `${(data.customers_likely_leave / data.total_customers_modelled) * 100}%` }}
            />
          </div>
        </div>
        <p className="text-xs text-gray-400">
          {data.retention_rate_pct}% retention rate across {data.total_customers_modelled} simulated customers
        </p>
      </div>

      {/* Scenarios Card */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <h3 className="mb-4 text-sm font-semibold text-gray-900">Scenario Analysis</h3>
        <div className="space-y-3">
          <div className="rounded-xl bg-green-50 p-3">
            <p className="text-xs font-medium text-green-700">Best case</p>
            <p className="mt-1 text-sm text-green-600">{data.best_case_summary}</p>
          </div>
          <div className="rounded-xl bg-gray-50 p-3">
            <p className="text-xs font-medium text-gray-700">Most likely</p>
            <p className="mt-1 text-sm text-gray-600">{data.most_likely_summary}</p>
          </div>
          <div className="rounded-xl bg-red-50 p-3">
            <p className="text-xs font-medium text-red-700">Worst case</p>
            <p className="mt-1 text-sm text-red-600">{data.worst_case_summary}</p>
          </div>
        </div>

        {/* Decision */}
        <div className={`mt-4 rounded-xl ${dc.bg} p-4`}>
          <p className={`text-sm font-medium ${dc.text}`}>
            {data.decision_reasoning}
          </p>
        </div>
      </div>
    </div>
  );
}
