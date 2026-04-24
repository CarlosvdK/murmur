"use client";

import { useEffect, useRef } from "react";

interface EntropyProps {
  className?: string;
  /** Square side length in CSS pixels. */
  size?: number;
}

// Brand palette -- same colors the Murmuration component uses so the whole
// site reads as one family.
const BRAND_PALETTE: [number, number, number][] = [
  [68, 140, 253], // blue  #448CFD
  [255, 141, 228], // pink  #FF8DE4
  [255, 135, 32], // orange #FF8720
];

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

/** Sample the brand gradient at t in [0, 1]. */
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

export function Entropy({ className = "", size = 500 }: EntropyProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const width = size;
    const height = size;

    class Particle {
      x: number;
      y: number;
      size: number;
      order: boolean;
      velocity: { x: number; y: number };
      originalX: number;
      originalY: number;
      influence: number;
      neighbors: Particle[];
      color: [number, number, number];

      constructor(
        x: number,
        y: number,
        order: boolean,
        color: [number, number, number]
      ) {
        this.x = x;
        this.y = y;
        this.originalX = x;
        this.originalY = y;
        this.size = 2;
        this.order = order;
        this.velocity = {
          x: (Math.random() - 0.5) * 2,
          y: (Math.random() - 0.5) * 2,
        };
        this.influence = 0;
        this.neighbors = [];
        this.color = color;
      }

      update() {
        if (this.order) {
          // Ordered particle: returns toward its grid home, perturbed by
          // chaotic neighbours when they get close.
          const dx = this.originalX - this.x;
          const dy = this.originalY - this.y;

          const chaos = { x: 0, y: 0 };
          this.neighbors.forEach((n) => {
            if (!n.order) {
              const d = Math.hypot(this.x - n.x, this.y - n.y);
              const strength = Math.max(0, 1 - d / 100);
              chaos.x += n.velocity.x * strength;
              chaos.y += n.velocity.y * strength;
              this.influence = Math.max(this.influence, strength);
            }
          });

          this.x +=
            dx * 0.05 * (1 - this.influence) + chaos.x * this.influence;
          this.y +=
            dy * 0.05 * (1 - this.influence) + chaos.y * this.influence;

          this.influence *= 0.99;
        } else {
          // Chaotic particle: Brownian-ish drift, bounded by the right half.
          this.velocity.x += (Math.random() - 0.5) * 0.5;
          this.velocity.y += (Math.random() - 0.5) * 0.5;
          this.velocity.x *= 0.95;
          this.velocity.y *= 0.95;
          this.x += this.velocity.x;
          this.y += this.velocity.y;

          if (this.x < width / 2 || this.x > width) this.velocity.x *= -1;
          if (this.y < 0 || this.y > height) this.velocity.y *= -1;
          this.x = Math.max(width / 2, Math.min(width, this.x));
          this.y = Math.max(0, Math.min(height, this.y));
        }
      }

      draw(ctx: CanvasRenderingContext2D) {
        const alpha = this.order ? 0.85 - this.influence * 0.5 : 0.85;
        const [r, g, b] = this.color;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    const particles: Particle[] = [];

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);

    const cols = 25;
    const rows = 25;
    const spacingX = width / cols;
    const spacingY = height / rows;
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        const x = spacingX * i + spacingX / 2;
        const y = spacingY * j + spacingY / 2;
        const order = x < width / 2;
        const t = order ? i / cols : (i - cols / 2) / (cols / 2);
        particles.push(new Particle(x, y, order, brandColor(t)));
      }
    }

    const updateNeighbors = () => {
      particles.forEach((p) => {
        p.neighbors = particles.filter((o) => {
          if (o === p) return false;
          return Math.hypot(p.x - o.x, p.y - o.y) < 100;
        });
      });
    };

    let time = 0;
    let animationId = 0;

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      if (time % 30 === 0) updateNeighbors();

      particles.forEach((p) => {
        p.update();
        p.draw(ctx);

        p.neighbors.forEach((n) => {
          const d = Math.hypot(p.x - n.x, p.y - n.y);
          if (d < 50) {
            const alpha = 0.25 * (1 - d / 50);
            // Average the two endpoints' colors for the edge.
            const r = (p.color[0] + n.color[0]) / 2;
            const g = (p.color[1] + n.color[1]) / 2;
            const b = (p.color[2] + n.color[2]) / 2;
            ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
            ctx.lineWidth = 0.75;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(n.x, n.y);
            ctx.stroke();
          }
        });
      });

      // Centre divider -- very subtle.
      ctx.strokeStyle = "rgba(0, 0, 0, 0.08)";
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(width / 2, 0);
      ctx.lineTo(width / 2, height);
      ctx.stroke();

      time++;
      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [size]);

  return (
    <div
      className={`relative mx-auto ${className}`}
      style={{ width: size, height: size }}
    >
      <canvas ref={canvasRef} className="absolute inset-0" />
    </div>
  );
}
