import type { DashboardHabit, Category } from "@/types";
import { getCategoryColor, getCategoryLabel, todayISO } from "@/lib/category";
import { useCompleteHabit, useSkipHabit } from "@/hooks/useHabits";
import { useMasterStore } from "@/stores/master";
import { useAuraStore } from "@/stores/aura";
import { Button } from "@/components/ui/button";
import { Check, X } from "lucide-react";

interface HabitCardProps {
  habit: DashboardHabit;
}

export default function HabitCard({ habit }: HabitCardProps) {
  const complete = useCompleteHabit();
  const skip = useSkipHabit();
  const showMaster = useMasterStore((s) => s.show);
  const triggerFlare = useAuraStore((s) => s.triggerFlare);
  const color = getCategoryColor(habit.category);
  const isPending = habit.status === "pending";
  const isDone = habit.status === "completed";

  const handleComplete = () => {
    complete.mutate(
      { habitId: habit.id, date: todayISO() },
      {
        onSuccess: (data) => {
          triggerFlare(habit.category);
          if (data.narration) {
            showMaster({ content: data.narration.content, category: habit.category });
          }
        },
      },
    );
  };

  const handleSkip = () => {
    skip.mutate(
      { habitId: habit.id, date: todayISO() },
      {
        onSuccess: (data) => {
          if (data.narration) {
            showMaster({ content: data.narration.content, category: habit.category });
          }
        },
      },
    );
  };

  return (
    <div
      className={`flex items-center gap-3 rounded-xl border bg-card p-4 transition-opacity ${
        !isPending ? "opacity-50" : ""
      }`}
      style={{ borderLeftWidth: 3, borderLeftColor: color }}
    >
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium leading-tight">{habit.title}</p>
        <div className="mt-1 flex items-center gap-2">
          <span
            className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold"
            style={{ backgroundColor: `${color}20`, color }}
          >
            {getCategoryLabel(habit.category as Category)}
          </span>
        </div>
      </div>

      {isPending ? (
        <div className="flex shrink-0 gap-1.5">
          <Button
            size="sm"
            className="h-8 gap-1 px-3 text-xs"
            style={{ backgroundColor: color }}
            onClick={handleComplete}
            disabled={complete.isPending}
          >
            <Check className="h-3.5 w-3.5" />
            Done
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="h-8 gap-1 px-3 text-xs"
            onClick={handleSkip}
            disabled={skip.isPending}
          >
            <X className="h-3.5 w-3.5" />
            Skip
          </Button>
        </div>
      ) : (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full" style={{ backgroundColor: isDone ? `${color}20` : undefined }}>
          {isDone ? (
            <Check className="h-4 w-4" style={{ color }} />
          ) : (
            <X className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      )}
    </div>
  );
}
