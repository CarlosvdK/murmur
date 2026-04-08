"use client";

import { useEffect, useState } from "react";
import { listSimulations, listContacts, getAccuracyStats, Simulation } from "@/lib/api";

export default function ReportsPage() {
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [tab, setTab] = useState<"history" | "accuracy" | "usage">("history");
  const [customerCount, setCustomerCount] = useState(0);
  const [vendorCount, setVendorCount] = useState(0);
  const [twinCount, setTwinCount] = useState(0);
  const [accuracy, setAccuracy] = useState<{ total_outcomes: number; matched: number; accuracy_pct: number | null }>({ total_outcomes: 0, matched: 0, accuracy_pct: null });

  useEffect(() => {
    listSimulations().then(setSimulations).catch(() => {});
    listContacts({ contact_type: "customer" }).then((c) => {
      setCustomerCount(c.length);
      setTwinCount((prev) => prev + c.filter((x) => x.has_twin).length);
    }).catch(() => {});
    listContacts({ contact_type: "vendor" }).then((v) => {
      setVendorCount(v.length);
      setTwinCount((prev) => prev + v.filter((x) => x.has_twin).length);
    }).catch(() => {});
    getAccuracyStats().then(setAccuracy).catch(() => {});
  }, []);

  const completed = simulations.filter((s) => s.status === "completed");

  return (
    <div className="overflow-y-auto p-8">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-2 text-2xl font-bold text-black">Reports</h1>
        <p className="mb-6 text-gray-500">Simulation history, accuracy tracking, and usage.</p>

        <div className="mb-6 flex gap-1 border-b border-[#E5E2DC]">
          {(["history", "accuracy", "usage"] as const).map((t) => (
            <button key={t} onClick={() => setTab(t)} className={`px-5 py-2.5 text-sm font-medium ${tab === t ? "border-b-2 border-brand-orange text-black" : "text-gray-400"}`}>
              {t === "history" ? "Simulation History" : t === "accuracy" ? "Accuracy" : "Usage"}
            </button>
          ))}
        </div>

        {tab === "history" && (
          <div className="rounded-xl border border-[#E5E2DC] bg-white">
            {completed.length === 0 ? (
              <div className="py-16 text-center"><p className="text-gray-400">No simulations yet.</p></div>
            ) : (
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#E5E2DC] text-left text-[11px] font-medium uppercase tracking-wider text-gray-400">
                    <th className="px-6 py-3">Question</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3">Personas</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {completed.map((s) => (
                    <tr key={s.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="px-6 py-3 text-sm text-black">{s.question.slice(0, 60)}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{new Date(s.created_at).toLocaleDateString()}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{s.persona_count}</td>
                      <td className="px-4 py-3"><span className="rounded-full bg-green-50 px-2 py-0.5 text-xs text-green-600">Complete</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {tab === "accuracy" && (
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-6">
              <p className="text-4xl font-bold text-black">{accuracy.accuracy_pct !== null ? `${accuracy.accuracy_pct}%` : "--"}</p>
              <p className="mt-1 text-sm text-gray-500">Prediction accuracy</p>
              {accuracy.total_outcomes === 0 && <p className="mt-1 text-xs text-gray-400">Report real outcomes to start tracking</p>}
            </div>
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-6">
              <p className="text-4xl font-bold text-black">{accuracy.total_outcomes}</p>
              <p className="mt-1 text-sm text-gray-500">Validated predictions</p>
            </div>
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-6">
              <p className="text-4xl font-bold text-black">{completed.length}</p>
              <p className="mt-1 text-sm text-gray-500">Total simulations</p>
            </div>
          </div>
        )}

        {tab === "usage" && (
          <div className="grid gap-4 sm:grid-cols-4">
            {[
              [simulations.length, "Simulations"],
              [customerCount, "Customers"],
              [vendorCount, "Vendors"],
              [twinCount, "Active twins"],
            ].map(([val, label]) => (
              <div key={label as string} className="rounded-xl border border-[#E5E2DC] bg-white p-5">
                <p className="text-3xl font-bold text-black">{val}</p>
                <p className="mt-1 text-sm text-gray-500">{label}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
