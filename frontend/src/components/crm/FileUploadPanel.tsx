"use client";

import { useState } from "react";
import { CRMContact } from "@/lib/api";

const DATA_SOURCES = [
  {
    category: "Email",
    description: "Email conversations with this contact",
    formats: ".mbox .eml .txt",
    source_type: "email",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
      </svg>
    ),
  },
  {
    category: "WhatsApp / Chat",
    description: "WhatsApp exports, Telegram, or other chat logs",
    formats: ".txt .csv",
    source_type: "whatsapp",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
      </svg>
    ),
  },
  {
    category: "Meeting notes",
    description: "Transcripts, notes from calls or meetings",
    formats: ".txt .pdf .docx",
    source_type: "meeting_notes",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
      </svg>
    ),
  },
  {
    category: "LinkedIn / Social",
    description: "LinkedIn messages, social media conversations",
    formats: ".csv .txt .json",
    source_type: "linkedin",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
      </svg>
    ),
  },
  {
    category: "Documents",
    description: "Contracts, proposals, or shared documents",
    formats: ".pdf .docx .xlsx",
    source_type: "document",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
    ),
  },
  {
    category: "CRM export",
    description: "HubSpot, Salesforce, or other CRM data",
    formats: ".csv .json",
    source_type: "crm_export",
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
      </svg>
    ),
  },
];

interface Props {
  contact: CRMContact;
  accentColor?: string;
  contactType: "customer" | "vendor";
  onUpdate: () => void;
}

export default function FileUploadPanel({ contact, accentColor = "#448CFD", onUpdate }: Props) {
  const [uploading, setUploading] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<{ count: number; confidence: string } | null>(null);

  const handleUpload = async (file: File, sourceType: string) => {
    setUploading(sourceType);
    setUploadResult(null);
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
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api"}/crm/twin/upload/${contact.id}`,
        { method: "POST", headers, body: formData }
      );

      if (res.ok) {
        const data = await res.json();
        setUploadResult({ count: data.message_count, confidence: data.twin_confidence });
        onUpdate();
      } else {
        const err = await res.text();
        alert(`Upload failed: ${err}`);
      }
    } catch {
      alert("Upload failed");
    }
    setUploading(null);
  };

  return (
    <div className="space-y-5">
      <div>
        <h4 className="mb-1 text-sm font-semibold text-black">Build {contact.first_name}&apos;s digital twin</h4>
        <p className="mb-4 text-xs text-gray-500">
          Upload any communication you have with {contact.first_name}. The more data sources, the more accurate the twin.
        </p>
      </div>

      {uploadResult && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-3">
          <p className="text-xs font-medium text-green-700">Upload successful</p>
          <p className="mt-1 text-[11px] text-green-600">
            {uploadResult.count} messages processed. Twin confidence: {uploadResult.confidence}.
          </p>
        </div>
      )}

      {contact.has_twin && (
        <div className="flex items-center gap-3 rounded-lg border border-[#E5E2DC] bg-gray-50 p-3">
          <div className="h-2 w-2 rounded-full bg-green-500" />
          <div className="flex-1">
            <p className="text-xs font-medium text-black">Twin active -- {contact.twin_corpus_size} messages</p>
            <p className="text-[11px] text-gray-500">Confidence: {contact.twin_confidence || "N/A"}. Upload more to improve.</p>
          </div>
        </div>
      )}

      {/* Data source cards */}
      <div className="grid gap-2">
        {DATA_SOURCES.map((src) => (
          <label
            key={src.category}
            className="group flex cursor-pointer items-center gap-4 rounded-xl border border-[#E5E2DC] bg-white p-4 transition-all hover:border-gray-400 hover:shadow-sm"
          >
            <input
              type="file"
              accept={src.formats.replace(/ /g, ",")}
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleUpload(file, src.source_type);
                e.target.value = "";
              }}
            />
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-gray-400 group-hover:text-gray-600" style={{ background: `${accentColor}10` }}>
              <div style={{ color: accentColor }}>{src.icon}</div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-black">{src.category}</p>
              <p className="text-xs text-gray-400">{src.description}</p>
            </div>
            <div className="text-right">
              {uploading === src.source_type ? (
                <span className="text-xs text-gray-400">Uploading...</span>
              ) : (
                <>
                  <p className="text-xs font-medium group-hover:underline" style={{ color: accentColor }}>Upload</p>
                  <p className="text-[10px] text-gray-300">{src.formats}</p>
                </>
              )}
            </div>
          </label>
        ))}
      </div>

      {/* Privacy notice */}
      <div className="rounded-lg border border-[#E5E2DC] bg-gray-50 p-3">
        <p className="text-xs font-medium text-gray-600">Privacy guarantee</p>
        <p className="mt-1 text-[11px] text-gray-400">
          Raw files are deleted immediately after processing. Only anonymised communication patterns are stored -- never actual message content.
          You must have the right to upload any correspondence you share.
        </p>
      </div>
    </div>
  );
}
