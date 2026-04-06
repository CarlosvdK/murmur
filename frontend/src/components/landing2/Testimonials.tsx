"use client";

import SectionReveal from "./SectionReveal";

const QUOTES = [
  {
    text: "I raised my prices after Murmur told me most of my regulars would accept it. They did. I've never had that kind of confidence going into a decision before.",
    author: "Restaurant owner, Barcelona",
  },
  {
    text: "I was going to open Sundays. Murmur showed me the demand wasn't there yet. Saved me a month of exhausting shifts.",
    author: "Barber, London",
  },
  {
    text: "It feels like having a conversation with your own customers -- but at midnight when you're actually making the decision.",
    author: "Cafe owner, Dublin",
  },
];

export default function Testimonials() {
  return (
    <section className="px-8 py-24 lg:px-16 xl:px-24">
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

        <div className="grid gap-6 md:grid-cols-3">
          {QUOTES.map((q, i) => (
            <SectionReveal key={i} delay={i * 0.1}>
              <div className="flex h-full flex-col justify-between rounded-xl border border-murmur-border bg-murmur-cream p-6">
                <p className="mb-6 text-lg italic leading-relaxed text-murmur-ink">
                  &ldquo;{q.text}&rdquo;
                </p>
                <p className="text-base text-gray-400">-- {q.author}</p>
              </div>
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
