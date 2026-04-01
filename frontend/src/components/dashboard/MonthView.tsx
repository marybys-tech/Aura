import { useDashboardMonth } from "@/hooks/useDashboard";

export default function MonthView() {
  const { data, isLoading, isError } = useDashboardMonth();

  if (isError) return <p className="py-8 text-center text-sm text-destructive">Failed to load monthly data. Please refresh.</p>;
  if (isLoading) return <div className="h-48 animate-pulse rounded-xl bg-muted" />;
  if (!data) return null;

  const todayStr = new Date().toISOString().split("T")[0];
  const firstDay = new Date(data.year, data.month - 1, 1);
  const startPad = (firstDay.getDay() + 6) % 7;

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          {firstDay.toLocaleDateString("en", { month: "long", year: "numeric" })}
        </h2>
        <span className="text-xs text-muted-foreground">Read-only</span>
      </div>
      <div className="rounded-xl border border-black/5 bg-white/70 p-4 shadow-sm backdrop-blur-xl dark:border-white/10 dark:bg-white/5 dark:shadow-none">
      <div className="grid grid-cols-7 gap-1 text-center text-[10px]">
        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d) => (
          <div key={d} className="pb-1 font-medium text-muted-foreground">{d}</div>
        ))}
        {Array.from({ length: startPad }).map((_, i) => <div key={`pad-${i}`} />)}
        {data.days.map((day) => {
          const isToday = day.date === todayStr;
          const isFuture = day.date > todayStr;
          const ratio = day.total > 0 ? day.completed / day.total : 0;
          const dateNum = new Date(day.date + "T00:00:00").getDate();

          let bg = "bg-transparent";
          if (!isFuture && day.total > 0) {
            if (ratio >= 0.8) bg = "bg-stamina/20";
            else if (ratio >= 0.4) bg = "bg-sociality/20";
            else bg = "bg-muted";
          }

          return (
            <div
              key={day.date}
              className={`flex flex-col items-center justify-center rounded-lg p-1.5 ${bg} ${
                isToday ? "ring-2 ring-primary ring-offset-1 ring-offset-background" : ""
              } ${isFuture ? "opacity-40" : ""}`}
            >
              <span className="text-xs font-medium">{dateNum}</span>
              {!isFuture && day.total > 0 && (
                <span className="text-[9px] text-muted-foreground">
                  {day.completed}/{day.total}
                </span>
              )}
            </div>
          );
        })}
      </div>
      </div>
    </div>
  );
}
