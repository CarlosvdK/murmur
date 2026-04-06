"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getContact, askTwin, getTwinQueries, getContactSignals, CRMContact, TwinQuery, SignalAlert } from "@/lib/api";
import HealthBadge from "@/components/crm/HealthBadge";

export default function ContactProfilePage() {
  const params = useParams();
  const contactId = params.id as string;

  const [contact, setContact] = useState<CRMContact | null>(null);
  const [tab, setTab] = useState<"overview" | "twin" | "files">("overview");
  const [signals, setSignals] = useState<SignalAlert[]>([]);
  const [queries, setQueries] = useState<TwinQuery[]>([]);
  const [question, setQuestion] = useState("");
  const [askLoading, setAskLoading] = useState(false);

  useEffect(() => {
    if (!contactId) return;
    getContact(contactId).then(setContact).catch(() => {});
    getContactSignals(contactId).then((r) => setSignals(r.signals || [])).catch(() => {});
    getTwinQueries(contactId).then(setQueries).catch(() => {});
  }, [contactId]);

  const handleAskTwin = async () => {
    if (!question.trim() || !contactId) return;
    setAskLoading(true);
    try {
      const result = await askTwin(contactId, question.trim());
      setQueries((prev) => [result, ...prev]);
      setQuestion("");
    } catch { /* ignore */ }
    setAskLoading(false);
  };

  if (!contact) {
    return <div className="py-16 text-center text-gray-400">Loading...</div>;
  }

  return (
    <div className="mx-auto max-w-5xl">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-blue text-xl font-bold text-white">
            {contact.first_name[0]}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-black">{contact.full_name}</h1>
            <p className="text-gray-500">{contact.job_title || contact.contact_type}</p>
          </div>
        </div>
        <HealthBadge sentiment={contact.current_sentiment} hasTwin={contact.has_twin} />
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 border-b border-gray-200">
        {(["overview", "twin", "files"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              tab === t
                ? "border-b-2 border-black text-black"
                : "text-gray-400 hover:text-gray-600"
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {tab === "overview" && (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main content */}
          <div className="space-y-6 lg:col-span-2">
            {/* Signals */}
            {signals.length > 0 && (
              <div>
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Signals detected</h3>
                <div className="space-y-2">
                  {signals.map((s, i) => (
                    <div key={i} className={`rounded-xl border p-4 ${
                      s.severity === "warning" ? "border-amber-200 bg-amber-50" : "border-gray-200 bg-white"
                    }`}>
                      <p className="text-sm font-medium text-black">{s.title}</p>
                      <p className="mt-1 text-sm text-gray-500">{s.message}</p>
                      <p className="mt-2 text-xs text-gray-400">{s.recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Communication style (if twin exists) */}
            {contact.has_twin && contact.communication_style && (
              <div className="rounded-xl border border-gray-200 bg-white p-5">
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Communication style</h3>
                <p className="text-sm text-gray-600">
                  {contact.full_name}&apos;s communication style is <span className="font-medium text-black">{contact.communication_style}</span>.
                  Twin confidence: {contact.twin_confidence}. Based on {contact.twin_corpus_size} messages.
                </p>
              </div>
            )}

            {/* Quick ask */}
            {contact.has_twin && (
              <div className="rounded-xl border border-gray-200 bg-white p-5">
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Ask {contact.first_name}&apos;s twin</h3>
                <div className="flex gap-2">
                  <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAskTwin()}
                    placeholder={`How will ${contact.first_name} react to...`}
                    className="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none"
                  />
                  <button
                    onClick={handleAskTwin}
                    disabled={askLoading || !question.trim()}
                    className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
                  >
                    {askLoading ? "Asking..." : "Ask"}
                  </button>
                </div>
              </div>
            )}

            {!contact.has_twin && (
              <div className="rounded-xl border border-dashed border-gray-300 py-12 text-center">
                <p className="mb-2 text-gray-400">No twin data yet.</p>
                <p className="text-sm text-gray-400">Upload correspondence to build {contact.first_name}&apos;s digital twin.</p>
                <button
                  onClick={() => setTab("files")}
                  className="mt-4 rounded-lg bg-black px-4 py-2 text-sm font-medium text-white"
                >
                  Upload correspondence
                </button>
              </div>
            )}
          </div>

          {/* Right sidebar */}
          <div className="space-y-4">
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Contact info</h3>
              <div className="space-y-2 text-sm">
                {contact.email && <p className="text-gray-600">{contact.email}</p>}
                {contact.phone && <p className="text-gray-600">{contact.phone}</p>}
                {contact.city && <p className="text-gray-600">{contact.city}{contact.country ? `, ${contact.country}` : ""}</p>}
                <p className="text-gray-400">Type: {contact.contact_type}</p>
                {contact.role_label && <p className="text-gray-400">Role: {contact.role_label}</p>}
              </div>
            </div>

            {contact.has_twin && (
              <div className="rounded-xl border border-gray-200 bg-white p-5">
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Twin status</h3>
                <div className="space-y-1 text-sm">
                  <p className="text-gray-600">Active -- {contact.twin_corpus_size} messages processed</p>
                  <p className="text-gray-400">Confidence: {contact.twin_confidence}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Twin Tab */}
      {tab === "twin" && (
        <div className="space-y-6">
          {contact.has_twin ? (
            <>
              <div className="rounded-xl border border-gray-200 bg-white p-5">
                <p className="mb-4 text-sm text-gray-500">
                  {contact.full_name}&apos;s twin is based on {contact.twin_corpus_size} messages.
                  Confidence: {contact.twin_confidence}. This is a preparation tool, not a prediction.
                </p>
                <div className="flex gap-2">
                  <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAskTwin()}
                    placeholder="Ask anything about your relationship..."
                    className="flex-1 rounded-lg border border-gray-200 px-4 py-3 text-sm focus:border-brand-blue focus:outline-none"
                  />
                  <button
                    onClick={handleAskTwin}
                    disabled={askLoading || !question.trim()}
                    className="rounded-lg bg-black px-6 py-3 text-sm font-medium text-white disabled:opacity-40"
                  >
                    {askLoading ? "Thinking..." : "Ask twin"}
                  </button>
                </div>
              </div>

              {/* Previous queries */}
              {queries.length > 0 && (
                <div>
                  <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Previous queries</h3>
                  {queries.map((q) => (
                    <div key={q.id} className="mb-4 rounded-xl border border-gray-200 bg-white p-5">
                      <p className="mb-2 text-sm font-medium text-black">Q: {q.question}</p>
                      <p className="mb-3 text-sm leading-relaxed text-gray-600">{q.answer}</p>
                      <div className="flex flex-wrap gap-2">
                        <span className={`rounded-full px-2 py-0.5 text-xs ${
                          q.confidence === "high" ? "bg-green-50 text-green-600" :
                          q.confidence === "medium" ? "bg-amber-50 text-amber-600" :
                          "bg-gray-100 text-gray-500"
                        }`}>
                          Confidence: {q.confidence}
                        </span>
                        {q.caveats.map((c, i) => (
                          <span key={i} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{c}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="rounded-xl border border-dashed border-gray-300 py-16 text-center">
              <p className="text-gray-400">Upload correspondence to build this twin.</p>
            </div>
          )}
        </div>
      )}

      {/* Files Tab */}
      {tab === "files" && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h3 className="mb-4 font-semibold text-black">Upload correspondence</h3>
          <p className="mb-4 text-sm text-gray-500">
            Upload emails, WhatsApp exports, or call transcripts to build {contact.first_name}&apos;s digital twin.
          </p>

          <div className="rounded-xl border-2 border-dashed border-gray-200 p-12 text-center">
            <p className="mb-2 text-gray-400">Drop files here or click to browse</p>
            <p className="text-xs text-gray-300">Accepted: .txt .pdf .docx .mbox</p>
          </div>

          <div className="mt-4 rounded-lg bg-gray-50 p-4">
            <p className="text-xs font-medium text-gray-500">Privacy</p>
            <p className="mt-1 text-xs text-gray-400">
              Files are anonymised immediately on upload. Raw files are deleted within 60 seconds of processing.
              Only communication patterns are stored -- not message content.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
