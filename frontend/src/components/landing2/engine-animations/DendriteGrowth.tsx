"use client";

import { useEffect, useRef } from "react";
import {
  CANVAS_SIZE,
  brandColor,
  brandRgba,
  clamp01,
  setupCanvas,
  smoothstep,
} from "./shared";

/**
 * Dendrite growth -- a small network that grows organically outward from
 * a seed node, branches thickening where they persist and pulses firing
 * along existing edges. Supports Tab 3 "Twins grow smarter over time".
 */
export default function DendriteGrowth() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = setupCanvas(canvas);
    if (!ctx) return;

    const CX = CANVAS_SIZE / 2;
    const CY = CANVAS_SIZE / 2;

    type Node = {
      x: number;
      y: number;
      parent: number | null;
      bornMs: number;
      colorT: number;
    };

    const nodes: Node[] = [
      { x: CX, y: CY, parent: null, bornMs: 0, colorT: 0.5 },
    ];

    const MAX_NODES = 24;
    const SPAWN_INTERVAL = 650; // ms
    let nextSpawnAt = SPAWN_INTERVAL;

    type Pulse = { fromIdx: number; toIdx: number; startMs: number };
    const pulses: Pulse[] = [];
    let nextPulseAt = 1800;

    const start = performance.now();
    let animationId = 0;

    const distance = (a: { x: number; y: number }, b: { x: number; y: number }) =>
      Math.hypot(a.x - b.x, a.y - b.y);

    const nodeDepth = (n: Node): number => {
      let d = 0;
      let cur: Node | null = n;
      while (cur && cur.parent !== null) {
        cur = nodes[cur.parent];
        d++;
      }
      return d;
    };

    const spawnNode = (elapsed: number) => {
      if (nodes.length >= MAX_NODES) return;
      // Pick an existing node weighted toward leaves (fewer existing children).
      const childCount = new Array(nodes.length).fill(0);
      for (const n of nodes) if (n.parent !== null) childCount[n.parent]++;
      const weights = nodes.map((_, i) => 1 / (1 + childCount[i] * 2));
      const totalW = weights.reduce((a, b) => a + b, 0);
      let pick = Math.random() * totalW;
      let parentIdx = 0;
      for (let i = 0; i < weights.length; i++) {
        pick -= weights[i];
        if (pick <= 0) {
          parentIdx = i;
          break;
        }
      }
      const parent = nodes[parentIdx];
      const depth = nodeDepth(parent) + 1;

      // Angle away from the parent's own parent (so branches reach outward).
      let awayAngle = Math.random() * Math.PI * 2;
      if (parent.parent !== null) {
        const gp = nodes[parent.parent];
        awayAngle = Math.atan2(parent.y - gp.y, parent.x - gp.x);
      }
      const angle = awayAngle + (Math.random() - 0.5) * 1.4;
      const dist = 48 + Math.random() * 26;
      let x = parent.x + Math.cos(angle) * dist;
      let y = parent.y + Math.sin(angle) * dist;

      // Keep inside canvas with a margin.
      x = Math.max(20, Math.min(CANVAS_SIZE - 20, x));
      y = Math.max(20, Math.min(CANVAS_SIZE - 20, y));

      // Avoid collisions with other nodes.
      for (const existing of nodes) {
        if (distance(existing, { x, y }) < 28) return; // skip this tick
      }

      nodes.push({
        x,
        y,
        parent: parentIdx,
        bornMs: elapsed,
        // Colour shifts with depth along the brand palette.
        colorT: clamp01(depth / 5),
      });
    };

    const animate = (now: number) => {
      const elapsed = now - start;
      ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

      if (elapsed >= nextSpawnAt) {
        spawnNode(elapsed);
        nextSpawnAt =
          elapsed + SPAWN_INTERVAL * (0.85 + Math.random() * 0.4);
      }

      // Schedule edge pulses once we have a handful of edges.
      if (elapsed >= nextPulseAt && nodes.length > 4) {
        // Pick a random edge.
        const childCandidates = nodes
          .map((n, i) => (n.parent !== null ? i : -1))
          .filter((i) => i >= 0);
        if (childCandidates.length) {
          const idx =
            childCandidates[Math.floor(Math.random() * childCandidates.length)];
          pulses.push({
            fromIdx: nodes[idx].parent!,
            toIdx: idx,
            startMs: elapsed,
          });
          nextPulseAt = elapsed + 650 + Math.random() * 900;
        }
      }

      // --- Draw edges
      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];
        if (n.parent === null) continue;
        const p = nodes[n.parent];
        const age = clamp01((elapsed - n.bornMs) / 900);
        const alpha = 0.55 * age;
        ctx.strokeStyle = brandRgba(n.colorT, alpha);
        ctx.lineWidth = 1 + age * 0.6;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        // Partial line during growth for a "draw-on" feel.
        const drawT = smoothstep(age);
        ctx.lineTo(
          p.x + (n.x - p.x) * drawT,
          p.y + (n.y - p.y) * drawT
        );
        ctx.stroke();
      }

      // --- Draw pulses travelling along edges
      for (let i = pulses.length - 1; i >= 0; i--) {
        const pulse = pulses[i];
        const age = (elapsed - pulse.startMs) / 700;
        if (age >= 1) {
          pulses.splice(i, 1);
          continue;
        }
        const from = nodes[pulse.fromIdx];
        const to = nodes[pulse.toIdx];
        if (!to) continue;
        const t = smoothstep(age);
        const x = from.x + (to.x - from.x) * t;
        const y = from.y + (to.y - from.y) * t;
        const alpha = (1 - age) * 0.9;
        const [r, g, b] = brandColor(to.colorT);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(x, y, 3.2, 0, Math.PI * 2);
        ctx.fill();
      }

      // --- Draw nodes
      for (const n of nodes) {
        const age = clamp01((elapsed - n.bornMs) / 700);
        const radius = 3 + 1.5 * smoothstep(age);
        const [r, g, b] = brandColor(n.colorT);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.95 * age})`;
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
        ctx.fill();
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationId);
  }, []);

  return <canvas ref={canvasRef} />;
}
