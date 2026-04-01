import { useDashboardToday } from "@/hooks/useDashboard";
import HabitCard from "./HabitCard";

export default function TodayView() {
  const { data, isLoading, isError } = useDashboardToday();

  if (isError) return <p className="py-8 text-center text-sm text-destructive">Failed to load habits. Please refresh.</p>;
  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => <div key={i} className="h-16 animate-pulse rounded-xl bg-muted" />)}
      </div>
    );
  }
  if (!data) return null;

  const pending = data.habits.filter((h) => h.status === "pending");
  const done = data.habits.filter((h) => h.status !== "pending");

  return (
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
  );
}
