"use client";

import { useEffect, useState } from "react";
import { listContacts, CRMContact } from "@/lib/api";
import HealthBadge from "@/components/crm/HealthBadge";

export default function CRMHome() {
  const [contacts, setContacts] = useState<CRMContact[]>([]);

  useEffect(() => {
    listContacts().then(setContacts).catch(() => {});
  }, []);

  const withTwins = contacts.filter((c) => c.has_twin);
  const flagged = contacts.filter(
    (c) => c.current_sentiment === "negative" || c.current_sentiment === "very_negative"
  );

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="mb-2 text-2xl font-bold text-black">Relationships</h1>
      <p className="mb-8 text-gray-500">Your relationship intelligence overview.</p>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Left: feed */}
        <div className="space-y-4 lg:col-span-3">
          {flagged.length > 0 && (
            <div>
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
                Needs attention
              </h3>
              {flagged.map((c) => (
                <a
                  key={c.id}
                  href={`/crm/contacts/${c.id}`}
                  className="mb-2 block rounded-xl border border-amber-200 bg-amber-50 p-4 transition-colors hover:border-amber-300"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-black">{c.full_name}</p>
                      <p className="text-sm text-gray-500">
                        {c.job_title}{c.organisation_name ? ` at ${c.organisation_name}` : ""}
                      </p>
                    </div>
                    <HealthBadge sentiment={c.current_sentiment} hasTwin={c.has_twin} />
                  </div>
                </a>
              ))}
            </div>
          )}

          {contacts.length > 0 ? (
            <div>
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
                Recent contacts
              </h3>
              {contacts.slice(0, 8).map((c) => (
                <a
                  key={c.id}
                  href={`/crm/contacts/${c.id}`}
                  className="mb-2 flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 transition-colors hover:border-gray-300"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-blue text-sm font-bold text-white">
                      {c.first_name[0]}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-black">{c.full_name}</p>
                      <p className="text-xs text-gray-400">{c.contact_type}</p>
                    </div>
                  </div>
                  <HealthBadge sentiment={c.current_sentiment} hasTwin={c.has_twin} />
                </a>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-gray-300 py-16 text-center">
              <p className="text-gray-400">No contacts yet.</p>
              <a href="/crm/contacts?new=1" className="mt-2 inline-block text-sm font-medium text-brand-blue">
                Add your first contact
              </a>
            </div>
          )}
        </div>

        {/* Right: stats */}
        <div className="space-y-4 lg:col-span-2">
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
              Your relationships
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Contacts</span>
                <span className="font-medium text-black">{contacts.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">With active twins</span>
                <span className="font-medium text-black">{withTwins.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Flagged signals</span>
                <span className="font-medium text-black">{flagged.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
