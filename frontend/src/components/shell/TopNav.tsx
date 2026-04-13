"use client";

import { usePathname, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

const TABS = [
  { label: "Home", href: "/app", exact: true },
  { label: "Simulate", href: "/app/simulate" },
  { label: "Customers", href: "/app/customers" },
  { label: "Vendors", href: "/app/vendors" },
  { label: "Intelligence", href: "/app/intelligence" },
  { label: "Reports", href: "/app/reports" },
];

export default function TopNav() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/");
    router.refresh();
  }

  return (
    <header className="sticky top-0 z-50 flex h-20 items-center border-b border-[#E5E2DC] bg-white px-6">
      {/* Logo */}
      <a href="/app" className="mr-8 flex items-center gap-2 text-lg font-bold text-black">
        <img src="/murmur-logo.png" alt="" className="h-[72px] w-[72px] rounded-xl" />
        Murmur
      </a>

      {/* Tabs */}
      <nav className="flex h-full items-center gap-1">
        {TABS.map((tab) => {
          const isActive = (tab as { exact?: boolean }).exact
            ? pathname === tab.href
            : pathname?.startsWith(tab.href);
          const isSoon = (tab as { soon?: boolean }).soon;

          return (
            <div key={tab.label} className="group relative flex h-full items-center">
              <a
                data-tut={`nav-${tab.label.toLowerCase()}`}
                href={isSoon ? undefined : tab.href}
                className={`relative flex h-full items-center px-4 text-sm font-medium transition-colors ${
                  isActive
                    ? "text-black"
                    : isSoon
                      ? "cursor-default text-gray-300"
                      : "text-gray-400 hover:text-gray-700"
                }`}
              >
                {tab.label}
                {/* Active indicator */}
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-orange" />
                )}
              </a>
              {/* Coming soon tooltip */}
              {isSoon && (
                <span className="pointer-events-none absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-md bg-black px-2.5 py-1 text-[10px] text-white opacity-0 transition-opacity group-hover:opacity-100">
                  Coming soon
                </span>
              )}
            </div>
          );
        })}
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right: settings + avatar */}
      <div className="flex items-center gap-3">
        <a
          href="/app/settings"
          className="text-gray-400 transition-colors hover:text-black"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
          </svg>
        </a>
        <button
          onClick={handleSignOut}
          className="text-sm text-gray-400 transition-colors hover:text-black"
        >
          Sign out
        </button>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-blue text-xs font-bold text-white">
          U
        </div>
      </div>
    </header>
  );
}
