import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useThemeStore } from "@/stores/theme";
import type { CategoryScore, Category } from "@/types";

interface AuraCanvasProps {
  scores: Record<string, CategoryScore>;
  flareCategory?: string | null;
  flareSeq?: number;
}

interface BlobConfig {
  category: Category;
  color: string;
  duration: number;
  delay: number;
  xPath: number[];
  yPath: number[];
  baseSize: number;
}

const BLOBS: BlobConfig[] = [
  { category: "intelligence", color: "#8B5CF6", duration: 14, delay: 0,   xPath: [-20, 25, -5, -20],  yPath: [-15, 10, 20, -15],  baseSize: 55 },
  { category: "stamina",      color: "#10B981", duration: 16, delay: 1.5, xPath: [25, -20, 10, 25],   yPath: [15, -25, 5, 15],    baseSize: 50 },
  { category: "sociality",    color: "#F59E0B", duration: 18, delay: 3,   xPath: [-15, 15, -25, -15], yPath: [20, -10, -20, 20],  baseSize: 47 },
  { category: "creativity",   color: "#F97316", duration: 13, delay: 2,   xPath: [20, -25, 15, 20],   yPath: [-20, 15, -10, -20], baseSize: 48 },
  { category: "discipline",   color: "#0EA5E9", duration: 15, delay: 4,   xPath: [-10, 30, -15, -10], yPath: [25, -15, 10, 25],   baseSize: 52 },
  { category: "wellness",     color: "#EC4899", duration: 12, delay: 0.5, xPath: [15, -10, 20, 15],   yPath: [-25, 20, -5, -25],  baseSize: 46 },
];

export default function AuraCanvas({ scores, flareCategory, flareSeq }: AuraCanvasProps) {
  const isDark = useThemeStore((s) => s.theme) === "dark";

  // Compute total Aura power: Σ (level × (vitality/100 + 0.2))

  const vitalities = useMemo(
    () => BLOBS.map((b) => scores[b.category]?.vitality ?? 0),
    [scores],
  );
  const maxVitality = Math.max(...vitalities);
  // Fresh: everyone at initial 50 and level 0
  const isFresh = vitalities.every((v) => v === 50) && Object.values(scores).every((s) => (s?.level ?? 0) === 0);
  const isNeglected = !isFresh && maxVitality < 5;

  return (
    <div className="space-y-2">
      <div
        className="relative overflow-hidden rounded-2xl"
        style={{
          backgroundColor: "transparent",
          height: "clamp(280px, 42vh, 420px)",
        }}
      >
        {/* Dark: screen blend (additive, colors glow). Light: normal blend (pure colors on light bg) */}
        <div className="absolute inset-0" style={{ mixBlendMode: isDark ? "screen" : "normal" }}>
          {BLOBS.map((blob) => {
            const vitality = scores[blob.category]?.vitality ?? 0;
            const vitalityNorm = vitality / 100;
            // sqrt curve: vitality 20 → 0.45, 50 → 0.71, 80 → 0.89, 100 → 1.0
            const visualStrength = Math.sqrt(vitalityNorm);

            // Size: fresh = equal medium, active = scales with visual strength
            let size: number;
            if (isNeglected) size = blob.baseSize * 0.2;
            else if (isFresh) size = blob.baseSize * 0.7;
            else size = blob.baseSize * (0.35 + 0.65 * visualStrength);

            // Opacity: generous at low scores so early progress feels rewarding
            let opacity: number;
            if (isNeglected) opacity = 0.08;
            else if (isFresh) opacity = isDark ? 0.5 : 0.6;
            else opacity = isDark
              ? 0.20 + 0.70 * visualStrength
              : 0.35 + 0.55 * visualStrength;

            return (
              <motion.div
                key={blob.category}
                style={{
                  position: "absolute",
                  left: "50%",
                  top: "50%",
                  width: `${size}%`,
                  height: `${size}%`,
                  borderRadius: "50%",
                  background: blob.color,
                  filter: `blur(${isDark ? 35 + 20 * (1 - visualStrength) : 28 + 15 * (1 - visualStrength)}px)`,
                  opacity,
                  x: "-50%",
                  y: "-50%",
                }}
                animate={{
                  x: blob.xPath.map((v) => `calc(-50% + ${v}%)`),
                  y: blob.yPath.map((v) => `calc(-50% + ${v}%)`),
                  scale: [1, 1.08 + 0.12 * visualStrength, 0.95, 1],
                }}
                transition={{
                  duration: blob.duration,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: blob.delay,
                }}
              />
            );
          })}
        </div>

        {/* Flare burst */}
        <AnimatePresence>
          {flareCategory && flareSeq ? (
            <motion.div
              key={`flare-${flareSeq}`}
              className="absolute inset-0"
              style={{
                background: `radial-gradient(circle, ${
                  BLOBS.find((b) => b.category === flareCategory)?.color ?? "#8B5CF6"
                } 0%, transparent 60%)`,
                mixBlendMode: "screen",
              }}
              initial={{ opacity: 0.9, scale: 0.3 }}
              animate={{ opacity: 0, scale: 2 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.2, ease: "easeOut" }}
            />
          ) : null}
        </AnimatePresence>

        {/* Sparkle core */}
        <div className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          <div
            style={{
              width: "160px", height: "160px", borderRadius: "50%",
              background: "radial-gradient(circle, rgba(200,180,255,0.25) 0%, rgba(139,92,246,0.08) 50%, transparent 100%)",
              filter: "blur(15px)", transform: "translate(-50%, -50%)",
              position: "absolute", left: "50%", top: "50%",
            }}
          />
          <div
            style={{
              width: "44px", height: "44px", borderRadius: "50%",
              background: "radial-gradient(circle, rgba(255,255,255,0.7) 0%, rgba(200,180,255,0.25) 50%, transparent 100%)",
              filter: "blur(3px)", transform: "translate(-50%, -50%)",
              position: "absolute", left: "50%", top: "50%",
            }}
          />
          <div
            style={{
              width: "10px", height: "10px", borderRadius: "50%",
              background: "rgba(255,255,255,0.85)",
              boxShadow: "0 0 8px 3px rgba(255,255,255,0.5), 0 0 20px 6px rgba(167,139,250,0.3)",
              transform: "translate(-50%, -50%)",
              position: "absolute", left: "50%", top: "50%",
            }}
          />
          {[0, 45, 90, 135].map((deg, i) => (
            <motion.div
              key={deg}
              style={{
                position: "absolute", left: "50%", top: "50%", height: "1px",
                background: "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.35) 20%, rgba(255,255,255,0.5) 50%, rgba(255,255,255,0.35) 80%, transparent 100%)",
                transform: `translate(-50%, -50%) rotate(${deg}deg)`,
                filter: "blur(0.5px)",
              }}
              animate={{
                width: ["120px", "180px", "100px", "160px", "120px"],
                opacity: [0.4, 0.7, 0.3, 0.6, 0.4],
              }}
              transition={{ duration: 6 + i * 1.5, repeat: Infinity, ease: "easeInOut" }}
            />
          ))}
        </div>
      </div>

    </div>
  );
}
