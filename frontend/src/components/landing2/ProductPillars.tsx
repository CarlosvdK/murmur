"use client";

import SectionReveal from "./SectionReveal";

const PILLARS = [
  {
    label: "Simulate",
    color: "#448CFD",
    image: "/simulation.png",
    title: "Test any decision before you make it",
    desc: "Generate a panel of 15-75 AI customers calibrated to your business -- built from your actual customer demographics, local market data, and industry behavioural norms. Each persona is independently interviewed in a 3-turn focus group: warmup, core reaction, and depth analysis.",
    details: [
      "Includes the silent majority (55-70%) -- customers who never leave reviews but quietly decide your revenue",
      "Each persona reports what they would say AND what they would actually do -- the gap is corrected automatically",
      "Results show probability estimates and confidence intervals, not binary yes/no",
      "Live web search and semantic research lookup run before every simulation",
    ],
    examples: [
      "What if I raised prices 15%?",
      "Would customers use a loyalty app?",
      "Should I switch to appointment-only?",
      "Would free shipping over $50 increase average order?",
    ],
    best: "Any business with customers -- restaurants, SaaS, e-commerce, gyms, clinics, retail, B2B",
  },
  {
    label: "Customer twins",
    color: "#FF8720",
    image: "/customer_twin.png",
    title: "A digital copy of every relationship that matters",
    desc: "Upload your real conversations -- WhatsApp, email, meeting notes -- and Murmur builds a digital twin of that specific person. Not a generic archetype, but a model of how this individual communicates, decides, objects, and responds.",
    details: [
      "Extracts communication patterns: response time, formality, decision style, objection tendencies, priorities",
      "Enriched with cultural psychology for the contact's country and live web intelligence on every query",
      "Automatic health signals: detects when response times increase, formality shifts, or sentiment drops",
      "Your raw correspondence is processed in memory and immediately deleted -- only patterns are kept",
    ],
    examples: [
      "Would Sarah accept a 20% rate increase?",
      "How should I pitch this new service to David?",
      "Is this client at risk of leaving?",
      "What is the best way to deliver bad news to this person?",
    ],
    best: "Fewer than 100 high-value clients who make up the bulk of your revenue -- agencies, consultants, B2B, private practices, luxury services",
  },
  {
    label: "Vendor twins",
    color: "#FF8DE4",
    image: "/vendor_twin.png",
    title: "Walk into every negotiation prepared",
    desc: "Build digital twins of your suppliers, partners, and vendors from your correspondence history. Murmur analyses their negotiation patterns, communication style, and decision-making tendencies. Before any contract renewal, price discussion, or difficult conversation, ask the twin what to expect and how to prepare.",
    details: [
      "Negotiation pattern analysis: how they respond to pushback, their typical counter-offer range, what concessions they prioritise",
      "Communication style profiling: formality level, response speed, who initiates, typical objections",
      "Grounded in behavioural research on B2B negotiation and supplier relationship dynamics",
      "Preparation tips generated for every query -- concrete things to do before the conversation",
    ],
    examples: [
      "Will my supplier accept 60-day payment terms?",
      "What is their likely counter-offer on bulk discount?",
      "How would they react if I shifted 30% of volume elsewhere?",
      "Should I renegotiate now or wait until renewal?",
    ],
    best: "Any business that negotiates with suppliers, freelancers, landlords, or partners",
  },
];

export default function ProductPillars() {
  return (
    <section id="product" className="bg-[#F5F3EF] px-6 py-28 lg:px-12 xl:px-20">
      <div className="mx-auto max-w-[1400px]">
        <SectionReveal className="mx-auto mb-20 max-w-3xl text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-gray-400">
            Three tools, one platform
          </p>
          <h2 className="mb-6 text-4xl font-black leading-[1.05] tracking-[-0.025em] text-black sm:text-5xl lg:text-6xl">
            CRM that understands
            <br />
            your relationships
          </h2>
          <p className="text-xl leading-relaxed text-gray-500">
            Traditional CRMs store data. Murmur thinks with it. Simulate decisions
            across your entire customer base, or zoom into individual relationships
            with digital twins built from your real conversations.
          </p>
        </SectionReveal>

        <div className="space-y-20">
          {PILLARS.map((p, i) => (
            <SectionReveal key={p.label} delay={0.1}>
              <div className={`grid items-center gap-10 lg:grid-cols-2 ${i % 2 === 1 ? "lg:direction-rtl" : ""}`}>
                {/* Image side */}
                <div className={`overflow-hidden rounded-2xl ${i % 2 === 1 ? "lg:order-2" : ""}`}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={p.image}
                    alt={p.label}
                    className="w-full rounded-2xl object-cover"
                  />
                </div>

                {/* Content side */}
                <div className={i % 2 === 1 ? "lg:order-1" : ""}>
                  <div
                    className="mb-4 h-1 w-12 rounded-full"
                    style={{ backgroundColor: p.color }}
                  />
                  <p
                    className="mb-2 text-sm font-bold uppercase tracking-[0.12em]"
                    style={{ color: p.color }}
                  >
                    {p.label}
                  </p>

                  <h3 className="mb-4 text-3xl font-black tracking-tight text-black lg:text-4xl">
                    {p.title}
                  </h3>

                  <p className="mb-6 text-base leading-relaxed text-gray-500">
                    {p.desc}
                  </p>

                  {/* Detail bullets */}
                  <ul className="mb-6 space-y-2">
                    {p.details.map((d) => (
                      <li key={d} className="flex items-start gap-2 text-sm text-gray-500">
                        <span className="mt-1 shrink-0 text-xs" style={{ color: p.color }}>&#9679;</span>
                        {d}
                      </li>
                    ))}
                  </ul>

                  {/* Example questions */}
                  <div className="mb-6 rounded-xl bg-gray-50 p-5">
                    <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Example questions</p>
                    <div className="space-y-1.5">
                      {p.examples.map((ex) => (
                        <p key={ex} className="text-sm italic text-gray-500">
                          &ldquo;{ex}&rdquo;
                        </p>
                      ))}
                    </div>
                  </div>

                  {/* Best for */}
                  <div className="rounded-lg border border-gray-200 px-4 py-3">
                    <p className="text-xs font-medium text-gray-400">Best for</p>
                    <p className="text-sm text-gray-600">{p.best}</p>
                  </div>
                </div>
              </div>
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
