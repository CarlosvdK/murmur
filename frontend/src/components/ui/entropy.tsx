"use client";

import { useEffect, useRef } from "react";

interface EntropyProps {
  className?: string;
  /** Optional fixed side. When omitted, fills container width and is square. */
  size?: number;
  /** Seconds for one full chaos -> text -> chaos loop. */
  cycleSeconds?: number;
  /** Line(s) of text the central particles form. Multiple entries = multiple lines. */
  text?: string[];
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

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: [number, number, number];
  /** If set, this particle is a "text actor" and will ease toward this point. */
  targetX?: number;
  targetY?: number;
};

/**
 * Compute the set of (x, y) pixel positions occupied by one or more lines of
 * bold text, rendered centred in the given box. Used to pin particles to text.
 */
function computeTextMask(
  lines: string[],
  canvasWidth: number,
  canvasHeight: number,
  fontSize: number,
  lineGap: number,
  stride: number
): { x: number; y: number }[] {
  if (typeof document === "undefined") return [];
  const off = document.createElement("canvas");
  off.width = canvasWidth;
  off.height = canvasHeight;
  const octx = off.getContext("2d");
  if (!octx) return [];

  octx.fillStyle = "white";
  octx.font = `900 ${fontSize}px Inter, system-ui, sans-serif`;
  octx.textAlign = "center";
  octx.textBaseline = "middle";

  const totalHeight = lines.length * fontSize + (lines.length - 1) * lineGap;
  const startY = canvasHeight / 2 - totalHeight / 2 + fontSize / 2;
  lines.forEach((line, i) => {
    octx.fillText(line, canvasWidth / 2, startY + i * (fontSize + lineGap));
  });

  const img = octx.getImageData(0, 0, canvasWidth, canvasHeight);
  const points: { x: number; y: number }[] = [];
  for (let y = 0; y < canvasHeight; y += stride) {
    for (let x = 0; x < canvasWidth; x += stride) {
      const idx = (y * canvasWidth + x) * 4;
      if (img.data[idx + 3] > 128) {
        points.push({ x, y });
      }
    }
  }
  return points;
}

/**
 * Entropy -- a field that loops from pure noise into a readable word and back.
 * Edge particles keep drifting chaotically throughout; central "text actors"
 * migrate toward glyph positions during the settle phase of each cycle.
 */
export function Entropy({
  className = "",
  size,
  cycleSeconds = 28,
  text = ["MAKE SENSE", "OF THE NOISE"],
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

    let particles: Particle[] = [];

    const rebuild = () => {
      // Font size scales with the canvas. Tuned so the default two-liner
      // reads clearly at ~500-900px wide.
      const fontSize = Math.max(44, Math.floor(width / 10));
      const lineGap = Math.floor(fontSize * 0.12);
      // Stride controls how dense the text is. Smaller = more particles.
      const stride = Math.max(5, Math.round(width / 140));

      const textPoints = computeTextMask(
        text,
        width,
        height,
        fontSize,
        lineGap,
        stride
      );

      particles = [];

      // Text actors -- one per sampled text pixel.
      for (const pt of textPoints) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 3,
          vy: (Math.random() - 0.5) * 3,
          color: brandColor(pt.x / width),
          targetX: pt.x,
          targetY: pt.y,
        });
      }

      // Edge / chaos actors -- persistent random walkers scattered across the
      // canvas. Count scales with canvas area.
      const EDGE_COUNT = Math.round((width * height) / 1700);
      for (let i = 0; i < EDGE_COUNT; i++) {
        const x = Math.random() * width;
        const y = Math.random() * height;
        particles.push({
          x,
          y,
          vx: (Math.random() - 0.5) * 3,
          vy: (Math.random() - 0.5) * 3,
          color: brandColor(x / width),
        });
      }
    };

    const resize = () => {
      if (size) {
        width = size;
        height = size;
      } else {
        // Fill the parent: width AND height, not a forced square.
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

    const CYCLE_MS = Math.max(2000, cycleSeconds * 1000);
    const start = performance.now();
    let animationId = 0;
    let lastCycle = -1;

    const scatterTextActors = () => {
      for (const p of particles) {
        if (p.targetX === undefined) continue;
        // Throw them across the full canvas with fresh random velocity so the
        // noise restart is visually striking.
        p.x = Math.random() * width;
        p.y = Math.random() * height;
        p.vx = (Math.random() - 0.5) * 2.2;
        p.vy = (Math.random() - 0.5) * 2.2;
      }
    };

    // Radius around a target within which a text actor counts as "resolved".
    // Connections and jitter fade out based on this so the letter edges go
    // crisp exactly as the particle arrives.
    const SETTLE_RADIUS = 80;

    const particleSettled = (p: Particle): number => {
      if (p.targetX === undefined || p.targetY === undefined) return 0;
      const dx = p.targetX - p.x;
      const dy = p.targetY - p.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      return Math.max(0, 1 - d / SETTLE_RADIUS);
    };

    const animate = (now: number) => {
      const elapsed = now - start;
      const cycleIndex = Math.floor(elapsed / CYCLE_MS);
      const t = (elapsed % CYCLE_MS) / CYCLE_MS; // 0..1

      if (cycleIndex !== lastCycle) {
        scatterTextActors();
        lastCycle = cycleIndex;
      }

      // Time-based envelope for the force applied to text actors.
      //   t in [0.00, 0.06]  noise pass -- particles drift randomly
      //   t in [0.06, 0.75]  slow migration toward each glyph position
      //   t in [0.75, 0.92]  held in place
      //   t in [0.92, 1.00]  released back into chaos so the next cycle's
      //                      scatter does not feel abrupt
      let phase: number;
      if (t < 0.06) phase = 0;
      else if (t < 0.75) phase = smoothstep((t - 0.06) / 0.69);
      else if (t < 0.92) phase = 1;
      else phase = 1 - smoothstep((t - 0.92) / 0.08);

      const textJitter = (1 - phase) * 0.4;
      // Max return force 0.035 (was 0.065) so particles glide in rather than
      // snap. The longer cycle compensates so they still arrive in time.
      const textReturnForce = 0.0025 + phase * 0.032;
      const textDamping = 0.93 + phase * 0.04;

      ctx.clearRect(0, 0, width, height);

      // Update
      for (const p of particles) {
        if (p.targetX !== undefined && p.targetY !== undefined) {
          p.vx += (p.targetX - p.x) * textReturnForce;
          p.vy += (p.targetY - p.y) * textReturnForce;
          p.vx += (Math.random() - 0.5) * textJitter;
          p.vy += (Math.random() - 0.5) * textJitter;
          p.vx *= textDamping;
          p.vy *= textDamping;
        } else {
          // Edge / chaos actor -- always drifting, and lively.
          p.vx += (Math.random() - 0.5) * 0.65;
          p.vy += (Math.random() - 0.5) * 0.65;
          p.vx *= 0.93;
          p.vy *= 0.93;
          if (p.x < 0 || p.x > width) p.vx *= -1;
          if (p.y < 0 || p.y > height) p.vy *= -1;
        }
        p.x += p.vx;
        p.y += p.vy;
        p.x = Math.max(0, Math.min(width, p.x));
        p.y = Math.max(0, Math.min(height, p.y));
      }

      // Precompute per-particle settle factor for the draw passes below.
      const settleFactor = new Float32Array(particles.length);
      for (let i = 0; i < particles.length; i++) {
        settleFactor[i] = particleSettled(particles[i]);
      }

      // Connections between nearby particles -- the web. A line fades out as
      // either endpoint approaches its glyph target, so the letterforms
      // resolve crisply instead of staying tangled with cross-hatching.
      const CONNECT = 54;
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i];
        const sA = settleFactor[i];
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dSq = dx * dx + dy * dy;
          if (dSq >= CONNECT * CONNECT) continue;
          const sB = settleFactor[j];
          const resolveFade = 1 - Math.max(sA, sB);
          if (resolveFade < 0.05) continue; // both particles home -- no line
          const d = Math.sqrt(dSq);
          const alpha = 0.3 * (1 - d / CONNECT) * resolveFade;
          const r = (a.color[0] + b.color[0]) / 2;
          const g = (a.color[1] + b.color[1]) / 2;
          const bl = (a.color[2] + b.color[2]) / 2;
          ctx.strokeStyle = `rgba(${r}, ${g}, ${bl}, ${alpha})`;
          ctx.lineWidth = 0.9;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }

      // Draw particles on top. Text actors brighten + enlarge slightly as
      // they reach their glyph so the word has visual weight when it lands.
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        const isText = p.targetX !== undefined;
        const s = isText ? settleFactor[i] : 0;
        const alpha = isText ? 0.72 + 0.25 * s : 0.75;
        const radius = isText ? 1.9 + 0.5 * s : 1.9;
        const [r, g, b] = p.color;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
        ctx.fill();
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationId);
      ro.disconnect();
    };
  }, [size, cycleSeconds, text]);

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
