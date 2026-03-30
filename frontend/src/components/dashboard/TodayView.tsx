import { useDashboardToday } from "@/hooks/useDashboard";
import AuraPlaceholder from "@/components/aura/AuraPlaceholder";
import StatsPanel from "./StatsPanel";
import QuestSection from "./QuestSection";
import HabitCard from "./HabitCard";

export default function TodayView() {
  const { data, isLoading } = useDashboardToday();

  if (isLoading) return <ViewSkeleton />;
  if (!data) return null;

  const pending = data.habits.filter((h) => h.status === "pending");
  const done = data.habits.filter((h) => h.status !== "pending");

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
      <div className="space-y-4">
        <AuraPlaceholder scores={data.scores} />

        <div>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Today's Habits</h2>
            <span className="text-xs text-muted-foreground">
              {pending.length} of {data.habits.length} remaining
            </span>
          </div>
          <div className="space-y-2">
            {pending.map((h) => <HabitCard key={h.id} habit={h} />)}
            {done.map((h) => <HabitCard key={h.id} habit={h} />)}
          </div>
          {data.habits.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No habits due today. Add some in the Habits page!
            </p>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <StatsPanel scores={data.scores} />
        <QuestSection quests={data.active_quests} />
      </div>
    </div>
  );
}

function ViewSkeleton() {
  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
      <div className="space-y-4">
        <div className="h-48 animate-pulse rounded-xl bg-muted" />
        <div className="space-y-2">
          {[1, 2, 3].map((i) => <div key={i} className="h-16 animate-pulse rounded-xl bg-muted" />)}
        </div>
      </div>
      <div className="space-y-4">
        <div className="h-64 animate-pulse rounded-xl bg-muted" />
        <div className="h-40 animate-pulse rounded-xl bg-muted" />
      </div>
    </div>
  );
}
