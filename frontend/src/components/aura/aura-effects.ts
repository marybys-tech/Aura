/**
 * Aura sparkle core and flare burst effects.
 */

import { BLOBS } from "./aura-blobs";

// --- Sparkle Core ---

export function paintCore(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  vitality: number, // 0.2 (dead) → 1.0 (full)
  time: number,
  w: number,
  h: number,
) {
  ctx.save();
  ctx.globalCompositeOperation = "source-over";

  // Outer halo
  const haloR = 70 * vitality;
  const halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, haloR);
  halo.addColorStop(0, `rgba(200,180,255,${0.15 * vitality})`);
  halo.addColorStop(0.5, `rgba(139,92,246,${0.06 * vitality})`);
  halo.addColorStop(1, "rgba(139,92,246,0)");
  ctx.fillStyle = halo;
  ctx.fillRect(0, 0, w, h);

  // Inner bright core
  const coreR = 18 * vitality;
  const core = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreR);
  core.addColorStop(0, `rgba(255,255,255,${0.5 * vitality})`);
  core.addColorStop(0.5, `rgba(200,180,255,${0.2 * vitality})`);
  core.addColorStop(1, "rgba(200,180,255,0)");
  ctx.fillStyle = core;
  ctx.fillRect(0, 0, w, h);

  // Sparkle point
  const pointR = 3 + 2 * vitality;
  ctx.beginPath();
  ctx.arc(cx, cy, pointR, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(255,255,255,${0.6 * vitality})`;
  ctx.fill();

  // 4 breathing beams
  ctx.lineCap = "round";
  for (let i = 0; i < 4; i++) {
    const angle = (i * Math.PI) / 4;
    const phase = time * 0.4 + i * 1.3;
    const len = (50 + 40 * Math.sin(phase)) * vitality;
    const alpha = (0.15 + 0.15 * Math.sin(phase + 0.5)) * vitality;

    const ex = cx + Math.cos(angle) * len;
    const ey = cy + Math.sin(angle) * len;

    const grad = ctx.createLinearGradient(cx, cy, ex, ey);
    grad.addColorStop(0, `rgba(255,255,255,${alpha})`);
    grad.addColorStop(0.6, `rgba(200,180,255,${alpha * 0.3})`);
    grad.addColorStop(1, "rgba(200,180,255,0)");

    ctx.strokeStyle = grad;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(ex, ey);
    ctx.stroke();
  }

  ctx.restore();
}

// --- Flare Burst ---

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  h: number;
  s: number;
  l: number;
  size: number;
}

const MAX_PARTICLES = 50;

export class FlareSystem {
  private particles: Particle[] = [];

  trigger(category: string, cx: number, cy: number) {
    const blob = BLOBS.find((b) => b.category === category);
    if (!blob) return;

    const count = 25 + Math.floor(Math.random() * 15);
    for (let i = 0; i < count && this.particles.length < MAX_PARTICLES; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1.5 + Math.random() * 3;
      this.particles.push({
        x: cx,
        y: cy,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1.0,
        maxLife: 40 + Math.random() * 20,
        h: blob.h,
        s: blob.s,
        l: blob.l,
        size: 3 + Math.random() * 5,
      });
    }
  }

  update() {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.97;
      p.vy *= 0.97;
      p.life -= 1 / p.maxLife;
      if (p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }
  }

  paint(ctx: CanvasRenderingContext2D) {
    if (this.particles.length === 0) return;
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    for (const p of this.particles) {
      const alpha = p.life * 0.6;
      const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
      grad.addColorStop(0, `hsla(${p.h},${p.s}%,${p.l}%,${alpha})`);
      grad.addColorStop(1, `hsla(${p.h},${p.s}%,${p.l}%,0)`);
      ctx.fillStyle = grad;
      ctx.fillRect(p.x - p.size, p.y - p.size, p.size * 2, p.size * 2);
    }
    ctx.restore();
  }
}
