import type { Habit, Category } from "@/types";
import { getCategoryColor, getCategoryLabel, formatSchedule } from "@/lib/category";
import { useDeleteHabit } from "@/hooks/useHabits";
import { Button } from "@/components/ui/button";
import { Flame, Trash2 } from "lucide-react";

interface HabitListCardProps {
  habit: Habit;
}

export default function HabitListCard({ habit }: HabitListCardProps) {
  const deleteHabit = useDeleteHabit();
  const color = getCategoryColor(habit.category as Category);

  return (
    <div
      className="rounded-xl border bg-card p-4 transition-colors hover:bg-accent/30"
      style={{ borderLeftWidth: 3, borderLeftColor: color }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium">{habit.title}</p>
          {habit.description && (
            <p className="mt-0.5 text-xs text-muted-foreground line-clamp-1">{habit.description}</p>
          )}
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span
              className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold"
              style={{ backgroundColor: `${color}20`, color }}
            >
              {getCategoryLabel(habit.category as Category)}
            </span>
            <span className="text-[10px] text-muted-foreground">
              {formatSchedule(habit.schedule_type, habit.schedule_days, habit.times_per_day)}
            </span>
          </div>
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 shrink-0 text-muted-foreground hover:text-destructive"
          onClick={() => deleteHabit.mutate(habit.id)}
          disabled={deleteHabit.isPending}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
