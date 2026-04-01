import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { TodayResponse, WeekResponse, MonthResponse, StatsResponse } from "@/types";

export function useDashboardToday() {
  return useQuery<TodayResponse>({
    queryKey: ["dashboard", "today"],
    queryFn: async () => (await api.get("/dashboard/today")).data,
  });
}

export function useDashboardWeek(date?: string) {
  return useQuery<WeekResponse>({
    queryKey: ["dashboard", "week", date],
    queryFn: async () => (await api.get("/dashboard/week", { params: date ? { date } : {} })).data,
  });
}

export function useDashboardMonth(date?: string) {
  return useQuery<MonthResponse>({
    queryKey: ["dashboard", "month", date],
    queryFn: async () => (await api.get("/dashboard/month", { params: date ? { date } : {} })).data,
  });
}

export function useStats() {
  return useQuery<StatsResponse>({
    queryKey: ["stats"],
    queryFn: async () => (await api.get("/stats")).data,
  });
}
