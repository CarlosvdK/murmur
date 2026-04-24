"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";

const WORDS = [
  { text: "simulated.", color: "text-brand-orange" },
  { text: "listened to.", color: "text-brand-blue" },
  { text: "understood.", color: "text-brand-pink" },
  { text: "predicted.", color: "text-brand-orange" },
  { text: "interviewed.", color: "text-brand-blue" },
  { text: "prepared for.", color: "text-brand-pink" },
  { text: "known.", color: "text-brand-orange" },
];

export default function RotatingWord() {
  const [index, setIndex] = useState(0);
  const reduced = useReducedMotion();

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % WORDS.length);
    }, 2800);
    return () => clearInterval(interval);
  }, []);

  const word = WORDS[index];

  if (reduced) {
    return <span className={word.color}>{word.text}</span>;
  }

  return (
    <span className="relative inline-block">
      <AnimatePresence mode="wait">
        <motion.span
          key={word.text}
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 40 }}
          transition={{ duration: 0.4, ease: "easeInOut" }}
          className={`inline-block ${word.color}`}
        >
          {word.text}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}
