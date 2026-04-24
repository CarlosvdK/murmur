// Shared helpers for the EngineSection animations. Kept small and local
// so each animation file can stay self-contained.

export const PALETTE: [number, number, number][] = [
  [68, 140, 253], // #448CFD
  [255, 141, 228], // #FF8DE4
  [255, 135, 32], // #FF8720
];

export function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

export function clamp01(t: number): number {
  return Math.min(Math.max(t, 0), 1);
}

export function smoothstep(t: number): number {
  const x = clamp01(t);
  return x * x * (3 - 2 * x);
}

export function brandColor(t: number): [number, number, number] {
  const segments = PALETTE.length - 1;
  const scaled = clamp01(t) * segments;
  const i = Math.floor(scaled);
  const frac = scaled - i;
  const a = PALETTE[i];
  const b = PALETTE[Math.min(i + 1, segments)];
  return [
    Math.round(lerp(a[0], b[0], frac)),
    Math.round(lerp(a[1], b[1], frac)),
    Math.round(lerp(a[2], b[2], frac)),
  ];
}

export function brandRgba(t: number, alpha: number): string {
  const [r, g, b] = brandColor(t);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export const CANVAS_SIZE = 400;

export function setupCanvas(canvas: HTMLCanvasElement): CanvasRenderingContext2D | null {
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = CANVAS_SIZE * dpr;
  canvas.height = CANVAS_SIZE * dpr;
  canvas.style.width = `${CANVAS_SIZE}px`;
  canvas.style.height = `${CANVAS_SIZE}px`;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(dpr, dpr);
  return ctx;
}
