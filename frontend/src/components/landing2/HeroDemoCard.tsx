"use client";

import { useState, useEffect } from "react";
import { motion, useReducedMotion } from "framer-motion";

const PERSONAS = [
  {
    initial: "M",
    name: "Maya, 31",
    desc: "Weekly regular",
    sentiment: 72,
    color: "bg-murmur-positive",
    barColor: "bg-murmur-positive",
    label: "Likely to accept",
    quote:
      "I'd pay it for weekend brunch, honestly. The atmosphere is worth it.",
  },
  {
    initial: "D",
    name: "David, 48",
    desc: "Occasional visitor",
    sentiment: 40,
    color: "bg-murmur-amber",
    barColor: "bg-murmur-amber",
    label: "Uncertain",
    quote:
      "Depends what's on the menu. If it feels special enough, maybe.",
  },
  {
    initial: "S",
    name: "Sophie, 26",
    desc: "Price-conscious lunch regular",
    sentiment: 20,
    color: "bg-murmur-negative",
    barColor: "bg-murmur-negative",
    label: "Likely to switch",
    quote:
      "3 more on a Saturday? I'd just go to the place round the corner.",
  },
];

const AVATAR_COLORS = ["#C4874A", "#3D7A5C", "#9B4040", "#7A6E5A", "#8C8580"];

export default function HeroDemoCard() {
  const [visibleCards, setVisibleCards] = useState(0);
  const [showSummary, setShowSummary] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const reduced = useReducedMotion();

  useEffect(() => {
    // Auto-play sequence
    const t1 = setTimeout(() => setIsRunning(true), 1000);
    const t2 = setTimeout(() => setVisibleCards(1), 2000);
    const t3 = setTimeout(() => setVisibleCards(2), 2800);
    const t4 = setTimeout(() => setVisibleCards(3), 3600);
    const t5 = setTimeout(() => {
      setShowSummary(true);
      setIsRunning(false);
    }, 5000);

    return () => {
      [t1, t2, t3, t4, t5].forEach(clearTimeout);
    };
  }, []);

  return (
    <div className="w-full">
      <div className="overflow-hidden rounded-2xl border border-murmur-border bg-white shadow-xl shadow-murmur-ink/5">
        {/* Business + Question header */}
        <div className="border-b border-murmur-border bg-murmur-cream/50 px-6 py-4">
          <div className="flex items-center gap-2 text-sm text-murmur-warm-grey">
            <span className="rounded-full bg-murmur-amber/10 px-3 py-0.5 text-xs font-medium text-murmur-amber">
              Rosa&apos;s Cafe, Hackney
            </span>
            {isRunning && (
              <span className="ml-auto flex items-center gap-1.5 text-xs text-murmur-amber">
                <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-murmur-amber" />
                Running...
              </span>
            )}
          </div>
          <p className="mt-2 text-sm font-medium text-murmur-ink">
            Would my regulars accept a new weekend brunch menu at 3 more per
            dish?
          </p>
        </div>

        {/* Persona response cards */}
        <div className="space-y-0 divide-y divide-murmur-border/50">
          {PERSONAS.map((p, i) => (
            <motion.div
              key={p.name}
              initial={reduced ? { opacity: 1 } : { opacity: 0, x: 20 }}
              animate={
                i < visibleCards
                  ? { opacity: 1, x: 0 }
                  : reduced
                    ? {}
                    : { opacity: 0, x: 20 }
              }
              transition={{ duration: 0.5, ease: "easeOut" }}
              className={`px-6 py-4 ${i >= visibleCards ? "invisible" : ""}`}
            >
              <div className="flex items-start gap-3">
                {/* Avatar */}
                <div
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold text-white"
                  style={{ backgroundColor: AVATAR_COLORS[i] }}
                >
                  {p.initial}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-murmur-ink">
                        {p.name}
                      </span>
                      <span className="ml-2 text-xs text-murmur-warm-grey">
                        {p.desc}
                      </span>
                    </div>
                  </div>
                  {/* Sentiment bar */}
                  <div className="mt-2 flex items-center gap-2">
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-murmur-border/50">
                      <motion.div
                        className={`h-full rounded-full ${p.barColor}`}
                        initial={{ width: 0 }}
                        animate={
                          i < visibleCards
                            ? { width: `${p.sentiment}%` }
                            : { width: 0 }
                        }
                        transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                      />
                    </div>
                    <span className="shrink-0 text-xs text-murmur-warm-grey">
                      {p.label}
                    </span>
                  </div>
                  {/* Quote */}
                  <p className="mt-2 text-sm italic text-murmur-warm-grey">
                    &ldquo;{p.quote}&rdquo;
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Summary pill */}
        <motion.div
          initial={reduced ? { opacity: 1 } : { opacity: 0, y: 10 }}
          animate={
            showSummary ? { opacity: 1, y: 0 } : reduced ? {} : { opacity: 0, y: 10 }
          }
          transition={{ duration: 0.5 }}
          className={`border-t border-murmur-border bg-murmur-cream/30 px-6 py-3 ${
            !showSummary ? "invisible" : ""
          }`}
        >
          <p className="text-center text-sm text-murmur-ink">
            <span className="mr-1 text-murmur-positive">&#8599;</span>
            Most regulars would accept
            <span className="mx-2 text-murmur-border">|</span>
            <span className="text-murmur-amber">
              Price-sensitive segment at risk
            </span>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
