"use client";

import { usePathname } from "next/navigation";


export default function CRMSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-gray-200 bg-white">
      {/* Header */}
      <div className="border-b border-gray-100 px-5 py-4">
        <p className="text-sm font-bold text-black">Murmur CRM</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
          Overview
        </p>
        <a
          href="/crm"
          className={`mb-1 flex items-center rounded-lg px-3 py-2 text-sm transition-colors ${
            pathname === "/crm"
              ? "bg-gray-100 font-medium text-black"
              : "text-gray-500 hover:bg-gray-50 hover:text-black"
          }`}
        >
          Home
        </a>

        <p className="mb-2 mt-6 px-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
          Contacts
        </p>
        <a
          href="/crm/contacts"
          className={`mb-1 flex items-center rounded-lg px-3 py-2 text-sm transition-colors ${
            pathname?.startsWith("/crm/contacts")
              ? "bg-gray-100 font-medium text-black"
              : "text-gray-500 hover:bg-gray-50 hover:text-black"
          }`}
        >
          All contacts
        </a>

        <p className="mb-2 mt-6 px-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
          Organisations
        </p>
        <a
          href="/crm/organisations"
          className={`mb-1 flex items-center rounded-lg px-3 py-2 text-sm transition-colors ${
            pathname?.startsWith("/crm/organisations")
              ? "bg-gray-100 font-medium text-black"
              : "text-gray-500 hover:bg-gray-50 hover:text-black"
          }`}
        >
          All organisations
        </a>
      </nav>

      {/* Footer actions */}
      <div className="border-t border-gray-100 p-3">
        <a
          href="/crm/contacts?new=1"
          className="mb-2 flex w-full items-center justify-center rounded-lg bg-black py-2 text-sm font-medium text-white transition-opacity hover:opacity-80"
        >
          Add contact
        </a>
        <a
          href="/crm/organisations?new=1"
          className="flex w-full items-center justify-center rounded-lg border border-gray-200 py-2 text-sm text-gray-600 transition-colors hover:bg-gray-50"
        >
          Add organisation
        </a>
      </div>
    </aside>
  );
}
