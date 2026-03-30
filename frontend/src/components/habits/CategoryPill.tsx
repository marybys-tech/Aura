import type { Category } from "@/types";
import { getCategoryColor, getCategoryLabel } from "@/lib/category";

interface CategoryPillProps {
  category: Category;
  selected?: boolean;
  onClick?: () => void;
}

export default function CategoryPill({ category, selected, onClick }: CategoryPillProps) {
  const color = getCategoryColor(category);
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors ${
        selected ? "text-white" : ""
      }`}
      style={{
        backgroundColor: selected ? color : `${color}15`,
        borderColor: selected ? color : `${color}30`,
        color: selected ? "#fff" : color,
      }}
    >
      <div className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: selected ? "#fff" : color }} />
      {getCategoryLabel(category)}
    </button>
  );
}
