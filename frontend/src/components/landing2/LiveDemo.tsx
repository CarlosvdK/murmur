"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, useInView, useReducedMotion } from "framer-motion";
import { useRef } from "react";
import SectionReveal from "./SectionReveal";

const AVATAR_COLORS = ["#C4874A", "#3D7A5C", "#9B4040", "#7A6E5A", "#8C8580",
  "#C4874A", "#3D7A5C", "#9B4040", "#7A6E5A", "#8C8580", "#C4874A", "#3D7A5C", "#9B4040"];
const INITIALS = "M C D J L R A S P T K E N".split(" ");

const RESPONSES = [
  {
    name: "Maria, 34",
    desc: "Friday regular",
    sentiment: 72,
    sentLabel: "positive",
    color: "bg-murmur-positive",
    quote: "I come every week with the kids. An extra dollar? I'd grumble but still come. It's our routine.",
  },
  {
    name: "Carlos, 28",
    desc: "Lunch regular",
    sentiment: 31,
    sentLabel: "negative",
    color: "bg-murmur-negative",
    quote: "I already think it's a bit much for a food truck. Another 10% and I'd try the new place on 5th.",
  },
  {
    name: "Diane, 52",
    desc: "Monthly visitor",
    sentiment: 58,
    sentLabel: "neutral",
    color: "bg-murmur-neutral",
    quote: "I only come once a month for the al pastor. Honestly wouldn't even notice a small difference.",
  },
];

const THEMES = [
  { text: "Price tolerance among regulars", delay: 6000 },
  { text: "Risk: lunch crowd substitution", delay: 9000, flagged: true },
  { text: "Low sensitivity: occasional visitors", delay: 12000 },
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

    // Avatars appear
    for (let i = 0; i < 13; i++) {
      setTimeout(() => setAvatarsShown((p) => p + 1), 1500 + i * 120);
    }
    // Phase: running
    setTimeout(() => setPhase(2), 3500);
    // Responses
    setTimeout(() => setResponsesShown(1), 5000);
    setTimeout(() => setResponsesShown(2), 8000);
    setTimeout(() => setResponsesShown(3), 11000);
    // Themes
    setTimeout(() => setThemesShown(1), 6000);
    setTimeout(() => setThemesShown(2), 9000);
    setTimeout(() => setThemesShown(3), 12000);
    // Result
    setTimeout(() => {
      setPhase(3);
      setShowResult(true);
    }, 14000);
  }, []);

  useEffect(() => {
    if (isInView && !hasPlayed) {
      setHasPlayed(true);
      play();
    }
  }, [isInView, hasPlayed, play]);

  return (
    <section className="px-8 py-24 lg:px-16 xl:px-24" ref={containerRef}>
      <div className="w-full">
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

        {/* Demo card */}
        <div className="overflow-hidden rounded-2xl border border-murmur-border bg-murmur-cream shadow-lg shadow-murmur-ink/5">
          {/* Top bar */}
          <div className="flex items-center justify-between border-b border-murmur-border px-6 py-3">
            <div className="flex items-center gap-3">
              <span className="rounded-full bg-murmur-amber/10 px-3 py-1 text-xs font-medium text-murmur-amber">
                Tony&apos;s Taco Truck -- East Austin, TX
              </span>
            </div>
            <div className="flex items-center gap-2">
              {phase === 2 && (
                <span className="flex items-center gap-1.5 text-xs text-murmur-amber">
                  <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-murmur-amber" />
                  Running...
                </span>
              )}
              {phase === 3 && (
                <span className="text-xs text-murmur-positive">Complete</span>
              )}
            </div>
          </div>

          {/* Question */}
          <div className="border-b border-murmur-border bg-white px-6 py-3">
            <p className="text-sm text-murmur-ink">
              &ldquo;What would happen if I raised all prices by 10%?&rdquo;
            </p>
          </div>

          {/* Main content grid */}
          <div className="grid grid-cols-1 gap-0 divide-y divide-murmur-border lg:grid-cols-3 lg:divide-x lg:divide-y-0">
            {/* Left: Customer avatars */}
            <div className="p-6">
              <p className="mb-4 text-xs font-medium uppercase tracking-wider text-murmur-warm-grey">
                Your customers
              </p>
              <div className="flex flex-wrap gap-2">
                {INITIALS.map((initial, i) => (
                  <motion.div
                    key={i}
                    initial={reduced ? { opacity: 1 } : { opacity: 0, scale: 0 }}
                    animate={
                      i < avatarsShown
                        ? { opacity: 1, scale: 1 }
                        : {}
                    }
                    transition={{ duration: 0.3 }}
                    className={`flex h-9 w-9 items-center justify-center rounded-full text-xs font-semibold text-white ${
                      i >= avatarsShown ? "invisible" : ""
                    }`}
                    style={{ backgroundColor: AVATAR_COLORS[i] }}
                  >
                    {initial}
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Middle: Live transcript */}
            <div className="p-6">
              <p className="mb-4 text-xs font-medium uppercase tracking-wider text-murmur-warm-grey">
                Live responses
              </p>
              <div className="space-y-4">
                {RESPONSES.map((r, i) => (
                  <motion.div
                    key={r.name}
                    initial={reduced ? { opacity: 1 } : { opacity: 0, y: 10 }}
                    animate={
                      i < responsesShown ? { opacity: 1, y: 0 } : {}
                    }
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
                      <span className="text-sm font-medium text-murmur-ink">
                        {r.name}
                      </span>
                      <span className="text-xs text-murmur-warm-grey">
                        {r.desc}
                      </span>
                    </div>
                    <div className="mt-1.5 flex items-center gap-2">
                      <div className="h-1 flex-1 overflow-hidden rounded-full bg-murmur-border/50">
                        <motion.div
                          className={`h-full rounded-full ${r.color}`}
                          initial={{ width: 0 }}
                          animate={
                            i < responsesShown
                              ? { width: `${r.sentiment}%` }
                              : {}
                          }
                          transition={{ duration: 0.8, delay: 0.2 }}
                        />
                      </div>
                      <span className="text-[10px] text-murmur-warm-grey">
                        {r.sentiment}%
                      </span>
                    </div>
                    <p className="mt-1.5 text-xs italic text-murmur-warm-grey">
                      &ldquo;{r.quote}&rdquo;
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Right: Emerging themes */}
            <div className="p-6">
              <p className="mb-4 text-xs font-medium uppercase tracking-wider text-murmur-warm-grey">
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
                      i >= themesShown
                        ? "invisible"
                        : theme.flagged
                          ? "border-murmur-amber/30 bg-murmur-amber/5 text-murmur-amber"
                          : "border-murmur-border bg-white text-murmur-ink"
                    }`}
                  >
                    {theme.text}
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Result summary */}
          <motion.div
            initial={reduced ? { opacity: 1 } : { opacity: 0, y: 15 }}
            animate={showResult ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className={`border-t border-murmur-border bg-white p-6 ${
              !showResult ? "invisible" : ""
            }`}
          >
            <p className="text-sm font-medium text-murmur-ink">
              Most of your regulars would accept the increase. Your
              price-conscious lunch crowd is the risk -- they have alternatives
              nearby. Consider a partial increase rather than across the board.
            </p>
            <p className="mt-3 text-xs text-murmur-warm-grey">
              Caveat: This is a simulation. A real price test with a subset of
              dishes would validate this before committing fully.
            </p>
          </motion.div>

          {/* Replay + CTA */}
          <div className="flex items-center justify-between border-t border-murmur-border bg-murmur-cream/50 px-6 py-3">
            <button
              onClick={() => {
                setHasPlayed(false);
                setTimeout(() => {
                  setHasPlayed(true);
                  play();
                }, 100);
              }}
              className="text-xs text-murmur-warm-grey transition-colors hover:text-murmur-ink"
            >
              Replay
            </button>
            <a
              href="/signup"
              className="text-sm font-medium text-murmur-amber transition-colors hover:text-murmur-ink"
            >
              Try it with your business &#8594;
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
