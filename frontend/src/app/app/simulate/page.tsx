"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ChatInterface from "@/components/simulate2/ChatInterface";
import RightSidebar from "@/components/simulate2/RightSidebar";
import { listBusinesses, listSimulations } from "@/lib/api";

export default function SimulatePage() {
  const router = useRouter();
  const [businessId, setBusinessId] = useState<string | null>(null);
  const [history, setHistory] = useState<
    { id: string; question: string; verdict: string; date: string }[]
  >([]);
  const [personaCount, setPersonaCount] = useState(35);

  useEffect(() => {
    listBusinesses()
      .then((businesses) => {
        if (businesses.length === 0) {
          router.replace("/onboarding");
        } else {
          setBusinessId(businesses[0].id);
        }
      })
      .catch(() => {
        router.replace("/onboarding");
      });

    // Load past simulations from database
    listSimulations()
      .then((sims) => {
        const past = sims
          .filter((s) => s.status === "completed")
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 20)
          .map((s) => ({
            id: s.id,
            question: s.question,
            verdict: "completed",
            date: new Date(s.created_at).toLocaleDateString(),
          }));
        setHistory(past);
      })
      .catch(() => {});
  }, [router]);

  const handleSimComplete = (sim: { id: string; question: string; verdict: string }) => {
    setHistory((prev) => [
      { ...sim, date: "Just now" },
      ...prev,
    ]);
  };

  if (!businessId) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      <ChatInterface
        businessId={businessId}
        personaCount={personaCount}
        onSimulationComplete={handleSimComplete}
      />
      <RightSidebar
        history={history}
        personaCount={personaCount}
        onPersonaCountChange={setPersonaCount}
        onSelect={() => {
          // TODO: load past simulation
        }}
      />
    </div>
  );
}
