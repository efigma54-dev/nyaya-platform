"use client";

import Link from "next/link";
import {
  ACADEMIC_RESEARCH_POINTERS,
  OFFICIAL_LEGAL_SOURCES,
  SUGGESTED_REFERENCE_BOOKS,
  TECHNICAL_ROADMAP,
  type OfficialSource,
} from "@/lib/legal-references";
import { ArrowLeft, ExternalLink } from "lucide-react";
import SiteHeader from "@/components/SiteHeader";
import { useLocale } from "@/components/LocaleProvider";
import { useReferenceBookmarks } from "@/hooks/useReferenceBookmarks";
import ReferenceBookmarkStar from "@/components/ReferenceBookmarkStar";

function sourceLabel(s: OfficialSource, hi: boolean) {
  if (hi && s.titleHi) return s.titleHi;
  return s.title;
}

function sourceDesc(s: OfficialSource, hi: boolean) {
  if (hi && s.descriptionHi) return s.descriptionHi;
  return s.description;
}

export default function ReferencesClient() {
  const { lang, t } = useLocale();
  const hi = lang === "hi";
  const { list, isSaved, toggle, remove } = useReferenceBookmarks();

  return (
    <div className="min-h-screen bg-[#f6f2ea] text-slate-900 paper-grain">
      <SiteHeader variant="light" />

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-10 pb-28">
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            {t.references.back}
          </Link>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-800/80 mb-2">
            {t.references.badge}
          </p>
          <h1 className="font-legal-serif text-3xl sm:text-4xl font-bold tracking-tight text-slate-900">
            {t.references.title}
          </h1>
          <p className="mt-3 text-sm text-slate-600 leading-relaxed">
            {t.references.intro}
          </p>
        </div>

        <section
          id="bookmarks"
          className="scroll-mt-28 rounded-2xl border border-amber-200/60 bg-white/90 p-5 shadow-md ring-1 ring-slate-900/5"
        >
          <h2 className="font-legal-serif text-lg font-semibold text-slate-900 mb-2">
            {t.references.bookmarksHeading}
          </h2>
          {list.length === 0 ? (
            <p className="text-sm text-slate-500">{t.references.bookmarksEmpty}</p>
          ) : (
            <ul className="space-y-2">
              {list.map((b) => (
                <li
                  key={b.href}
                  className="flex items-start justify-between gap-2 rounded-xl border border-slate-100 bg-slate-50/80 px-3 py-2"
                >
                  <a
                    href={b.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-slate-800 hover:underline break-all"
                  >
                    {b.title}
                  </a>
                  <button
                    type="button"
                    onClick={() => remove(b.href)}
                    className="shrink-0 text-xs font-semibold text-amber-800 hover:text-amber-950"
                  >
                    {t.references.bookmarkRemove}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section id="official" className="scroll-mt-24">
          <h2 className="font-legal-serif text-xl font-semibold text-slate-900 mb-4 border-l-4 border-amber-600 pl-3">
            {t.references.officialHeading}
          </h2>
          <ul className="space-y-3">
            {OFFICIAL_LEGAL_SOURCES.map((s) => (
              <li
                key={s.id}
                className="rounded-2xl border border-slate-200/90 bg-white p-4 shadow-sm flex gap-2 items-start"
              >
                <ReferenceBookmarkStar
                  saved={isSaved(s.href)}
                  onToggle={() =>
                    toggle({
                      id: s.id,
                      href: s.href,
                      title: sourceLabel(s, hi),
                    })
                  }
                  labels={{
                    add: t.references.bookmarkAdd,
                    remove: t.references.bookmarkRemove,
                  }}
                />
                <div className="min-w-0 flex-1">
                  <a
                    href={s.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-semibold text-slate-900 hover:underline inline-flex items-center gap-1.5"
                  >
                    {sourceLabel(s, hi)}
                    <ExternalLink className="w-3.5 h-3.5 opacity-60 shrink-0" />
                  </a>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                    {sourceDesc(s, hi)}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section id="academic" className="scroll-mt-24">
          <h2 className="font-legal-serif text-xl font-semibold text-slate-900 mb-3 border-l-4 border-slate-700 pl-3">
            {t.references.academicHeading}
          </h2>
          <p className="text-sm text-slate-600 mb-4 leading-relaxed">
            {t.references.academicIntro}
          </p>
          <ul className="space-y-3">
            {ACADEMIC_RESEARCH_POINTERS.map((s) => (
              <li
                key={s.id}
                className="rounded-2xl border border-slate-200/90 bg-white p-4 shadow-sm flex gap-2 items-start"
              >
                <ReferenceBookmarkStar
                  saved={isSaved(s.href)}
                  onToggle={() =>
                    toggle({
                      id: s.id,
                      href: s.href,
                      title: sourceLabel(s, hi),
                    })
                  }
                  labels={{
                    add: t.references.bookmarkAdd,
                    remove: t.references.bookmarkRemove,
                  }}
                />
                <div className="min-w-0 flex-1">
                  <a
                    href={s.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-semibold text-slate-900 hover:underline inline-flex items-center gap-1.5"
                  >
                    {sourceLabel(s, hi)}
                    <ExternalLink className="w-3.5 h-3.5 opacity-60 shrink-0" />
                  </a>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                    {sourceDesc(s, hi)}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section id="books" className="scroll-mt-24">
          <h2 className="font-legal-serif text-xl font-semibold text-slate-900 mb-3 border-l-4 border-amber-600 pl-3">
            {t.references.booksHeading}
          </h2>
          <p className="text-sm text-slate-600 mb-3">{t.references.booksIntro}</p>
          <ul className="rounded-2xl border border-slate-200 bg-white divide-y divide-slate-100 shadow-sm overflow-hidden">
            {SUGGESTED_REFERENCE_BOOKS.map((b) => (
              <li
                key={`${b.author}-${b.title}`}
                className="px-4 py-3 text-sm text-slate-700 flex flex-col sm:flex-row sm:gap-2"
              >
                <span className="font-semibold text-slate-900">{b.author}</span>
                <span className="text-slate-400 hidden sm:inline">—</span>
                <span className="italic">{b.title}</span>
              </li>
            ))}
          </ul>
        </section>

        <section id="technical" className="scroll-mt-24">
          <h2 className="font-legal-serif text-xl font-semibold text-slate-900 mb-4 border-l-4 border-slate-700 pl-3">
            {t.references.techHeading}
          </h2>
          <ul className="space-y-2">
            {TECHNICAL_ROADMAP.map((item) => {
              const loc =
                t.references.techItems[
                  item.title as keyof typeof t.references.techItems
                ];
              return (
                <li
                  key={item.title}
                  className="rounded-xl border border-dashed border-slate-300/90 bg-white/70 px-4 py-3 text-sm"
                >
                  <span className="font-semibold text-slate-800">
                    {loc?.title ?? item.title}
                  </span>
                  <span className="text-slate-600">
                    {" "}
                    — {loc?.detail ?? item.detail}
                  </span>
                </li>
              );
            })}
          </ul>
        </section>

        <p className="text-xs text-slate-500 leading-relaxed border-t border-slate-200/80 pt-6">
          {t.references.disclaimer}
        </p>
      </main>
    </div>
  );
}
