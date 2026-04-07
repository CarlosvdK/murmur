"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { listBusinesses, listSimulations, listContacts } from "@/lib/api";

export default function AppHome() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [stats, setStats] = useState({ simulations: 0, customers: 0, vendors: 0, twins: 0 });

  useEffect(() => {
    listBusinesses()
      .then((businesses) => {
        if (businesses.length === 0) {
          router.replace("/onboarding");
        } else {
          setReady(true);
          // Fetch stats in parallel
          Promise.all([
            listSimulations().catch(() => []),
            listContacts({ contact_type: "customer" }).catch(() => []),
            listContacts({ contact_type: "vendor" }).catch(() => []),
          ]).then(([sims, customers, vendors]) => {
            setStats({
              simulations: sims.length,
              customers: customers.length,
              vendors: vendors.length,
              twins: [...customers, ...vendors].filter((c) => c.has_twin).length,
            });
          });
        }
      })
      .catch(() => {
        router.replace("/onboarding");
      });
  }, [router]);

  if (!ready) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="overflow-y-auto p-8 lg:p-12">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-1 text-3xl font-bold text-black">
          Welcome to Murmur
        </h1>
        <p className="mb-10 text-lg text-gray-500">
          What would you like to do?
        </p>

        {/* Stats bar */}
        <div className="mb-10 flex gap-8">
          {[
            [stats.simulations, "Simulations"],
            [stats.customers, "Customers"],
            [stats.vendors, "Vendors"],
            [stats.twins, "Active twins"],
          ].map(([val, label], i) => (
            <div key={label as string} className="flex items-center gap-8">
              <div>
                <p className="text-2xl font-bold text-black">{val}</p>
                <p className="text-xs text-gray-400">{label}</p>
              </div>
              {i < 3 && <div className="h-8 w-px bg-[#E5E2DC]" />}
            </div>
          ))}
        </div>

        {/* Feature cards -- full width grid */}
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {/* Simulate */}
          <a
            href="/app/simulate"
            className="group rounded-2xl border border-[#E5E2DC] bg-white p-6 transition-all hover:-translate-y-1 hover:border-brand-blue hover:shadow-lg"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-blue/10">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#448CFD" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 20V10" /><path d="M18 20V4" /><path d="M6 20v-4" />
              </svg>
            </div>
            <h3 className="mb-1 text-lg font-bold text-black">Simulate</h3>
            <p className="mb-4 text-sm leading-relaxed text-gray-500">
              Ask any question about your business and see how your customers
              would react. Get a verdict, breakdown, and recommendation.
            </p>
            <span className="flex items-center gap-1 text-sm font-medium text-brand-blue">
              Run a simulation <ArrowRight className="h-4 w-4" />
            </span>
          </a>

          {/* Customer Twins */}
          <a
            href="/app/customers"
            className="group rounded-2xl border border-[#E5E2DC] bg-white p-6 transition-all hover:-translate-y-1 hover:border-brand-orange hover:shadow-lg"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-orange/10">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF8720" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <h3 className="mb-1 text-lg font-bold text-black">Customer Twins</h3>
            <p className="mb-4 text-sm leading-relaxed text-gray-500">
              Build digital twins of your real customers from correspondence.
              Ask them anything about your relationship.
            </p>
            <span className="flex items-center gap-1 text-sm font-medium text-brand-orange">
              Manage customers <ArrowRight className="h-4 w-4" />
            </span>
          </a>

          {/* Vendor Twins */}
          <a
            href="/app/vendors"
            className="group rounded-2xl border border-[#E5E2DC] bg-white p-6 transition-all hover:-translate-y-1 hover:border-brand-pink hover:shadow-lg"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-pink/10">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF8DE4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect width="20" height="14" x="2" y="5" rx="2" /><line x1="2" x2="22" y1="10" y2="10" />
              </svg>
            </div>
            <h3 className="mb-1 text-lg font-bold text-black">Vendor Twins</h3>
            <p className="mb-4 text-sm leading-relaxed text-gray-500">
              Understand your suppliers and prepare for negotiations. Know
              how they will respond before you ask.
            </p>
            <span className="flex items-center gap-1 text-sm font-medium text-brand-pink">
              Manage vendors <ArrowRight className="h-4 w-4" />
            </span>
          </a>
        </div>

        {/* Recent activity section */}
        <div className="mt-12">
          <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">Recent activity</h2>
          <div className="rounded-xl border border-[#E5E2DC] bg-white p-8 text-center">
            <p className="text-sm text-gray-400">Run your first simulation to see activity here.</p>
            <a href="/app/simulate" className="mt-3 inline-block text-sm font-medium text-brand-blue hover:underline">
              Go to Simulate
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
