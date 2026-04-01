import { create } from "zustand";

interface SidebarStore {
  collapsed: boolean;
  toggle: () => void;
}

function getInitialCollapsed(): boolean {
  // Expanded by default on xl+ (1280px+), collapsed on smaller
  if (typeof window !== "undefined") {
    return window.innerWidth < 1280;
  }
  return true;
}

export const useSidebarStore = create<SidebarStore>((set) => ({
  collapsed: getInitialCollapsed(),
  toggle: () => set((s) => ({ collapsed: !s.collapsed })),
}));
