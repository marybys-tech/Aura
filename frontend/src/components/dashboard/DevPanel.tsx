import { useState } from "react";
import { api } from "@/api/client";

const SCENARIOS = [
  { id: "fresh", label: "Fresh User", desc: "Just signed up, no activity" },
  { id: "day1_active", label: "Day 1 Active", desc: "Completed a few habits today" },
  { id: "week1", label: "Week 1", desc: "3 categories progressing" },
  { id: "month1", label: "Month 1", desc: "2 strong, 2 moderate, 2 weak" },
  { id: "balanced_pro", label: "Balanced Pro", desc: "3 months balanced, all Lv 5-8" },
  { id: "one_dominant", label: "One Dominant", desc: "Intelligence Lv 13, rest neglected" },
  { id: "neglected", label: "Neglected", desc: "Abandoned — all vitality 0" },
  { id: "comeback", label: "Comeback", desc: "Returning after neglect" },
];

export default function DevPanel() {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);

  const apply = async (id: string) => {
    setLoading(id);
    try {
      await api.post(`/dev/scenarios/${id}`);
      window.location.reload();
    } catch {
      setLoading(null);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-4 right-4 z-50 rounded-full bg-primary/80 px-3 py-1.5 text-[10px] font-bold text-white shadow-lg backdrop-blur-sm hover:bg-primary lg:bottom-6 lg:right-6"
      >
        DEV
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-72 rounded-xl border border-border bg-card p-4 shadow-2xl lg:bottom-6 lg:right-6">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
          Test Scenarios
        </span>
        <button
          onClick={() => setOpen(false)}
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          Close
        </button>
      </div>
      <div className="space-y-1.5">
        {SCENARIOS.map((s) => (
          <button
            key={s.id}
            onClick={() => apply(s.id)}
            disabled={loading !== null}
            className="flex w-full flex-col items-start rounded-lg border border-border px-3 py-2 text-left transition-colors hover:bg-accent disabled:opacity-50"
          >
            <span className="text-xs font-medium">
              {loading === s.id ? "Applying..." : s.label}
            </span>
            <span className="text-[10px] text-muted-foreground">{s.desc}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
