/**
 * Aura blob definitions and painting.
 * Each blob = one habit category, rendered as a radial gradient on Canvas.
 */

// --- Inline simplex-ish 2D noise (no dependencies) ---

const P = new Uint8Array(512);
const G = [[1,1],[-1,1],[1,-1],[-1,-1],[1,0],[-1,0],[0,1],[0,-1]];
(function seed() {
  const p = Array.from({ length: 256 }, (_, i) => i);
  for (let i = 255; i > 0; i--) {
    const j = (i * 7 + 13) & 255; // deterministic shuffle
    [p[i], p[j]] = [p[j], p[i]];
  }
  for (let i = 0; i < 512; i++) P[i] = p[i & 255];
})();

function fade(t: number) { return t * t * t * (t * (t * 6 - 15) + 10); }
function lerp(a: number, b: number, t: number) { return a + t * (b - a); }

export function noise2D(x: number, y: number): number {
  const X = Math.floor(x) & 255, Y = Math.floor(y) & 255;
  const xf = x - Math.floor(x), yf = y - Math.floor(y);
  const u = fade(xf), v = fade(yf);
  const dot = (g: number[], dx: number, dy: number) => g[0] * dx + g[1] * dy;
  const aa = G[P[P[X] + Y] & 7], ab = G[P[P[X] + Y + 1] & 7];
  const ba = G[P[P[X + 1] + Y] & 7], bb = G[P[P[X + 1] + Y + 1] & 7];
  return lerp(
    lerp(dot(aa, xf, yf), dot(ba, xf - 1, yf), u),
    lerp(dot(ab, xf, yf - 1), dot(bb, xf - 1, yf - 1), u),
    v,
  );
}

// --- Blob configuration ---

export interface BlobConfig {
  category: string;
  h: number;  // hue
  s: number;  // saturation %
  l: number;  // lightness %
  baseAngle: number;
  noiseSeedX: number;
  noiseSeedY: number;
}

export const BLOBS: BlobConfig[] = [
  { category: "intelligence", h: 263, s: 90, l: 65, baseAngle: 0.0,  noiseSeedX: 0,    noiseSeedY: 0    },
  { category: "stamina",      h: 160, s: 85, l: 55, baseAngle: 1.05, noiseSeedX: 3.7,  noiseSeedY: 1.2  },
  { category: "sociality",    h: 45,  s: 95, l: 55, baseAngle: 2.09, noiseSeedX: 7.1,  noiseSeedY: 5.3  },
  { category: "creativity",   h: 25,  s: 95, l: 58, baseAngle: 3.14, noiseSeedX: 11.3, noiseSeedY: 8.7  },
  { category: "discipline",   h: 200, s: 90, l: 58, baseAngle: 4.19, noiseSeedX: 15.9, noiseSeedY: 2.1  },
  { category: "wellness",     h: 330, s: 85, l: 63, baseAngle: 5.24, noiseSeedX: 20.1, noiseSeedY: 12.4 },
];

// --- Painting ---

export interface BlobState {
  scoreNorm: number;   // 0-1
  isFresh: boolean;    // user has no progress yet
  isNeglected: boolean; // all categories abandoned
}

export function paintBlob(
  ctx: CanvasRenderingContext2D,
  blob: BlobConfig,
  state: BlobState,
  time: number,
  cx: number,
  cy: number,
  span: number, // max(width, height)
  breath: number, // breathing multiplier ~0.95-1.05
  isDark: boolean,
) {
  const { scoreNorm, isFresh, isNeglected } = state;

  // Position: orbit around center with noise perturbation
  const nx = noise2D(time * 0.12 + blob.noiseSeedX, blob.noiseSeedY);
  const ny = noise2D(blob.noiseSeedX, time * 0.12 + blob.noiseSeedY);
  const angle = blob.baseAngle + time * 0.06 + nx * 0.9;
  const orbit = span * 0.10 * (0.7 + ny * 0.4);
  const bx = cx + Math.cos(angle) * orbit;
  const by = cy + Math.sin(angle) * orbit;

  // Size: fresh=medium equal, active=scales with score, neglected=tiny
  let radiusMult: number;
  if (isNeglected) {
    radiusMult = 0.15;
  } else if (isFresh) {
    radiusMult = 0.40;
  } else {
    radiusMult = 0.20 + 0.55 * scoreNorm; // 0.20 (score 0) → 0.75 (score 100)
  }
  const radius = span * 0.5 * radiusMult * breath;

  // Opacity
  let alpha: number;
  if (isNeglected) {
    alpha = 0.06;
  } else if (isFresh) {
    alpha = isDark ? 0.22 : 0.35;
  } else {
    alpha = isDark
      ? 0.10 + 0.65 * scoreNorm  // 0.10 → 0.75
      : 0.20 + 0.50 * scoreNorm; // 0.20 → 0.70
  }

  // Saturation: always 100% unless total neglect
  const sat = isNeglected ? 20 : blob.s;

  // Build HSL color string
  const hsl = (a: number) => `hsla(${blob.h}, ${sat}%, ${blob.l}%, ${a})`;

  // Radial gradient — the gradient IS the softness, no blur needed
  const grad = ctx.createRadialGradient(bx, by, 0, bx, by, radius);
  grad.addColorStop(0.0, hsl(alpha));
  grad.addColorStop(0.25, hsl(alpha * 0.8));
  grad.addColorStop(0.55, hsl(alpha * 0.35));
  grad.addColorStop(1.0, hsl(0));

  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, ctx.canvas.width / (window.devicePixelRatio || 1), ctx.canvas.height / (window.devicePixelRatio || 1));
}
