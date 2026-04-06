"use client";

import { motion, useReducedMotion } from "framer-motion";
import SectionReveal from "./SectionReveal";

export default function ProblemSection() {
  const reduced = useReducedMotion();

  return (
    <section className="px-8 py-28 lg:px-16 xl:px-24">
      <div className="mx-auto max-w-7xl">
        {/* Text centered above */}
        <SectionReveal className="mx-auto mb-16 max-w-3xl text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-gray-400">
            The alternative
          </p>
          <h2 className="mb-6 text-4xl font-black leading-[1.05] tracking-[-0.025em] text-black sm:text-5xl lg:text-6xl">
            Most small business decisions are made on gut feel.
          </h2>
          <p className="text-xl leading-relaxed text-gray-500">
            You raise prices and hope for the best. You change your hours and
            see what happens. Market research costs thousands and takes weeks.
            Murmur gives you the same advantage. In 60 seconds.
          </p>
        </SectionReveal>

        {/* Two path cards side by side */}
        <div className="grid gap-6 lg:grid-cols-2">
          <SectionReveal>
            <div className="h-full rounded-2xl border border-gray-200 bg-white p-8 opacity-60">
              <p className="mb-4 text-sm font-medium uppercase tracking-wider text-gray-400 line-through">
                Traditional route
              </p>
              <div className="flex flex-wrap items-center gap-2 text-base text-gray-400">
                <span className="rounded-lg border border-gray-200 px-3 py-1.5">Survey design</span>
                <span className="text-gray-300">&#8594;</span>
                <span className="rounded-lg border border-gray-200 px-3 py-1.5">Recruit (2-4 weeks)</span>
                <span className="text-gray-300">&#8594;</span>
                <span className="rounded-lg border border-gray-200 px-3 py-1.5">Run study</span>
                <span className="text-gray-300">&#8594;</span>
                <span className="rounded-lg border border-gray-200 px-3 py-1.5">Analyse</span>
                <span className="text-gray-300">&#8594;</span>
                <span className="rounded-lg border border-gray-200 px-3 py-1.5">Maybe get an answer</span>
              </div>
            </div>
          </SectionReveal>

          <SectionReveal delay={0.15}>
            <motion.div
              initial={reduced ? {} : { opacity: 0, scale: 0.98 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="h-full rounded-2xl border-2 border-brand-orange/30 bg-brand-orange/5 p-8"
            >
              <p className="mb-4 text-sm font-medium uppercase tracking-wider text-brand-orange">
                Murmur
              </p>
              <div className="flex flex-wrap items-center gap-3 text-base font-medium text-black">
                <span className="rounded-lg bg-brand-orange/10 px-4 py-2">Describe your business</span>
                <span className="text-brand-orange">&#8594;</span>
                <span className="rounded-lg bg-brand-orange/10 px-4 py-2">Ask your question</span>
                <span className="text-brand-orange">&#8594;</span>
                <span className="rounded-lg bg-brand-orange/10 px-4 py-2">Get your answer</span>
              </div>
            </motion.div>
          </SectionReveal>
        </div>
      </div>
    </section>
  );
}
