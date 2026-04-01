export default function LoginPage() {
  return (
    <div className="relative flex min-h-screen items-center justify-center bg-background p-4">
      {/* Atmospheric background glows */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
        <div
          className="absolute left-1/2 top-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-20 blur-[120px]"
          style={{ backgroundColor: "#A78BFA" }}
        />
        <div
          className="absolute left-1/4 top-1/3 h-[300px] w-[300px] rounded-full opacity-15 blur-[100px]"
          style={{ backgroundColor: "#34D399" }}
        />
        <div
          className="absolute bottom-1/4 right-1/4 h-[300px] w-[300px] rounded-full opacity-15 blur-[100px]"
          style={{ backgroundColor: "#F472B6" }}
        />
      </div>

      {/* Login card */}
      <div className="relative w-full max-w-sm rounded-2xl border border-border bg-card/80 p-10 shadow-2xl backdrop-blur-md">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex items-center gap-2.5">
            <div
              className="h-3.5 w-3.5 rounded-full"
              style={{ backgroundColor: "#A78BFA", boxShadow: "0 0 14px rgba(167,139,250,0.6)" }}
            />
            <h1 className="text-3xl font-bold tracking-tight">Aura</h1>
          </div>
          <p className="text-sm text-muted-foreground">
            Track your growth. Master your habits.
          </p>
        </div>

        <div className="mt-10 space-y-4">
          <p className="text-center text-sm font-medium text-foreground">
            Sign in to continue
          </p>
          <a
            href="/api/v1/auth/github/login"
            className="flex h-12 w-full items-center justify-center gap-3 rounded-xl border border-border bg-secondary text-sm font-medium transition-colors hover:bg-accent"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12Z" />
            </svg>
            Continue with GitHub
          </a>
        </div>

        <p className="mt-8 text-center text-xs text-muted-foreground">
          By continuing, you agree to our Terms &amp; Privacy Policy
        </p>
      </div>
    </div>
  );
}
