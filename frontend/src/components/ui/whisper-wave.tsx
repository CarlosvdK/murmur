"use client";

import { useEffect, useRef } from "react";

interface WhisperWaveProps {
  className?: string;
  /** Optional fixed side. When omitted, fills container width + height. */
  size?: number;
  /** How many vertical bars. */
  barCount?: number;
}

// Brand palette: blue -> pink -> orange. Bars tint horizontally across this.
const PALETTE: [number, number, number][] = [
  [68, 140, 253], // #448CFD
  [255, 141, 228], // #FF8DE4
  [255, 135, 32], // #FF8720
];

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

function brandColor(t: number): [number, number, number] {
  const segments = PALETTE.length - 1;
  const scaled = Math.min(Math.max(t, 0), 1) * segments;
  const i = Math.floor(scaled);
  const frac = scaled - i;
  const a = PALETTE[i];
  const b = PALETTE[Math.min(i + 1, segments)];
  return [
    Math.round(lerp(a[0], b[0], frac)),
    Math.round(lerp(a[1], b[1], frac)),
    Math.round(lerp(a[2], b[2], frac)),
  ];
}

type Bar = {
  x: number;
  color: [number, number, number];
  /** 0-1 per-bar height scaler. Mixed so some bars are naturally taller. */
  baseAmpFactor: number;
  phase: number;
  phaseSpeed: number;
  /** Scheduled start time for the current swell (or null). */
  swellStart: number | null;
  swellDuration: number;
  /** How strong this particular bar's swell is -- depends on distance from the swell centre. */
  swellStrength: number;
  /** Dynamic loudness multiplier; 1.0 at rest, up to ~2.5 during swell. */
  loudness: number;
};

/**
 * WhisperWave — vertical bars arranged in a row like a voicenote waveform.
 * Each bar pulses slowly on its own phase. Every few seconds a swell
 * propagates across a cluster of neighbouring bars, rising and decaying
 * in a short wave, like a voice momentarily speaking up.
 */
export function WhisperWave({
  className = "",
  size,
  barCount = 72,
}: WhisperWaveProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    let width = 0;
    let height = 0;
    let bars: Bar[] = [];
    let nextSwellTime = 0;

    const BAR_WIDTH = 3;
    const MAX_AMP_FRACTION = 0.85; // tallest possible bar = 85% of canvas height
    const MIN_HALF_AMP = 4; // minimum half-height (px) so every bar is always visible

    const rebuild = () => {
      bars = [];
      // Evenly space bars horizontally with a half-step padding on each end.
      const spacing = width / barCount;
      for (let i = 0; i < barCount; i++) {
        const centerX = spacing * (i + 0.5);
        bars.push({
          x: centerX - BAR_WIDTH / 2,
          color: brandColor(barCount > 1 ? i / (barCount - 1) : 0.5),
          baseAmpFactor: 0.35 + Math.random() * 0.65,
          phase: Math.random() * Math.PI * 2,
          // Slow individual drift.
          phaseSpeed: 0.006 + Math.random() * 0.012,
          swellStart: null,
          swellDuration: 0,
          swellStrength: 0,
          loudness: 1,
        });
      }
    };

    const resize = () => {
      if (size) {
        width = size;
        height = size;
      } else {
        width = container.clientWidth;
        height = Math.max(container.clientHeight, 420);
      }
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
      rebuild();
    };

    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(container);

    const start = performance.now();
    nextSwellTime = start + 900;
    let animationId = 0;

    const triggerSwell = (now: number) => {
      if (!bars.length) return;
      const centerIdx = Math.floor(Math.random() * bars.length);
      const radius = 4 + Math.floor(Math.random() * 5); // 4-8 bars each side
      const propagationMs = 65; // delay per neighbour, makes it ripple

      for (let offset = -radius; offset <= radius; offset++) {
        const idx = centerIdx + offset;
        if (idx < 0 || idx >= bars.length) continue;
        const dist = Math.abs(offset);
        const falloff = 1 - dist / (radius + 1); // 1 at centre, 0 at edges
        const b = bars[idx];
        b.swellStart = now + dist * propagationMs;
        b.swellDuration = 850 + Math.random() * 400;
        b.swellStrength = falloff * 1.6;
      }
      nextSwellTime = now + 1200 + Math.random() * 2200;
    };

    const animate = (now: number) => {
      if (now >= nextSwellTime) triggerSwell(now);

      ctx.clearRect(0, 0, width, height);

      const centerY = height / 2;
      const maxHalfAmp = (height * MAX_AMP_FRACTION) / 2;

      for (const bar of bars) {
        bar.phase += bar.phaseSpeed;

        // Swell envelope: attack 0.2, hold 0.3, decay 0.5.
        if (bar.swellStart !== null && now >= bar.swellStart) {
          const t = (now - bar.swellStart) / bar.swellDuration;
          if (t >= 1) {
            bar.loudness = 1;
            bar.swellStart = null;
          } else {
            let env: number;
            if (t < 0.2) env = t / 0.2;
            else if (t < 0.5) env = 1;
            else env = 1 - (t - 0.5) / 0.5;
            bar.loudness = 1 + env * bar.swellStrength;
          }
        }

        // Base amplitude from sum-of-sines on this bar's phase, normalised 0..1.
        const w =
          Math.sin(bar.phase) * 0.5 +
          Math.sin(bar.phase * 2.3 + 1.2) * 0.3 +
          Math.sin(bar.phase * 4.1 + 3.7) * 0.2;
        const normalised = (w + 1) / 2;

        const halfAmp =
          MIN_HALF_AMP +
          (maxHalfAmp - MIN_HALF_AMP) *
            normalised *
            bar.baseAmpFactor *
            bar.loudness;
        const clampedHalf = Math.min(halfAmp, maxHalfAmp);
        const top = centerY - clampedHalf;
        const barH = clampedHalf * 2;

        const alpha = 0.55 + (bar.loudness - 1) * 0.3;
        const [r, g, b] = bar.color;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${Math.min(alpha, 1)})`;
        ctx.beginPath();
        if (typeof ctx.roundRect === "function") {
          ctx.roundRect(bar.x, top, BAR_WIDTH, barH, BAR_WIDTH / 2);
        } else {
          ctx.rect(bar.x, top, BAR_WIDTH, barH);
        }
        ctx.fill();
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationId);
      ro.disconnect();
    };
  }, [size, barCount]);

  return (
    <div
      ref={containerRef}
      className={`relative mx-auto ${className}`}
      style={
        size
          ? { width: size, height: size }
          : { width: "100%", height: "100%", minHeight: 420 }
      }
    >
      <canvas ref={canvasRef} className="absolute inset-0" />
    </div>
  );
}
