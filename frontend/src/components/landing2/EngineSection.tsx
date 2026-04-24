"use client";

import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import SectionReveal from "./SectionReveal";
import ContextStreams from "./engine-animations/ContextStreams";
import ConstraintLattice from "./engine-animations/ConstraintLattice";
import DendriteGrowth from "./engine-animations/DendriteGrowth";
import ConfidenceField from "./engine-animations/ConfidenceField";

const ANIMATIONS = [
  ContextStreams,
  ConstraintLattice,
  DendriteGrowth,
  ConfidenceField,
];

const POINTS = [
  {
    title: "Context-first, not prompt-first",
    body: "Before generating anything, Murmur runs up to 8 intelligence tools in parallel: competitor analysis, local demographics, pricing benchmarks, social sentiment, and more. The AI only speaks after it understands your world.",
  },
  {
    title: "Structured personas, not random generation",
    body: "Personas are not freely imagined by the AI. Each one is anchored to a fixed demographic spec (age, income, visit frequency, price sensitivity) derived from review data and industry norms. The AI adds personality within those constraints, not the other way around.",
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
        {/* Left: animation that changes per open accordion tab. */}
        <SectionReveal className="flex items-center justify-center">
          <div className="relative h-[400px] w-[400px]">
            <AnimatePresence mode="wait">
              {(() => {
                const idx = openIdx ?? 0;
                const ActiveAnimation = ANIMATIONS[idx];
                return (
                  <motion.div
                    key={idx}
                    initial={reduced ? {} : { opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={reduced ? {} : { opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    className="absolute inset-0 flex items-center justify-center"
                  >
                    <ActiveAnimation />
                  </motion.div>
                );
              })()}
            </AnimatePresence>
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
