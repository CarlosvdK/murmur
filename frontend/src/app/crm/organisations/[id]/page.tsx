"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getOrganisation, listContacts, CRMOrganisation, CRMContact } from "@/lib/api";
import HealthBadge from "@/components/crm/HealthBadge";

export default function OrganisationProfilePage() {
  const params = useParams();
  const orgId = params.id as string;

  const [org, setOrg] = useState<CRMOrganisation | null>(null);
  const [contacts, setContacts] = useState<CRMContact[]>([]);

  useEffect(() => {
    if (!orgId) return;
    getOrganisation(orgId).then(setOrg).catch(() => {});
    // Get contacts linked to this org
    listContacts().then((all) => {
      setContacts(all.filter((c) => c.organisation_id === orgId));
    }).catch(() => {});
  }, [orgId]);

  if (!org) return <div className="py-16 text-center text-gray-400">Loading...</div>;

  return (
    <div className="mx-auto max-w-5xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-orange text-lg font-bold text-white">
            {org.name[0]}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-black">{org.name}</h1>
            <p className="text-gray-500">{org.organisation_type} -- {org.city}{org.country ? `, ${org.country}` : ""}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* People */}
        <div className="lg:col-span-2">
          <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">People at {org.name}</h3>
          {contacts.length > 0 ? (
            <div className="rounded-xl border border-gray-200 bg-white">
              {contacts.map((c) => (
                <a key={c.id} href={`/crm/contacts/${c.id}`} className="flex items-center justify-between border-b border-gray-50 px-5 py-4 last:border-0 hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-blue text-xs font-bold text-white">{c.first_name[0]}</div>
                    <div>
                      <p className="text-sm font-medium text-black">{c.full_name}</p>
                      <p className="text-xs text-gray-400">{c.role_label || c.job_title || c.contact_type}</p>
                    </div>
                  </div>
                  <HealthBadge sentiment={c.current_sentiment} hasTwin={c.has_twin} />
                </a>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-gray-300 py-12 text-center">
              <p className="text-gray-400">No contacts linked to this organisation yet.</p>
              <a href="/crm/contacts?new=1" className="mt-2 inline-block text-sm font-medium text-brand-blue">Add a contact</a>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Details</h3>
            <div className="space-y-2 text-sm">
              <p className="text-gray-600">Type: {org.organisation_type}</p>
              {org.industry && <p className="text-gray-600">Industry: {org.industry}</p>}
              {org.size_category && <p className="text-gray-600">Size: {org.size_category}</p>}
              <p className="text-gray-400">Status: {org.relationship_status}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
