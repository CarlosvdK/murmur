"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  listContacts,
  askTwin,
  getContactSignals,
  getTwinQueries,
  CRMContact,
  TwinQuery,
  SignalAlert,
} from "@/lib/api";
import FileUploadZone from "@/components/forms/FileUploadZone";

const AVATAR_COLORS = ["#448CFD", "#FF8720", "#FF8DE4", "#22c55e", "#f59e0b", "#ef4444"];
function avatarColor(name: string) { return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]; }

function HealthDot({ sentiment }: { sentiment: string | null }) {
  const colors: Record<string, string> = {
    positive: "bg-green-500", very_positive: "bg-green-500",
    neutral: "bg-gray-300", negative: "bg-amber-500",
    very_negative: "bg-red-500", unknown: "bg-gray-200",
  };
  return <div className={`h-2.5 w-2.5 rounded-full ${colors[sentiment || "unknown"] || colors.unknown}`} />;
}

type Filter = "all" | "has_twin" | "no_twin";

export default function CustomersPage() {
  const router = useRouter();
  const [contacts, setContacts] = useState<CRMContact[]>([]);
  const [selected, setSelected] = useState<CRMContact | null>(null);
  const [signals, setSignals] = useState<SignalAlert[]>([]);
  const [queries, setQueries] = useState<TwinQuery[]>([]);
  const [twinQ, setTwinQ] = useState("");
  const [twinLoading, setTwinLoading] = useState(false);
  const [profileTab, setProfileTab] = useState<"activity" | "twin" | "files">("activity");
  const [filter, setFilter] = useState<Filter>("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    listContacts({ contact_type: "customer" }).then(setContacts).catch(() => {});
  }, []);

  const filtered = contacts.filter((c) => {
    if (filter === "has_twin" && !c.has_twin) return false;
    if (filter === "no_twin" && c.has_twin) return false;
    if (search && !c.full_name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const selectContact = async (c: CRMContact) => {
    setSelected(c);
    setProfileTab("activity");
    getContactSignals(c.id).then((r) => setSignals(r.signals || [])).catch(() => setSignals([]));
    getTwinQueries(c.id).then(setQueries).catch(() => setQueries([]));
  };

  const handleAskTwin = async () => {
    if (!twinQ.trim() || !selected) return;
    setTwinLoading(true);
    try {
      const result = await askTwin(selected.id, twinQ.trim());
      setQueries((prev) => [result, ...prev]);
      setTwinQ("");
    } catch { /* */ }
    setTwinLoading(false);
  };

  return (
    <div className="flex h-full">
      {/* LEFT: Contact table */}
      <div className="flex-1 overflow-y-auto">
        <div className="sticky top-0 z-10 border-b border-[#E5E2DC] bg-white px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold text-black">Customers</h2>
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{contacts.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search..."
                className="w-40 rounded-lg border border-[#E5E2DC] px-3 py-1.5 text-sm focus:border-brand-blue focus:outline-none" />
              <button onClick={() => router.push("/app/customers/new")}
                className="rounded-lg bg-black px-4 py-1.5 text-sm font-medium text-white hover:opacity-80">
                + Add customer
              </button>
            </div>
          </div>
          <div className="mt-2 flex gap-1.5">
            {([["all", "All"], ["has_twin", "Has Twin"], ["no_twin", "No Twin"]] as [Filter, string][]).map(([key, label]) => (
              <button key={key} onClick={() => setFilter(key)}
                className={`rounded-lg px-3 py-1 text-xs ${filter === key ? "bg-black text-white" : "text-gray-400 hover:bg-gray-100"}`}>
                {label}
              </button>
            ))}
          </div>
        </div>

        <table className="w-full">
          <thead>
            <tr className="border-b border-[#E5E2DC] text-left text-[11px] font-medium uppercase tracking-wider text-gray-400">
              <th className="px-6 py-2.5">Name</th>
              <th className="px-4 py-2.5">Title</th>
              <th className="px-4 py-2.5">Email</th>
              <th className="px-4 py-2.5">Health</th>
              <th className="px-4 py-2.5">Twin</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => (
              <tr key={c.id} onClick={() => selectContact(c)}
                className={`cursor-pointer border-b border-gray-50 transition-colors ${selected?.id === c.id ? "bg-blue-50" : "hover:bg-gray-50"}`}>
                <td className="px-6 py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white" style={{ background: avatarColor(c.first_name) }}>
                      {c.first_name[0]}{c.last_name?.[0] || ""}
                    </div>
                    <span className="text-sm font-medium text-black">{c.full_name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{c.job_title || "--"}</td>
                <td className="px-4 py-3 text-sm text-gray-400">{c.email || "--"}</td>
                <td className="px-4 py-3"><HealthDot sentiment={c.current_sentiment} /></td>
                <td className="px-4 py-3">
                  {c.has_twin ? <span className="text-xs font-medium text-brand-blue">{c.twin_corpus_size} msgs</span> : <span className="text-xs text-gray-300">--</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {contacts.length === 0 && (
          <div className="py-20 text-center">
            <p className="text-lg font-semibold text-black">No customers yet.</p>
            <p className="mt-1 text-sm text-gray-500">Start building your customer intelligence.</p>
            <p className="mx-auto mt-3 max-w-md text-xs text-gray-400">
              The more you know about each customer, the more accurately Murmur can predict how they&apos;ll react to any change you make.
            </p>
            <button onClick={() => router.push("/app/customers/new")}
              className="mt-4 rounded-lg bg-black px-6 py-2 text-sm font-medium text-white hover:opacity-80">
              + Add your first customer
            </button>
          </div>
        )}
      </div>

      {/* RIGHT: Profile panel */}
      {selected && (
        <div className="flex w-[520px] shrink-0 flex-col overflow-hidden border-l border-[#E5E2DC] bg-white">
          <div className="border-b border-[#E5E2DC] p-5">
            <button onClick={() => setSelected(null)} className="text-xs text-gray-400 hover:text-black">Close</button>
            <div className="mt-3 flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full text-lg font-bold text-white" style={{ background: avatarColor(selected.first_name) }}>
                {selected.first_name[0]}{selected.last_name?.[0] || ""}
              </div>
              <div>
                <h3 className="text-lg font-bold text-black">{selected.full_name}</h3>
                <p className="text-sm text-gray-500">{selected.job_title || "Customer"}</p>
              </div>
            </div>
            <div className="mt-4 flex gap-1.5">
              {["Email", "Call", "Note", "Task"].map((a) => (
                <button key={a} className="rounded-lg border border-[#E5E2DC] px-3 py-1.5 text-xs text-gray-500 hover:bg-gray-50">{a}</button>
              ))}
              <button onClick={() => setProfileTab("twin")} className="rounded-lg border border-brand-blue bg-brand-blue/5 px-3 py-1.5 text-xs font-medium text-brand-blue">Ask Twin</button>
            </div>
          </div>

          <div className="flex border-b border-[#E5E2DC]">
            {(["activity", "twin", "files"] as const).map((t) => (
              <button key={t} onClick={() => setProfileTab(t)} className={`flex-1 py-2 text-center text-sm font-medium ${profileTab === t ? "border-b-2 border-brand-orange text-black" : "text-gray-400"}`}>
                {t === "activity" ? "Activity" : t === "twin" ? "Twin" : "Files"}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-5">
            {profileTab === "activity" && (
              <div className="space-y-4">
                <div>
                  <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">About this contact</h4>
                  <div className="space-y-2 text-sm">
                    {[
                      ["Email", selected.email], ["Phone / WhatsApp", selected.phone],
                      ["LinkedIn", selected.linkedin_url],
                      ["Location", [selected.city, selected.country].filter(Boolean).join(", ") || null],
                      ["Type", selected.contact_type], ["Style", selected.communication_style],
                    ].map(([label, val]) => (
                      <div key={label} className="flex justify-between">
                        <span className="text-gray-400">{label}</span>
                        <span className="text-black">{val || "--"}</span>
                      </div>
                    ))}
                  </div>
                </div>
                {signals.length > 0 && (
                  <div>
                    <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">Signals</h4>
                    {signals.map((s, i) => (
                      <div key={i} className={`mb-2 rounded-lg border p-3 ${s.severity === "warning" ? "border-amber-200 bg-amber-50" : "border-[#E5E2DC]"}`}>
                        <p className="text-sm font-medium text-black">{s.title}</p>
                        <p className="mt-1 text-xs text-gray-500">{s.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {profileTab === "twin" && (
              <div className="space-y-4">
                {selected.has_twin ? (
                  <>
                    <div className="rounded-lg bg-gray-50 p-3 text-sm text-gray-600">
                      {selected.twin_corpus_size} messages -- Confidence: {selected.twin_confidence || "N/A"}
                    </div>
                    <div className="flex gap-2">
                      <input value={twinQ} onChange={(e) => setTwinQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleAskTwin()}
                        placeholder={`Ask about ${selected.first_name}...`}
                        className="flex-1 rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
                      <button onClick={handleAskTwin} disabled={twinLoading || !twinQ.trim()}
                        className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-30">
                        {twinLoading ? "..." : "Ask"}
                      </button>
                    </div>
                    {queries.map((q) => (
                      <div key={q.id} className="rounded-lg border border-[#E5E2DC] p-4">
                        <p className="mb-2 text-sm font-medium text-black">Q: {q.question}</p>
                        <p className="text-sm text-gray-600">{q.answer}</p>
                        <p className="mt-2 text-xs text-gray-400">Confidence: {q.confidence}</p>
                      </div>
                    ))}
                  </>
                ) : (
                  <div className="py-8 text-center">
                    <p className="text-gray-400">No twin yet. Upload correspondence first.</p>
                    <button onClick={() => setProfileTab("files")} className="mt-3 rounded-lg bg-black px-4 py-2 text-sm font-medium text-white">Upload files</button>
                  </div>
                )}
              </div>
            )}

            {profileTab === "files" && (
              <FileUploadZone
                contactId={selected.id}
                contactType="customer"
                contactName={selected.first_name}
                onUploadComplete={() => listContacts({ contact_type: "customer" }).then(setContacts)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
