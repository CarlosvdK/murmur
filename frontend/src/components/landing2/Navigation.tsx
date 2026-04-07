"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";

const NAV_LINKS = [
  { label: "How it works", href: "#how-it-works" },
  { label: "Use cases", href: "#use-cases" },
  { label: "Accuracy", href: "#accuracy" },
  { label: "Pricing", href: "#", disabled: true, tooltip: "Coming soon" },
];

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const reduced = useReducedMotion();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <motion.header
        initial={reduced ? {} : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className={`fixed left-0 right-0 top-0 z-50 transition-all duration-300 ${
          scrolled
            ? "border-b border-murmur-border bg-[#F5F3EF]/90 backdrop-blur-md"
            : "bg-transparent"
        }`}
      >
        <div className="mx-auto flex h-16 w-full max-w-none items-center justify-between px-6">
          {/* Wordmark */}
          <a href="/" className="font-serif-display text-2xl text-murmur-ink">
            Murmur
          </a>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-8 md:flex">
            {NAV_LINKS.map((link) => (
              <div key={link.label} className="group relative">
                <a
                  href={link.disabled ? undefined : link.href}
                  className={`text-sm transition-colors ${
                    link.disabled
                      ? "cursor-default text-murmur-warm-grey/50"
                      : "text-murmur-warm-grey hover:text-murmur-ink"
                  }`}
                >
                  {link.label}
                </a>
                {link.disabled && link.tooltip && (
                  <span className="pointer-events-none absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-md bg-murmur-ink px-2.5 py-1 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100">
                    {link.tooltip}
                  </span>
                )}
              </div>
            ))}
          </nav>

          {/* Desktop CTAs */}
          <div className="hidden items-center gap-3 md:flex">
            <a
              href="/login"
              className="text-sm text-murmur-warm-grey transition-colors hover:text-murmur-ink"
            >
              Sign in
            </a>
            <a
              href="/signup"
              className="rounded-full bg-black px-5 py-2 text-sm font-bold text-white transition-all hover:opacity-80 hover:scale-[1.02]"
            >
              Try free
            </a>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="flex h-10 w-10 items-center justify-center md:hidden"
            aria-label="Menu"
          >
            <div className="space-y-1.5">
              <span
                className={`block h-0.5 w-5 bg-murmur-ink transition-transform ${
                  mobileOpen ? "translate-y-2 rotate-45" : ""
                }`}
              />
              <span
                className={`block h-0.5 w-5 bg-murmur-ink transition-opacity ${
                  mobileOpen ? "opacity-0" : ""
                }`}
              />
              <span
                className={`block h-0.5 w-5 bg-murmur-ink transition-transform ${
                  mobileOpen ? "-translate-y-2 -rotate-45" : ""
                }`}
              />
            </div>
          </button>
        </div>
      </motion.header>

      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 flex flex-col items-center justify-center gap-8 bg-murmur-cream md:hidden"
          >
            {NAV_LINKS.filter((l) => !l.disabled).map((link) => (
              <a
                key={link.label}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="font-serif-display text-3xl text-murmur-ink"
              >
                {link.label}
              </a>
            ))}
            <a
              href="/login"
              onClick={() => setMobileOpen(false)}
              className="mt-4 text-lg text-murmur-warm-grey"
            >
              Sign in
            </a>
            <a
              href="/signup"
              onClick={() => setMobileOpen(false)}
              className="mt-4 rounded-full bg-murmur-amber px-8 py-3 text-lg font-semibold text-white"
            >
              Try free
            </a>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
