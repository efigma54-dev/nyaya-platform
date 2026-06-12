"use client";

import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

type Props = {
  saved: boolean;
  onToggle: () => void;
  labels: { add: string; remove: string };
};

export default function ReferenceBookmarkStar({
  saved,
  onToggle,
  labels,
}: Props) {
  return (
    <button
      type="button"
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        onToggle();
      }}
      title={saved ? labels.remove : labels.add}
      aria-label={saved ? labels.remove : labels.add}
      aria-pressed={saved}
      className={cn(
        "shrink-0 rounded-lg p-2 transition-colors",
        saved
          ? "text-amber-600 bg-amber-50 hover:bg-amber-100"
          : "text-slate-400 hover:bg-slate-100 hover:text-amber-600"
      )}
    >
      <Star
        className={cn(
          "w-4 h-4",
          saved ? "fill-amber-400 text-amber-600" : "fill-transparent"
        )}
      />
    </button>
  );
}
