"use client";

import { useState, useEffect } from "react";
import { useLocale } from "@/components/LocaleProvider";
import { cn } from "@/lib/utils";

type Props = {
  className?: string;
  /** Button styling for dark navy headers vs light paper headers */
  surface?: "dark" | "light";
};

export default function SiteLanguageToggle({ className, surface = "dark" }: Props) {
  const { lang, setLang } = useLocale();
  const [mounted, setMounted] = useState(false);
  const light = surface === "light";

  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return null;

  return (
    <div
      className={cn(
        "inline-flex rounded-full border p-0.5 text-[11px] font-semibold backdrop-blur-sm",
        light
          ? "border-slate-200 bg-slate-100/90"
          : "border-white/15 bg-black/25",
        className
      )}
      role="group"
      aria-label="Interface language"
    >
      <button
        type="button"
        onClick={() => setLang("en")}
        className={cn(
          "rounded-full px-2.5 py-1 transition-colors",
          lang === "en"
            ? light
              ? "bg-white text-slate-900 shadow-sm ring-1 ring-slate-200"
              : "bg-amber-100 text-amber-950 shadow-sm"
            : light
              ? "text-slate-600 hover:text-slate-900"
              : "text-amber-100/80 hover:text-white"
        )}
      >
        EN
      </button>
      <button
        type="button"
        onClick={() => setLang("hi")}
        className={cn(
          "rounded-full px-2.5 py-1 transition-colors",
          lang === "hi"
            ? light
              ? "bg-white text-slate-900 shadow-sm ring-1 ring-slate-200"
              : "bg-amber-100 text-amber-950 shadow-sm"
            : light
              ? "text-slate-600 hover:text-slate-900"
              : "text-amber-100/80 hover:text-white"
        )}
      >
        हिंदी
      </button>
    </div>
  );
}
