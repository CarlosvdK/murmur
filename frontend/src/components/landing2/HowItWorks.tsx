"use client";

import SectionReveal from "./SectionReveal";

const STEPS = [
  {
    num: "01",
    title: "Tell us about your business",
    desc: "Answer a few plain-English questions about your business, your customers, and what you're deciding. No forms. No jargon. Just describe it like you'd explain it to a friend.",
  },
  {
    num: "02",
    title: "We do our research",
    desc: "Before building anything, Murmur gathers real-world context about your market, your area, and your customers. This is what makes the simulation specific to you -- not generic.",
  },
  {
    num: "03",
    title: "Your customers come to life",
    desc: "We generate a diverse group of simulated customers -- each with their own personality, spending habits, loyalty level, and relationship with your business. Including the ones who'd never leave you a review.",
  },
  {
    num: "04",
    title: "Honest, plain-English results",
    desc: "Each customer answers your question in their own voice. You see the themes, the tension points, and a clear recommendation -- with honest caveats about what we don't know.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="px-8 py-28 lg:px-16 xl:px-24">
      <div className="mx-auto max-w-7xl">
        {/* Centered header */}
        <SectionReveal className="mx-auto mb-16 max-w-3xl text-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.15em] text-gray-400">
            The process
          </p>
          <h2 className="mb-4 text-4xl font-black leading-[1.05] tracking-[-0.025em] text-black sm:text-5xl lg:text-6xl">
            From question to clarity
            <br />
            in under a minute
          </h2>
          <p className="text-xl text-gray-500">
            No data science. No surveys. No waiting.
          </p>
        </SectionReveal>

        {/* 4 step cards in a grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((step, i) => (
            <SectionReveal key={step.num} delay={i * 0.08}>
              <div className="h-full rounded-2xl border border-gray-200 bg-white p-8">
                <span className="mb-4 inline-block text-4xl font-black text-brand-orange/20">
                  {step.num}
                </span>
                <h3 className="mb-3 text-lg font-bold text-black">
                  {step.title}
                </h3>
                <p className="text-base leading-relaxed text-gray-500">
                  {step.desc}
                </p>
              </div>
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
