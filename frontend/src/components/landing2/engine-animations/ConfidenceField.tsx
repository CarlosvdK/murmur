"use client";

import { useEffect, useRef } from "react";
import {
  CANVAS_SIZE,
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
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = setupCanvas(canvas);
    if (!ctx) return;

    const SAMPLES = 120;
    const AXIS_Y = CANVAS_SIZE * 0.62;
    const PEAK_HEIGHT = 150; // how tall a peak of height 1 draws

    type Shape = { label: string; fn: (x: number) => number };

    const gauss = (mu: number, sigma: number) => (x: number) =>
      Math.exp(-((x - mu) ** 2) / (2 * sigma * sigma));

    // Each shape is a function over x in [0,1]. We normalise y so the peak = 1.
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

    const start = performance.now();
    let animationId = 0;

    const animate = (now: number) => {
      const elapsed = now - start;
      ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

      // --- Drive the state machine
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

      // --- Draw baseline axis
      const axisMargin = 60;
      ctx.strokeStyle = "rgba(0, 0, 0, 0.18)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(axisMargin, AXIS_Y);
      ctx.lineTo(CANVAS_SIZE - axisMargin, AXIS_Y);
      ctx.stroke();

      // End ticks.
      ctx.beginPath();
      ctx.moveTo(axisMargin, AXIS_Y - 4);
      ctx.lineTo(axisMargin, AXIS_Y + 4);
      ctx.moveTo(CANVAS_SIZE - axisMargin, AXIS_Y - 4);
      ctx.lineTo(CANVAS_SIZE - axisMargin, AXIS_Y + 4);
      ctx.stroke();

      // --- Draw the curve as a filled area below the stroke
      const xAt = (i: number): number =>
        axisMargin + ((CANVAS_SIZE - 2 * axisMargin) * i) / (SAMPLES - 1);
      const yAt = (i: number): number =>
        AXIS_Y - currentCurve[i] * PEAK_HEIGHT;

      // Gradient fill from left (blue) to right (orange) with soft alpha.
      const fillGrad = ctx.createLinearGradient(axisMargin, 0, CANVAS_SIZE - axisMargin, 0);
      for (let i = 0; i <= 4; i++) {
        const t = i / 4;
        const [r, g, b] = brandColor(t);
        fillGrad.addColorStop(t, `rgba(${r}, ${g}, ${b}, 0.18)`);
      }
      ctx.fillStyle = fillGrad;
      ctx.beginPath();
      ctx.moveTo(xAt(0), AXIS_Y);
      for (let i = 0; i < SAMPLES; i++) {
        ctx.lineTo(xAt(i), yAt(i));
      }
      ctx.lineTo(xAt(SAMPLES - 1), AXIS_Y);
      ctx.closePath();
      ctx.fill();

      // Curve stroke on top.
      const strokeGrad = ctx.createLinearGradient(axisMargin, 0, CANVAS_SIZE - axisMargin, 0);
      for (let i = 0; i <= 4; i++) {
        const t = i / 4;
        const [r, g, b] = brandColor(t);
        strokeGrad.addColorStop(t, `rgba(${r}, ${g}, ${b}, 0.75)`);
      }
      ctx.strokeStyle = strokeGrad;
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      for (let i = 0; i < SAMPLES; i++) {
        const x = xAt(i);
        const y = yAt(i);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // --- Label above the current peak, uppercase with loose tracking.
      // Find the x-index of the maximum in current curve.
      let peakIdx = 0;
      let peakVal = -Infinity;
      for (let i = 0; i < SAMPLES; i++) {
        if (currentCurve[i] > peakVal) {
          peakVal = currentCurve[i];
          peakIdx = i;
        }
      }
      // Fade label with the transition so it breathes between states.
      const labelAlpha = transitioning
        ? 1 - smoothstep((elapsed - transitionStart) / TRANSITION_MS)
        : clamp01((elapsed - transitionStart - TRANSITION_MS) / 400);
      ctx.fillStyle = `rgba(40, 40, 45, ${0.55 * labelAlpha})`;
      ctx.font = "600 10px Inter, system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "bottom";
      const labelText = (transitioning ? currentLabel : nextLabel).toUpperCase();
      // Letter spacing: render characters with manual tracking.
      const peakX = xAt(peakIdx);
      const peakY = yAt(peakIdx) - 14;
      const tracked = labelText.split("").join("\u2009\u2009"); // thin spaces
      ctx.fillText(tracked, peakX, peakY);

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationId);
  }, []);

  return <canvas ref={canvasRef} />;
}
