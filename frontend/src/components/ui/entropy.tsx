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

// Motion feel. Everything moves at the same slow constant speed. Directions
// drift smoothly via small angular noise -- no velocity accumulation, no
// damping oscillation. This removes the "fast/slow/fast" pulsing.
const BASE_SPEED = 0.55; // pixels per frame
const ANGULAR_JITTER = 0.06; // radians per frame (edge actors + scatter phase)
const TEXT_ARRIVAL_RADIUS = 8; // px; speed decays to zero within this of target

// Web topology. Instead of "connect any two within R" we use K-nearest
// neighbours. Each particle always has K edges -> no stranded clusters.
const K_NEAREST = 3;
const KNN_RECOMPUTE_FRAMES = 4; // only rebuild the KNN graph every N frames
const MAX_EDGE_DRAW_DIST = 120; // px; don't streak ultra-long outliers

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
  /** Glyph target (undefined for edge/chaos actors). */
  targetX?: number;
  targetY?: number;
};

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
      if (img.data[idx + 3] > 128) points.push({ x, y });
    }
  }
  return points;
}

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
    let edges: [number, number][] = [];

    const rebuild = () => {
      const fontSize = Math.max(44, Math.floor(width / 10));
      const lineGap = Math.floor(fontSize * 0.12);
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

      // Text actors -- one per sampled text pixel. Start at random positions
      // + random angles. They will pick up a bias toward their target during
      // the settle phase.
      for (const pt of textPoints) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          angle: Math.random() * Math.PI * 2,
          color: brandColor(pt.x / width),
          targetX: pt.x,
          targetY: pt.y,
        });
      }

      // Edge / chaos actors -- always drifting.
      const EDGE_COUNT = Math.round((width * height) / 1700);
      for (let i = 0; i < EDGE_COUNT; i++) {
        const x = Math.random() * width;
        const y = Math.random() * height;
        particles.push({
          x,
          y,
          angle: Math.random() * Math.PI * 2,
          color: brandColor(x / width),
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

      // Time-based phase:
      //   [0.00, 0.06] noise
      //   [0.06, 0.75] formation -- particles glide toward glyphs
      //   [0.75, 0.92] held word
      //   [0.92, 1.00] release back to noise
      let phase: number;
      if (t < 0.06) phase = 0;
      else if (t < 0.75) phase = smoothstep((t - 0.06) / 0.69);
      else if (t < 0.92) phase = 1;
      else phase = 1 - smoothstep((t - 0.92) / 0.08);

      ctx.clearRect(0, 0, width, height);

      // --- Update particles -----------------------------------------------
      // All particles move at the same constant BASE_SPEED. Only direction
      // changes frame-to-frame. This is what gives the "slow, uniform" feel.
      for (const p of particles) {
        const hasTarget = p.targetX !== undefined && p.targetY !== undefined;

        if (hasTarget && phase > 0) {
          // Blend current heading toward the target heading weighted by phase.
          const dx = p.targetX! - p.x;
          const dy = p.targetY! - p.y;
          const dist = Math.hypot(dx, dy);
          const angleToTarget = dist > 0.0001 ? Math.atan2(dy, dx) : p.angle;

          // Direction blend via unit-vector average (no angle-wrap artifacts).
          const cx = Math.cos(p.angle) * (1 - phase) + Math.cos(angleToTarget) * phase;
          const cy = Math.sin(p.angle) * (1 - phase) + Math.sin(angleToTarget) * phase;
          const norm = Math.hypot(cx, cy) || 1;
          p.angle = Math.atan2(cy / norm, cx / norm);

          // A little residual wander, stronger during noise, near-zero at hold.
          p.angle += (Math.random() - 0.5) * ANGULAR_JITTER * (1 - 0.8 * phase);

          // Ease speed to zero once within TEXT_ARRIVAL_RADIUS of target.
          const arrivalFactor = Math.min(1, dist / TEXT_ARRIVAL_RADIUS);
          const speed = BASE_SPEED * (arrivalFactor * phase + (1 - phase));
          p.x += Math.cos(p.angle) * speed;
          p.y += Math.sin(p.angle) * speed;
        } else {
          // Edge actor, or text actor during pure-noise phase.
          p.angle += (Math.random() - 0.5) * ANGULAR_JITTER;
          p.x += Math.cos(p.angle) * BASE_SPEED;
          p.y += Math.sin(p.angle) * BASE_SPEED;

          // Reflect cleanly off the canvas walls so particles never leave.
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
