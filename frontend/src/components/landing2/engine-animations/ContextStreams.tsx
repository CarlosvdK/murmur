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
 * Convergent streams -- eight curved traces drawing themselves inward
 * toward a central focal point. Supports Tab 1 "Context-first".
 */
export default function ContextStreams() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    type Stream = {
      sx: number;
      sy: number;
      mx: number;
      my: number;
      colorT: number;
      arrivalStart: number;
      arrivalDuration: number;
    };

    let width = 0;
    let height = 0;
    let cx = 0;
    let cy = 0;
    let ctx: CanvasRenderingContext2D | null = null;
    let streams: Stream[] = [];
    const triggered = new Set<number>();
    let pulses: { startMs: number; colorT: number }[] = [];

    const CYCLE_MS = 11000;

    const rebuild = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      if (!width || !height) return;
      cx = width / 2;
      cy = height / 2;
      ctx = setupCanvas(canvas, width, height);

      const startRadius = Math.min(cx, cy) * 0.88;
      streams = Array.from({ length: 8 }, (_, i) => {
        const angle = (i / 8) * Math.PI * 2 - Math.PI / 2;
        const sx = cx + Math.cos(angle) * startRadius;
        const sy = cy + Math.sin(angle) * startRadius;
        const perpAngle = angle + Math.PI / 2;
        const bend = Math.min(cx, cy) * 0.16 * ((i % 2) * 2 - 1);
        const midX = (sx + cx) / 2 + Math.cos(perpAngle) * bend;
        const midY = (sy + cy) / 2 + Math.sin(perpAngle) * bend;
        return {
          sx,
          sy,
          mx: midX,
          my: midY,
          colorT: i / 7,
          arrivalStart: 400 + i * 520,
          arrivalDuration: 1800,
        };
      });

      triggered.clear();
      pulses = [];
    };

    rebuild();
    const ro = new ResizeObserver(rebuild);
    ro.observe(container);

    const bezierPoint = (s: Stream, t: number) => {
      const mt = 1 - t;
      return {
        x: mt * mt * s.sx + 2 * mt * t * s.mx + t * t * cx,
        y: mt * mt * s.sy + 2 * mt * t * s.my + t * t * cy,
      };
    };

    const drawBezierHead = (s: Stream, progress: number, alpha: number) => {
      if (!ctx) return;
      const steps = 40;
      const endStep = Math.max(1, Math.floor(steps * progress));
      for (let k = 0; k < endStep; k++) {
        const p0 = bezierPoint(s, k / steps);
        const p1 = bezierPoint(s, (k + 1) / steps);
        const tailBrightness = clamp01((k - endStep + 14) / 14);
        ctx.strokeStyle = brandRgba(s.colorT, 0.7 * tailBrightness * alpha);
        ctx.lineWidth = 1.6;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(p0.x, p0.y);
        ctx.lineTo(p1.x, p1.y);
        ctx.stroke();
      }
      const head = bezierPoint(s, progress);
      const [r, g, b] = brandColor(s.colorT);
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.95 * alpha})`;
      ctx.beginPath();
      ctx.arc(head.x, head.y, 3, 0, Math.PI * 2);
      ctx.fill();
    };

    const start = performance.now();
    let animationId = 0;

    const animate = (now: number) => {
      if (!ctx) {
        animationId = requestAnimationFrame(animate);
        return;
      }
      const elapsed = (now - start) % CYCLE_MS;

      if (elapsed < 120) {
        triggered.clear();
        pulses = [];
      }

      const overallAlpha =
        smoothstep(elapsed / 300) *
        (1 - smoothstep((elapsed - (CYCLE_MS - 1000)) / 1000));

      ctx.clearRect(0, 0, width, height);

      // Soft halo anchoring the focal point.
      const gradRadius = Math.min(cx, cy) * 0.45;
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, gradRadius);
      grad.addColorStop(0, `rgba(255, 135, 32, ${0.08 * overallAlpha})`);
      grad.addColorStop(1, "rgba(255, 135, 32, 0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      streams.forEach((s, i) => {
        if (elapsed < s.arrivalStart) return;
        const p = clamp01((elapsed - s.arrivalStart) / s.arrivalDuration);
        drawBezierHead(s, p, overallAlpha);
        if (p >= 1 && !triggered.has(i)) {
          triggered.add(i);
          pulses.push({ startMs: elapsed, colorT: s.colorT });
        }
      });

      pulses = pulses.filter((pulse) => elapsed - pulse.startMs < 1200);
      for (const pulse of pulses) {
        const age = (elapsed - pulse.startMs) / 1200;
        const radius = 6 + age * 40;
        const alpha = (1 - age) * 0.55 * overallAlpha;
        ctx.strokeStyle = brandRgba(pulse.colorT, alpha);
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.stroke();
      }

      const focalBrightness = triggered.size / streams.length;
      const focalAlpha = (0.2 + focalBrightness * 0.6) * overallAlpha;
      ctx.fillStyle = `rgba(255, 135, 32, ${focalAlpha})`;
      ctx.beginPath();
      ctx.arc(cx, cy, 6, 0, Math.PI * 2);
      ctx.fill();

      const OUTGOING_START = 7800;
      if (elapsed > OUTGOING_START) {
        const t = clamp01((elapsed - OUTGOING_START) / 1800);
        const env = smoothstep(t) * (1 - smoothstep((t - 0.6) / 0.4));
        const length = Math.min(cx, cy) * 0.18 * smoothstep(t);
        ctx.strokeStyle = `rgba(255, 135, 32, ${env * 0.9 * overallAlpha})`;
        ctx.lineWidth = 1.8;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(cx, cy + 9);
        ctx.lineTo(cx, cy + 9 + length);
        ctx.stroke();
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
