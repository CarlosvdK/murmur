"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import EnrichedSurvey from "@/components/questionnaire/EnrichedSurvey";
import { createBusiness, BusinessCreate } from "@/lib/api";

export default function OnboardingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: BusinessCreate) => {
    setLoading(true);
    setError(null);
    try {
      await createBusiness(data);
      router.push("/app");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create business");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4">
      <EnrichedSurvey onSubmit={handleSubmit} loading={loading} />

      {error && (
        <div className="mx-auto mt-4 max-w-2xl rounded-lg bg-red-50 p-3 text-center text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  );
}
