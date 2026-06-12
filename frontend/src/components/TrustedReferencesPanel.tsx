"use client";

import { useState } from "react";
import {
  OFFICIAL_LEGAL_SOURCES,
  SUGGESTED_REFERENCE_BOOKS,
  type OfficialSource,
} from "@/lib/legal-references";
import {
  BookOpen,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Landmark,
} from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";

type Variant = "chat" | "inline";

interface Props {
  variant?: Variant;
  /** When true, panel starts expanded (e.g. on home teaser). */
  defaultOpen?: boolean;
}

function label(s: OfficialSource, hi: boolean) {
  if (hi && s.titleHi) return s.titleHi;
  return s.title;
}

function desc(s: OfficialSource, hi: boolean) {
  if (hi && s.descriptionHi) return s.descriptionHi;
  return s.description;
}

export default function TrustedReferencesPanel({
  variant = "chat",
  defaultOpen = false,
}: Props) {
  const { lang, t } = useLocale();
  const hi = lang === "hi";
  const [open, setOpen] = useState(defaultOpen);

  if (variant === "inline") {
    return (
      <div className="rounded-2xl border border-amber-200/50 bg-gradient-to-br from-white to-amber-50/40 p-4 shadow-md ring-1 ring-slate-900/5">
        <div className="flex items-center gap-2 text-slate-900 font-semibold text-sm mb-3 font-legal-serif">
          <Landmark className="w-4 h-4 text-amber-700 shrink-0" />
          {t.trustedPanel.inlineTitle}
        </div>
        <ul className="space-y-2">
          {OFFICIAL_LEGAL_SOURCES.slice(0, 5).map((s) => (
            <li key={s.id}>
              <a
                href={s.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-slate-700 hover:text-amber-950 underline-offset-2 hover:underline inline-flex items-center gap-1.5 font-medium"
              >
                {label(s, hi)}
                <ExternalLink className="w-3 h-3 opacity-60 shrink-0" />
              </a>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200/90 bg-white/90 overflow-hidden shadow-sm">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between gap-2 px-3 py-2.5 text-left text-xs font-semibold text-slate-700 hover:bg-amber-50/50 transition-colors"
      >
        <span className="flex items-center gap-2">
          <Landmark className="w-3.5 h-3.5 text-amber-700 shrink-0" />
          {t.trustedPanel.chatToggle}
        </span>
        {open ? (
          <ChevronDown className="w-4 h-4 text-slate-400 shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
        )}
      </button>
      {open && (
        <div className="border-t border-slate-200/80 px-3 py-3 space-y-3 bg-amber-50/20">
          <ul className="space-y-2">
            {OFFICIAL_LEGAL_SOURCES.map((s) => (
              <li key={s.id}>
                <a
                  href={s.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex flex-col gap-0.5 rounded-lg px-1 py-0.5 -mx-1 hover:bg-white/80"
                >
                  <span className="text-xs font-semibold text-slate-800 group-hover:underline underline-offset-2 inline-flex items-center gap-1">
                    {label(s, hi)}
                    <ExternalLink className="w-3 h-3 opacity-50" />
                  </span>
                  <span className="text-[11px] text-slate-500 leading-snug">
                    {desc(s, hi)}
                  </span>
                </a>
              </li>
            ))}
          </ul>
          <div className="pt-2 border-t border-slate-200/80">
            <p className="text-[10px] font-bold uppercase tracking-wide text-slate-500 mb-1.5 flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              {t.trustedPanel.booksLabel}
            </p>
            <ul className="text-[11px] text-slate-600 space-y-0.5 columns-1 sm:columns-2 gap-x-4">
              {SUGGESTED_REFERENCE_BOOKS.map((b) => (
                <li key={`${b.author}-${b.title}`} className="break-inside-avoid">
                  <span className="text-slate-800">{b.author}</span>
                  {" — "}
                  <span className="italic">{b.title}</span>
                </li>
              ))}
            </ul>
          </div>
          <p className="text-[10px] text-slate-400 leading-relaxed">
            {t.trustedPanel.footnote}
          </p>
        </div>
      )}
    </div>
  );
}
