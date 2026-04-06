"use client";

const STEPS = [
  {
    id: "profile",
    label: "Business Profile",
    sub: "You describe your business and customers",
  },
  {
    id: "context",
    label: "Context Engine",
    sub: "We research competitors, pricing, local trends",
  },
  {
    id: "swarm",
    label: "Persona Swarm",
    sub: "15 unique customers are generated and interviewed",
  },
  {
    id: "report",
    label: "Plain-English Report",
    sub: "Themes, key voices, recommendation with caveats",
  },
];

export default function ProcessDiagram() {
  return (
    <div className="mx-auto max-w-2xl">
      <div className="relative">
        {STEPS.map((step, i) => (
          <div key={step.id} className="relative flex items-start gap-5 pb-10 last:pb-0">
            {/* Vertical connector line */}
            {i < STEPS.length - 1 && (
              <div
                className="absolute left-[19px] top-10 h-full w-px"
                style={{
                  background: `linear-gradient(to bottom, #448cfd, #ff8720, #ff8de4)`,
                  opacity: 0.3,
                }}
              />
            )}

            {/* Step number circle */}
            <div
              className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 bg-white text-sm font-bold"
              style={{
                borderColor:
                  i === 0
                    ? "#448cfd"
                    : i === 1
                      ? "#ff8720"
                      : i === 2
                        ? "#ff8de4"
                        : "#000000",
                color:
                  i === 0
                    ? "#448cfd"
                    : i === 1
                      ? "#ff8720"
                      : i === 2
                        ? "#ff8de4"
                        : "#000000",
              }}
            >
              {String(i + 1).padStart(2, "0")}
            </div>

            {/* Step content */}
            <div className="pt-1.5">
              <h4 className="text-base font-semibold text-gray-900">
                {step.label}
              </h4>
              <p className="mt-0.5 text-sm text-gray-500">{step.sub}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
