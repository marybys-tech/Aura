import { useState } from "react";
import { useCreateHabit } from "@/hooks/useHabits";
import { ALL_CATEGORIES } from "@/lib/constants";
import type { Category } from "@/types";
import CategoryPill from "./CategoryPill";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

interface AddHabitDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function AddHabitDialog({ open, onOpenChange }: AddHabitDialogProps) {
  const createHabit = useCreateHabit();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<Category>("intelligence");
  const [scheduleType, setScheduleType] = useState<string>("daily");
  const [scheduleDays, setScheduleDays] = useState<number[]>([]);
  const [timesPerDay, setTimesPerDay] = useState(2);

  const reset = () => {
    setTitle("");
    setDescription("");
    setCategory("intelligence");
    setScheduleType("daily");
    setScheduleDays([]);
    setTimesPerDay(2);
  };

  const handleSubmit = () => {
    createHabit.mutate(
      {
        title,
        description: description || undefined,
        category,
        schedule_type: scheduleType,
        schedule_days: scheduleType === "specific_days" ? scheduleDays : undefined,
        times_per_day: scheduleType === "multiple_daily" ? timesPerDay : 1,
      },
      {
        onSuccess: () => {
          reset();
          onOpenChange(false);
        },
      },
    );
  };

  const toggleDay = (day: number) => {
    setScheduleDays((prev) => (prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-lg">Add New Habit</DialogTitle>
        </DialogHeader>

        <div className="space-y-5 py-2">
          <fieldset className="space-y-2">
            <label htmlFor="title" className="text-xs font-medium text-muted-foreground">
              Habit Name
            </label>
            <Input
              id="title"
              placeholder="e.g. Read 30 minutes"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </fieldset>

          <fieldset className="space-y-2">
            <label htmlFor="desc" className="text-xs font-medium text-muted-foreground">
              Description (optional)
            </label>
            <Textarea
              id="desc"
              placeholder="Describe your habit goal..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
            />
          </fieldset>

          <fieldset className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Category</label>
            <div className="flex flex-wrap gap-2">
              {ALL_CATEGORIES.map((cat) => (
                <CategoryPill
                  key={cat}
                  category={cat as Category}
                  selected={category === cat}
                  onClick={() => setCategory(cat as Category)}
                />
              ))}
            </div>
          </fieldset>

          <fieldset className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Schedule</label>
            <div className="flex flex-wrap gap-2">
              {[
                { value: "daily", label: "Every day" },
                { value: "specific_days", label: "Specific days" },
                { value: "multiple_daily", label: "Multiple daily" },
              ].map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setScheduleType(opt.value)}
                  className={`rounded-lg border px-3 py-2 text-xs font-medium transition-colors ${
                    scheduleType === opt.value
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-muted-foreground hover:border-foreground/20"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            {scheduleType === "specific_days" && (
              <div className="flex gap-1.5 pt-1">
                {DAYS.map((name, i) => (
                  <button
                    key={name}
                    type="button"
                    onClick={() => toggleDay(i + 1)}
                    className={`flex h-9 w-9 items-center justify-center rounded-lg text-xs font-medium transition-colors ${
                      scheduleDays.includes(i + 1)
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-accent"
                    }`}
                  >
                    {name[0]}
                  </button>
                ))}
              </div>
            )}

            {scheduleType === "multiple_daily" && (
              <div className="flex items-center gap-3 pt-1">
                <label htmlFor="times" className="text-xs text-muted-foreground">
                  Times per day:
                </label>
                <Input
                  id="times"
                  type="number"
                  min={2}
                  max={10}
                  value={timesPerDay}
                  onChange={(e) => setTimesPerDay(Number(e.target.value))}
                  className="w-20"
                />
              </div>
            )}
          </fieldset>
        </div>

        <DialogFooter className="gap-2 pt-2">
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!title.trim() || createHabit.isPending}>
            Create Habit
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
