"use client";

import SectionReveal from "./SectionReveal";

const QUOTES = [
  {
    text: "I raised my prices after Murmur told me most of my regulars would accept it. They did. I have never had that kind of confidence going into a decision before.",
    author: "Restaurant owner, Barcelona",
    tool: "Simulation",
  },
  {
    text: "Before a contract renewal I asked the twin how my client would react to a scope change. It flagged that their response times had been slowing, so I adjusted my approach and kept the account.",
    author: "Agency director, Amsterdam",
    tool: "Customer twin",
  },
  {
    text: "I was going to open Sundays. Murmur showed me the demand was not there yet. Saved me a month of exhausting shifts.",
    author: "Barber, London",
    tool: "Simulation",
  },
  {
    text: "I used the vendor twin before renegotiating with my main supplier. It predicted their counter-offer almost exactly. I walked in prepared and got better terms.",
    author: "Retail buyer, Dublin",
    tool: "Vendor twin",
  },
  {
    text: "It feels like having a conversation with your own customers, but at midnight when you are actually making the decision.",
    author: "Cafe owner, Dublin",
    tool: "Simulation",
  },
  {
    text: "We have 40 key accounts. Each one has a twin now. Before any pricing conversation, we check the twin first. It has changed how we prepare.",
    author: "SaaS founder, Berlin",
    tool: "Customer twin",
  },
];

const TOOL_COLORS: Record<string, string> = {
  Simulation: "text-brand-blue",
  "Customer twin": "text-brand-orange",
  "Vendor twin": "text-brand-pink",
};

export default function Testimonials() {
  return (
    <section className="bg-white px-6 py-24 lg:px-12 xl:px-20">
      <div className="w-full">
        <SectionReveal className="mb-16 text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-murmur-warm-grey">
            Early voices
          </p>
          <h2 className="font-serif-display text-4xl font-black leading-[1.05] tracking-[-0.025em] text-murmur-ink sm:text-5xl lg:text-6xl">
            What business owners
            <br />
            actually said
          </h2>
        </SectionReveal>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {QUOTES.map((q, i) => (
            <SectionReveal key={i} delay={i * 0.08}>
              <div className="flex h-full flex-col justify-between rounded-xl border border-murmur-border bg-murmur-cream p-6">
                <div>
                  <span
                    className={`mb-4 inline-block text-[10px] font-semibold uppercase tracking-wider ${TOOL_COLORS[q.tool]}`}
                  >
                    {q.tool}
                  </span>
                  <p className="mb-6 text-lg italic leading-relaxed text-murmur-ink">
                    &ldquo;{q.text}&rdquo;
                  </p>
                </div>
                <p className="text-base text-gray-400">-- {q.author}</p>
              </div>
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
