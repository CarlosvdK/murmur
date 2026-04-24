"use client";

import SectionReveal from "./SectionReveal";
import Murmuration from "./Murmuration";

export default function FinalCTA() {
  return (
    <section className="relative overflow-hidden bg-[#F5F3EF] px-6 py-28 lg:px-12 xl:px-20">
      {/* Murmuration dots -- decorative, does not react to input (see Murmuration.tsx) */}
      <Murmuration />

      <div className="relative z-10 mx-auto max-w-4xl text-center">
        <SectionReveal>
          <h2 className="mb-6 text-[clamp(36px,5vw,64px)] font-black leading-[1.05] tracking-[-0.025em] text-black">
            Stop guessing.
            <br />
            Start simulating.
          </h2>
          <p className="mx-auto mb-12 max-w-2xl text-lg text-gray-600">
            Your first simulation is free. No credit card, no setup, no surveys to design.
            Just describe your business and ask.
          </p>
        </SectionReveal>

        <SectionReveal delay={0.2}>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <a
              href="/signup"
              className="rounded-full bg-black px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-gray-900 hover:scale-[1.02]"
            >
              Start for free
            </a>
            <a
              href="#product"
              className="rounded-full border border-gray-400 bg-white/60 px-8 py-3.5 text-sm font-medium text-black backdrop-blur-sm transition-colors hover:border-gray-600"
            >
              See the three tools
            </a>
          </div>
        </SectionReveal>
      </div>
    </section>
  );
}
