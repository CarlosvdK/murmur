"use client";

import { useEffect, useRef } from "react";
import {
  brandColor,
  brandRgba,
  setupCanvas,
  smoothstep,
} from "./shared";

/**
 * Constraint lattice -- chaotic dots pulled into a structured grid, then
 * breathing softly in place. Supports Tab 2 "Structured personas".
 */
export default function ConstraintLattice() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const COLS = 5;
    const ROWS = 4;

    type Dot = {
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

    let width = 0;
    let height = 0;
    let ctx: CanvasRenderingContext2D | null = null;
    let dots: Dot[] = [];
    const pulses: { dotIdx: number; startMs: number }[] = [];
    let nextPulseAt = 5500;
    let gridLeft = 0;
    let gridTop = 0;
    let gridW = 0;
    let gridH = 0;

    const start = performance.now();
    const CHAOS_END = 2000;
    const SETTLE_END = 4500;

    const rebuild = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      if (!width || !height) return;
      ctx = setupCanvas(canvas, width, height);

      gridW = width * 0.62;
      gridH = height * 0.52;
      gridLeft = (width - gridW) / 2;
      gridTop = (height - gridH) / 2;

      dots = [];
      let idx = 0;
      for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
          const slotX =
            gridLeft +
            (gridW / (COLS - 1)) * c +
            (Math.random() - 0.5) * 8;
          const slotY =
            gridTop +
            (gridH / (ROWS - 1)) * r +
            (Math.random() - 0.5) * 8;
          const chaosX = width * 0.08 + Math.random() * width * 0.84;
          const chaosY = height * 0.08 + Math.random() * height * 0.84;
          dots.push({
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
    };

    rebuild();
    const ro = new ResizeObserver(rebuild);
    ro.observe(container);

    let animationId = 0;

    const animate = (now: number) => {
      if (!ctx) {
        animationId = requestAnimationFrame(animate);
        return;
      }
      const elapsed = now - start;
      ctx.clearRect(0, 0, width, height);

      let settle = 0;
      if (elapsed < CHAOS_END) settle = 0;
      else if (elapsed < SETTLE_END)
        settle = smoothstep((elapsed - CHAOS_END) / (SETTLE_END - CHAOS_END));
      else settle = 1;

      for (const d of dots) {
        if (settle < 1) {
          d.vx += (Math.random() - 0.5) * 0.35;
          d.vy += (Math.random() - 0.5) * 0.35;
          d.vx *= 0.94;
          d.vy *= 0.94;
          const chaosX = d.x + d.vx;
          const chaosY = d.y + d.vy;
          d.x = chaosX * (1 - settle) + d.slotX * settle;
          d.y = chaosY * (1 - settle) + d.slotY * settle;
        } else {
          d.phase += d.phaseSpeed;
          const breath = Math.sin(d.phase) * 1.3;
          d.x = d.slotX + Math.cos(d.phase * 0.7) * 0.6;
          d.y = d.slotY + breath * 0.6;
        }
      }

      if (elapsed > SETTLE_END && elapsed > nextPulseAt) {
        pulses.push({
          dotIdx: Math.floor(Math.random() * dots.length),
          startMs: elapsed,
        });
        nextPulseAt = elapsed + 600 + Math.random() * 900;
      }

      // Scaffold grid (fades in with settle).
      if (settle > 0.4) {
        const gridAlpha = smoothstep((settle - 0.4) / 0.6) * 0.06;
        ctx.strokeStyle = `rgba(0, 0, 0, ${gridAlpha})`;
        ctx.lineWidth = 0.5;
        for (let r = 0; r < ROWS; r++) {
          const y = gridTop + (gridH / (ROWS - 1)) * r;
          ctx.beginPath();
          ctx.moveTo(gridLeft - 14, y);
          ctx.lineTo(gridLeft + gridW + 14, y);
          ctx.stroke();
        }
        for (let c = 0; c < COLS; c++) {
          const x = gridLeft + (gridW / (COLS - 1)) * c;
          ctx.beginPath();
          ctx.moveTo(x, gridTop - 14);
          ctx.lineTo(x, gridTop + gridH + 14);
          ctx.stroke();
        }
      }

      for (let i = pulses.length - 1; i >= 0; i--) {
        const p = pulses[i];
        const age = (elapsed - p.startMs) / 1200;
        if (age >= 1) {
          pulses.splice(i, 1);
          continue;
        }
        const d = dots[p.dotIdx];
        const radius = 4 + age * 34;
        const alpha = (1 - age) * 0.45;
        ctx.strokeStyle = brandRgba(d.colorT, alpha);
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(d.x, d.y, radius, 0, Math.PI * 2);
        ctx.stroke();
      }

      for (const d of dots) {
        const [r, g, b] = brandColor(d.colorT);
        const alpha = 0.55 + 0.35 * settle;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(d.x, d.y, 5, 0, Math.PI * 2);
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
