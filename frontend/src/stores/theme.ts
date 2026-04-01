import { create } from "zustand";

type Theme = "dark" | "light";

interface ThemeStore {
  theme: Theme;
  toggle: () => void;
  set: (theme: Theme) => void;
}

function getInitialTheme(): Theme {
  const stored = localStorage.getItem("aura-theme") as Theme | null;
  if (stored) return stored;
  return "dark";
}

function applyTheme(theme: Theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
  localStorage.setItem("aura-theme", theme);
}

export const useThemeStore = create<ThemeStore>((set) => {
  const initial = getInitialTheme();
  applyTheme(initial);

  return {
    theme: initial,
    toggle: () =>
      set((state) => {
        const next = state.theme === "dark" ? "light" : "dark";
        applyTheme(next);
        return { theme: next };
      }),
    set: (theme) => {
      applyTheme(theme);
      set({ theme });
    },
  };
});
