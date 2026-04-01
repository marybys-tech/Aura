import { useState } from "react";
import type { CategoryScore, Category } from "@/types";
import { getCategoryColor, getCategoryLabel } from "@/lib/category";
import { ALL_CATEGORIES } from "@/lib/constants";

interface StatsPanelProps {
  scores: Record<string, CategoryScore>;
}

export default function StatsPanel({ scores }: StatsPanelProps) {
  return (
    <div>
      <h3 className="mb-3 text-lg font-semibold">Category Stats</h3>
      <div className="rounded-xl border border-black/5 bg-white/70 backdrop-blur-xl dark:border-white/10 dark:bg-white/5">
        {ALL_CATEGORIES.map((cat, i) => (
          <StatRow
            key={cat}
            category={cat as Category}
            score={scores[cat]}
            isLast={i === ALL_CATEGORIES.length - 1}
          />
        ))}
      </div>
    </div>
  );
}

function StatRow({ category, score, isLast }: { category: Category; score?: CategoryScore; isLast: boolean }) {
  const [hovered, setHovered] = useState(false);
  const level = score?.level ?? 0;
  const xp = score?.xp ?? 0;
  const xpToNext = score?.xp_to_next ?? 10;
  const vitality = score?.vitality ?? 0;
  const color = getCategoryColor(category);
  const xpProgress = xpToNext > 0 ? (xp / xpToNext) * 100 : 0;

  return (
    <div
      className={`flex items-center gap-3 px-3 py-2 transition-colors duration-200 ${!isLast ? "border-b border-border/50" : ""}`}
      style={{
        backgroundColor: hovered ? `${color}08` : undefined,
        borderLeftWidth: 3,
        borderLeftColor: hovered ? color : "transparent",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Dot + Name */}
      <div className="flex items-center gap-1.5 shrink-0 w-[80px]">
        <div
          className="h-2 w-2 shrink-0 rounded-full"
          style={{ backgroundColor: color, boxShadow: hovered ? `0 0 6px ${color}` : "none" }}
        />
        <span className="text-[11px] font-medium truncate">{getCategoryLabel(category)}</span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${xpProgress}%`, backgroundColor: color }}
        />
      </div>

      {/* Level */}
      <span className="shrink-0 text-[10px] font-semibold" style={{ color }}>
        Lv.{level}
      </span>

      {/* Vitality */}
      <span className="shrink-0 w-[28px] text-right text-[10px] text-muted-foreground" style={{ color: vitality > 60 ? color : undefined }}>
        {vitality > 0 ? `♥${Math.round(vitality)}` : "—"}
      </span>
    </div>
  );
}
