"use client";

import { useState } from "react";

function Tooltip({ content, children }: { content: string; children: React.ReactNode }) {
  const [show, setShow] = useState(false);
  return (
    <span className="relative" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <span className="absolute bottom-full right-0 z-50 mb-2 w-56 rounded-lg bg-black p-2.5 text-[11px] leading-relaxed text-white shadow-lg">
          {content}
        </span>
      )}
    </span>
  );
}

interface ChipOption { value: string; label: string }

function ChipSelector({ options, value, onChange, multi = true }: {
  options: ChipOption[]; value: string | string[]; onChange: (v: string | string[]) => void; multi?: boolean;
}) {
  const selected = Array.isArray(value) ? value : value ? [value] : [];
  const toggle = (v: string) => {
    if (multi) {
      onChange(selected.includes(v) ? selected.filter((x) => x !== v) : [...selected, v]);
    } else {
      onChange(v);
    }
  };
  return (
    <div className="flex flex-wrap gap-1.5">
      {options.map((o) => (
        <button key={o.value} type="button" onClick={() => toggle(o.value)}
          className={`rounded-lg border px-3 py-1.5 text-xs transition-all ${
            selected.includes(o.value)
              ? "border-brand-orange bg-brand-orange text-white"
              : "border-[#E5E2DC] text-gray-500 hover:bg-gray-50"
          }`}
        >{o.label}</button>
      ))}
    </div>
  );
}

function StarRating({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <button key={n} type="button" onClick={() => onChange(n)}
          className={`text-xl transition-colors ${n <= value ? "text-brand-orange" : "text-gray-200 hover:text-gray-300"}`}
        >*</button>
      ))}
    </div>
  );
}

function SliderField({ value, onChange, leftLabel, rightLabel }: {
  value: number; onChange: (v: number) => void; leftLabel?: string; rightLabel?: string;
}) {
  return (
    <div>
      <input type="range" min={1} max={5} value={value || 3} onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-brand-orange" />
      <div className="flex justify-between text-[10px] text-gray-400">
        <span>{leftLabel}</span><span>{rightLabel}</span>
      </div>
    </div>
  );
}

interface FormFieldProps {
  label: string;
  name: string;
  type?: "text" | "textarea" | "select" | "chips" | "slider" | "stars" | "date" | "number";
  formatHint?: string;
  whyItMatters?: string;
  placeholder?: string;
  value: unknown;
  onChange: (v: unknown) => void;
  options?: ChipOption[] | { left?: string; right?: string };
  multi?: boolean;
  rows?: number;
}

export default function FormField({
  label, type = "text", formatHint, whyItMatters, placeholder,
  value, onChange, options, multi = true, rows = 3,
}: FormFieldProps) {
  const inputClass = "w-full rounded-lg border border-[#E5E2DC] bg-white px-3 py-2 text-sm text-black placeholder-gray-300 focus:border-brand-blue focus:outline-none";

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <label className="text-sm text-gray-600">
          {label}
          <span className="ml-1 text-[10px] text-gray-300">(optional)</span>
        </label>
        {whyItMatters && (
          <Tooltip content={whyItMatters}>
            <span className="cursor-help text-[10px] text-gray-300 hover:text-gray-500">Why this?</span>
          </Tooltip>
        )}
      </div>

      {type === "text" && <input className={inputClass} placeholder={placeholder} value={(value as string) || ""} onChange={(e) => onChange(e.target.value)} />}
      {type === "number" && <input type="number" className={inputClass} placeholder={placeholder} value={(value as string) || ""} onChange={(e) => onChange(e.target.value)} />}
      {type === "date" && <input type="date" className={inputClass} value={(value as string) || ""} onChange={(e) => onChange(e.target.value)} />}
      {type === "textarea" && <textarea rows={rows} className={inputClass} placeholder={placeholder} value={(value as string) || ""} onChange={(e) => onChange(e.target.value)} />}

      {type === "select" && Array.isArray(options) && (
        <select className={inputClass} value={(value as string) || ""} onChange={(e) => onChange(e.target.value)}>
          <option value="">Select...</option>
          {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      )}

      {type === "chips" && Array.isArray(options) && (
        <ChipSelector options={options} value={value as string | string[]} onChange={onChange as (v: string | string[]) => void} multi={multi} />
      )}

      {type === "slider" && (
        <SliderField value={(value as number) || 3} onChange={onChange as (v: number) => void}
          leftLabel={(options as { left?: string; right?: string })?.left}
          rightLabel={(options as { left?: string; right?: string })?.right} />
      )}

      {type === "stars" && <StarRating value={(value as number) || 0} onChange={onChange as (v: number) => void} />}
      {formatHint && <p className="text-[10px] text-gray-400">{formatHint}</p>}
    </div>
  );
}
