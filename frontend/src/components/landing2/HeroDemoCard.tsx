"use client";

import { useState, useEffect } from "react";
import { motion, useReducedMotion } from "framer-motion";

const PERSONAS = [
  {
    initial: "M",
    name: "Maya, 31",
    segment: "Silent regular",
    sentiment: 0.35,
    gut: "stay",
    stated: "I'd still come but I'd notice.",
    actual: "Honestly, I'd just pay it. Switching cafes is too much effort.",
    color: "bg-green-500",
  },
  {
    initial: "D",
    name: "David, 48",
    segment: "Occasional visitor",
    sentiment: -0.1,
    gut: "neutral",
    stated: "Depends what's on the menu. If it feels special enough, maybe.",
    actual: "I only come monthly. I'd forget about the price change by next time.",
    color: "bg-amber-500",
  },
  {
    initial: "S",
    name: "Sophie, 26",
    segment: "Price-sensitive lunch regular",
    sentiment: -0.6,
    gut: "reduce",
    stated: "I'd definitely look for alternatives.",
    actual: "I'd probably complain but still come twice a month instead of weekly.",
    color: "bg-red-500",
  },
];

const AVATAR_COLORS = ["#C4874A", "#3D7A5C", "#9B4040"];

export default function HeroDemoCard() {
  const [visibleCards, setVisibleCards] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const reduced = useReducedMotion();

  const play = () => {
    setVisibleCards(0);
    setShowResult(false);
    setIsRunning(true);
    const t2 = setTimeout(() => setVisibleCards(1), 1000);
    const t3 = setTimeout(() => setVisibleCards(2), 1800);
    const t4 = setTimeout(() => setVisibleCards(3), 2600);
    const t5 = setTimeout(() => {
      setShowResult(true);
      setIsRunning(false);
    }, 4000);
    return [t2, t3, t4, t5];
  };

  useEffect(() => {
    let timers: ReturnType<typeof setTimeout>[] = [];
    const startCycle = () => {
      timers = play();
      // Pause 5s on result, then restart
      const restart = setTimeout(() => {
        startCycle();
      }, 9000);
      timers.push(restart);
    };
    const initial = setTimeout(startCycle, 1000);
    return () => { clearTimeout(initial); timers.forEach(clearTimeout); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="w-full">
      <div className="overflow-hidden rounded-2xl border border-murmur-border bg-white shadow-xl shadow-murmur-ink/5">
        {/* Header */}
        <div className="border-b border-murmur-border bg-murmur-cream/50 px-6 py-4">
          <div className="flex items-center gap-2 text-sm text-murmur-warm-grey">
            <span className="rounded-full bg-murmur-amber/10 px-3 py-0.5 text-xs font-medium text-murmur-amber">
              Rosa&apos;s Cafe, Hackney
            </span>
            {isRunning && (
              <span className="ml-auto flex items-center gap-1.5 text-xs text-murmur-amber">
                <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-murmur-amber" />
                Interviewing...
              </span>
            )}
            {showResult && (
              <span className="ml-auto text-xs text-green-600">Complete</span>
            )}
          </div>
          <p className="mt-2 text-sm font-medium text-murmur-ink">
            Would my regulars accept a new weekend brunch menu at 3 more per dish?
          </p>
        </div>

        {/* Persona responses */}
        <div className="space-y-0 divide-y divide-murmur-border/50">
          {PERSONAS.map((p, i) => (
            <motion.div
              key={p.name}
              initial={reduced ? { opacity: 1 } : { opacity: 0, x: 20 }}
              animate={i < visibleCards ? { opacity: 1, x: 0 } : reduced ? {} : { opacity: 0, x: 20 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className={`px-6 py-4 ${i >= visibleCards ? "invisible" : ""}`}
            >
              <div className="flex items-start gap-3">
                <div
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold text-white"
                  style={{ backgroundColor: AVATAR_COLORS[i] }}
                >
                  {p.initial}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-murmur-ink">{p.name}</span>
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500">{p.segment}</span>
                    <span className="ml-auto text-[10px] text-gray-400">Gut: {p.gut}</span>
                  </div>
                  {/* Sentiment bar */}
                  <div className="mt-2 flex items-center gap-2">
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-gray-100">
                      <motion.div
                        className={`h-full rounded-full ${p.color}`}
                        initial={{ width: 0 }}
                        animate={i < visibleCards ? { width: `${Math.abs(p.sentiment) * 100}%` } : { width: 0 }}
                        transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                      />
                    </div>
                    <span className="shrink-0 text-[10px] font-medium text-gray-500">
                      {p.sentiment > 0 ? "+" : ""}{p.sentiment.toFixed(1)}
                    </span>
                  </div>
                  {/* Say vs Do */}
                  <div className="mt-2 space-y-1">
                    <p className="text-xs text-gray-500">
                      <span className="font-medium text-gray-400">Says: </span>
                      &ldquo;{p.stated}&rdquo;
                    </p>
                    <p className="text-xs text-gray-500">
                      <span className="font-medium text-murmur-amber">Would do: </span>
                      &ldquo;{p.actual}&rdquo;
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* CI result bar */}
        <motion.div
          initial={reduced ? { opacity: 1 } : { opacity: 0, y: 10 }}
          animate={showResult ? { opacity: 1, y: 0 } : reduced ? {} : { opacity: 0, y: 10 }}
          transition={{ duration: 0.5 }}
          className={`border-t border-murmur-border bg-murmur-cream/30 px-6 py-4 ${!showResult ? "invisible" : ""}`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="rounded-full bg-amber-50 border border-amber-200 px-2.5 py-0.5 text-[10px] font-semibold text-amber-700">Caution</span>
            <span className="text-[10px] text-gray-400">67% positive / 33% negative</span>
          </div>
          {/* Mini CI bar */}
          <div className="relative h-2 w-full rounded-full bg-gradient-to-r from-red-100 via-amber-100 to-green-100">
            <div className="absolute top-0 h-full rounded-full bg-amber-300/60" style={{ left: "35%", width: "30%" }} />
            <div className="absolute top-1/2 h-3 w-3 -translate-y-1/2 rounded-full border-2 border-white bg-amber-500 shadow-sm" style={{ left: "48%" }} />
          </div>
          <p className="mt-2 text-xs text-gray-500">
            Regulars would accept. Price-sensitive lunch crowd at risk of reducing visits.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
