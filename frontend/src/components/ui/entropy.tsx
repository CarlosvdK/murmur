"use client";

import { useEffect, useRef } from "react";

interface EntropyProps {
  className?: string;
  /** Optional fixed side. When omitted, fills container width + height. */
  size?: number;
  /** Seconds for one full chaos -> text -> chaos loop. */
  cycleSeconds?: number;
  /** Line(s) of text the central particles form. */
  text?: string[];
}

// Brand palette -- matches Murmuration so the site reads as one family.
const BRAND_PALETTE: [number, number, number][] = [
  [68, 140, 253], // blue  #448CFD
  [255, 141, 228], // pink  #FF8DE4
  [255, 135, 32], // orange #FF8720
];

// Motion feel. Everything that moves moves at the same slow constant speed.
// Directions drift via small angular noise -- no velocity accumulation, no
// damping oscillation. Many dots don't move at all (anchors) so the web has
// stable structure.
const BASE_SPEED = 0.28; // pixels per frame for moving edge dots
const SETTLE_SPEED = 1.9; // px/frame for text actors travelling to their glyph
const ANGULAR_JITTER = 0.025; // radians per frame -- lazy direction drift
const TEXT_ARRIVAL_RADIUS = 8; // px; speed decays to zero within this of target
const ANCHOR_FRACTION = 0.55; // share of edge dots that never move

// Web topology. Instead of "connect any two within R" we use K-nearest
// neighbours. Each particle always has K edges -> no stranded clusters.
const K_NEAREST = 3;
const KNN_RECOMPUTE_FRAMES = 5; // rebuild the KNN graph every N frames
const MAX_EDGE_DRAW_DIST = 140; // px; don't streak ultra-long outliers

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
  angle: number; // current heading in radians
  color: [number, number, number];
  /** True for edge dots that never move. Creates the "anchor" feel of a web. */
  anchor: boolean;
  /** Glyph target (undefined for edge/chaos actors). */
  targetX?: number;
  targetY?: number;
};

/**
 * Sample points along the OUTLINE of each glyph (not the filled interior).
 * This gives the "spider writes letters with web threads" feel from
 * Charlotte's Web -- dots trace the strokes of the letters, and when KNN
 * connects them the web literally draws the words.
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

  // Stroke the glyphs instead of filling them. lineWidth is a bit wider
  // than the sampling stride so every part of the stroke is reliably
  // caught by the sample grid -- otherwise stride alignment artifacts
  // make letters render as blocky rectangles.
  octx.strokeStyle = "white";
  octx.lineWidth = Math.max(3, fontSize * 0.065);
  octx.lineJoin = "round";
  octx.lineCap = "round";
  octx.font = `800 ${fontSize}px Inter, system-ui, sans-serif`;
  octx.textAlign = "center";
  octx.textBaseline = "middle";

  const totalHeight = lines.length * fontSize + (lines.length - 1) * lineGap;
  const startY = canvasHeight / 2 - totalHeight / 2 + fontSize / 2;
  lines.forEach((line, i) => {
    octx.strokeText(line, canvasWidth / 2, startY + i * (fontSize + lineGap));
  });

  const img = octx.getImageData(0, 0, canvasWidth, canvasHeight);
  const points: { x: number; y: number }[] = [];
  for (let y = 0; y < canvasHeight; y += stride) {
    for (let x = 0; x < canvasWidth; x += stride) {
      const idx = (y * canvasWidth + x) * 4;
      if (img.data[idx + 3] > 128) points.push({ x, y });
    }
  }
  return points;
}

export function Entropy({
  className = "",
  size,
  cycleSeconds = 16,
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
    let edges: [number, number][] = [];

    const rebuild = () => {
      const fontSize = Math.max(44, Math.floor(width / 10));
      const lineGap = Math.floor(fontSize * 0.12);
      // Stride must be smaller than the stroke lineWidth so every part of
      // the letter gets caught, otherwise the sample grid aliasing turns
      // round glyphs into blocky rectangles. Keep stride ~= lineWidth.
      const stride = Math.max(5, Math.round(width / 130));
      const textPoints = computeTextMask(
        text,
        width,
        height,
        fontSize,
        lineGap,
        stride
      );

      particles = [];

      // Text actors -- one per sampled contour pixel. Always mobile; they
      // need to reach their glyph position. Once they arrive the settle
      // logic clamps speed to 0, so they effectively become anchors on the
      // letter itself.
      for (const pt of textPoints) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          angle: Math.random() * Math.PI * 2,
          color: brandColor(pt.x / width),
          anchor: false,
          targetX: pt.x,
          targetY: pt.y,
        });
      }

      // Edge / chaos actors. Each one gets a coin flip for anchor-ness; the
      // anchor fraction controls how "living" vs "structural" the web feels.
      const EDGE_COUNT = Math.round((width * height) / 1700);
      for (let i = 0; i < EDGE_COUNT; i++) {
        const x = Math.random() * width;
        const y = Math.random() * height;
        particles.push({
          x,
          y,
          angle: Math.random() * Math.PI * 2,
          color: brandColor(x / width),
          anchor: Math.random() < ANCHOR_FRACTION,
        });
      }

      edges = [];
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

    const CYCLE_MS = Math.max(2000, cycleSeconds * 1000);
    const start = performance.now();
    let animationId = 0;
    let lastCycle = -1;
    let frame = 0;

    const scatterTextActors = () => {
      for (const p of particles) {
        if (p.targetX === undefined) continue;
        p.x = Math.random() * width;
        p.y = Math.random() * height;
        p.angle = Math.random() * Math.PI * 2;
      }
    };

    /** Recompute K-nearest-neighbour edges. Dedupes so we do not draw the
     *  same line twice. O(N * K * N) with an incremental top-K rather than
     *  a full sort, but plain enough for N in the low thousands. */
    const computeKNN = () => {
      const N = particles.length;
      const topD = new Float32Array(K_NEAREST);
      const topJ = new Int32Array(K_NEAREST);
      const seen = new Set<number>();
      const fresh: [number, number][] = [];

      for (let i = 0; i < N; i++) {
        for (let k = 0; k < K_NEAREST; k++) {
          topD[k] = Infinity;
          topJ[k] = -1;
        }
        const pi = particles[i];
        for (let j = 0; j < N; j++) {
          if (j === i) continue;
          const dx = pi.x - particles[j].x;
          const dy = pi.y - particles[j].y;
          const d = dx * dx + dy * dy;
          // Insertion into the top-K buffer (keeps it sorted ascending).
          if (d < topD[K_NEAREST - 1]) {
            let k = K_NEAREST - 1;
            while (k > 0 && topD[k - 1] > d) {
              topD[k] = topD[k - 1];
              topJ[k] = topJ[k - 1];
              k--;
            }
            topD[k] = d;
            topJ[k] = j;
          }
        }
        for (let k = 0; k < K_NEAREST; k++) {
          const j = topJ[k];
          if (j < 0) continue;
          const key = i < j ? i * N + j : j * N + i;
          if (seen.has(key)) continue;
          seen.add(key);
          fresh.push(i < j ? [i, j] : [j, i]);
        }
      }

      edges = fresh;
    };

    const animate = (now: number) => {
      const elapsed = now - start;
      const cycleIndex = Math.floor(elapsed / CYCLE_MS);
      const t = (elapsed % CYCLE_MS) / CYCLE_MS;

      if (cycleIndex !== lastCycle) {
        scatterTextActors();
        lastCycle = cycleIndex;
      }

      // Time-based phase, tuned to a 16s cycle:
      //   [0.00, 0.03]  scatter (~0.5s)
      //   [0.03, 0.47]  formation, ~7s of gliding toward glyphs
      //   [0.47, 0.91]  held word, ~7s
      //   [0.91, 1.00]  release back into noise, ~1.4s
      let phase: number;
      if (t < 0.03) phase = 0;
      else if (t < 0.47) phase = smoothstep((t - 0.03) / 0.44);
      else if (t < 0.91) phase = 1;
      else phase = 1 - smoothstep((t - 0.91) / 0.09);

      ctx.clearRect(0, 0, width, height);

      // --- Update particles -----------------------------------------------
      // Anchors do not move at all. Mobile particles glide at a single slow
      // constant speed; only direction drifts. That gives the "living web"
      // feel -- some threads taut, some breathing.
      for (const p of particles) {
        if (p.anchor) continue;

        const hasTarget = p.targetX !== undefined && p.targetY !== undefined;

        if (hasTarget && phase > 0) {
          // Blend current heading toward the target heading weighted by phase.
          const dx = p.targetX! - p.x;
          const dy = p.targetY! - p.y;
          const dist = Math.hypot(dx, dy);
          const angleToTarget = dist > 0.0001 ? Math.atan2(dy, dx) : p.angle;

          const cx = Math.cos(p.angle) * (1 - phase) + Math.cos(angleToTarget) * phase;
          const cy = Math.sin(p.angle) * (1 - phase) + Math.sin(angleToTarget) * phase;
          const norm = Math.hypot(cx, cy) || 1;
          p.angle = Math.atan2(cy / norm, cx / norm);

          // Residual wander decays to zero at phase=1 so landed particles
          // stay pinned to their glyph pixel instead of drifting off.
          p.angle += (Math.random() - 0.5) * ANGULAR_JITTER * (1 - phase);

          // Travel speed. Starts at BASE_SPEED during noise, ramps up to
          // SETTLE_SPEED quickly (phase ~ 0.2) so particles have the full
          // ~5s of cruising to cover the canvas, then decays with arrival
          // factor so they park cleanly on the target.
          const speedRamp = Math.min(1, phase * 5);
          const cruiseSpeed = BASE_SPEED + (SETTLE_SPEED - BASE_SPEED) * speedRamp;
          const arrivalFactor = Math.min(1, dist / TEXT_ARRIVAL_RADIUS);
          const speed = cruiseSpeed * arrivalFactor;
          p.x += Math.cos(p.angle) * speed;
          p.y += Math.sin(p.angle) * speed;
        } else {
          // Mobile edge actor, or text actor during pure-noise phase.
          p.angle += (Math.random() - 0.5) * ANGULAR_JITTER;
          p.x += Math.cos(p.angle) * BASE_SPEED;
          p.y += Math.sin(p.angle) * BASE_SPEED;

          if (p.x < 0) {
            p.x = 0;
            p.angle = Math.PI - p.angle;
          } else if (p.x > width) {
            p.x = width;
            p.angle = Math.PI - p.angle;
          }
          if (p.y < 0) {
            p.y = 0;
            p.angle = -p.angle;
          } else if (p.y > height) {
            p.y = height;
            p.angle = -p.angle;
          }
        }
      }

      // --- KNN graph ------------------------------------------------------
      if (frame % KNN_RECOMPUTE_FRAMES === 0 || edges.length === 0) {
        computeKNN();
      }

      // --- Draw edges -----------------------------------------------------
      for (const [i, j] of edges) {
        const a = particles[i];
        const b = particles[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d > MAX_EDGE_DRAW_DIST) continue;
        const alpha = 0.38 * (1 - d / MAX_EDGE_DRAW_DIST);
        const r = (a.color[0] + b.color[0]) / 2;
        const g = (a.color[1] + b.color[1]) / 2;
        const bl = (a.color[2] + b.color[2]) / 2;
        ctx.strokeStyle = `rgba(${r}, ${g}, ${bl}, ${alpha})`;
        ctx.lineWidth = 0.85;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }

      // --- Draw particles -------------------------------------------------
      // Text actors lean slightly brighter + larger as they approach their
      // target so the word has visual weight but never disconnects from the
      // web.
      for (const p of particles) {
        let settled = 0;
        if (p.targetX !== undefined && p.targetY !== undefined) {
          const dx = p.targetX - p.x;
          const dy = p.targetY - p.y;
          const d = Math.sqrt(dx * dx + dy * dy);
          settled = Math.max(0, 1 - d / 60);
        }
        const alpha = 0.78 + 0.18 * settled;
        const radius = 1.95 + 0.45 * settled;
        const [r, g, b] = p.color;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
        ctx.fill();
      }

      frame++;
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
