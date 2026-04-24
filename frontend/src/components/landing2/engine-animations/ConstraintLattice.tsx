"use client";

import { useEffect, useRef } from "react";
import {
  CANVAS_SIZE,
  brandColor,
  brandRgba,
  setupCanvas,
  smoothstep,
} from "./shared";

/**
 * Constraint lattice -- chaotic dots pulled into a structured grid, then
 * breathing softly in place. Supports Tab 2 "Structured personas".
 *
 * Phases: chaos (0-2s) -> settle (2-4.5s) -> hold with breath (4.5s+).
 * Not looped. Component remounts each time the tab re-opens.
 */
export default function ConstraintLattice() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = setupCanvas(canvas);
    if (!ctx) return;

    const CX = CANVAS_SIZE / 2;
    const CY = CANVAS_SIZE / 2;
    const COLS = 5;
    const ROWS = 4;
    const GRID_W = 260;
    const GRID_H = 200;

    type Dot = {
      chaosX: number;
      chaosY: number;
      slotX: number;
      slotY: number;
      x: number;
      y: number;
      vx: number;
      vy: number;
      phase: number;
      phaseSpeed: number;
      colorT: number;
    };

    const dots: Dot[] = [];
    let idx = 0;
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const slotX =
          CX -
          GRID_W / 2 +
          (GRID_W / (COLS - 1)) * c +
          (Math.random() - 0.5) * 8;
        const slotY =
          CY -
          GRID_H / 2 +
          (GRID_H / (ROWS - 1)) * r +
          (Math.random() - 0.5) * 8;
        const chaosX = CANVAS_SIZE * 0.1 + Math.random() * CANVAS_SIZE * 0.8;
        const chaosY = CANVAS_SIZE * 0.1 + Math.random() * CANVAS_SIZE * 0.8;
        dots.push({
          chaosX,
          chaosY,
          slotX,
          slotY,
          x: chaosX,
          y: chaosY,
          vx: (Math.random() - 0.5) * 2,
          vy: (Math.random() - 0.5) * 2,
          phase: Math.random() * Math.PI * 2,
          phaseSpeed: 0.018 + Math.random() * 0.015,
          colorT: idx / (ROWS * COLS - 1),
        });
        idx++;
      }
    }

    type Pulse = { dotIdx: number; startMs: number };
    const pulses: Pulse[] = [];
    let nextPulseAt = 5500;

    const CHAOS_END = 2000;
    const SETTLE_END = 4500;

    const start = performance.now();
    let animationId = 0;

    const animate = (now: number) => {
      const elapsed = now - start;
      ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

      // Compute settle factor (0 during chaos, 1 once fully locked in).
      let settle = 0;
      if (elapsed < CHAOS_END) settle = 0;
      else if (elapsed < SETTLE_END)
        settle = smoothstep((elapsed - CHAOS_END) / (SETTLE_END - CHAOS_END));
      else settle = 1;

      // --- Update dots
      for (const d of dots) {
        if (settle < 1) {
          // Chaos drift + easing toward slot, weighted by settle.
          d.vx += (Math.random() - 0.5) * 0.35;
          d.vy += (Math.random() - 0.5) * 0.35;
          d.vx *= 0.94;
          d.vy *= 0.94;
          const chaosX = d.x + d.vx;
          const chaosY = d.y + d.vy;
          d.x = chaosX * (1 - settle) + d.slotX * settle;
          d.y = chaosY * (1 - settle) + d.slotY * settle;
        } else {
          // Held in place with gentle breath.
          d.phase += d.phaseSpeed;
          const breath = Math.sin(d.phase) * 1.3;
          d.x = d.slotX + Math.cos(d.phase * 0.7) * 0.6;
          d.y = d.slotY + breath * 0.6;
        }
      }

      // --- Trigger pulses during hold
      if (elapsed > SETTLE_END && elapsed > nextPulseAt) {
        pulses.push({
          dotIdx: Math.floor(Math.random() * dots.length),
          startMs: elapsed,
        });
        nextPulseAt = elapsed + 600 + Math.random() * 900;
      }

      // --- Draw faint grid scaffolding (implied lattice). Fades in with settle.
      if (settle > 0.4) {
        const gridAlpha = smoothstep((settle - 0.4) / 0.6) * 0.06;
        ctx.strokeStyle = `rgba(0, 0, 0, ${gridAlpha})`;
        ctx.lineWidth = 0.5;
        for (let r = 0; r < ROWS; r++) {
          ctx.beginPath();
          const y = CY - GRID_H / 2 + (GRID_H / (ROWS - 1)) * r;
          ctx.moveTo(CX - GRID_W / 2 - 10, y);
          ctx.lineTo(CX + GRID_W / 2 + 10, y);
          ctx.stroke();
        }
        for (let c = 0; c < COLS; c++) {
          ctx.beginPath();
          const x = CX - GRID_W / 2 + (GRID_W / (COLS - 1)) * c;
          ctx.moveTo(x, CY - GRID_H / 2 - 10);
          ctx.lineTo(x, CY + GRID_H / 2 + 10);
          ctx.stroke();
        }
      }

      // --- Draw active pulses first (behind dots).
      for (let i = pulses.length - 1; i >= 0; i--) {
        const p = pulses[i];
        const age = (elapsed - p.startMs) / 1200;
        if (age >= 1) {
          pulses.splice(i, 1);
          continue;
        }
        const d = dots[p.dotIdx];
        const radius = 4 + age * 28;
        const alpha = (1 - age) * 0.45;
        ctx.strokeStyle = brandRgba(d.colorT, alpha);
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(d.x, d.y, radius, 0, Math.PI * 2);
        ctx.stroke();
      }

      // --- Draw dots
      for (const d of dots) {
        const [r, g, b] = brandColor(d.colorT);
        // Dots brighten once settled.
        const alpha = 0.55 + 0.35 * settle;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(d.x, d.y, 4.2, 0, Math.PI * 2);
        ctx.fill();
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationId);
  }, []);

  return <canvas ref={canvasRef} />;
}
