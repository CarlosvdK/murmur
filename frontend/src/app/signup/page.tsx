"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import Link from "next/link";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const supabase = createClient();

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      setDone(true);
      setLoading(false);
    }
  }

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "#F5F3EF" }}>
        <div className="w-full max-w-sm text-center">
          <h1 className="text-2xl font-bold mb-4" style={{ color: "#1a1a1a" }}>
            Check your email
          </h1>
          <p style={{ color: "#4a4a4a" }}>
            We sent a confirmation link to <strong>{email}</strong>.
            Click it to activate your account, then come back and sign in.
          </p>
          <Link
            href="/login"
            className="inline-block mt-6 underline text-sm"
            style={{ color: "#1a1a1a" }}
          >
            Back to sign in
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: "#F5F3EF" }}>
      <div className="w-full max-w-sm">
        <h1
          className="text-3xl font-bold text-center mb-8"
          style={{ color: "#1a1a1a" }}
        >
          Create your account
        </h1>

        <form onSubmit={handleSignup} className="space-y-4">
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
              minLength={6}
              className="w-full px-3 py-2 rounded-lg border focus:outline-none focus:ring-2"
              style={{
                borderColor: "#d4d0c8",
                background: "#ffffff",
                color: "#1a1a1a",
              }}
              placeholder="At least 6 characters"
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
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-center mt-6 text-sm" style={{ color: "#7a7a7a" }}>
          Already have an account?{" "}
          <Link href="/login" className="underline" style={{ color: "#1a1a1a" }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
