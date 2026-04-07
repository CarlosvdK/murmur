"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const supabase = createClient();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      // Check if user has a business -- if not, send to onboarding
      try {
        const { listBusinesses } = await import("@/lib/api");
        const businesses = await listBusinesses();
        if (businesses.length === 0) {
          router.push("/onboarding");
        } else {
          router.push("/app");
        }
      } catch {
        router.push("/onboarding");
      }
      router.refresh();
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: "#F5F3EF" }}>
      <div className="w-full max-w-sm">
        <h1
          className="text-3xl font-bold text-center mb-8"
          style={{ color: "#1a1a1a" }}
        >
          Sign in to Murmur
        </h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: "#4a4a4a" }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 rounded-lg border focus:outline-none focus:ring-2"
              style={{
                borderColor: "#d4d0c8",
                background: "#ffffff",
                color: "#1a1a1a",
              }}
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: "#4a4a4a" }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 rounded-lg border focus:outline-none focus:ring-2"
              style={{
                borderColor: "#d4d0c8",
                background: "#ffffff",
                color: "#1a1a1a",
              }}
              placeholder="Your password"
            />
          </div>

          {error && (
            <p className="text-sm" style={{ color: "#c44" }}>{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 rounded-lg font-medium transition-opacity"
            style={{
              background: "#1a1a1a",
              color: "#F5F3EF",
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="text-center mt-6 text-sm" style={{ color: "#7a7a7a" }}>
          No account yet?{" "}
          <Link href="/signup" className="underline" style={{ color: "#1a1a1a" }}>
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
