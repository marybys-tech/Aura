import { useMasterStore } from "@/stores/master";
import { getCategoryColor } from "@/lib/category";
import { X, Sparkles } from "lucide-react";

export default function MasterPopup() {
  const { message, dismiss } = useMasterStore();

  if (!message) return null;

  const color = getCategoryColor(message.category);

  return (
    <div className="fixed bottom-24 left-1/2 z-50 w-[90%] max-w-md -translate-x-1/2 lg:bottom-8">
      <div
        className="relative rounded-xl border bg-card p-4 shadow-lg backdrop-blur-sm"
        style={{ borderColor: `${color}40`, boxShadow: `0 0 20px ${color}20` }}
      >
        <button onClick={dismiss} className="absolute right-3 top-3 text-muted-foreground hover:text-foreground" aria-label="Dismiss message">
          <X className="h-4 w-4" />
        </button>
        <div className="flex items-start gap-3">
          <div
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
            style={{ backgroundColor: `${color}20` }}
          >
            <Sparkles className="h-5 w-5" style={{ color }} />
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
              Master's Words
            </p>
            <p className="mt-1 text-sm italic leading-relaxed text-foreground">
              "{message.content}"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
