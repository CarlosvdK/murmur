"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, useInView, useReducedMotion } from "framer-motion";
import SectionReveal from "./SectionReveal";

const AVATAR_COLORS = ["#C4874A", "#3D7A5C", "#9B4040", "#7A6E5A", "#8C8580",
  "#C4874A", "#3D7A5C", "#9B4040", "#7A6E5A", "#8C8580", "#C4874A", "#3D7A5C", "#9B4040"];
const INITIALS = "M C D J L R A S P T K E N".split(" ");

const RESPONSES = [
  {
    name: "Maria, 34",
    segment: "Silent regular",
    sentiment: 0.35,
    gut: "stay",
    says: "An extra dollar? I'd grumble but still come. It's our family routine.",
    does: "Would actually keep coming weekly. Switching with two kids is too much hassle.",
    color: "bg-green-500",
  },
  {
    name: "Carlos, 28",
    segment: "Price-sensitive lunch",
    sentiment: -0.55,
    gut: "reduce",
    says: "I already think it's a bit much. Another 10% and I'd try the new place on 5th.",
    does: "Would reduce from 3x/week to 1x/week. Too lazy to fully switch but would cut back.",
    color: "bg-red-500",
  },
  {
    name: "Diane, 52",
    segment: "Monthly occasional",
    sentiment: 0.1,
    gut: "neutral",
    says: "I only come once a month for the al pastor. Wouldn't even notice.",
    does: "No behaviour change. Would not notice the price difference at all.",
    color: "bg-amber-500",
  },
];

const THEMES = [
  { text: "Regulars tolerate increases due to habit and switching cost", type: "positive" },
  { text: "Lunch crowd has nearby alternatives and is price-elastic", type: "warning" },
  { text: "Occasional visitors unaffected: too infrequent to notice", type: "neutral" },
];

export default function LiveDemo() {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: "-100px" });
  const reduced = useReducedMotion();
  const [phase, setPhase] = useState(0);
  const [avatarsShown, setAvatarsShown] = useState(0);
  const [responsesShown, setResponsesShown] = useState(0);
  const [themesShown, setThemesShown] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [hasPlayed, setHasPlayed] = useState(false);

  const play = useCallback(() => {
    setPhase(1);
    setAvatarsShown(0);
    setResponsesShown(0);
    setThemesShown(0);
    setShowResult(false);

    for (let i = 0; i < 13; i++) {
      setTimeout(() => setAvatarsShown((p) => p + 1), 1500 + i * 120);
    }
    setTimeout(() => setPhase(2), 3500);
    setTimeout(() => setResponsesShown(1), 5000);
    setTimeout(() => setResponsesShown(2), 8000);
    setTimeout(() => setResponsesShown(3), 11000);
    setTimeout(() => setThemesShown(1), 6000);
    setTimeout(() => setThemesShown(2), 9000);
    setTimeout(() => setThemesShown(3), 12000);
    setTimeout(() => { setPhase(3); setShowResult(true); }, 14000);
  }, []);

  useEffect(() => {
    if (isInView && !hasPlayed) {
      setHasPlayed(true);
      play();
    }
  }, [isInView, hasPlayed, play]);

  // Auto-replay loop after completion
  useEffect(() => {
    if (phase !== 3) return;
    const restart = setTimeout(() => {
      play();
    }, 6000);
    return () => clearTimeout(restart);
  }, [phase, play]);

  const themeStyles: Record<string, string> = {
    positive: "border-green-200 bg-green-50 text-green-700",
    warning: "border-amber-200 bg-amber-50 text-amber-700",
    neutral: "border-gray-200 bg-white text-gray-600",
  };

  return (
    <section className="bg-white px-6 py-24 lg:px-12 xl:px-20" ref={containerRef}>
      <div className="mx-auto max-w-[1400px]">
        <SectionReveal className="mb-12 text-center">
          <p className="mb-4 text-xs font-medium uppercase tracking-[0.15em] text-murmur-warm-grey">
            See it in action
          </p>
          <h2 className="font-serif-display text-4xl font-black leading-[1.05] tracking-[-0.025em] text-murmur-ink sm:text-5xl lg:text-6xl">
            A real simulation,
            <br />
            running right now
          </h2>
        </SectionReveal>

        <div className="overflow-hidden rounded-2xl border border-murmur-border bg-[#F5F3EF] shadow-lg shadow-murmur-ink/5">
          {/* Top bar */}
          <div className="flex items-center justify-between border-b border-murmur-border bg-white px-6 py-3">
            <div className="flex items-center gap-3">
              <span className="rounded-full bg-murmur-amber/10 px-3 py-1 text-xs font-medium text-murmur-amber">
                Tony&apos;s Taco Truck, East Austin, TX
              </span>
              <span className="text-xs text-gray-400">15 personas</span>
            </div>
            <div className="flex items-center gap-2">
              {phase === 2 && (
                <span className="flex items-center gap-1.5 text-xs text-murmur-amber">
                  <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-murmur-amber" />
                  Interviewing customers...
                </span>
              )}
              {phase === 3 && <span className="text-xs text-green-600">Complete</span>}
            </div>
          </div>

          {/* Question */}
          <div className="border-b border-murmur-border bg-white px-6 py-3">
            <p className="text-sm text-murmur-ink">
              &ldquo;What would happen if I raised all prices by 10%?&rdquo;
            </p>
          </div>

          {/* Main grid */}
          <div className="grid grid-cols-1 gap-0 divide-y divide-murmur-border lg:grid-cols-3 lg:divide-x lg:divide-y-0">
            {/* Left: avatars */}
            <div className="p-6">
              <p className="mb-4 text-xs font-medium uppercase tracking-wider text-gray-400">
                Customer panel
              </p>
              <div className="flex flex-wrap gap-2">
                {INITIALS.map((initial, i) => (
                  <motion.div
                    key={i}
                    initial={reduced ? { opacity: 1 } : { opacity: 0, scale: 0 }}
                    animate={i < avatarsShown ? { opacity: 1, scale: 1 } : {}}
                    transition={{ duration: 0.3 }}
                    className={`flex h-9 w-9 items-center justify-center rounded-full text-xs font-semibold text-white ${i >= avatarsShown ? "invisible" : ""}`}
                    style={{ backgroundColor: AVATAR_COLORS[i] }}
                  >
                    {initial}
                  </motion.div>
                ))}
              </div>
              <p className="mt-4 text-[10px] text-gray-400">
                55% silent majority, 30% regulars, 15% occasional
              </p>
            </div>

            {/* Middle: responses with say-do gap */}
            <div className="p-6">
              <p className="mb-4 text-xs font-medium uppercase tracking-wider text-gray-400">
                Interview responses
              </p>
              <div className="space-y-4">
                {RESPONSES.map((r, i) => (
                  <motion.div
                    key={r.name}
                    initial={reduced ? { opacity: 1 } : { opacity: 0, y: 10 }}
                    animate={i < responsesShown ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.5 }}
                    className={i >= responsesShown ? "invisible" : ""}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="flex h-7 w-7 items-center justify-center rounded-full text-[10px] font-bold text-white"
                        style={{ backgroundColor: AVATAR_COLORS[i] }}
                      >
                        {r.name[0]}
                      </div>
                      <span className="text-sm font-medium text-murmur-ink">{r.name}</span>
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[9px] text-gray-500">{r.segment}</span>
                    </div>
                    <div className="mt-1.5 flex items-center gap-2">
                      <div className="h-1 flex-1 overflow-hidden rounded-full bg-gray-100">
                        <motion.div
                          className={`h-full rounded-full ${r.color}`}
                          initial={{ width: 0 }}
                          animate={i < responsesShown ? { width: `${Math.abs(r.sentiment) * 100}%` } : {}}
                          transition={{ duration: 0.8, delay: 0.2 }}
                        />
                      </div>
                      <span className="text-[10px] font-medium text-gray-500">
                        {r.sentiment > 0 ? "+" : ""}{r.sentiment.toFixed(1)}
                      </span>
                    </div>
                    <div className="mt-1.5 space-y-0.5">
                      <p className="text-[11px] text-gray-500">
                        <span className="text-gray-400">Says: </span>&ldquo;{r.says}&rdquo;
                      </p>
                      <p className="text-[11px] text-gray-500">
                        <span className="text-murmur-amber">Would do: </span>&ldquo;{r.does}&rdquo;
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Right: themes */}
            <div className="p-6">
              <p className="mb-4 text-xs font-medium uppercase tracking-wider text-gray-400">
                Emerging themes
              </p>
              <div className="space-y-2">
                {THEMES.map((theme, i) => (
                  <motion.div
                    key={theme.text}
                    initial={reduced ? { opacity: 1 } : { opacity: 0, x: 10 }}
                    animate={i < themesShown ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.4 }}
                    className={`rounded-lg border px-3 py-2 text-xs ${
                      i >= themesShown ? "invisible" : themeStyles[theme.type]
                    }`}
                  >
                    {theme.text}
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Result: CI chart + decision */}
          <motion.div
            initial={reduced ? { opacity: 1 } : { opacity: 0, y: 15 }}
            animate={showResult ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className={`border-t border-murmur-border bg-white p-6 ${!showResult ? "invisible" : ""}`}
          >
            <div className="grid gap-6 lg:grid-cols-2">
              {/* Left: CI visualization */}
              <div>
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-xs font-medium uppercase tracking-wider text-gray-400">Estimated impact</span>
                  <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-0.5 text-[10px] font-semibold text-amber-700">
                    Caution
                  </span>
                </div>
                {/* CI bar */}
                <div className="relative h-3 w-full rounded-full bg-gradient-to-r from-red-100 via-amber-100 to-green-100">
                  <div className="absolute top-0 h-full rounded-full bg-amber-300/50" style={{ left: "30%", width: "28%" }} />
                  <div className="absolute top-1/2 h-4 w-4 -translate-y-1/2 rounded-full border-2 border-white bg-amber-500 shadow" style={{ left: "42%" }} />
                  {/* Zero line */}
                  <div className="absolute top-0 h-full w-px bg-gray-300" style={{ left: "50%" }} />
                </div>
                <div className="mt-1 flex justify-between text-[9px] text-gray-400">
                  <span>-5.2%</span>
                  <span>-1.8% (estimate)</span>
                  <span>+1.4%</span>
                </div>
                <div className="mt-3 flex gap-4 text-[10px] text-gray-500">
                  <span>P(positive): 34%</span>
                  <span>P(negative): 52%</span>
                  <span>P(negligible): 14%</span>
                </div>
              </div>

              {/* Right: summary */}
              <div>
                <p className="text-sm font-medium text-murmur-ink">
                  Most regulars would absorb the increase due to habit and switching cost.
                  Your price-sensitive lunch crowd is the risk: they have nearby alternatives
                  and would reduce frequency rather than leave entirely.
                </p>
                <div className="mt-3 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
                  <p className="text-[10px] font-medium text-gray-400">Say-do gap</p>
                  <p className="text-xs text-gray-500">
                    40% of personas said they would leave but predicted they would actually just reduce visits.
                    Corrected with Murphy et al. (2005) 28% stated-revealed gap.
                  </p>
                </div>
              </div>
            </div>

            <p className="mt-4 text-[10px] text-gray-400">
              Caveat: This is a simulation of 15 synthetic customers. A partial price test on 2-3 items would validate before full rollout.
            </p>
          </motion.div>

          {/* Replay */}
          <div className="flex items-center justify-between border-t border-murmur-border bg-[#F5F3EF] px-6 py-3">
            <button
              onClick={() => { setHasPlayed(false); setTimeout(() => { setHasPlayed(true); play(); }, 100); }}
              className="text-xs text-gray-400 transition-colors hover:text-murmur-ink"
            >
              Replay
            </button>
            <a href="/signup" className="text-sm font-medium text-murmur-amber transition-colors hover:text-murmur-ink">
              Try it with your business &#8594;
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
