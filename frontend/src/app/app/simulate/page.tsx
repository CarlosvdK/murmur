"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ChatInterface from "@/components/simulate2/ChatInterface";
import RightSidebar from "@/components/simulate2/RightSidebar";
import { listBusinesses } from "@/lib/api";

export default function SimulatePage() {
  const router = useRouter();
  const [businessId, setBusinessId] = useState<string | null>(null);
  const [history, setHistory] = useState<
    { id: string; question: string; verdict: string; date: string }[]
  >([]);

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
        onSimulationComplete={handleSimComplete}
      />
      <RightSidebar
        history={history}
        onSelect={() => {
          // TODO: load past simulation
        }}
      />
    </div>
  );
}
