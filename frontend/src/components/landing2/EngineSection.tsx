"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import SectionReveal from "./SectionReveal";

const POINTS = [
  {
    title: "Built from real-world context, not assumptions",
    body: "Before generating a single simulated customer, Murmur gathers real intelligence about your business, your market, and your area. The simulation reflects your actual situation -- not a generic version of it.",
  },
  {
    title: "Diverse customers, including the ones who never speak up",
    body: "Most feedback tools only capture the loudest voices. Murmur deliberately includes the customers who never leave reviews, never complain, and quietly make decisions. They're often the ones who matter most.",
  },
  {
    title: "Honest about what it doesn't know",
    body: "Every simulation includes clear caveats. If the signal is weak, we say so. If a real test would give you more confidence, we recommend it. We reduce risk -- we don't replace judgment.",
  },
];

export default function EngineSection() {
  const [openIdx, setOpenIdx] = useState<number | null>(0);
  const reduced = useReducedMotion();

  return (
    <section className="px-8 py-28 lg:px-16 xl:px-24">
      {/* REVERSED: diagram LEFT, text RIGHT */}
      <div className="mx-auto grid max-w-7xl gap-16 lg:grid-cols-2">
        {/* Left: diagram */}
        <SectionReveal className="flex items-center justify-center">
          <div className="w-full max-w-sm">
            <div className="mb-6 flex flex-wrap justify-center gap-3">
              {Array.from({ length: 8 }).map((_, i) => (
                <motion.div
                  key={i}
                  className="h-3.5 w-3.5 rounded-full"
                  style={{ backgroundColor: ["#448CFD", "#FF8DE4", "#FF8720"][i % 3] }}
                  animate={{ scale: [1, 1.3, 1], opacity: [0.4, 0.8, 0.4] }}
                  transition={{ duration: 2.5, delay: i * 0.3, repeat: Infinity, repeatDelay: 2 }}
                />
              ))}
            </div>
            <div className="flex justify-center"><div className="h-10 w-px bg-gray-200" /></div>
            <div className="flex justify-center py-3">
              <motion.div
                className="flex h-20 w-20 items-center justify-center rounded-full border-2 border-brand-orange bg-brand-orange/5"
                animate={{ rotate: 360 }}
                transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
              >
                <span className="text-xl font-black text-brand-orange">M</span>
              </motion.div>
            </div>
            <div className="flex justify-center"><div className="h-10 w-px bg-gray-200" /></div>
            <div className="flex flex-wrap justify-center gap-2.5">
              {Array.from({ length: 15 }).map((_, i) => (
                <motion.div
                  key={i}
                  className="h-4.5 w-4.5 rounded-full"
                  style={{
                    width: 18, height: 18,
                    backgroundColor: ["#448CFD", "#FF8DE4", "#FF8720", "#6EB0FF"][i % 4],
                  }}
                  animate={{ opacity: [0.35, 0.75, 0.35] }}
                  transition={{ duration: 3, delay: i * 0.2, repeat: Infinity }}
                />
              ))}
            </div>
          </div>
        </SectionReveal>

        {/* Right: text with accordion */}
        <SectionReveal delay={0.15}>
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-gray-400">
            What makes it work
          </p>
          <h2 className="mb-8 text-4xl font-black leading-[1.05] tracking-[-0.025em] text-black sm:text-5xl lg:text-6xl">
            Not a chatbot.
            <br />
            Not a survey.
          </h2>

          <div className="space-y-0 divide-y divide-gray-200">
            {POINTS.map((point, i) => (
              <div key={i} className="py-5">
                <button
                  onClick={() => setOpenIdx(openIdx === i ? null : i)}
                  className="flex w-full items-start justify-between text-left"
                >
                  <span className="pr-4 text-lg font-semibold text-black">
                    {point.title}
                  </span>
                  <span className="mt-1 shrink-0 text-lg text-gray-400">
                    {openIdx === i ? "−" : "+"}
                  </span>
                </button>
                <AnimatePresence>
                  {openIdx === i && (
                    <motion.div
                      initial={reduced ? {} : { height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={reduced ? {} : { height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <p className="pt-3 text-base leading-relaxed text-gray-500">
                        {point.body}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </SectionReveal>
      </div>
    </section>
  );
}
