"use client";

import { useEffect, useRef } from "react";

interface EntropyProps {
  className?: string;
  /** Optional fixed side. When omitted, fills container width and is square. */
  size?: number;
  /** Seconds for one full chaos -> order -> pause loop. */
  cycleSeconds?: number;
}

// Brand palette -- matches Murmuration so the site reads as one family.
const BRAND_PALETTE: [number, number, number][] = [
  [68, 140, 253], // blue  #448CFD
  [255, 141, 228], // pink  #FF8DE4
  [255, 135, 32], // orange #FF8720
];

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

function smoothstep(t: number) {
  const x = Math.min(Math.max(t, 0), 1);
  return x * x * (3 - 2 * x);
}

function brandColor(t: number): [number, number, number] {
  const segments = BRAND_PALETTE.length - 1;
  const scaled = Math.min(Math.max(t, 0), 1) * segments;
  const i = Math.floor(scaled);
  const frac = scaled - i;
  const a = BRAND_PALETTE[i];
  const b = BRAND_PALETTE[Math.min(i + 1, segments)];
  return [
    Math.round(lerp(a[0], b[0], frac)),
    Math.round(lerp(a[1], b[1], frac)),
    Math.round(lerp(a[2], b[2], frac)),
  ];
}

/**
 * Entropy -- a field of particles that cycles from a chaotic web into a
 * clean grid and back. "Making sense of the mess."
 *
 * Phases inside one cycle (t in [0, 1]):
 *   scatter  t in [0.00, 0.08]  quick burst of random velocity
 *   settle   t in [0.08, 0.80]  particles ease toward their grid home,
 *                               random jitter fades out
 *   hold     t in [0.80, 1.00]  clean grid holds still before restart
 */
export function Entropy({
  className = "",
  size,
  cycleSeconds = 11,
}: EntropyProps) {
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

    type Particle = {
      x: number;
      y: number;
      homeX: number;
      homeY: number;
      vx: number;
      vy: number;
      color: [number, number, number];
    };

    let particles: Particle[] = [];
    const COLS = 24;
    const ROWS = 24;

    const rebuild = () => {
      particles = [];
      const spacingX = width / COLS;
      const spacingY = height / ROWS;
      for (let i = 0; i < COLS; i++) {
        for (let j = 0; j < ROWS; j++) {
          const homeX = spacingX * i + spacingX / 2;
          const homeY = spacingY * j + spacingY / 2;
          particles.push({
            x: homeX + (Math.random() - 0.5) * width * 0.4,
            y: homeY + (Math.random() - 0.5) * height * 0.4,
            homeX,
            homeY,
            vx: (Math.random() - 0.5) * 3,
            vy: (Math.random() - 0.5) * 3,
            color: brandColor(i / (COLS - 1)),
          });
        }
      }
    };

    const resize = () => {
      const side = size ?? Math.min(container.clientWidth, 900);
      width = side;
      height = side;
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

    const CYCLE_MS = Math.max(2000, cycleSeconds * 1000);
    const start = performance.now();
    let animationId = 0;

    const scatter = () => {
      particles.forEach((p) => {
        p.x = p.homeX + (Math.random() - 0.5) * width * 0.45;
        p.y = p.homeY + (Math.random() - 0.5) * height * 0.45;
        p.vx = (Math.random() - 0.5) * 2.5;
        p.vy = (Math.random() - 0.5) * 2.5;
      });
    };

    let lastCycleIndex = -1;

    const animate = (now: number) => {
      const elapsed = now - start;
      const cycleIndex = Math.floor(elapsed / CYCLE_MS);
      const t = (elapsed % CYCLE_MS) / CYCLE_MS; // 0..1

      if (cycleIndex !== lastCycleIndex) {
        // Freshly entered a new cycle -- re-scatter to hide the reset.
        scatter();
        lastCycleIndex = cycleIndex;
      }

      // Phase weights
      // settleAmount goes 0 -> 1 as t moves from 0.08 to 0.80, then stays at 1.
      const settleAmount = smoothstep((t - 0.08) / (0.8 - 0.08));
      const jitter = (1 - settleAmount) * 0.35; // random noise, fades out
      const returnForce = 0.004 + settleAmount * 0.055; // spring to home
      const damping = 0.9 + settleAmount * 0.07; // more damping as we settle

      ctx.clearRect(0, 0, width, height);

      // Update
      for (const p of particles) {
        p.vx += (p.homeX - p.x) * returnForce;
        p.vy += (p.homeY - p.y) * returnForce;
        p.vx += (Math.random() - 0.5) * jitter;
        p.vy += (Math.random() - 0.5) * jitter;
        p.vx *= damping;
        p.vy *= damping;
        p.x += p.vx;
        p.y += p.vy;
      }

      // Draw edges between nearby particles. As particles settle into the
      // grid, edges naturally align into the lattice -- web becomes grid.
      const CONNECT = 56;
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i];
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dSq = dx * dx + dy * dy;
          if (dSq < CONNECT * CONNECT) {
            const d = Math.sqrt(dSq);
            const alpha = 0.22 * (1 - d / CONNECT);
            const r = (a.color[0] + b.color[0]) / 2;
            const g = (a.color[1] + b.color[1]) / 2;
            const bl = (a.color[2] + b.color[2]) / 2;
            ctx.strokeStyle = `rgba(${r}, ${g}, ${bl}, ${alpha})`;
            ctx.lineWidth = 0.8;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }

      // Draw particles on top
      for (const p of particles) {
        const [r, g, b] = p.color;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.88)`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2.2, 0, Math.PI * 2);
        ctx.fill();
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationId);
      ro.disconnect();
    };
  }, [size, cycleSeconds]);

  return (
    <div
      ref={containerRef}
      className={`relative mx-auto ${className}`}
      style={size ? { width: size, height: size } : { width: "100%", aspectRatio: "1 / 1" }}
    >
      <canvas ref={canvasRef} className="absolute inset-0" />
    </div>
  );
}
