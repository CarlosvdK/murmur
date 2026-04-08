"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function RedirectContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const params = searchParams.toString();
    router.replace(`/app/simulate${params ? `?${params}` : ""}`);
  }, [router, searchParams]);

  return <div className="flex h-screen items-center justify-center"><p className="text-gray-400">Redirecting...</p></div>;
}

export default function SimulatePage() {
  return <Suspense><RedirectContent /></Suspense>;
}
