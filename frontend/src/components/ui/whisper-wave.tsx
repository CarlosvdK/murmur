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
  /** Small per-bar phase offset so neighbours aren't perfectly locked. */
  personalOffset: number;
};

/**
 * A travelling "voice phrase" -- a zone of elevated loudness whose centre
 * crosses the bar row from left to right over its lifetime.
 */
type Swell = {
  startTime: number;
  /** How long the centre takes to cross from bar 0 to bar (N-1). */
  lifetimeMs: number;
  /** Spatial width of the zone, in bars. */
  width: number;
  /** Peak loudness boost at the zone's centre. */
  strength: number;
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
    let swells: Swell[] = [];
    let nextSwellTime = 0;
    let globalPhase = 0;

    const BAR_WIDTH = 3;
    const MAX_AMP_FRACTION = 0.85;
    const MIN_HALF_AMP = 4;
    // Base drift speed. Low = slow, meditative bars.
    const PHASE_SPEED = 0.006;
    // How much each bar's phase shifts from its left neighbour. Higher ->
    // the wave pattern visibly travels left-to-right at a quicker pace.
    const SPATIAL_STEP = 0.22;

    const rebuild = () => {
      bars = [];
      swells = [];
      const spacing = width / barCount;
      for (let i = 0; i < barCount; i++) {
        const centerX = spacing * (i + 0.5);
        bars.push({
          x: centerX - BAR_WIDTH / 2,
          color: brandColor(barCount > 1 ? i / (barCount - 1) : 0.5),
          baseAmpFactor: 0.35 + Math.random() * 0.65,
          // Keep the personal offset small so the L->R traveling pattern
          // stays visually coherent instead of looking like random noise.
          personalOffset: (Math.random() - 0.5) * 1.2,
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
      swells.push({
        startTime: now,
        // 3.5-5.5s for a phrase to cross the entire row left-to-right.
        lifetimeMs: 3500 + Math.random() * 2000,
        width: 6 + Math.random() * 5, // 6-11 bars wide
        strength: 0.9 + Math.random() * 0.7, // 0.9-1.6 peak boost
      });
      // Next phrase starts while the current is still crossing, so we
      // always have something moving rightward.
      nextSwellTime = now + 900 + Math.random() * 1500;
      // Prune finished swells.
      swells = swells.filter((s) => now - s.startTime < s.lifetimeMs + 400);
    };

    const animate = (now: number) => {
      if (now >= nextSwellTime) triggerSwell(now);

      // One global phase advances slowly; each bar derives its phase from
      // (globalPhase + personalOffset - i * SPATIAL_STEP) so the pattern
      // visibly travels left to right.
      globalPhase += PHASE_SPEED;

      ctx.clearRect(0, 0, width, height);

      const centerY = height / 2;
      const maxHalfAmp = (height * MAX_AMP_FRACTION) / 2;

      for (let i = 0; i < bars.length; i++) {
        const bar = bars[i];

        // Accumulated swell contribution from every active phrase whose
        // centre is currently passing near this bar.
        let loudness = 1;
        for (const s of swells) {
          const progress = (now - s.startTime) / s.lifetimeMs;
          if (progress < 0 || progress > 1) continue;
          // Swell centre sweeps from bar 0 to bar (N-1) across its lifetime.
          const centreIdx = progress * (bars.length - 1);
          const dist = Math.abs(i - centreIdx);
          if (dist > s.width) continue;
          const spatial = 1 - dist / s.width;
          // Envelope: fade in over first 12% of life, fade out over last 12%.
          let env: number;
          if (progress < 0.12) env = progress / 0.12;
          else if (progress > 0.88) env = (1 - progress) / 0.12;
          else env = 1;
          loudness += s.strength * spatial * env;
        }

        // Base sum-of-sines at this bar, normalised to 0..1.
        const p = globalPhase + bar.personalOffset - i * SPATIAL_STEP;
        const w =
          Math.sin(p) * 0.5 +
          Math.sin(p * 2.3 + 1.2) * 0.3 +
          Math.sin(p * 4.1 + 3.7) * 0.2;
        const normalised = (w + 1) / 2;

        const halfAmp =
          MIN_HALF_AMP +
          (maxHalfAmp - MIN_HALF_AMP) *
            normalised *
            bar.baseAmpFactor *
            loudness;
        const clampedHalf = Math.min(halfAmp, maxHalfAmp);
        const top = centerY - clampedHalf;
        const barH = clampedHalf * 2;

        const alpha = Math.min(0.55 + (loudness - 1) * 0.3, 1);
        const [r, g, b] = bar.color;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
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
