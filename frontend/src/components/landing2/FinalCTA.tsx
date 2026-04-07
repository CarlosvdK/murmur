"use client";

import SectionReveal from "./SectionReveal";

export default function FinalCTA() {
  return (
    <section className="grad-c-animate px-8 py-24 lg:px-16 xl:px-24">
      <div className="mx-auto max-w-3xl text-center">
        <SectionReveal>
          <h2 className="mb-4 text-[clamp(36px,5vw,64px)] font-black leading-[1.05] tracking-[-0.025em] text-white">
            Ask your first question today.
          </h2>
          <p className="mb-10 text-white/70">
            No credit card. No data science degree.
            <br />
            Just describe your business and ask.
          </p>
        </SectionReveal>

        <SectionReveal delay={0.2}>
          <a
            href="/signup"
            className="inline-block rounded-full bg-black px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-900 hover:scale-[1.02]"
          >
            Create an account
          </a>
        </SectionReveal>

        <SectionReveal delay={0.3}>
          <p className="mt-8 text-xs text-white/50">
            Your first simulation is free. No credit card required.
          </p>
        </SectionReveal>
      </div>
    </section>
  );
}
