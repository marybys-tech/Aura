import type { CategoryScore, Category } from "@/types";
import { getCategoryColor, getCategoryLabel } from "@/lib/category";
import { ALL_CATEGORIES } from "@/lib/constants";

interface StatsPanelProps {
  scores: Record<string, CategoryScore>;
}

export default function StatsPanel({ scores }: StatsPanelProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <h3 className="mb-4 text-sm font-semibold">Category Stats</h3>
      <div className="space-y-3.5">
        {ALL_CATEGORIES.map((cat) => {
          const s = scores[cat];
          const level = s?.level ?? 0;
          const xp = s?.xp ?? 0;
          const xpToNext = s?.xp_to_next ?? 10;
          const vitality = s?.vitality ?? 0;
          const color = getCategoryColor(cat as Category);
          const xpProgress = xpToNext > 0 ? (xp / xpToNext) * 100 : 0;

          return (
            <div key={cat} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
                  <span className="font-medium">{getCategoryLabel(cat as Category)}</span>
                </div>
                <span className="font-semibold" style={{ color }}>
                  Lv. {level}
                </span>
              </div>
              {/* XP progress bar */}
              <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${xpProgress}%`, backgroundColor: color }}
                />
              </div>
              <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                <span>{Math.round(xp)} / {Math.round(xpToNext)} XP</span>
                <span style={{ color: vitality > 60 ? color : undefined }}>
                  {vitality > 0 ? `♥ ${Math.round(vitality)}` : "dormant"}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
