import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export function getCategoryColor(category: string | null): string {
  const colors: Record<string, string> = {
    criminal: "bg-red-100 text-red-800 border-red-200",
    consumer: "bg-blue-100 text-blue-800 border-blue-200",
    constitutional: "bg-purple-100 text-purple-800 border-purple-200",
    family: "bg-pink-100 text-pink-800 border-pink-200",
    property: "bg-amber-100 text-amber-800 border-amber-200",
    labour: "bg-green-100 text-green-800 border-green-200",
    corporate: "bg-slate-100 text-slate-800 border-slate-200",
    civil: "bg-cyan-100 text-cyan-800 border-cyan-200",
    cyber: "bg-teal-100 text-teal-800 border-teal-200",
    tax: "bg-orange-100 text-orange-800 border-orange-200",
    environmental: "bg-emerald-100 text-emerald-800 border-emerald-200",
    narcotics: "bg-rose-100 text-rose-800 border-rose-200",
  };
  return colors[category || ""] || "bg-slate-100 text-slate-800 border-slate-200";
}

export function getCategoryLabel(category: string | null): string {
  const labels: Record<string, string> = {
    criminal: "Criminal Law",
    consumer: "Consumer Law",
    constitutional: "Constitutional Law",
    family: "Family & Domestic Violence",
    property: "Property Law",
    labour: "Labour Law",
    corporate: "Corporate Law",
    civil: "Civil Law",
    cyber: "Cyber Law",
    tax: "Tax Law",
    environmental: "Environmental Law",
    narcotics: "Narcotics Law",
  };
  return labels[category || ""] || "General Law";
}

/** Left border accent for section cards. */
export function getCategoryAccentBorder(category: string | null): string {
  const b: Record<string, string> = {
    criminal: "border-l-4 border-l-red-500",
    consumer: "border-l-4 border-l-blue-500",
    constitutional: "border-l-4 border-l-purple-500",
    family: "border-l-4 border-l-pink-500",
    property: "border-l-4 border-l-amber-500",
    labour: "border-l-4 border-l-green-600",
    corporate: "border-l-4 border-l-slate-500",
    civil: "border-l-4 border-l-cyan-600",
    cyber: "border-l-4 border-l-teal-600",
  };
  return b[category || ""] || "border-l-4 border-l-slate-400";
}
