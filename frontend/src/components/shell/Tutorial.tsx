"use client";

import { useState, useEffect, useCallback } from "react";

const STEPS = [
  {
    id: "welcome",
    title: "Welcome to Murmur",
    body: "Let us show you around. This will take 30 seconds.",
  },
  {
    id: "nav-simulate",
    title: "Simulate",
    body: "Run a full customer simulation. Describe your business, ask a question, and get honest feedback from a panel of AI customers tailored to you.",
  },
  {
    id: "nav-customers",
    title: "Customer Twins",
    body: "Build a digital twin of each high-value customer from your real conversations. Upload WhatsApp, email, or meeting notes and ask the twin how they would react to any change.",
  },
  {
    id: "nav-vendors",
    title: "Vendor Twins",
    body: "Create digital twins of your suppliers and partners. Predict their negotiation style, anticipate counter-offers, and prepare for every conversation.",
  },
  {
    id: "nav-intelligence",
    title: "Intelligence",
    body: "View insights and patterns across all your simulations and twins in one place.",
  },
  {
    id: "card-simulate",
    title: "Run your first simulation",
    body: "Start here. Describe your business, ask any question about a decision you are considering, and see how your customers would react. Results include confidence intervals, say-do gap corrections, and honest caveats.",
  },
  {
    id: "card-customers",
    title: "Build your first customer twin",
    body: "Best for businesses with fewer than 100 high-value clients. Upload your correspondence and the twin learns how each person communicates, decides, and negotiates.",
  },
  {
    id: "card-vendors",
    title: "Build your first vendor twin",
    body: "Upload conversations with a supplier or partner. The twin extracts their negotiation patterns, response style, and what matters most to them.",
  },
  {
    id: "done",
    title: "You are all set",
    body: "Start with a simulation to see Murmur in action. You can always come back to explore twins later.",
  },
];

export default function Tutorial({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(0);
  const [highlight, setHighlight] = useState<{
    top: number;
    left: number;
    width: number;
    height: number;
  } | null>(null);

  const cur = STEPS[step];

  const updateHighlight = useCallback(() => {
    if (cur.id === "welcome" || cur.id === "done") {
      setHighlight(null);
      return;
    }
    const el = document.querySelector(`[data-tut="${cur.id}"]`);
    if (!el) {
      setHighlight(null);
      return;
    }
    const r = el.getBoundingClientRect();
    const pad = 6;
    setHighlight({
      top: r.top - pad,
      left: r.left - pad,
      width: r.width + pad * 2,
      height: r.height + pad * 2,
    });
  }, [cur.id]);

  useEffect(() => {
    updateHighlight();
    window.addEventListener("resize", updateHighlight);
    return () => window.removeEventListener("resize", updateHighlight);
  }, [updateHighlight]);

  const next = () => {
    if (step < STEPS.length - 1) setStep(step + 1);
    else onComplete();
  };

  const clipPath = highlight
    ? `polygon(
        0% 0%, 0% 100%,
        ${highlight.left}px 100%,
        ${highlight.left}px ${highlight.top}px,
        ${highlight.left + highlight.width}px ${highlight.top}px,
        ${highlight.left + highlight.width}px ${highlight.top + highlight.height}px,
        ${highlight.left}px ${highlight.top + highlight.height}px,
        ${highlight.left}px 100%,
        100% 100%, 100% 0%
      )`
    : "none";

  // Position card near highlighted element
  const getCardStyle = (): React.CSSProperties => {
    if (!highlight) {
      return {
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      };
    }
    const cardW = 360;
    const cardH = 200;
    let top = highlight.top + highlight.height + 16;
    let left = highlight.left;

    // If card would go below viewport, place above
    if (top + cardH > window.innerHeight - 20) {
      top = highlight.top - cardH - 16;
    }
    // Keep within viewport horizontally
    if (left + cardW > window.innerWidth - 20) {
      left = window.innerWidth - cardW - 20;
    }
    if (left < 20) left = 20;
    if (top < 20) top = 80;

    return { position: "fixed", top, left };
  };

  return (
    <>
      {/* Dark overlay with cutout */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 10000,
          background: "rgba(0,0,0,0.55)",
          backdropFilter: "blur(2px)",
          clipPath,
          transition: "clip-path 0.3s ease",
        }}
      />

      {/* Pulsing ring around highlighted element */}
      {highlight && (
        <div
          style={{
            position: "fixed",
            top: highlight.top,
            left: highlight.left,
            width: highlight.width,
            height: highlight.height,
            zIndex: 10001,
            borderRadius: 8,
            border: "2px solid #FF8720",
            boxShadow: "0 0 0 0 rgba(255,135,32,0.4)",
            animation: "tutPulse 1.5s ease-in-out infinite",
            pointerEvents: "none",
          }}
        />
      )}

      {/* Tutorial card */}
      <div
        style={{
          ...getCardStyle(),
          zIndex: 10002,
          width: 360,
          animation: "tutFadeIn 0.3s ease",
        }}
      >
        <div
          style={{
            background: "white",
            borderRadius: 16,
            padding: "28px 24px 20px",
            boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
          }}
        >
          {/* Step indicator */}
          <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
            {STEPS.map((_, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  height: 3,
                  borderRadius: 2,
                  background: i <= step ? "#FF8720" : "#E5E2DC",
                  transition: "background 0.3s",
                }}
              />
            ))}
          </div>

          <h3
            style={{
              fontSize: 18,
              fontWeight: 800,
              color: "#000",
              marginBottom: 8,
            }}
          >
            {cur.title}
          </h3>
          <p
            style={{
              fontSize: 14,
              lineHeight: 1.6,
              color: "#6b7280",
              marginBottom: 20,
            }}
          >
            {cur.body}
          </p>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <button
              onClick={onComplete}
              style={{
                fontSize: 13,
                color: "#9ca3af",
                background: "none",
                border: "none",
                cursor: "pointer",
              }}
            >
              Skip
            </button>
            <button
              onClick={next}
              style={{
                fontSize: 14,
                fontWeight: 700,
                color: "#fff",
                background: "#000",
                border: "none",
                borderRadius: 999,
                padding: "10px 24px",
                cursor: "pointer",
              }}
            >
              {step === STEPS.length - 1 ? "Get started" : "Next"}
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes tutFadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes tutPulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(255,135,32,0.4); }
          50% { box-shadow: 0 0 0 12px rgba(255,135,32,0); }
        }
      `}</style>
    </>
  );
}
