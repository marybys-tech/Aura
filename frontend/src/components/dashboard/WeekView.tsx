import { useDashboardWeek } from "@/hooks/useDashboard";
import { getCategoryColor } from "@/lib/category";
import type { Category } from "@/types";
import { Check, X, Minus } from "lucide-react";

export default function WeekView() {
  const { data, isLoading, isError } = useDashboardWeek();

  if (isError) return <p className="py-8 text-center text-sm text-destructive">Failed to load weekly data. Please refresh.</p>;
  if (isLoading) return <div className="h-48 animate-pulse rounded-xl bg-muted" />;
  if (!data) return null;

  const dayHeaders = data.habits[0]?.days.map((d) => {
    const date = new Date(d.date + "T00:00:00");
    return {
      date: d.date,
      label: date.toLocaleDateString("en", { weekday: "short" }),
      day: date.getDate(),
      isToday: d.date === new Date().toISOString().split("T")[0],
    };
  }) ?? [];

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Weekly Performance</h2>
        <span className="text-xs text-muted-foreground">Read-only</span>
      </div>
      <div className="overflow-x-auto rounded-xl border border-black/5 bg-white/70 p-4 shadow-sm backdrop-blur-xl dark:border-white/10 dark:bg-white/5 dark:shadow-none">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="pb-2 pr-4 text-left font-medium text-muted-foreground">Habit</th>
              {dayHeaders.map((d) => (
                <th key={d.date} className={`w-10 pb-2 text-center font-medium ${d.isToday ? "text-primary" : "text-muted-foreground"}`}>
                  <div>{d.label}</div>
                  <div className="text-[10px]">{d.day}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.habits.map((row) => {
              const color = getCategoryColor(row.category as Category);
              return (
                <tr key={row.habit_id} className="border-t border-border/50">
                  <td className="py-2.5 pr-4">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: color }} />
                      <span className="truncate font-medium">{row.title}</span>
                    </div>
                  </td>
                  {row.days.map((d) => (
                    <td key={d.date} className="py-2.5 text-center">
                      <StatusIcon status={d.status} color={color} />
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusIcon({ status, color }: { status: string | null; color: string }) {
  if (status === "completed") return <Check className="mx-auto h-4 w-4" style={{ color }} />;
  if (status === "skipped") return <X className="mx-auto h-4 w-4 text-destructive/60" />;
  if (status === "pending") return <div className="mx-auto h-3 w-3 rounded-full border-2 border-muted-foreground/30" />;
  return <Minus className="mx-auto h-3 w-3 text-muted-foreground/20" />;
}
