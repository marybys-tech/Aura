import { create } from "zustand";
import type { Category } from "@/types";

interface MasterMessage {
  content: string;
  category: Category;
}

interface MasterStore {
  message: MasterMessage | null;
  show: (msg: MasterMessage) => void;
  dismiss: () => void;
}

export const useMasterStore = create<MasterStore>((set) => ({
  message: null,
  show: (msg) => {
    set({ message: msg });
    setTimeout(() => set({ message: null }), 6000);
  },
  dismiss: () => set({ message: null }),
}));
