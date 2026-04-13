"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import SectionReveal from "./SectionReveal";

const POINTS = [
  {
    title: "Context-first, not prompt-first",
    body: "Before generating anything, Murmur runs up to 8 intelligence tools in parallel -- competitor analysis, local demographics, pricing benchmarks, social sentiment, and more. The AI only speaks after it understands your world.",
  },
  {
    title: "Structured personas, not random generation",
    body: "Personas are not freely imagined by the AI. Each one is anchored to a fixed demographic spec -- age, income, visit frequency, price sensitivity -- derived from review data and industry norms. The AI adds personality within those constraints, not the other way around.",
  },
  {
    title: "Twins grow smarter over time",
    body: "Every conversation you upload adds to the twin's pattern model. Early queries work from basic profile data. After 50+ messages, the twin can predict response style, objection patterns, and negotiation tendencies with high confidence.",
  },
  {
    title: "Designed to be wrong sometimes",
    body: "We calibrate for honesty, not optimism. If the data is thin, the confidence drops. If personas disagree, you see the tension. If a real test would give better answers, we tell you. Murmur is a preparation tool, not an oracle.",
  },
];

export default function EngineSection() {
  const [openIdx, setOpenIdx] = useState<number | null>(0);
  const reduced = useReducedMotion();

  return (
    <section className="bg-[#F5F3EF] px-6 py-28 lg:px-12 xl:px-20">
      {/* REVERSED: diagram LEFT, text RIGHT */}
      <div className="mx-auto grid max-w-[1400px] gap-16 lg:grid-cols-2">
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
                    {openIdx === i ? "\u2212" : "+"}
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
