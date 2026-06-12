"use client";

import Link from "next/link";
import { Scale, BookMarked } from "lucide-react";
import SiteLanguageToggle from "@/components/SiteLanguageToggle";
import { useLocale } from "@/components/LocaleProvider";
import { cn } from "@/lib/utils";

type Variant = "dark" | "light";

export default function SiteHeader({
  variant = "dark",
  className,
}: {
  variant?: Variant;
  className?: string;
}) {
  const { t } = useLocale();
  const isDark = variant === "dark";

  return (
    <header
      className={cn(
        "shrink-0 border-b px-3 sm:px-5 py-3 flex flex-wrap items-center justify-between gap-y-2 gap-x-3 backdrop-blur-md",
        isDark
          ? "border-white/10 bg-slate-950/70"
          : "border-slate-200/90 bg-white/95 shadow-sm",
        className
      )}
    >
      <Link
        href="/"
        className="flex items-center gap-2.5 min-w-0 group"
      >
        <div
          className={cn(
            "w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ring-1 transition-transform group-hover:scale-[1.02]",
            isDark
              ? "bg-gradient-to-br from-amber-200 to-amber-400 ring-amber-300/40"
              : "bg-gradient-to-br from-slate-800 to-slate-950 ring-slate-900/20"
          )}
        >
          <Scale
            className={cn(
              "w-5 h-5",
              isDark ? "text-slate-900" : "text-amber-100"
            )}
          />
        </div>
        <div className="min-w-0">
          <h1
            className={cn(
              "font-legal-serif text-base sm:text-lg font-semibold leading-tight truncate",
              isDark ? "text-white" : "text-slate-900"
            )}
          >
            {t.nav.brand}
          </h1>
          <p
            className={cn(
              "text-[11px] sm:text-xs leading-tight truncate",
              isDark ? "text-amber-100/70" : "text-slate-500"
            )}
          >
            {t.nav.tagline}
          </p>
        </div>
      </Link>

      <div className="flex items-center gap-2 sm:gap-3 shrink-0 flex-wrap justify-end">
        <SiteLanguageToggle surface={isDark ? "dark" : "light"} />
        <Link
          href="/references"
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full border px-2.5 sm:px-3 py-1.5 text-xs font-semibold transition-colors",
            isDark
              ? "border-white/20 bg-white/5 text-amber-50 hover:bg-white/10"
              : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-white"
          )}
        >
          <BookMarked className="w-3.5 h-3.5 shrink-0 opacity-80" />
          {t.nav.references}
        </Link>
        <Link
          href="/sections"
          className={cn(
            "text-xs font-semibold transition-colors",
            isDark
              ? "text-amber-100/85 hover:text-white"
              : "text-slate-600 hover:text-slate-900"
          )}
        >
          {t.nav.browseLaws}
        </Link>
        <div
          className={cn(
            "hidden sm:flex items-center gap-1.5 pl-2 text-xs",
            isDark ? "border-l border-white/15 text-amber-100/60" : "border-l border-slate-200 text-slate-500"
          )}
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          {t.nav.live}
        </div>
      </div>
    </header>
  );
}
