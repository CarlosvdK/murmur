import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        brand: {
          black: "#000000",
          blue: "#448CFD",
          orange: "#FF8720",
          pink: "#FF8DE4",
        },
        eggshell: "#F5F3EF",
        // Compat aliases
        murmur: {
          cream: "var(--murmur-cream)",
          ink: "var(--murmur-ink)",
          "warm-grey": "var(--murmur-warm-grey)",
          amber: "var(--murmur-amber)",
          "amber-light": "var(--murmur-amber-light)",
          white: "var(--murmur-white)",
          border: "var(--murmur-border)",
          positive: "var(--murmur-positive)",
          negative: "var(--murmur-negative)",
          neutral: "var(--murmur-neutral)",
        },
        legacy: {
          orange: "#FF6B35",
          navy: "#004E89",
          purple: "#7B2D8E",
          teal: "#1A936F",
          red: "#C5283D",
          coral: "#E9724C",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      keyframes: {
        breathe: {
          "0%, 100%": { opacity: "0.7", transform: "scale(1)" },
          "50%": { opacity: "1", transform: "scale(1.15)" },
        },
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        breathe: "breathe 2s ease-in-out infinite",
        "fade-in-up": "fade-in-up 0.3s ease-out",
      },
    },
  },
  plugins: [],
};
export default config;
