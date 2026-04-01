import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { Habit, CompletionWithScore } from "@/types";

export function useHabits(category?: string) {
  return useQuery<Habit[]>({
    queryKey: ["habits", { category }],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (category) params.category = category;
      return (await api.get("/habits", { params })).data;
    },
  });
}

export function useHabit(id: string) {
  return useQuery<Habit>({
    queryKey: ["habits", id],
    queryFn: async () => (await api.get(`/habits/${id}`)).data,
    enabled: !!id,
  });
}

export function useCreateHabit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      title: string;
      description?: string;
      category: string;
      schedule_type: string;
      schedule_days?: number[];
      times_per_day?: number;
    }) => (await api.post("/habits", data)).data as Habit,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["habits"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateHabit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...data }: { id: string; title?: string; description?: string; category?: string }) =>
      (await api.patch(`/habits/${id}`, data)).data as Habit,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["habits"] }),
  });
}

export function useDeleteHabit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => (await api.delete(`/habits/${id}`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["habits"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useCompleteHabit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ habitId, date }: { habitId: string; date: string }) =>
      (await api.post(`/habits/${habitId}/complete`, { date })).data as CompletionWithScore,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}

export function useSkipHabit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ habitId, date }: { habitId: string; date: string }) =>
      (await api.post(`/habits/${habitId}/skip`, { date })).data as CompletionWithScore,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}
