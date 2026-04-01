import { create } from "zustand";

interface AuraStore {
  lastFlareCategory: string | null;
  flareSeq: number;
  triggerFlare: (category: string) => void;
}

export const useAuraStore = create<AuraStore>((set) => ({
  lastFlareCategory: null,
  flareSeq: 0,
  triggerFlare: (category) =>
    set((state) => ({ lastFlareCategory: category, flareSeq: state.flareSeq + 1 })),
}));
