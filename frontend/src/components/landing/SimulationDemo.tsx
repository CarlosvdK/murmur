"use client";

import { useState, useEffect } from "react";

const STEPS = [
  { delay: 0, type: "business" as const },
  { delay: 1500, type: "question" as const },
  { delay: 3000, type: "persona1" as const },
  { delay: 4200, type: "persona2" as const },
  { delay: 5400, type: "persona3" as const },
  { delay: 7000, type: "result" as const },
];

const PERSONAS = [
  {
    name: "Maria",
    age: 34,
    sentiment: "+0.6",
    label: "Positive",
    color: "text-brand-blue",
    reaction:
      "I come every Friday with the kids. An extra dollar on tacos? I'd grumble but still come. It's our routine.",
  },
  {
    name: "Carlos",
    age: 28,
    sentiment: "-0.4",
    label: "Negative",
    color: "text-brand-orange",
    reaction:
      "Honestly, I already think it's a bit pricey for a food truck. Another 10% and I'd try the new place on 5th.",
  },
  {
    name: "Diane",
    age: 52,
    sentiment: "+0.2",
    label: "Neutral",
    color: "text-brand-pink",
    reaction:
      "I only come once a month for the al pastor. Wouldn't even notice a small increase, to be honest.",
  },
];

export default function SimulationDemo() {
  const [visibleSteps, setVisibleSteps] = useState<Set<string>>(new Set());
  const [isInView, setIsInView] = useState(false);
  const [hasPlayed, setHasPlayed] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasPlayed) {
          setIsInView(true);
          setHasPlayed(true);
        }
      },
      { threshold: 0.3 }
    );

    const el = document.getElementById("simulation-demo");
    if (el) observer.observe(el);
    return () => observer.disconnect();
  }, [hasPlayed]);

  useEffect(() => {
    if (!isInView) return;
    const timers: ReturnType<typeof setTimeout>[] = [];
    for (const step of STEPS) {
      timers.push(
        setTimeout(() => {
          setVisibleSteps((prev) => {
            const next = new Set(prev);
            next.add(step.type);
            return next;
          });
        }, step.delay)
      );
    }
    return () => timers.forEach(clearTimeout);
  }, [isInView]);

  const show = (key: string) => visibleSteps.has(key);

  return (
    <div id="simulation-demo" className="mx-auto max-w-3xl">
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-lg">
        {/* Title bar */}
        <div className="flex items-center gap-2 border-b border-gray-100 bg-gray-50 px-4 py-2.5">
          <div className="h-2.5 w-2.5 rounded-full bg-gray-300" />
          <div className="h-2.5 w-2.5 rounded-full bg-gray-300" />
          <div className="h-2.5 w-2.5 rounded-full bg-gray-300" />
          <span className="ml-2 text-xs text-gray-400">murmur simulation</span>
        </div>

        <div className="space-y-4 p-6">
          {/* Business card */}
          <div
            className={`transition-all duration-700 ${
              show("business")
                ? "translate-y-0 opacity-100"
                : "translate-y-4 opacity-0"
            }`}
          >
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wider text-gray-400">
                Business
              </p>
              <p className="mt-1 font-semibold text-gray-900">
                Tony&apos;s Taco Truck
              </p>
              <p className="text-sm text-gray-500">
                Food truck in East Austin, TX -- known for al pastor and
                breakfast tacos
              </p>
            </div>
          </div>

          {/* Question */}
          <div
            className={`transition-all duration-700 ${
              show("question")
                ? "translate-y-0 opacity-100"
                : "translate-y-4 opacity-0"
            }`}
          >
            <div className="rounded-lg border-2 border-brand-blue/20 bg-brand-blue/5 p-4">
              <p className="text-xs font-medium uppercase tracking-wider text-brand-blue">
                Question
              </p>
              <p className="mt-1 text-sm font-medium text-gray-900">
                &ldquo;What would happen if I raised all prices by 10%?&rdquo;
              </p>
            </div>
          </div>

          {/* Persona responses */}
          {PERSONAS.map((p, i) => (
            <div
              key={p.name}
              className={`transition-all duration-700 ${
                show(`persona${i + 1}`)
                  ? "translate-x-0 opacity-100"
                  : "translate-x-8 opacity-0"
              }`}
            >
              <div className="flex gap-3 rounded-lg border border-gray-100 p-4">
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white ${
                    i === 0
                      ? "bg-brand-blue"
                      : i === 1
                        ? "bg-brand-orange"
                        : "bg-brand-pink"
                  }`}
                >
                  {p.name[0]}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">
                      {p.name}, {p.age}
                    </p>
                    <span className={`text-xs font-mono ${p.color}`}>
                      {p.sentiment} {p.label}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-600">
                    &ldquo;{p.reaction}&rdquo;
                  </p>
                </div>
              </div>
            </div>
          ))}

          {/* Result summary */}
          <div
            className={`transition-all duration-700 ${
              show("result")
                ? "translate-y-0 opacity-100"
                : "translate-y-4 opacity-0"
            }`}
          >
            <div className="rounded-lg bg-black p-4 text-white">
              <p className="text-xs font-medium uppercase tracking-wider text-gray-400">
                Result
              </p>
              <p className="mt-1 text-sm font-medium">
                Most of your regulars would accept the increase, but your
                price-sensitive lunch crowd might try alternatives. Consider
                raising dinner prices only.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
