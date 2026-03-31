import { useState } from "react";
import { useHabits } from "@/hooks/useHabits";
import { ALL_CATEGORIES } from "@/lib/constants";
import type { Category } from "@/types";
import CategoryPill from "@/components/habits/CategoryPill";
import HabitListCard from "@/components/habits/HabitListCard";
import AddHabitDialog from "@/components/habits/AddHabitDialog";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default function HabitsPage() {
  const [filter, setFilter] = useState<string | undefined>(undefined);
  const [addOpen, setAddOpen] = useState(false);
  const { data: habits, isLoading } = useHabits(filter);

  return (
    <div className="p-4 lg:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">My Habits</h1>
        <Button size="sm" className="gap-1.5" onClick={() => setAddOpen(true)}>
          <Plus className="h-4 w-4" />
          Add Habit
        </Button>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        <button
          onClick={() => setFilter(undefined)}
          className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
            !filter ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground hover:border-foreground/20"
          }`}
        >
          All
        </button>
        {ALL_CATEGORIES.map((cat) => (
          <CategoryPill
            key={cat}
            category={cat as Category}
            selected={filter === cat}
            onClick={() => setFilter(filter === cat ? undefined : cat)}
          />
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => <div key={i} className="h-20 animate-pulse rounded-xl bg-muted" />)}
        </div>
      ) : habits && habits.length > 0 ? (
        <div className="grid gap-2 sm:grid-cols-2">
          {habits.map((h) => <HabitListCard key={h.id} habit={h} />)}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <p className="text-sm text-muted-foreground">No habits yet. Create your first one!</p>
          <Button className="mt-4 gap-1.5" onClick={() => setAddOpen(true)}>
            <Plus className="h-4 w-4" />
            Add Habit
          </Button>
        </div>
      )}

      <AddHabitDialog open={addOpen} onOpenChange={setAddOpen} defaultCategory={filter as Category | undefined} />
    </div>
  );
}
