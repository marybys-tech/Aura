import type { CategoryScore } from "@/types";

interface AuraPlaceholderProps {
  scores: Record<string, CategoryScore>;
  totalAura?: number;
}

export default function AuraPlaceholder({ scores, totalAura }: AuraPlaceholderProps) {
  const total = totalAura ?? Object.values(scores).reduce((sum, s) => sum + s.score, 0);

  return (
    <div className="relative flex flex-col items-center justify-center overflow-hidden rounded-xl border border-border bg-card p-6">
      {/* Gradient background simulating aura */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-32 w-32 rounded-full bg-intelligence/20 blur-[60px]" />
        <div className="absolute right-1/4 top-1/3 h-28 w-28 rounded-full bg-stamina/20 blur-[50px]" />
        <div className="absolute bottom-1/4 left-1/3 h-24 w-24 rounded-full bg-wellness/20 blur-[50px]" />
        <div className="absolute right-1/3 bottom-1/3 h-20 w-20 rounded-full bg-discipline/20 blur-[40px]" />
        <div className="absolute left-1/2 top-1/2 h-36 w-36 -translate-x-1/2 -translate-y-1/2 rounded-full bg-creativity/15 blur-[70px]" />
      </div>
      <div className="relative z-10 flex flex-col items-center">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
          Your Aura
        </p>
        <p className="mt-1 text-5xl font-bold tracking-tight">{Math.round(total)}</p>
      </div>
    </div>
  );
}
