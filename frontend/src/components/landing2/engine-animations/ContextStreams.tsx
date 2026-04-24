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
 * Convergent streams -- eight curved traces drawing themselves inward
 * toward a central focal point. Supports Tab 1 "Context-first": gather
 * from many sources, then speak.
 */
export default function ContextStreams() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = setupCanvas(canvas);
    if (!ctx) return;

    const cx = CANVAS_SIZE / 2;
    const cy = CANVAS_SIZE / 2;
    const START_RADIUS = 170;

    // Stream definitions. Each has an angle of approach and a color tint.
    const STREAMS = Array.from({ length: 8 }, (_, i) => {
      const angle = (i / 8) * Math.PI * 2 - Math.PI / 2; // start from top
      const sx = cx + Math.cos(angle) * START_RADIUS;
      const sy = cy + Math.sin(angle) * START_RADIUS;
      // Control point: pulled laterally so the curve bends nicely.
      const perpAngle = angle + Math.PI / 2;
      const bend = 28 * ((i % 2) * 2 - 1); // alternate sides
      const midX = (sx + cx) / 2 + Math.cos(perpAngle) * bend;
      const midY = (sy + cy) / 2 + Math.sin(perpAngle) * bend;
      return {
        sx,
        sy,
        mx: midX,
        my: midY,
        colorT: i / 7,
        arrivalStart: 400 + i * 520, // ms; staggered entrance
        arrivalDuration: 1800,
      };
    });

    const CYCLE_MS = 11000;

    // Arrivals ring-pulses triggered when a stream reaches the centre.
    type Pulse = { startMs: number; colorT: number };
    let pulses: Pulse[] = [];
    const triggered = new Set<number>();

    const start = performance.now();
    let animationId = 0;

    const drawBezierHead = (
      s: { sx: number; sy: number; mx: number; my: number; colorT: number },
      progress: number,
      alpha: number
    ) => {
      // Draw a bezier up to `progress` with a soft fade along its length.
      const steps = 40;
      const endStep = Math.max(1, Math.floor(steps * progress));
      for (let k = 0; k < endStep; k++) {
        const t0 = k / steps;
        const t1 = (k + 1) / steps;
        const p0 = bezierPoint(s, t0);
        const p1 = bezierPoint(s, t1);
        // Fade toward the tail (older segments dimmer).
        const tailBrightness = clamp01((k - endStep + 14) / 14);
        ctx.strokeStyle = brandRgba(s.colorT, 0.7 * tailBrightness * alpha);
        ctx.lineWidth = 1.4;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(p0.x, p0.y);
        ctx.lineTo(p1.x, p1.y);
        ctx.stroke();
      }

      // Head dot (leads the trace).
      const head = bezierPoint(s, progress);
      const [r, g, b] = brandColor(s.colorT);
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.95 * alpha})`;
      ctx.beginPath();
      ctx.arc(head.x, head.y, 2.6, 0, Math.PI * 2);
      ctx.fill();
    };

    function bezierPoint(
      s: { sx: number; sy: number; mx: number; my: number },
      t: number
    ) {
      const mt = 1 - t;
      return {
        x: mt * mt * s.sx + 2 * mt * t * s.mx + t * t * cx,
        y: mt * mt * s.sy + 2 * mt * t * s.my + t * t * cy,
      };
    }

    const animate = (now: number) => {
      const elapsed = (now - start) % CYCLE_MS;

      // At cycle boundary, reset arrival tracking.
      if (elapsed < 120) {
        triggered.clear();
        pulses = [];
      }

      // Overall alpha: fade in 0-0.3s, fade out last 1s of cycle.
      const overallAlpha = smoothstep(elapsed / 300) * (1 - smoothstep((elapsed - (CYCLE_MS - 1000)) / 1000));

      ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

      // Soft outer halo behind the focal point to anchor the composition.
      const gradRadius = 90;
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, gradRadius);
      grad.addColorStop(0, `rgba(255, 135, 32, ${0.08 * overallAlpha})`);
      grad.addColorStop(1, "rgba(255, 135, 32, 0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

      // Draw streams
      STREAMS.forEach((s, i) => {
        if (elapsed < s.arrivalStart) return;
        const p = clamp01((elapsed - s.arrivalStart) / s.arrivalDuration);
        drawBezierHead(s, p, overallAlpha);
        if (p >= 1 && !triggered.has(i)) {
          triggered.add(i);
          pulses.push({ startMs: elapsed, colorT: s.colorT });
        }
      });

      // Draw arrival pulses (ripples emanating from centre).
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

      // Focal point -- grows brighter as more streams arrive.
      const focalBrightness = triggered.size / STREAMS.length;
      const focalAlpha = (0.2 + focalBrightness * 0.6) * overallAlpha;
      ctx.fillStyle = `rgba(255, 135, 32, ${focalAlpha})`;
      ctx.beginPath();
      ctx.arc(cx, cy, 5.5, 0, Math.PI * 2);
      ctx.fill();

      // Outgoing stroke downward once all streams have arrived.
      const OUTGOING_START = 7800;
      if (elapsed > OUTGOING_START) {
        const t = clamp01((elapsed - OUTGOING_START) / 1800);
        const env = smoothstep(t) * (1 - smoothstep((t - 0.6) / 0.4));
        const length = 60 * smoothstep(t);
        ctx.strokeStyle = `rgba(255, 135, 32, ${env * 0.9 * overallAlpha})`;
        ctx.lineWidth = 1.6;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(cx, cy + 8);
        ctx.lineTo(cx, cy + 8 + length);
        ctx.stroke();
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationId);
  }, []);

  return <canvas ref={canvasRef} />;
}
