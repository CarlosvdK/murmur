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
  title,
  desc,
}: {
  title: string;
  desc: string;
}) {
  return (
    <div className="rounded-2xl bg-white/90 p-8 backdrop-blur-sm">
      <p className="mb-4 text-5xl font-black tracking-tight text-black lg:text-6xl">
        {title}
      </p>
      <p className="text-sm leading-relaxed text-murmur-warm-grey">{desc}</p>
    </div>
  );
}

export default function TrustBar() {
  return (
    <section className="grad-c-animate px-8 py-20 lg:px-16 xl:px-24">
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <SectionReveal>
          <AnimatedStatCard
            value={85}
            suffix=" - 92%"
            title="Synthetic-organic parity"
            desc="Measured across thematic overlap, depth and qualitative alignment"
          />
        </SectionReveal>
        <SectionReveal delay={0.1}>
          <AnimatedStatCard
            value={21}
            suffix="+"
            title="Peer-reviewed papers"
            desc="Incl. Science Magazine, The Atlantic, SAGE Journals"
          />
        </SectionReveal>
        <SectionReveal delay={0.2}>
          <StaticStatCard
            title="$2 - 60"
            desc="Per interview, versus $100+ with traditional research agencies. No recruitment fees, no scheduling overhead."
          />
        </SectionReveal>
        <SectionReveal delay={0.3}>
          <StaticStatCard
            title="60s"
            desc="Average time from question to full customer feedback report. No waiting for participants."
          />
        </SectionReveal>
      </div>
    </section>
  );
}
