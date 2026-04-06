"use client";

import { useCountUp } from "./useCountUp";
import SectionReveal from "./SectionReveal";

export default function AccuracySection() {
  const backtest = useCountUp(70, 1.2, "%+");
  const parity = useCountUp(85, 1.2, "-92%");
  const papers = useCountUp(21, 1.2, "+");

  return (
    <section id="accuracy" className="px-8 py-28 lg:px-16 xl:px-24">
      <div className="mx-auto max-w-7xl">
        {/* Centered header */}
        <SectionReveal className="mx-auto mb-16 max-w-3xl text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-gray-400">
            The science
          </p>
          <h2 className="text-4xl font-black leading-[1.05] tracking-[-0.025em] text-black sm:text-5xl lg:text-6xl">
            We obsess over
            <br />
            getting it right
          </h2>
        </SectionReveal>

        {/* Stats grid */}
        <div className="grid gap-8 md:grid-cols-3">
          <SectionReveal>
            <div className="rounded-2xl border border-gray-200 bg-[#F5F3EF] p-8">
              <p ref={backtest.ref} className="text-5xl font-black text-black">
                {backtest.display}
              </p>
              <p className="mt-3 text-base font-semibold text-black">Backtest accuracy</p>
              <p className="mt-2 text-base leading-relaxed text-gray-500">
                We test against published real-world A/B test results. 70% of the
                time, we predict the right winner.
              </p>
            </div>
          </SectionReveal>

          <SectionReveal delay={0.1}>
            <div className="rounded-2xl border border-gray-200 bg-[#F5F3EF] p-8">
              <p ref={parity.ref} className="text-5xl font-black text-black">
                {parity.display}
              </p>
              <p className="mt-3 text-base font-semibold text-black">Parity with real feedback</p>
              <p className="mt-2 text-base leading-relaxed text-gray-500">
                Themes, concerns, and key tensions overlap 85-92% with real
                customer interviews.
              </p>
            </div>
          </SectionReveal>

          <SectionReveal delay={0.2}>
            <div className="rounded-2xl border border-gray-200 bg-[#F5F3EF] p-8">
              <p ref={papers.ref} className="text-5xl font-black text-black">
                {papers.display}
              </p>
              <p className="mt-3 text-base font-semibold text-black">Research papers</p>
              <p className="mt-2 text-base leading-relaxed text-gray-500">
                Validated in peer-reviewed research including Science Magazine,
                SAGE Journals, and Nature.
              </p>
            </div>
          </SectionReveal>
        </div>

        <SectionReveal className="mx-auto mt-12 max-w-2xl text-center">
          <p className="text-lg leading-relaxed text-gray-500">
            We will always tell you when we are uncertain. A simulation is a
            starting point -- not a final answer.
          </p>
        </SectionReveal>
      </div>
    </section>
  );
}
