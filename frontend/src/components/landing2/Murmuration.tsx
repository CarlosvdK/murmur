"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

const BRAND_COLORS = [
  new THREE.Color("#448CFD"),
  new THREE.Color("#FF8DE4"),
  new THREE.Color("#FF8720"),
  new THREE.Color("#6EB0FF"),
  new THREE.Color("#FFB366"),
];

export default function Murmuration() {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<{
    renderer: THREE.WebGLRenderer;
    animationId: number;
    scene: THREE.Scene;
  } | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const w = () => el.clientWidth;
    const h = () => el.clientHeight;

    const SEPARATION = 90;
    const AMOUNTX = 160;
    const AMOUNTY = 90;
    const TOTAL = AMOUNTX * AMOUNTY;

    // Scene setup
    const scene = new THREE.Scene();
    // No fog -- keep dot colors vivid throughout

    const camera = new THREE.PerspectiveCamera(65, w() / h(), 1, 25000);
    camera.position.set(0, 600, 2000);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w(), h());
    renderer.setClearColor(0x000000, 0);
    el.appendChild(renderer.domElement);

    // Build point positions + colors
    // Front dots (low iy) are fully visible, back dots (high iy) fade out
    const positions = new Float32Array(TOTAL * 3);
    const colors = new Float32Array(TOTAL * 3);
    const BG = new THREE.Color("#F5F3EF"); // eggshell background

    let idx = 0;
    for (let ix = 0; ix < AMOUNTX; ix++) {
      for (let iy = 0; iy < AMOUNTY; iy++) {
        const x = ix * SEPARATION - (AMOUNTX * SEPARATION) / 2;
        const z = iy * SEPARATION - (AMOUNTY * SEPARATION) / 2;
        positions[idx * 3] = x;
        positions[idx * 3 + 1] = 0;
        positions[idx * 3 + 2] = z;

        // Brand color based on X position
        const t = ix / AMOUNTX;
        const colorIdx = Math.floor(t * BRAND_COLORS.length);
        const nextIdx = Math.min(colorIdx + 1, BRAND_COLORS.length - 1);
        const blend = (t * BRAND_COLORS.length) - colorIdx;
        const c = BRAND_COLORS[colorIdx].clone().lerp(BRAND_COLORS[nextIdx], blend);

        // Depth fade: front = full vivid color, back = slightly faded
        const depthT = iy / AMOUNTY;
        // Only fade the very back rows, keep most dots at full color
        const fadeAmount = Math.max(0, depthT - 0.5) * 0.6;
        c.lerp(BG, fadeAmount);

        colors[idx * 3] = c.r;
        colors[idx * 3 + 1] = c.g;
        colors[idx * 3 + 2] = c.b;

        idx++;
      }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 12,
      vertexColors: true,
      transparent: true,
      opacity: 1.0,
      sizeAttenuation: true,
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    let count = 0;
    let animationId = 0;

    const animate = () => {
      animationId = requestAnimationFrame(animate);

      const posAttr = geometry.attributes.position;
      const arr = posAttr.array as Float32Array;

      let i = 0;
      for (let ix = 0; ix < AMOUNTX; ix++) {
        for (let iy = 0; iy < AMOUNTY; iy++) {
          const arrIdx = i * 3;
          const baseX = ix * SEPARATION - (AMOUNTX * SEPARATION) / 2;
          const baseZ = iy * SEPARATION - (AMOUNTY * SEPARATION) / 2;

          // Wave sweeping front to back
          const yVal =
            Math.sin((iy * 0.4) + count * 0.8) * 45 +
            Math.sin((ix * 0.3) + count * 0.5) * 25 +
            Math.cos((ix * 0.2 + iy * 0.2) + count * 0.4) * 20;

          arr[arrIdx + 1] = yVal;
          i++;
        }
      }

      posAttr.needsUpdate = true;
      renderer.render(scene, camera);
      count += 0.015;
    };

    const handleResize = () => {
      camera.aspect = w() / h();
      camera.updateProjectionMatrix();
      renderer.setSize(w(), h());
    };

    el.addEventListener("touchmove", onTouchMove, { passive: true });
    el.addEventListener("touchend", onTouchEnd);
    window.addEventListener("resize", handleResize);

    animate();
    sceneRef.current = { renderer, animationId, scene };

    return () => {
      window.removeEventListener("resize", handleResize);

      if (sceneRef.current) {
        cancelAnimationFrame(sceneRef.current.animationId);
        scene.traverse((obj) => {
          if (obj instanceof THREE.Points) {
            obj.geometry.dispose();
            if (Array.isArray(obj.material)) obj.material.forEach((m) => m.dispose());
            else obj.material.dispose();
          }
        });
        renderer.dispose();
        if (renderer.domElement && el.contains(renderer.domElement)) {
          el.removeChild(renderer.domElement);
        }
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 overflow-hidden"
      style={{ zIndex: 1 }}
    />
  );
}
