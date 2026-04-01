import { describe, it, expect } from "vitest";
import { getCategoryColor, getCategoryGlow, getCategoryLabel, formatSchedule, todayISO } from "@/lib/category";
import { CATEGORIES, ALL_CATEGORIES } from "@/lib/constants";
import type { Category } from "@/types";

describe("getCategoryColor", () => {
  it("returns correct color for each category", () => {
    expect(getCategoryColor("intelligence")).toBe("#A78BFA");
    expect(getCategoryColor("stamina")).toBe("#34D399");
    expect(getCategoryColor("wellness")).toBe("#F472B6");
  });

  it("returns fallback for unknown category", () => {
    expect(getCategoryColor("bogus" as Category)).toBe("#A78BFA");
  });
});

describe("getCategoryGlow", () => {
  it("returns correct glow for a category", () => {
    expect(getCategoryGlow("discipline")).toBe("#7DD3FC");
  });

  it("returns fallback for unknown category", () => {
    expect(getCategoryGlow("nope" as Category)).toBe("#C4B5FD");
  });
});

describe("getCategoryLabel", () => {
  it("returns human-readable label", () => {
    expect(getCategoryLabel("sociality")).toBe("Sociality");
    expect(getCategoryLabel("creativity")).toBe("Creativity");
  });

  it("returns raw category string as fallback", () => {
    expect(getCategoryLabel("unknown" as Category)).toBe("unknown");
  });
});

describe("formatSchedule", () => {
  it("formats daily schedule", () => {
    expect(formatSchedule("daily")).toBe("Every day");
  });

  it("formats multiple_daily with given times", () => {
    expect(formatSchedule("multiple_daily", null, 3)).toBe("3x daily");
  });

  it("defaults to 2x when times is undefined", () => {
    expect(formatSchedule("multiple_daily")).toBe("2x daily");
  });

  it("formats specific_days with weekday names", () => {
    expect(formatSchedule("specific_days", [1, 3, 5])).toBe("Mon, Wed, Fri");
    expect(formatSchedule("specific_days", [6, 7])).toBe("Sat, Sun");
  });

  it("returns raw type for unknown schedule", () => {
    expect(formatSchedule("custom_thing")).toBe("custom_thing");
  });
});

describe("todayISO", () => {
  it("returns YYYY-MM-DD format", () => {
    expect(todayISO()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});

describe("constants", () => {
  it("ALL_CATEGORIES contains exactly 6 entries", () => {
    expect(ALL_CATEGORIES).toHaveLength(6);
  });

  it("CATEGORIES has matching keys", () => {
    expect(Object.keys(CATEGORIES).sort()).toEqual(ALL_CATEGORIES.slice().sort());
  });

  it("every category has color, glow, label, icon", () => {
    for (const meta of Object.values(CATEGORIES)) {
      expect(meta.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(meta.glow).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(meta.label).toBeTruthy();
      expect(meta.icon).toBeTruthy();
    }
  });
});
