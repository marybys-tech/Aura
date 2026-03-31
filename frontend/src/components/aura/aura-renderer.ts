/**
 * Aura renderer — orchestrates the Canvas 2D frame loop.
 *
 * Uses additive blending ("lighter") on dark backgrounds so overlapping
 * colors get brighter, never muddier. Each category blob is a radial
 * gradient — the gradient itself provides the soft falloff (no CSS blur).
 */

import { BLOBS, paintBlob, type BlobState } from "./aura-blobs";
import { paintCore, FlareSystem } from "./aura-effects";

export interface AuraScores {
  [category: string]: number; // 0-100
}

export class AuraRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private w = 0;
  private h = 0;
  private dpr = 1;
  private time = 0;
  private animId = 0;
  private scores: AuraScores = {};
  private isDark = true;
  private flares = new FlareSystem();

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d")!;
    this.dpr = Math.min(window.devicePixelRatio, 2);
    this.resize();
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    this.w = rect.width;
    this.h = rect.height;
    this.canvas.width = rect.width * this.dpr;
    this.canvas.height = rect.height * this.dpr;
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
  }

  setScores(scores: AuraScores) { this.scores = scores; }
  setDarkMode(dark: boolean) { this.isDark = dark; }

  triggerFlare(category: string) {
    this.flares.trigger(category, this.w / 2, this.h / 2);
  }

  start() {
    let last = performance.now();
    const loop = (now: number) => {
      this.time += (now - last) / 1000;
      last = now;
      this.render();
      this.animId = requestAnimationFrame(loop);
    };
    this.animId = requestAnimationFrame(loop);
  }

  stop() { cancelAnimationFrame(this.animId); }

  private render() {
    const { ctx, w, h, time, scores, isDark } = this;
    const cx = w / 2;
    const cy = h / 2;
    const span = Math.max(w, h);

    // --- Compute global state ---
    const scoreValues = BLOBS.map((b) => scores[b.category] ?? 0);
    const totalScore = scoreValues.reduce((a, b) => a + b, 0);
    const maxScore = Math.max(...scoreValues);
    const isFresh = totalScore === 0;
    const isNeglected = !isFresh && maxScore < 3;

    // Vitality: controls core brightness + breathing speed
    let vitality: number;
    if (isNeglected) vitality = 0.2;
    else if (isFresh) vitality = 0.7;
    else vitality = 0.7 + 0.3 * Math.min(totalScore / 300, 1);

    // Breathing
    const breathFreq = 0.3 + 0.5 * vitality;
    const breath = 1 + 0.04 * Math.sin(time * breathFreq * Math.PI * 2);

    // --- 1. Clear ---
    ctx.clearRect(0, 0, w, h);
    if (isDark) {
      ctx.fillStyle = "#050510";
      ctx.fillRect(0, 0, w, h);
    }

    // --- 2. Paint blobs with additive blending (dark) or source-over (light) ---
    ctx.save();
    ctx.globalCompositeOperation = isDark ? "lighter" : "source-over";

    for (const blob of BLOBS) {
      const score = scores[blob.category] ?? 0;
      const state: BlobState = {
        scoreNorm: score / 100,
        isFresh,
        isNeglected,
      };
      paintBlob(ctx, blob, state, time, cx, cy, span, breath, isDark);
    }
    ctx.restore();

    // --- 3. Core sparkle (always source-over so it stays white) ---
    paintCore(ctx, cx, cy, vitality, time, w, h);

    // --- 4. Flare particles ---
    this.flares.update();
    this.flares.paint(ctx);
  }
}
