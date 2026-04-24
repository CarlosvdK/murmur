"use client";

import { useEffect, useRef } from "react";

interface WhisperWaveProps {
  className?: string;
  /** Optional fixed side. When omitted, fills container width + height. */
  size?: number;
  /** How many horizontal lines. */
  lineCount?: number;
}

// Brand palette: blue -> pink -> orange. Each line picks its tint from here
// based on its vertical position, giving a soft top-to-bottom gradient.
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

/**
 * Sum-of-sines 1D field. Aperiodic-looking, smooth, no deps.
 * Returns a value roughly in [-1, 1].
 */
function smoothWave(x: number, phase: number): number {
  return (
    Math.sin(x * 0.018 + phase * 1.0) * 0.5 +
    Math.sin(x * 0.061 + phase * 0.7) * 0.3 +
    Math.sin(x * 0.117 + phase * 0.45) * 0.2
  );
}

type Line = {
  baselineY: number;
  phase: number;
  phaseSpeed: number;
  noiseScale: number;
  baseAmp: number;
  color: [number, number, number];
  swellStart: number | null;
  swellDuration: number;
  loudness: number; // 1.0 at rest, up to ~2.2 while swelling
};

/**
 * WhisperWave — ambient backdrop of a dozen thin wavy lines, each
 * representing a voice. Subtle all the time; occasionally one voice
 * swells briefly, then settles back into the murmur.
 */
export function WhisperWave({
  className = "",
  size,
  lineCount = 14,
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
    let lines: Line[] = [];
    let nextSwellTime = 0;

    const rebuild = () => {
      lines = [];
      // Distribute lines vertically with a touch of jitter so the stack
      // does not read as an equalizer grid.
      const jitter = height / (lineCount * 2);
      for (let i = 0; i < lineCount; i++) {
        const t = lineCount > 1 ? i / (lineCount - 1) : 0.5;
        const baselineY =
          lerp(height * 0.08, height * 0.92, t) +
          (Math.random() - 0.5) * jitter;
        lines.push({
          baselineY,
          phase: Math.random() * 1000,
          // Very slow drift: full cycle is ~minutes, not seconds.
          phaseSpeed: 0.002 + Math.random() * 0.004,
          noiseScale: 0.55 + Math.random() * 0.8,
          // Mixed amplitudes: some lines are almost flat, others more alive.
          baseAmp: 6 + Math.random() * 16,
          color: brandColor(t),
          swellStart: null,
          swellDuration: 0,
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
        height = Math.max(container.clientHeight, 560);
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
    nextSwellTime = start + 1000;
    let animationId = 0;

    const triggerSwell = (now: number) => {
      if (!lines.length) return;
      const idx = Math.floor(Math.random() * lines.length);
      lines[idx].swellStart = now;
      lines[idx].swellDuration = 1500 + Math.random() * 1200; // 1.5-2.7s
      nextSwellTime = now + 1400 + Math.random() * 2200; // next 1.4-3.6s
    };

    const animate = (now: number) => {
      if (now >= nextSwellTime) triggerSwell(now);

      // Update per-line state.
      for (const line of lines) {
        line.phase += line.phaseSpeed;

        if (line.swellStart !== null) {
          const t = (now - line.swellStart) / line.swellDuration;
          if (t >= 1) {
            line.loudness = 1;
            line.swellStart = null;
          } else {
            // Envelope: attack (0-0.2), hold (0.2-0.5), decay (0.5-1).
            let env: number;
            if (t < 0.2) env = t / 0.2;
            else if (t < 0.5) env = 1;
            else env = 1 - (t - 0.5) / 0.5;
            line.loudness = 1 + env * 1.2; // peak 2.2x
          }
        }
      }

      ctx.clearRect(0, 0, width, height);

      const step = 4; // sample every 4px along x; cheap + smooth
      for (const line of lines) {
        const amp = line.baseAmp * line.loudness;
        // Alpha + stroke width scale with loudness so a swelling line
        // visually rises out of the murmur.
        const alpha = 0.34 + (line.loudness - 1) * 0.5;
        const lw = 1.1 + (line.loudness - 1) * 1.2;
        const [r, g, b] = line.color;
        ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.lineWidth = lw;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.beginPath();
        for (let x = 0; x <= width; x += step) {
          const y = line.baselineY + amp * smoothWave(x * line.noiseScale, line.phase);
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationId);
      ro.disconnect();
    };
  }, [size, lineCount]);

  return (
    <div
      ref={containerRef}
      className={`relative mx-auto ${className}`}
      style={
        size
          ? { width: size, height: size }
          : { width: "100%", height: "100%", minHeight: 620 }
      }
    >
      <canvas ref={canvasRef} className="absolute inset-0" />
    </div>
  );
}
