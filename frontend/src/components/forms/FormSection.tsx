"use client";

import { useState } from "react";

interface Props {
  title: string;
  subtitle?: string;
  whyItMatters?: string;
  defaultOpen?: boolean;
  completedFields?: number;
  totalFields?: number;
  children: React.ReactNode;
}

export default function FormSection({
  title, subtitle, whyItMatters, defaultOpen = false,
  completedFields, totalFields, children,
}: Props) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded-xl border border-[#E5E2DC] bg-white">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between p-4 text-left"
      >
        <div>
          <span className="font-semibold text-black">{title}</span>
          {subtitle && <span className="ml-2 text-sm text-gray-400">{subtitle}</span>}
        </div>
        <div className="flex items-center gap-3">
          {completedFields !== undefined && totalFields !== undefined && completedFields > 0 && (
            <span className="text-[10px] text-gray-400">{completedFields}/{totalFields}</span>
          )}
          {whyItMatters && (
            <span className="text-[10px] text-gray-300" title={whyItMatters}>Why?</span>
          )}
          <svg className={`h-4 w-4 text-gray-300 transition-transform ${open ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      {open && <div className="space-y-4 border-t border-[#E5E2DC] px-4 pb-5 pt-4">{children}</div>}
    </div>
  );
}
