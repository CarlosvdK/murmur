"use client";

import { useState } from "react";

interface UploadSource {
  icon: string;
  label: string;
  description: string;
  formats: string;
  sourceType: string;
}

const CUSTOMER_SOURCES: UploadSource[] = [
  { icon: "msg", label: "WhatsApp conversation export", description: "Open chat > ... > More > Export Chat > Without Media", formats: ".txt", sourceType: "whatsapp" },
  { icon: "mail", label: "Email thread export", description: "In Gmail: select emails > ... > Download message", formats: ".eml .mbox .txt", sourceType: "email" },
  { icon: "mic", label: "Call or meeting transcript", description: "Any transcript tool (Otter, Rev, etc.)", formats: ".txt .pdf .docx", sourceType: "meeting_notes" },
  { icon: "note", label: "Your own notes about conversations", description: "Anything you've written down about them", formats: ".txt .pdf .docx", sourceType: "notes" },
  { icon: "chart", label: "Purchase or order history", description: "Export from your POS or booking system", formats: ".csv .xlsx", sourceType: "purchase_history" },
];

const VENDOR_SOURCES: UploadSource[] = [
  { icon: "msg", label: "WhatsApp conversations", description: "Export: Open chat > ... > More > Export Chat > Without Media", formats: ".txt", sourceType: "whatsapp" },
  { icon: "mail", label: "Email threads", description: "Negotiations, quotes, complaints, day-to-day orders", formats: ".eml .mbox .txt", sourceType: "email" },
  { icon: "doc", label: "Contracts and quotes", description: "Any contract, quote, proposal, or offer", formats: ".pdf .docx .txt", sourceType: "contract" },
  { icon: "chart", label: "Order and invoice history", description: "We extract: price history, payment terms, volume trends", formats: ".csv .xlsx", sourceType: "invoice_history" },
  { icon: "note", label: "Your notes from meetings or calls", description: "Any notes about conversations with this vendor", formats: ".txt .pdf .docx", sourceType: "meeting_notes" },
];

interface Props {
  contactId: string;
  contactType: "customer" | "vendor";
  contactName: string;
  onUploadComplete?: () => void;
}

export default function FileUploadZone({ contactId, contactType, contactName, onUploadComplete }: Props) {
  const [uploading, setUploading] = useState<string | null>(null);
  const [result, setResult] = useState<{ count: number; confidence: string } | null>(null);

  const sources = contactType === "vendor" ? VENDOR_SOURCES : CUSTOMER_SOURCES;

  const handleUpload = async (file: File, sourceType: string) => {
    setUploading(sourceType);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("source_type", sourceType);
      formData.append("confirm_rights", "true");
      const headers: Record<string, string> = {};
      const { createClient } = await import("@/lib/supabase/client");
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) headers["Authorization"] = `Bearer ${session.access_token}`;
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api"}/crm/twin/upload/${contactId}`,
        { method: "POST", headers, body: formData }
      );
      if (res.ok) {
        const data = await res.json();
        setResult({ count: data.message_count, confidence: data.twin_confidence });
        onUploadComplete?.();
      } else {
        alert(`Upload failed: ${await res.text()}`);
      }
    } catch { alert("Upload failed"); }
    setUploading(null);
  };

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-brand-blue/20 bg-brand-blue/5 p-4">
        <p className="text-sm font-semibold text-black">Activate {contactName}&apos;s digital twin</p>
        <p className="mt-1 text-xs text-gray-500">
          Upload real conversations with {contactName} and we&apos;ll build a digital twin -- so you can ask how they&apos;d react to anything. Prices, hours, menu changes, renovations, new staff, loyalty programmes, delivery terms -- anything.
        </p>
      </div>

      {result && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-3">
          <p className="text-xs font-medium text-green-700">Upload successful</p>
          <p className="mt-0.5 text-[11px] text-green-600">{result.count} messages processed. Twin confidence: {result.confidence}.</p>
        </div>
      )}

      <label className="group block cursor-pointer rounded-xl border-2 border-dashed border-[#E5E2DC] p-6 text-center transition-colors hover:border-brand-blue hover:bg-brand-blue/5">
        <input type="file" accept=".txt,.pdf,.docx,.eml,.mbox,.csv,.xlsx" className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f, "other"); e.target.value = ""; }} />
        <svg className="mx-auto mb-2 h-6 w-6 text-gray-300 group-hover:text-brand-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.036 4.187A3.75 3.75 0 0118 19.5H6.75z" />
        </svg>
        <p className="text-sm text-gray-400 group-hover:text-brand-blue">Drop files here or click to upload</p>
      </label>

      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">What to upload</p>
        <div className="space-y-1.5">
          {sources.map((src) => (
            <label key={src.sourceType} className="group flex cursor-pointer items-start gap-3 rounded-lg border border-[#E5E2DC] bg-white p-3 transition-all hover:border-gray-300 hover:shadow-sm">
              <input type="file" accept={src.formats.split(" ").join(",")} className="hidden"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f, src.sourceType); e.target.value = ""; }} />
              <div className="mt-0.5 text-gray-400">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-black">{src.label}</p>
                <p className="text-[11px] text-gray-400">{src.description}</p>
                <p className="mt-0.5 text-[10px] text-gray-300">Formats: {src.formats}</p>
              </div>
              <span className="shrink-0 text-[11px] text-brand-blue opacity-0 group-hover:opacity-100">
                {uploading === src.sourceType ? "Uploading..." : "Upload"}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-[#E5E2DC] bg-gray-50 p-3">
        <p className="text-[10px] font-medium text-gray-500">Privacy</p>
        <p className="mt-0.5 text-[10px] text-gray-400">
          All files are anonymised immediately on upload. Raw content is deleted within 60 seconds. Only communication patterns are stored -- never message content.
        </p>
      </div>
    </div>
  );
}
