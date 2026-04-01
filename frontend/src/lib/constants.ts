import type { Category, CategoryMeta } from "@/types";

export const CATEGORIES: Record<Category, CategoryMeta> = {
  intelligence: { color: "#A78BFA", glow: "#C4B5FD", label: "Intelligence", icon: "brain" },
  stamina: { color: "#34D399", glow: "#6EE7B7", label: "Stamina", icon: "flame" },
  sociality: { color: "#FBBF24", glow: "#FDE68A", label: "Sociality", icon: "users" },
  creativity: { color: "#FB923C", glow: "#FDBA74", label: "Creativity", icon: "palette" },
  discipline: { color: "#38BDF8", glow: "#7DD3FC", label: "Discipline", icon: "shield" },
  wellness: { color: "#F472B6", glow: "#F9A8D4", label: "Wellness", icon: "heart" },
};

export const ALL_CATEGORIES: Category[] = Object.keys(CATEGORIES) as Category[];
