"use client";

import { useEffect, useRef } from "react";
import {
  brandColor,
  clamp01,
  lerp,
  setupCanvas,
  smoothstep,
} from "./shared";

/**
 * Confidence field -- a single probability distribution hovering over a
 * baseline that reshapes between confident, uncertain and tension states.
 * Supports Tab 4 "Designed to be wrong sometimes".
 */
export default function ConfidenceField() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const SAMPLES = 160;

    type Shape = { label: string; fn: (x: number) => number };

    const gauss = (mu: number, sigma: number) => (x: number) =>
      Math.exp(-((x - mu) ** 2) / (2 * sigma * sigma));

    const normalise = (fn: (x: number) => number): ((x: number) => number) => {
      let peak = 0;
      for (let i = 0; i < SAMPLES; i++) {
        peak = Math.max(peak, fn(i / (SAMPLES - 1)));
      }
      return (x: number) => (peak > 0 ? fn(x) / peak : 0);
    };

    const shapes: Shape[] = [
      { label: "confident", fn: normalise(gauss(0.5, 0.05)) },
      { label: "uncertain", fn: normalise((x) => gauss(0.5, 0.17)(x)) },
      {
        label: "tension",
        fn: normalise((x) => gauss(0.3, 0.06)(x) + gauss(0.7, 0.06)(x)),
      },
      { label: "leaning low", fn: normalise(gauss(0.33, 0.11)) },
      { label: "leaning high", fn: normalise(gauss(0.67, 0.11)) },
    ];

    const sampleCurve = (fn: (x: number) => number): Float32Array => {
      const out = new Float32Array(SAMPLES);
      for (let i = 0; i < SAMPLES; i++) {
        out[i] = fn(i / (SAMPLES - 1));
      }
      return out;
    };

    let width = 0;
    let height = 0;
    let axisY = 0;
    let peakHeight = 0;
    let axisMargin = 0;
    let ctx: CanvasRenderingContext2D | null = null;
    let currentCurve: Float32Array = sampleCurve(shapes[0].fn);
    let targetCurve: Float32Array = sampleCurve(shapes[0].fn);
    let currentLabel = shapes[0].label;
    let nextLabel = currentLabel;
    let shapeIdx = 0;
    let transitionStart = 0;
    const TRANSITION_MS = 1100;
    const HOLD_MS = 1900;
    let stateEndAt = HOLD_MS;
    let transitioning = false;

    const rebuild = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      if (!width || !height) return;
      ctx = setupCanvas(canvas, width, height);
      axisY = height * 0.66;
      peakHeight = axisY * 0.78; // peaks tall enough to fill the room
      axisMargin = Math.max(30, width * 0.09);
    };

    rebuild();
    const ro = new ResizeObserver(rebuild);
    ro.observe(container);

    const start = performance.now();
    let animationId = 0;

    const animate = (now: number) => {
      if (!ctx) {
        animationId = requestAnimationFrame(animate);
        return;
      }
      const elapsed = now - start;
      ctx.clearRect(0, 0, width, height);

      if (!transitioning && elapsed >= stateEndAt) {
        shapeIdx = (shapeIdx + 1) % shapes.length;
        targetCurve = sampleCurve(shapes[shapeIdx].fn);
        nextLabel = shapes[shapeIdx].label;
        transitionStart = elapsed;
        transitioning = true;
      }
      if (transitioning) {
        const t = (elapsed - transitionStart) / TRANSITION_MS;
        if (t >= 1) {
          for (let i = 0; i < SAMPLES; i++) currentCurve[i] = targetCurve[i];
          currentLabel = nextLabel;
          transitioning = false;
          stateEndAt = elapsed + HOLD_MS;
        } else {
          const eased = smoothstep(t);
          for (let i = 0; i < SAMPLES; i++) {
            currentCurve[i] = lerp(currentCurve[i], targetCurve[i], eased * 0.18);
          }
        }
      }

      // Axis
      ctx.strokeStyle = "rgba(0, 0, 0, 0.18)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(axisMargin, axisY);
      ctx.lineTo(width - axisMargin, axisY);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(axisMargin, axisY - 5);
      ctx.lineTo(axisMargin, axisY + 5);
      ctx.moveTo(width - axisMargin, axisY - 5);
      ctx.lineTo(width - axisMargin, axisY + 5);
      ctx.stroke();

      const xAt = (i: number) =>
        axisMargin + ((width - 2 * axisMargin) * i) / (SAMPLES - 1);
      const yAt = (i: number) => axisY - currentCurve[i] * peakHeight;

      // Area fill with horizontal brand gradient.
      const fillGrad = ctx.createLinearGradient(axisMargin, 0, width - axisMargin, 0);
      for (let i = 0; i <= 4; i++) {
        const t = i / 4;
        const [r, g, b] = brandColor(t);
        fillGrad.addColorStop(t, `rgba(${r}, ${g}, ${b}, 0.18)`);
      }
      ctx.fillStyle = fillGrad;
      ctx.beginPath();
      ctx.moveTo(xAt(0), axisY);
      for (let i = 0; i < SAMPLES; i++) ctx.lineTo(xAt(i), yAt(i));
      ctx.lineTo(xAt(SAMPLES - 1), axisY);
      ctx.closePath();
      ctx.fill();

      // Stroke on top
      const strokeGrad = ctx.createLinearGradient(axisMargin, 0, width - axisMargin, 0);
      for (let i = 0; i <= 4; i++) {
        const t = i / 4;
        const [r, g, b] = brandColor(t);
        strokeGrad.addColorStop(t, `rgba(${r}, ${g}, ${b}, 0.75)`);
      }
      ctx.strokeStyle = strokeGrad;
      ctx.lineWidth = 1.8;
      ctx.beginPath();
      for (let i = 0; i < SAMPLES; i++) {
        const x = xAt(i);
        const y = yAt(i);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Label above peak, tracked uppercase.
      let peakIdx = 0;
      let peakVal = -Infinity;
      for (let i = 0; i < SAMPLES; i++) {
        if (currentCurve[i] > peakVal) {
          peakVal = currentCurve[i];
          peakIdx = i;
        }
      }
      const labelAlpha = transitioning
        ? 1 - smoothstep((elapsed - transitionStart) / TRANSITION_MS)
        : clamp01((elapsed - transitionStart - TRANSITION_MS) / 400);
      ctx.fillStyle = `rgba(40, 40, 45, ${0.55 * labelAlpha})`;
      ctx.font = "600 11px Inter, system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "bottom";
      const peakX = xAt(peakIdx);
      const peakY = yAt(peakIdx) - 16;
      const tracked = (transitioning ? currentLabel : nextLabel)
        .toUpperCase()
        .split("")
        .join("\u2009\u2009");
      ctx.fillText(tracked, peakX, peakY);

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
