import type { QuestSummary, Category } from "@/types";
import { getCategoryColor } from "@/lib/category";
import { useClaimQuest, useRequestQuest, useDismissQuest } from "@/hooks/useQuests";
import { useAuraStore } from "@/stores/aura";
import { useMasterStore } from "@/stores/master";
import { Button } from "@/components/ui/button";
import { Sparkles, Clock, Trophy, X } from "lucide-react";

interface QuestSectionProps {
  quests: QuestSummary[];
}

export default function QuestSection({ quests }: QuestSectionProps) {
  const request = useRequestQuest();
  const canRequest = quests.filter((q) => q.status !== "completed" && q.status !== "expired").length < 3;

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold">Quests</h3>
        {canRequest && (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 gap-1.5 px-2.5 text-[11px] text-primary hover:text-primary"
            onClick={() => request.mutate("daily")}
            disabled={request.isPending}
          >
            <Sparkles className="h-3.5 w-3.5" />
            {request.isPending ? "Asking..." : "Ask the Master"}
          </Button>
        )}
      </div>

      {quests.length === 0 ? (
        <div className="flex flex-col items-center py-4 text-center">
          <Sparkles className="mb-2 h-8 w-8 text-muted-foreground/30" />
          <p className="text-xs text-muted-foreground">
            No active quests.
          </p>
          <Button
            variant="outline"
            size="sm"
            className="mt-3 gap-1.5 text-xs"
            onClick={() => request.mutate("daily")}
            disabled={request.isPending}
          >
            <Sparkles className="h-3.5 w-3.5" />
            {request.isPending ? "The Master is thinking..." : "Request a Quest"}
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {quests.map((q) => (
            <QuestCard key={q.id} quest={q} />
          ))}
        </div>
      )}
    </div>
  );
}

function QuestCard({ quest }: { quest: QuestSummary }) {
  const claim = useClaimQuest();
  const dismiss = useDismissQuest();
  const triggerFlare = useAuraStore((s) => s.triggerFlare);
  const showMaster = useMasterStore((s) => s.show);
  const color = getCategoryColor(quest.target_category as Category);
  const progress = quest.progress_target > 0 ? quest.progress_current / quest.progress_target : 0;

  const handleClaim = () => {
    claim.mutate(quest.id, {
      onSuccess: () => {
        triggerFlare(quest.target_category);
        showMaster({
          content: `Quest complete! You earned ${quest.bonus_points} XP in ${quest.target_category}. The journey continues.`,
          category: quest.target_category as Category,
        });
      },
    });
  };

  return (
    <div
      className="relative rounded-lg border p-3"
      style={{ borderColor: quest.is_claimable ? color : `${color}30` }}
    >
      <button
        onClick={() => dismiss.mutate(quest.id)}
        className="absolute right-2 top-2 text-muted-foreground/40 hover:text-muted-foreground"
        disabled={dismiss.isPending}
      >
        <X className="h-3.5 w-3.5" />
      </button>
      <div className="flex items-start gap-3">
        <div
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
          style={{ backgroundColor: `${color}20` }}
        >
          {quest.is_claimable ? (
            <Trophy className="h-4 w-4" style={{ color }} />
          ) : (
            <Sparkles className="h-4 w-4" style={{ color }} />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium leading-tight">{quest.title}</p>
          <p className="mt-0.5 text-[11px] text-muted-foreground">{quest.description}</p>

          {/* Progress bar */}
          <div className="mt-2 flex items-center gap-2">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(progress * 100, 100)}%`,
                  backgroundColor: color,
                }}
              />
            </div>
            <span className="text-[10px] font-medium text-muted-foreground">
              {quest.progress_current}/{quest.progress_target}
            </span>
          </div>

          {/* Footer */}
          <div className="mt-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-semibold" style={{ color }}>
                +{quest.bonus_points} XP
              </span>
              {quest.expires_in_hours !== null && !quest.is_claimable && (
                <span className="flex items-center gap-0.5 text-[10px] text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {quest.expires_in_hours}h
                </span>
              )}
            </div>
            {quest.is_claimable && (
              <Button
                size="sm"
                className="h-7 gap-1 px-3 text-[11px] font-semibold"
                style={{ backgroundColor: color }}
                onClick={handleClaim}
                disabled={claim.isPending}
              >
                <Trophy className="h-3 w-3" />
                Claim
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
