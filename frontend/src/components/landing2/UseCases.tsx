"use client";

import SectionReveal from "./SectionReveal";

const CASES = [
  {
    type: "Restaurant",
    tool: "Simulate",
    q: "Should I raise weekend prices by 15%?",
    result: "Regulars accepting -- Lunch crowd at risk",
  },
  {
    type: "Consulting firm",
    tool: "Customer twin",
    q: "Would our biggest client accept a 20% rate increase?",
    result: "High confidence they will accept if tied to new deliverables",
  },
  {
    type: "B2B supplier",
    tool: "Vendor twin",
    q: "Will our main supplier accept 60-day payment terms?",
    result: "Likely to counter with 45 days -- prepare volume commitment",
  },
  {
    type: "Barber Shop",
    tool: "Simulate",
    q: "Would customers come in on Sundays?",
    result: "Strong demand in 30-45 age group",
  },
  {
    type: "Design agency",
    tool: "Customer twin",
    q: "Is this client at risk of churning?",
    result: "Response time increasing, formality rising -- schedule a check-in",
  },
  {
    type: "Gym",
    tool: "Simulate",
    q: "Would members accept a 10% price increase?",
    result: "Loyal members accepting -- At-risk: casual users",
  },
  {
    type: "E-commerce",
    tool: "Simulate",
    q: "Would free shipping over $50 increase average order?",
    result: "Under-35s strongly influenced -- older segments indifferent",
  },
  {
    type: "Private practice",
    tool: "Customer twin",
    q: "How should I communicate my new cancellation policy?",
    result: "Frame as availability improvement, not penalty -- matches their values",
  },
  {
    type: "Retailer",
    tool: "Vendor twin",
    q: "What is my supplier's likely counter-offer on bulk discount?",
    result: "Pattern suggests 8-12% based on prior negotiations",
  },
];

const TOOL_COLORS: Record<string, string> = {
  Simulate: "text-brand-blue bg-brand-blue/10",
  "Customer twin": "text-brand-orange bg-brand-orange/10",
  "Vendor twin": "text-brand-pink bg-brand-pink/10",
};

export default function UseCases() {
  return (
    <section id="use-cases" className="bg-white px-6 py-24 lg:px-12 xl:px-20">
      <div className="w-full">
        <SectionReveal className="mb-16 text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-murmur-warm-grey">
            Who uses Murmur
          </p>
          <h2 className="mb-4 font-serif-display text-4xl font-black leading-[1.05] tracking-[-0.025em] text-murmur-ink sm:text-5xl lg:text-6xl">
            Every industry. Every question.
            <br />
            Every relationship.
          </h2>
        </SectionReveal>

        {/* Cards grid -- horizontal scroll on mobile */}
        <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory md:grid md:grid-cols-3 md:overflow-visible md:pb-0">
          {CASES.map((c, i) => (
            <SectionReveal key={`${c.type}-${c.tool}`} delay={i * 0.04}>
              <div className="min-w-[280px] snap-start rounded-xl border border-murmur-border bg-murmur-cream p-6 transition-all hover:-translate-y-1 hover:shadow-md md:min-w-0">
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-sm font-medium uppercase tracking-wider text-murmur-warm-grey">
                    {c.type}
                  </p>
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${TOOL_COLORS[c.tool]}`}
                  >
                    {c.tool}
                  </span>
                </div>
                <p className="mb-4 text-lg font-medium italic text-murmur-ink">
                  &ldquo;{c.q}&rdquo;
                </p>
                <div className="flex items-start gap-1.5">
                  <span className="mt-0.5 text-xs text-murmur-amber">&#8594;</span>
                  <span className="text-sm text-gray-500">{c.result}</span>
                </div>
              </div>
            </SectionReveal>
          ))}
        </div>

        <SectionReveal className="mt-12 text-center">
          <p className="text-sm text-murmur-warm-grey">
            Murmur works for any business -- from solo consultants to multi-location retailers.
          </p>
          <a
            href="/signup"
            className="mt-2 inline-block text-sm font-medium text-murmur-amber transition-colors hover:text-murmur-ink"
          >
            Start for free &#8594;
          </a>
        </SectionReveal>
      </div>
    </section>
  );
}
