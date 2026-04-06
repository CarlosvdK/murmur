"use client";

import { useEffect, useState } from "react";
import { listOrganisations, createOrganisation, CRMOrganisation } from "@/lib/api";

export default function OrganisationsListPage() {
  const [orgs, setOrgs] = useState<CRMOrganisation[]>([]);
  const [showNew, setShowNew] = useState(false);
  const [newForm, setNewForm] = useState({ name: "", organisation_type: "customer", industry: "", city: "", country: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listOrganisations().then(setOrgs).catch(() => {});
    if (window.location.search.includes("new=1")) setShowNew(true);
  }, []);

  const handleCreate = async () => {
    if (!newForm.name.trim()) return;
    setLoading(true);
    try {
      const org = await createOrganisation(newForm);
      setOrgs((prev) => [org, ...prev]);
      setShowNew(false);
      setNewForm({ name: "", organisation_type: "customer", industry: "", city: "", country: "" });
    } catch { /* ignore */ }
    setLoading(false);
  };

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-black">Organisations</h1>
          <p className="text-sm text-gray-500">{orgs.length} total</p>
        </div>
        <button onClick={() => setShowNew(!showNew)} className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-80">
          Add organisation
        </button>
      </div>

      {showNew && (
        <div className="mb-6 rounded-xl border border-gray-200 bg-white p-6">
          <h3 className="mb-4 font-semibold text-black">New organisation</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <input value={newForm.name} onChange={(e) => setNewForm({ ...newForm, name: e.target.value })} placeholder="Organisation name *" className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
            <select value={newForm.organisation_type} onChange={(e) => setNewForm({ ...newForm, organisation_type: e.target.value })} className="rounded-lg border border-gray-200 px-3 py-2 text-sm">
              <option value="customer">Customer</option>
              <option value="vendor">Vendor</option>
              <option value="prospect">Prospect</option>
              <option value="partner">Partner</option>
            </select>
            <input value={newForm.city} onChange={(e) => setNewForm({ ...newForm, city: e.target.value })} placeholder="City" className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
            <input value={newForm.country} onChange={(e) => setNewForm({ ...newForm, country: e.target.value })} placeholder="Country" className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
          </div>
          <div className="mt-4 flex gap-2">
            <button onClick={handleCreate} disabled={loading || !newForm.name.trim()} className="rounded-lg bg-black px-6 py-2 text-sm font-medium text-white disabled:opacity-40">{loading ? "Creating..." : "Create"}</button>
            <button onClick={() => setShowNew(false)} className="text-sm text-gray-400">Cancel</button>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-gray-200 bg-white">
        {orgs.length === 0 ? (
          <div className="py-16 text-center"><p className="text-gray-400">No organisations yet.</p></div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
                <th className="px-5 py-3">Name</th>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3">Location</th>
                <th className="px-5 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {orgs.map((o) => (
                <tr key={o.id} className="border-b border-gray-50 transition-colors hover:bg-gray-50">
                  <td className="px-5 py-3">
                    <a href={`/crm/organisations/${o.id}`} className="text-sm font-medium text-black hover:text-brand-blue">{o.name}</a>
                  </td>
                  <td className="px-5 py-3"><span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{o.organisation_type}</span></td>
                  <td className="px-5 py-3 text-sm text-gray-500">{o.city}{o.country ? `, ${o.country}` : ""}</td>
                  <td className="px-5 py-3"><span className="text-xs text-gray-400">{o.relationship_status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
