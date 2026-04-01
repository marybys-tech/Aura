import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { UserWithScores } from "@/types";

export function useCurrentUser() {
  return useQuery<UserWithScores>({
    queryKey: ["user", "me"],
    queryFn: async () => (await api.get("/users/me")).data,
    retry: false,
  });
}

export function useUpdateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: { display_name?: string; timezone?: string }) =>
      (await api.patch("/users/me", data)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["user", "me"] }),
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        await api.post("/auth/logout", { refresh_token: refreshToken });
      }
    },
    onSettled: () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      qc.clear();
      window.location.href = "/login";
    },
  });
}
