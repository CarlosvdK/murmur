"use client";

import { useEffect, useRef } from "react";

interface Node {
  x: number;
  y: number;
  connections: number[];
}

interface Pulse {
  sourceIdx: number;
  progress: number; // 0 to 1
  speed: number;
}

const NODE_SPACING = 80;
const CONNECTION_DISTANCE = 120;
const PULSE_INTERVAL = 3000;
const PULSE_SPEED = 0.012;
const NODE_RADIUS = 1.5;
const LINE_OPACITY = 0.06;
const PULSE_GLOW_RADIUS = 200;

const COLORS = ["#448cfd", "#ff8720", "#ff8de4"];

export default function NetworkBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Node[]>([]);
  const pulsesRef = useRef<Pulse[]>([]);
  const frameRef = useRef<number>(0);
  const lastPulseRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    function buildNodes() {
      const w = canvas!.width;
      const h = canvas!.height;
      const nodes: Node[] = [];

      // Create a jittered grid of nodes
      for (let x = NODE_SPACING / 2; x < w; x += NODE_SPACING) {
        for (let y = NODE_SPACING / 2; y < h; y += NODE_SPACING) {
          nodes.push({
            x: x + (Math.random() - 0.5) * NODE_SPACING * 0.4,
            y: y + (Math.random() - 0.5) * NODE_SPACING * 0.4,
            connections: [],
          });
        }
      }

      // Build connections
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < CONNECTION_DISTANCE) {
            nodes[i].connections.push(j);
            nodes[j].connections.push(i);
          }
        }
      }

      nodesRef.current = nodes;
    }

    function resize() {
      const dpr = window.devicePixelRatio || 1;
      canvas!.width = canvas!.offsetWidth * dpr;
      canvas!.height = canvas!.offsetHeight * dpr;
      ctx!.scale(dpr, dpr);
      buildNodes();
    }

    function draw(timestamp: number) {
      const w = canvas!.offsetWidth;
      const h = canvas!.offsetHeight;
      ctx!.clearRect(0, 0, w, h);

      const nodes = nodesRef.current;
      const pulses = pulsesRef.current;

      // Trigger new pulse periodically
      if (timestamp - lastPulseRef.current > PULSE_INTERVAL && nodes.length > 0) {
        const sourceIdx = Math.floor(Math.random() * nodes.length);
        pulses.push({ sourceIdx, progress: 0, speed: PULSE_SPEED });
        lastPulseRef.current = timestamp;
      }

      // Update pulses
      for (let i = pulses.length - 1; i >= 0; i--) {
        pulses[i].progress += pulses[i].speed;
        if (pulses[i].progress > 1) {
          pulses.splice(i, 1);
        }
      }

      // Draw connections
      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        for (const j of node.connections) {
          if (j <= i) continue; // Draw each edge once
          const other = nodes[j];

          // Check if any pulse illuminates this edge
          let edgeBrightness = LINE_OPACITY;
          let edgeColor = `rgba(0,0,0,${LINE_OPACITY})`;

          for (const pulse of pulses) {
            const source = nodes[pulse.sourceIdx];
            const pulseRadius = pulse.progress * PULSE_GLOW_RADIUS;
            const fadeFactor = 1 - pulse.progress;

            const midX = (node.x + other.x) / 2;
            const midY = (node.y + other.y) / 2;
            const distToSource = Math.sqrt(
              (midX - source.x) ** 2 + (midY - source.y) ** 2
            );

            if (distToSource < pulseRadius) {
              const proximity = 1 - distToSource / pulseRadius;
              const intensity = proximity * fadeFactor * 0.6;
              if (intensity > edgeBrightness) {
                const colorIdx = pulse.sourceIdx % COLORS.length;
                edgeColor = COLORS[colorIdx];
                edgeBrightness = intensity;
              }
            }
          }

          ctx!.beginPath();
          ctx!.moveTo(node.x, node.y);
          ctx!.lineTo(other.x, other.y);
          ctx!.strokeStyle =
            edgeBrightness > LINE_OPACITY
              ? edgeColor + Math.round(edgeBrightness * 255).toString(16).padStart(2, "0")
              : `rgba(0,0,0,${LINE_OPACITY})`;
          ctx!.lineWidth = edgeBrightness > LINE_OPACITY ? 1.5 : 0.5;
          ctx!.stroke();
        }
      }

      // Draw nodes
      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        let nodeGlow = 0;
        let nodeColor = `rgba(0,0,0,0.1)`;

        for (const pulse of pulses) {
          const source = nodes[pulse.sourceIdx];
          const pulseRadius = pulse.progress * PULSE_GLOW_RADIUS;
          const dist = Math.sqrt(
            (node.x - source.x) ** 2 + (node.y - source.y) ** 2
          );

          if (dist < pulseRadius * 0.3) {
            const intensity = (1 - dist / (pulseRadius * 0.3)) * (1 - pulse.progress);
            if (intensity > nodeGlow) {
              nodeGlow = intensity;
              nodeColor = COLORS[pulse.sourceIdx % COLORS.length];
            }
          }
        }

        ctx!.beginPath();
        ctx!.arc(node.x, node.y, nodeGlow > 0.1 ? NODE_RADIUS * 2 : NODE_RADIUS, 0, Math.PI * 2);
        ctx!.fillStyle = nodeGlow > 0.1 ? nodeColor : `rgba(0,0,0,0.12)`;
        ctx!.fill();
      }

      frameRef.current = requestAnimationFrame(draw);
    }

    resize();
    frameRef.current = requestAnimationFrame(draw);

    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(frameRef.current);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 h-full w-full"
      style={{ opacity: 0.7 }}
    />
  );
}
