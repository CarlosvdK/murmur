"use client";

import { useEffect, useState } from "react";
import { listContacts, CRMContact } from "@/lib/api";

function HealthBar({ label, count, total, color }: { label: string; count: number; total: number; color: string }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div className="flex items-center gap-3">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-gray-100">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-20 text-right text-sm text-gray-600">{label}</span>
      <span className="w-8 text-right text-sm font-medium text-black">{count}</span>
    </div>
  );
}

export default function IntelligencePage() {
  const [contacts, setContacts] = useState<CRMContact[]>([]);

  useEffect(() => {
    listContacts().then(setContacts).catch(() => {});
  }, []);

  const customers = contacts.filter((c) => c.contact_type === "customer");
  const vendors = contacts.filter((c) => c.contact_type === "vendor");
  const withTwin = contacts.filter((c) => c.has_twin);
  const atRisk = contacts.filter((c) => c.current_sentiment === "negative" || c.current_sentiment === "very_negative");
  const strong = contacts.filter((c) => c.current_sentiment === "positive" || c.current_sentiment === "very_positive");
  const neutral = contacts.filter((c) => !c.current_sentiment || c.current_sentiment === "neutral" || c.current_sentiment === "unknown");

  return (
    <div className="overflow-y-auto p-8">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-2 text-2xl font-bold text-black">Intelligence</h1>
        <p className="mb-8 text-gray-500">Signals, health overview, and relationship insights.</p>

        <div className="grid gap-6 lg:grid-cols-5">
          <div className="space-y-4 lg:col-span-3">
            <div>
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Needs attention</h3>
              {atRisk.length > 0 ? (
                <div className="space-y-2">
                  {atRisk.map((c) => (
                    <a key={c.id} href={`/app/${c.contact_type === "vendor" ? "vendors" : "customers"}`} className="block rounded-xl border border-amber-200 bg-amber-50 p-4 hover:border-amber-300">
                      <p className="font-medium text-black">{c.full_name}</p>
                      <p className="text-sm text-gray-500">{c.job_title || c.contact_type}</p>
                    </a>
                  ))}
                </div>
              ) : (
                <div className="rounded-xl border border-[#E5E2DC] bg-white p-6 text-center">
                  <p className="text-sm text-gray-400">No signals requiring attention.</p>
                </div>
              )}
            </div>

            <div>
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Overview</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
                  <p className="text-3xl font-bold text-black">{customers.length}</p>
                  <p className="mt-1 text-sm text-gray-500">Customers</p>
                </div>
                <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
                  <p className="text-3xl font-bold text-black">{vendors.length}</p>
                  <p className="mt-1 text-sm text-gray-500">Vendors</p>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4 lg:col-span-2">
            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">Portfolio health</h3>
              <div className="space-y-3">
                <HealthBar label="Strong" count={strong.length} total={contacts.length} color="bg-green-400" />
                <HealthBar label="Neutral" count={neutral.length} total={contacts.length} color="bg-gray-300" />
                <HealthBar label="At risk" count={atRisk.length} total={contacts.length} color="bg-red-400" />
              </div>
            </div>

            <div className="rounded-xl border border-[#E5E2DC] bg-white p-5">
              <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">Quick stats</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-gray-500">Total contacts</span><span className="font-medium text-black">{contacts.length}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Active twins</span><span className="font-medium text-black">{withTwin.length}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">Flagged</span><span className="font-medium text-black">{atRisk.length}</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
