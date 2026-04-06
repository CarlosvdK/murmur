"use client";

import { useEffect, useState } from "react";
import { listContacts, createContact, CRMContact } from "@/lib/api";
import HealthBadge from "@/components/crm/HealthBadge";

export default function ContactsListPage() {
  const [contacts, setContacts] = useState<CRMContact[]>([]);
  const [showNew, setShowNew] = useState(false);
  const [newForm, setNewForm] = useState({ first_name: "", last_name: "", job_title: "", email: "", contact_type: "customer" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listContacts().then(setContacts).catch(() => {});
    if (window.location.search.includes("new=1")) setShowNew(true);
  }, []);

  const handleCreate = async () => {
    if (!newForm.first_name.trim()) return;
    setLoading(true);
    try {
      const c = await createContact(newForm);
      setContacts((prev) => [c, ...prev]);
      setShowNew(false);
      setNewForm({ first_name: "", last_name: "", job_title: "", email: "", contact_type: "customer" });
    } catch { /* ignore */ }
    setLoading(false);
  };

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-black">Contacts</h1>
          <p className="text-sm text-gray-500">{contacts.length} total</p>
        </div>
        <button
          onClick={() => setShowNew(!showNew)}
          className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-80"
        >
          Add contact
        </button>
      </div>

      {/* New contact form */}
      {showNew && (
        <div className="mb-6 rounded-xl border border-gray-200 bg-white p-6">
          <h3 className="mb-4 font-semibold text-black">New contact</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <input value={newForm.first_name} onChange={(e) => setNewForm({ ...newForm, first_name: e.target.value })} placeholder="First name *" className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
            <input value={newForm.last_name} onChange={(e) => setNewForm({ ...newForm, last_name: e.target.value })} placeholder="Last name" className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
            <input value={newForm.job_title} onChange={(e) => setNewForm({ ...newForm, job_title: e.target.value })} placeholder="Job title" className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
            <input value={newForm.email} onChange={(e) => setNewForm({ ...newForm, email: e.target.value })} placeholder="Email" className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
            <select value={newForm.contact_type} onChange={(e) => setNewForm({ ...newForm, contact_type: e.target.value })} className="rounded-lg border border-gray-200 px-3 py-2 text-sm">
              <option value="customer">Customer</option>
              <option value="vendor">Vendor</option>
              <option value="prospect">Prospect</option>
              <option value="partner">Partner</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="mt-4 flex gap-2">
            <button onClick={handleCreate} disabled={loading || !newForm.first_name.trim()} className="rounded-lg bg-black px-6 py-2 text-sm font-medium text-white disabled:opacity-40">
              {loading ? "Creating..." : "Create"}
            </button>
            <button onClick={() => setShowNew(false)} className="text-sm text-gray-400">Cancel</button>
          </div>
        </div>
      )}

      {/* Contacts list */}
      <div className="rounded-xl border border-gray-200 bg-white">
        {contacts.length === 0 ? (
          <div className="py-16 text-center">
            <p className="text-gray-400">No contacts yet. Add your first one above.</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
                <th className="px-5 py-3">Name</th>
                <th className="px-5 py-3">Title</th>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3">Health</th>
                <th className="px-5 py-3">Twin</th>
              </tr>
            </thead>
            <tbody>
              {contacts.map((c) => (
                <tr key={c.id} className="border-b border-gray-50 transition-colors hover:bg-gray-50">
                  <td className="px-5 py-3">
                    <a href={`/crm/contacts/${c.id}`} className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-blue text-xs font-bold text-white">
                        {c.first_name[0]}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-black">{c.full_name}</p>
                        {c.email && <p className="text-xs text-gray-400">{c.email}</p>}
                      </div>
                    </a>
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-500">{c.job_title || "--"}</td>
                  <td className="px-5 py-3">
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{c.contact_type}</span>
                  </td>
                  <td className="px-5 py-3">
                    <HealthBadge sentiment={c.current_sentiment} hasTwin={false} />
                  </td>
                  <td className="px-5 py-3">
                    {c.has_twin ? (
                      <span className="text-xs font-medium text-brand-blue">Active ({c.twin_corpus_size} msgs)</span>
                    ) : (
                      <span className="text-xs text-gray-300">None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
