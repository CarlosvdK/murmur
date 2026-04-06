"use client";

import { useState } from "react";
import ChatInterface from "@/components/simulate2/ChatInterface";
import RightSidebar from "@/components/simulate2/RightSidebar";

export default function SimulatePage() {
  const [history, setHistory] = useState<
    { id: string; question: string; verdict: string; date: string }[]
  >([]);

  const handleSimComplete = (sim: { id: string; question: string; verdict: string }) => {
    setHistory((prev) => [
      { ...sim, date: "Just now" },
      ...prev,
    ]);
  };

  return (
    <div className="flex h-full">
      <ChatInterface
        businessId={null}
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
