import { useEffect } from "react";
import { useNavigate, useSearch } from "@tanstack/react-router";

export default function OAuthCallbackPage() {
  const navigate = useNavigate();
  const search = useSearch({ strict: false }) as Record<string, string>;

  useEffect(() => {
    const accessToken = search.access_token;
    const refreshToken = search.refresh_token;

    if (accessToken && refreshToken) {
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);
      navigate({ to: "/", replace: true });
    } else {
      navigate({ to: "/login", replace: true });
    }
  }, [search, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex items-center gap-3">
        <div className="h-3 w-3 animate-pulse rounded-full bg-primary" />
        <p className="text-sm text-muted-foreground">Signing you in...</p>
      </div>
    </div>
  );
}
