import type { Category } from "@/types";
import { CATEGORIES } from "./constants";

export function getCategoryColor(category: Category): string {
  return CATEGORIES[category]?.color ?? "#A78BFA";
}

export function getCategoryGlow(category: Category): string {
  return CATEGORIES[category]?.glow ?? "#C4B5FD";
}

export function getCategoryLabel(category: Category): string {
  return CATEGORIES[category]?.label ?? category;
}

export function formatSchedule(type: string, days?: number[] | null, times?: number): string {
  if (type === "daily") return "Every day";
  if (type === "multiple_daily") return `${times ?? 2}x daily`;
  if (type === "specific_days" && days) {
    const names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    return days.map((d) => names[d - 1]).join(", ");
  }
  return type;
}

export function todayISO(): string {
  return new Date().toISOString().split("T")[0];
}
