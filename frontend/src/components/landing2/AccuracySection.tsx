"use client";

import { useCountUp } from "./useCountUp";
import SectionReveal from "./SectionReveal";

export default function AccuracySection() {
  const gap = useCountUp(28, 1.2, "%");
  const cultural = useCountUp(109, 1.2, "");
  const segments = useCountUp(243, 1.2, "");

  return (
    <section id="accuracy" className="bg-[#F5F3EF] px-6 py-28 lg:px-12 xl:px-20">
      <div className="mx-auto max-w-[1400px]">
        <SectionReveal className="mx-auto mb-16 max-w-3xl text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-gray-400">
            The science
          </p>
          <h2 className="mb-6 text-4xl font-black leading-[1.05] tracking-[-0.025em] text-black sm:text-5xl lg:text-6xl">
            Built on research
          </h2>
          <p className="text-xl leading-relaxed text-gray-500">
            Murmur does not prompt-engineer its way to answers. The architecture
            encodes peer-reviewed findings into every step: from persona generation
            to interview design to impact estimation.
          </p>
        </SectionReveal>

        <div className="grid gap-6 md:grid-cols-3">
          <SectionReveal>
            <div className="rounded-2xl border border-gray-200 bg-white p-8">
              <p ref={gap.ref} className="text-5xl font-black text-black">
                {gap.display}
              </p>
              <p className="mt-3 text-base font-semibold text-black">Say-do gap correction</p>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                Murphy et al. (2005) found people overstate their intentions by 28%. Every
                Murmur persona reports both what they would say and what they would actually
                do, and the aggregation corrects for the difference.
              </p>
            </div>
          </SectionReveal>

          <SectionReveal delay={0.08}>
            <div className="rounded-2xl border border-gray-200 bg-white p-8">
              <p ref={cultural.ref} className="text-5xl font-black text-black">
                {cultural.display}
              </p>
              <p className="mt-3 text-base font-semibold text-black">Industry behaviour profiles</p>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                Each simulation loads industry-specific norms (decision speed, switching cost,
                loyalty drivers, price sensitivity) so a gym member behaves differently from
                a SaaS subscriber.
              </p>
            </div>
          </SectionReveal>

          <SectionReveal delay={0.16}>
            <div className="rounded-2xl border border-gray-200 bg-white p-8">
              <p ref={segments.ref} className="text-5xl font-black text-black">
                {segments.display}
              </p>
              <p className="mt-3 text-base font-semibold text-black">Business type mappings</p>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                From taco trucks to SaaS platforms to dental practices. Customer segment
                templates, engagement models, and spend patterns adapt automatically
                to your specific business type.
              </p>
            </div>
          </SectionReveal>
        </div>

        <SectionReveal className="mx-auto mt-12 max-w-2xl text-center">
          <p className="text-lg leading-relaxed text-gray-500">
            Every result includes confidence intervals and caveats. When the signal
            is weak, we say so. A simulation reduces risk, it does not replace judgment.
          </p>
        </SectionReveal>
      </div>
    </section>
  );
}
