"use client";

import SectionReveal from "./SectionReveal";

const STEPS = [
  {
    num: "01",
    title: "Describe your business",
    desc: "Answer a few plain-English questions about your business, your customers, and what you sell. No forms. No jargon. Just describe it like you would explain it to a friend.",
  },
  {
    num: "02",
    title: "We gather intelligence",
    desc: "Before generating anything, Murmur researches your market, your area, your competitors, and published behavioural science. The result is grounded in your actual situation -- not a generic model.",
  },
  {
    num: "03",
    title: "Your customers come to life",
    desc: "For simulations: a diverse panel of AI customers is generated -- each with their own personality, habits, and loyalty level. For twins: your real conversations are analysed to build a digital copy of each relationship.",
  },
  {
    num: "04",
    title: "Ask anything, get honest answers",
    desc: "Ask your simulated customers or digital twins any question. They respond in their own voice with honest reactions, not what they think you want to hear. You see themes, tension points, and a clear recommendation -- with caveats about what we don't know.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-white px-6 py-28 lg:px-12 xl:px-20">
      <div className="mx-auto max-w-[1400px]">
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
            Four steps. Works the same whether you are simulating or building a twin.
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
