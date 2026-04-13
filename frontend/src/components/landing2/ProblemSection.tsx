"use client";

import { motion, useReducedMotion } from "framer-motion";
import SectionReveal from "./SectionReveal";

export default function ProblemSection() {
  const reduced = useReducedMotion();

  return (
    <section className="bg-white px-6 py-28 lg:px-12 xl:px-20">
      <div className="mx-auto max-w-[1400px]">
        <SectionReveal className="mx-auto mb-16 max-w-3xl text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-gray-400">
            The problem
          </p>
          <h2 className="mb-6 text-4xl font-black leading-[1.05] tracking-[-0.025em] text-black sm:text-5xl lg:text-6xl">
            Your CRM stores data.
            <br />
            It doesn&apos;t think.
          </h2>
          <p className="text-xl leading-relaxed text-gray-500">
            You know what your customers bought last month. But you have no idea
            how they would react if you changed your prices tomorrow. You know your
            vendor&apos;s email address, but not their negotiation patterns. Traditional
            CRMs are filing cabinets. Murmur is a thinking partner.
          </p>
        </SectionReveal>

        <div className="grid gap-6 lg:grid-cols-3">
          <SectionReveal>
            <div className="h-full rounded-2xl border border-gray-200 bg-white p-8 opacity-60">
              <p className="mb-4 text-sm font-medium uppercase tracking-wider text-gray-400 line-through">
                Traditional CRM
              </p>
              <ul className="space-y-3 text-sm text-gray-400">
                <li>Stores contact details and deal stages</li>
                <li>Tracks what already happened</li>
                <li>Cannot predict how anyone will react</li>
                <li>No intelligence about relationships</li>
                <li>Just a database with a nice UI</li>
              </ul>
            </div>
          </SectionReveal>

          <SectionReveal delay={0.1}>
            <div className="h-full rounded-2xl border border-gray-200 bg-white p-8 opacity-60">
              <p className="mb-4 text-sm font-medium uppercase tracking-wider text-gray-400 line-through">
                Market research
              </p>
              <ul className="space-y-3 text-sm text-gray-400">
                <li>Costs thousands per study</li>
                <li>Takes 2-6 weeks to recruit and run</li>
                <li>Generic panels, not your actual customers</li>
                <li>Surveys capture what people say, not what they do</li>
                <li>Results are stale by the time you get them</li>
              </ul>
            </div>
          </SectionReveal>

          <SectionReveal delay={0.2}>
            <motion.div
              initial={reduced ? {} : { opacity: 0, scale: 0.98 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4, duration: 0.5 }}
              className="h-full rounded-2xl border-2 border-brand-orange/30 bg-brand-orange/5 p-8"
            >
              <p className="mb-4 text-sm font-medium uppercase tracking-wider text-brand-orange">
                Murmur
              </p>
              <ul className="space-y-3 text-sm font-medium text-black">
                <li>Simulates your actual customer base in 60 seconds</li>
                <li>Predicts reactions before you make the change</li>
                <li>Digital twins of individual customers and vendors</li>
                <li>Corrects for the gap between what people say and do</li>
                <li>Grounded in 32 research domains and live market data</li>
              </ul>
            </motion.div>
          </SectionReveal>
        </div>
      </div>
    </section>
  );
}
