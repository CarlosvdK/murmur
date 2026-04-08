"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  listContacts, askTwin, getContactSignals, getTwinQueries,
  CRMContact, TwinQuery, SignalAlert,
} from "@/lib/api";
import FileUploadZone from "@/components/forms/FileUploadZone";

const AVATAR_COLORS = ["#FF8720", "#448CFD", "#FF8DE4", "#ef4444", "#f59e0b", "#22c55e"];
function avatarColor(name: string) { return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]; }
function HealthDot({ sentiment }: { sentiment: string | null }) {
  const colors: Record<string, string> = { positive: "bg-green-500", neutral: "bg-gray-300", negative: "bg-amber-500", very_negative: "bg-red-500", unknown: "bg-gray-200" };
  return <div className={`h-2.5 w-2.5 rounded-full ${colors[sentiment || "unknown"] || colors.unknown}`} />;
}

export default function VendorsPage() {
  const router = useRouter();
  const [vendors, setVendors] = useState<CRMContact[]>([]);
  const [selected, setSelected] = useState<CRMContact | null>(null);
  const [signals, setSignals] = useState<SignalAlert[]>([]);
  const [queries, setQueries] = useState<TwinQuery[]>([]);
  const [twinQ, setTwinQ] = useState("");
  const [twinLoading, setTwinLoading] = useState(false);
  const [profileTab, setProfileTab] = useState<"activity" | "twin" | "files">("activity");
  const [search, setSearch] = useState("");

  useEffect(() => { listContacts({ contact_type: "vendor" }).then(setVendors).catch(() => {}); }, []);

  const filtered = vendors.filter((v) => {
    if (search && !v.full_name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const selectVendor = async (c: CRMContact) => {
    setSelected(c); setProfileTab("activity");
    getContactSignals(c.id).then((r) => setSignals(r.signals || [])).catch(() => setSignals([]));
    getTwinQueries(c.id).then(setQueries).catch(() => setQueries([]));
  };

  const handleAskTwin = async () => {
    if (!twinQ.trim() || !selected) return;
    setTwinLoading(true);
    try { const r = await askTwin(selected.id, twinQ.trim()); setQueries((p) => [r, ...p]); setTwinQ(""); } catch { /* */ }
    setTwinLoading(false);
  };

  return (
    <div className="flex h-full">
      <div className="flex-1 overflow-y-auto">
        <div className="sticky top-0 z-10 border-b border-[#E5E2DC] bg-white px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold text-black">Vendors</h2>
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{vendors.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search..."
                className="w-40 rounded-lg border border-[#E5E2DC] px-3 py-1.5 text-sm focus:border-brand-orange focus:outline-none" />
              <button onClick={() => router.push("/app/vendors/new")}
                className="rounded-lg bg-black px-4 py-1.5 text-sm font-medium text-white hover:opacity-80">+ New Twin</button>
            </div>
          </div>
        </div>

        <table className="w-full">
          <thead><tr className="border-b border-[#E5E2DC] text-left text-[11px] font-medium uppercase tracking-wider text-gray-400">
            <th className="px-6 py-2.5">Name</th><th className="px-4 py-2.5">Company</th>
            <th className="px-4 py-2.5">Role</th><th className="px-4 py-2.5">Health</th><th className="px-4 py-2.5">Confidence</th>
          </tr></thead>
          <tbody>
            {filtered.map((v) => (
              <tr key={v.id} onClick={() => selectVendor(v)}
                className={`cursor-pointer border-b border-gray-50 transition-colors ${selected?.id === v.id ? "bg-orange-50" : "hover:bg-gray-50"}`}>
                <td className="px-6 py-3"><div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white" style={{ background: avatarColor(v.first_name) }}>{v.first_name[0]}</div>
                  <span className="text-sm font-medium text-black">{v.full_name}</span>
                </div></td>
                <td className="px-4 py-3 text-sm text-gray-500">{v.organisation_name || "--"}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{v.job_title || "--"}</td>
                <td className="px-4 py-3"><HealthDot sentiment={v.current_sentiment} /></td>
                <td className="px-4 py-3"><span className={`text-xs font-medium ${v.twin_confidence === "high" ? "text-green-600" : v.twin_confidence === "medium" ? "text-brand-orange" : "text-gray-400"}`}>{v.twin_confidence || "low"}</span></td>
              </tr>
            ))}
          </tbody>
        </table>

        {vendors.length === 0 && (
          <div className="py-20 text-center">
            <p className="text-lg font-semibold text-black">No vendors yet.</p>
            <p className="mt-1 text-sm text-gray-500">Start building your vendor intelligence.</p>
            <p className="mx-auto mt-3 max-w-md text-xs text-gray-400">
              The more you know about each vendor, the better Murmur can predict how they&apos;ll respond to negotiations.
            </p>
            <button onClick={() => router.push("/app/vendors/new")}
              className="mt-4 rounded-lg bg-black px-6 py-2 text-sm font-medium text-white hover:opacity-80">+ Create your first vendor twin</button>
          </div>
        )}
      </div>

      {selected && (
        <div className="flex w-[520px] shrink-0 flex-col overflow-hidden border-l border-[#E5E2DC] bg-white">
          <div className="border-b border-[#E5E2DC] p-5">
            <button onClick={() => setSelected(null)} className="text-xs text-gray-400 hover:text-black">Close</button>
            <div className="mt-3 flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full text-lg font-bold text-white" style={{ background: avatarColor(selected.first_name) }}>{selected.first_name[0]}</div>
              <div>
                <h3 className="text-lg font-bold text-black">{selected.full_name}</h3>
                <p className="text-sm text-gray-500">{selected.job_title || "Vendor"}{selected.organisation_name ? ` at ${selected.organisation_name}` : ""}</p>
              </div>
            </div>
            <div className="mt-4 flex gap-1.5">
              {["Email", "Call", "Note"].map((a) => (
                <button key={a} className="rounded-lg border border-[#E5E2DC] px-3 py-1.5 text-xs text-gray-500 hover:bg-gray-50">{a}</button>
              ))}
              <button onClick={() => setProfileTab("twin")} className="rounded-lg border border-brand-orange bg-brand-orange/5 px-3 py-1.5 text-xs font-medium text-brand-orange">Ask Twin</button>
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
                  <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">About this vendor</h4>
                  <div className="space-y-2 text-sm">
                    {[["Email", selected.email], ["Phone", selected.phone], ["LinkedIn", selected.linkedin_url],
                      ["Company", selected.organisation_name], ["Location", [selected.city, selected.country].filter(Boolean).join(", ") || null],
                      ["Style", selected.communication_style]].map(([l, v]) => (
                      <div key={l} className="flex justify-between"><span className="text-gray-400">{l}</span><span className="text-black">{v || "--"}</span></div>
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
                <div className="rounded-lg bg-gray-50 p-3 text-sm text-gray-600">
                  Twin confidence: <span className={`font-medium ${selected.twin_confidence === "high" ? "text-green-600" : selected.twin_confidence === "medium" ? "text-brand-orange" : "text-gray-400"}`}>{selected.twin_confidence || "low"}</span>
                  <span className="ml-2 text-xs text-gray-400">Add more profile data to improve accuracy</span>
                </div>
                <div className="flex gap-2">
                  <input value={twinQ} onChange={(e) => setTwinQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleAskTwin()}
                    placeholder={`Ask how ${selected.first_name} would react to...`}
                    className="flex-1 rounded-lg border border-[#E5E2DC] px-3 py-2 text-sm focus:border-brand-orange focus:outline-none" />
                  <button onClick={handleAskTwin} disabled={twinLoading || !twinQ.trim()}
                    className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-30">{twinLoading ? "..." : "Ask"}</button>
                </div>
                {queries.map((q) => (
                  <div key={q.id} className="rounded-lg border border-[#E5E2DC] p-4">
                    <p className="mb-2 text-sm font-medium text-black">Q: {q.question}</p>
                    <p className="text-sm text-gray-600">{q.answer}</p>
                    <p className="mt-2 text-xs text-gray-400">Confidence: {q.confidence}</p>
                  </div>
                ))}
              </div>
            )}

            {profileTab === "files" && (
              <FileUploadZone contactId={selected.id} contactType="vendor" contactName={selected.first_name}
                onUploadComplete={() => listContacts({ contact_type: "vendor" }).then(setVendors)} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
