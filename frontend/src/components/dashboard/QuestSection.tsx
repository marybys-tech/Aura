import type { QuestSummary, Category } from "@/types";
import { getCategoryColor } from "@/lib/category";
import { Sparkles } from "lucide-react";

interface QuestSectionProps {
  quests: QuestSummary[];
}

export default function QuestSection({ quests }: QuestSectionProps) {
  if (quests.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-card p-4">
        <h3 className="mb-2 text-sm font-semibold">Active Quests</h3>
        <p className="text-xs text-muted-foreground">No active quests. Complete habits to unlock quests from the Master.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold">Active Quests</h3>
      <div className="space-y-3">
        {quests.map((q) => {
          const color = getCategoryColor(q.target_category as Category);
          return (
            <div
              key={q.id}
              className="flex items-start gap-3 rounded-lg border p-3"
              style={{ borderColor: `${color}30` }}
            >
              <div
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
                style={{ backgroundColor: `${color}20` }}
              >
                <Sparkles className="h-4 w-4" style={{ color }} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium leading-tight">{q.title}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{q.description}</p>
                <p className="mt-1.5 text-[10px] font-semibold" style={{ color }}>
                  +{q.bonus_points} pts
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
