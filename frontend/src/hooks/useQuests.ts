import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";

export function useClaimQuest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (questId: string) => (await api.post(`/quests/${questId}/claim`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}

export function useRequestQuest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (questType: string = "daily") =>
      (await api.post(`/quests/generate?quest_type=${questType}`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDismissQuest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (questId: string) => (await api.delete(`/quests/${questId}`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
