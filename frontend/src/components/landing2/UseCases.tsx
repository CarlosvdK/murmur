"use client";

import SectionReveal from "./SectionReveal";

const CASES = [
  { type: "Restaurant", q: "Should I raise weekend prices by 15%?", result: "Regulars accepting -- Lunch crowd at risk" },
  { type: "Barber Shop", q: "Would customers come in on Sundays?", result: "Strong demand in 30-45 age group" },
  { type: "Cafe", q: "Would a loyalty card keep people coming back?", result: "Most regulars would use it -- New customers less likely" },
  { type: "Boutique", q: "Should I move to appointment-only?", result: "Divided response -- Strong preference for walk-in" },
  { type: "Gym", q: "Would members accept a 10% price increase?", result: "Loyal members accepting -- At-risk: casual users" },
  { type: "Grocery Store", q: "Would customers use self-checkout?", result: "Under-40s enthusiastic -- Over-60s strongly opposed" },
];

export default function UseCases() {
  return (
    <section id="use-cases" className="px-8 py-24 lg:px-16 xl:px-24">
      <div className="w-full">
        <SectionReveal className="mb-16 text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-murmur-warm-grey">
            Who uses Murmur
          </p>
          <h2 className="mb-4 font-serif-display text-4xl font-black leading-[1.05] tracking-[-0.025em] text-murmur-ink sm:text-5xl lg:text-6xl">
            Any business with customers
            <br />
            can ask any question
          </h2>
        </SectionReveal>

        {/* Cards grid -- horizontal scroll on mobile */}
        <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory md:grid md:grid-cols-3 md:overflow-visible md:pb-0">
          {CASES.map((c, i) => (
            <SectionReveal key={c.type} delay={i * 0.05}>
              <div className="min-w-[260px] snap-start rounded-xl border border-murmur-border bg-murmur-cream p-6 transition-all hover:-translate-y-1 hover:shadow-md md:min-w-0">
                <p className="mb-3 text-sm font-medium uppercase tracking-wider text-murmur-warm-grey">
                  {c.type}
                </p>
                <p className="mb-4 text-lg font-medium italic text-murmur-ink">
                  &ldquo;{c.q}&rdquo;
                </p>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-murmur-amber">&#8594;</span>
                  <span className="text-sm text-gray-500">
                    {c.result}
                  </span>
                </div>
              </div>
            </SectionReveal>
          ))}
        </div>

        <SectionReveal className="mt-12 text-center">
          <p className="text-sm text-murmur-warm-grey">
            Not on this list? Murmur works for any business with customers.
          </p>
          <a
            href="/signup"
            className="mt-2 inline-block text-sm font-medium text-murmur-amber transition-colors hover:text-murmur-ink"
          >
            Tell us your use case &#8594;
          </a>
        </SectionReveal>
      </div>
    </section>
  );
}
