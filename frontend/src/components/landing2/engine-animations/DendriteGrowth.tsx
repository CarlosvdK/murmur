"use client";

import { useEffect, useRef } from "react";
import {
  brandColor,
  brandRgba,
  clamp01,
  setupCanvas,
  smoothstep,
} from "./shared";

/**
 * Dendrite growth -- a small network grows outward from a seed node,
 * branches thickening where they persist and pulses firing along existing
 * edges. Supports Tab 3 "Twins grow smarter over time".
 */
export default function DendriteGrowth() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    type Node = {
      x: number;
      y: number;
      parent: number | null;
      bornMs: number;
      colorT: number;
    };

    let width = 0;
    let height = 0;
    let ctx: CanvasRenderingContext2D | null = null;
    let nodes: Node[] = [];
    let nextSpawnAt = 0;
    const pulses: { fromIdx: number; toIdx: number; startMs: number }[] = [];
    let nextPulseAt = 1800;

    const MAX_NODES = 28;
    const SPAWN_INTERVAL = 650;

    const start = performance.now();

    const rebuild = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      if (!width || !height) return;
      ctx = setupCanvas(canvas, width, height);
      // Seed node at centre of the current canvas size.
      nodes = [
        {
          x: width / 2,
          y: height / 2,
          parent: null,
          bornMs: 0,
          colorT: 0.5,
        },
      ];
      nextSpawnAt = SPAWN_INTERVAL;
    };

    rebuild();
    const ro = new ResizeObserver(rebuild);
    ro.observe(container);

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

      let awayAngle = Math.random() * Math.PI * 2;
      if (parent.parent !== null) {
        const gp = nodes[parent.parent];
        awayAngle = Math.atan2(parent.y - gp.y, parent.x - gp.x);
      }
      const angle = awayAngle + (Math.random() - 0.5) * 1.4;
      // Scale branch length with canvas size.
      const baseLen = Math.min(width, height) * 0.11;
      const dist = baseLen + Math.random() * baseLen * 0.55;
      let x = parent.x + Math.cos(angle) * dist;
      let y = parent.y + Math.sin(angle) * dist;

      const margin = 22;
      x = Math.max(margin, Math.min(width - margin, x));
      y = Math.max(margin, Math.min(height - margin, y));

      for (const existing of nodes) {
        if (distance(existing, { x, y }) < 30) return;
      }

      nodes.push({
        x,
        y,
        parent: parentIdx,
        bornMs: elapsed,
        colorT: clamp01(depth / 5),
      });
    };

    let animationId = 0;

    const animate = (now: number) => {
      if (!ctx) {
        animationId = requestAnimationFrame(animate);
        return;
      }
      const elapsed = now - start;
      ctx.clearRect(0, 0, width, height);

      if (elapsed >= nextSpawnAt) {
        spawnNode(elapsed);
        nextSpawnAt = elapsed + SPAWN_INTERVAL * (0.85 + Math.random() * 0.4);
      }

      if (elapsed >= nextPulseAt && nodes.length > 4) {
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

      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];
        if (n.parent === null) continue;
        const p = nodes[n.parent];
        const age = clamp01((elapsed - n.bornMs) / 900);
        const alpha = 0.55 * age;
        ctx.strokeStyle = brandRgba(n.colorT, alpha);
        ctx.lineWidth = 1.1 + age * 0.8;
        ctx.lineCap = "round";
        const drawT = smoothstep(age);
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(p.x + (n.x - p.x) * drawT, p.y + (n.y - p.y) * drawT);
        ctx.stroke();
      }

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
        ctx.arc(x, y, 3.4, 0, Math.PI * 2);
        ctx.fill();
      }

      for (const n of nodes) {
        const age = clamp01((elapsed - n.bornMs) / 700);
        const radius = 3.2 + 1.8 * smoothstep(age);
        const [r, g, b] = brandColor(n.colorT);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.95 * age})`;
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
        ctx.fill();
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationId);
      ro.disconnect();
    };
  }, []);

  return (
    <div ref={containerRef} className="h-full w-full">
      <canvas ref={canvasRef} />
    </div>
  );
}
