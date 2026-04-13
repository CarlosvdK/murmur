"use client";

import { useCountUp } from "./useCountUp";
import SectionReveal from "./SectionReveal";

function AnimatedStatCard({
  value,
  suffix,
  title,
  desc,
}: {
  value: number;
  suffix: string;
  title: string;
  desc: string;
}) {
  const counter = useCountUp(value, 1.2, suffix);
  return (
    <div className="rounded-2xl bg-white/90 p-8 backdrop-blur-sm">
      <p ref={counter.ref} className="mb-4 text-5xl font-black tracking-tight text-black lg:text-6xl">
        {counter.display}
      </p>
      <p className="mb-2 text-sm font-semibold text-murmur-ink">{title}</p>
      <p className="text-sm leading-relaxed text-murmur-warm-grey">{desc}</p>
    </div>
  );
}

function StaticStatCard({
  value,
  title,
  desc,
}: {
  value: string;
  title: string;
  desc: string;
}) {
  return (
    <div className="rounded-2xl bg-white/90 p-8 backdrop-blur-sm">
      <p className="mb-4 text-5xl font-black tracking-tight text-black lg:text-6xl">
        {value}
      </p>
      <p className="mb-2 text-sm font-semibold text-murmur-ink">{title}</p>
      <p className="text-sm leading-relaxed text-murmur-warm-grey">{desc}</p>
    </div>
  );
}

export default function TrustBar() {
  return (
    <section className="grad-c-animate px-6 py-20 lg:px-12 xl:px-20">
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <SectionReveal>
          <AnimatedStatCard
            value={86}
            suffix="%"
            title="Backtest accuracy"
            desc="Predicted the correct outcome in 30 of 35 published A/B test cases."
          />
        </SectionReveal>
        <SectionReveal delay={0.1}>
          <AnimatedStatCard
            value={225}
            suffix=""
            title="Research sections"
            desc="Behavioural science embedded via semantic search -- from pricing psychology to negotiation dynamics."
          />
        </SectionReveal>
        <SectionReveal delay={0.2}>
          <StaticStatCard
            value="3"
            title="Intelligence layers"
            desc="Customer simulation, individual customer twins, and vendor twins. One platform for every decision."
          />
        </SectionReveal>
        <SectionReveal delay={0.3}>
          <StaticStatCard
            value="0"
            title="Raw data stored"
            desc="Twins extract communication patterns only. Correspondence is processed in memory and immediately deleted."
          />
        </SectionReveal>
      </div>
    </section>
  );
}
