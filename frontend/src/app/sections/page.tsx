// frontend/src/app/sections/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getActs, getSections } from "@/lib/api";
import type { Act, SectionCard } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Scale,
  Search,
  ChevronRight,
  BookOpen,
  Library,
  ArrowRight,
  Loader2,
  History,
} from "lucide-react";
import axios from "axios";
import { getCategoryColor, getCategoryLabel, getCategoryAccentBorder } from "@/lib/utils";
import { useLocale } from "@/components/LocaleProvider";
import SiteLanguageToggle from "@/components/SiteLanguageToggle";

const SECTION_FILTERS = [
  { id: "all", label: "All" },
  { id: "non-bailable", label: "Non-Bailable" },
  { id: "bailable", label: "Bailable" },
  { id: "cognizable", label: "Cognizable" },
  { id: "criminal", label: "Criminal" },
  { id: "family", label: "Family" },
  { id: "cyber", label: "Cyber" },
] as const;

export default function SectionsPage() {
  const { t } = useLocale();
  const [acts, setActs] = useState<Act[]>([]);
  const [sections, setSections] = useState<SectionCard[]>([]);
  const [selectedAct, setSelectedAct] = useState<Act | null>(null);
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");
  const [actsLoading, setActsLoading] = useState(true);
  const [sectionsLoading, setSectionsLoading] = useState(false);

  const [selectedState, setSelectedState] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SectionCard[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set());

  useEffect(() => {
    let cancelled = false;
    setActsLoading(true);
    // Fetch acts with state filter if selected
    const url = selectedState ? `/api/sections/acts/list?state=${selectedState}` : `/api/sections/acts/list`;
    axios.get(url)
      .then((res) => {
        if (!cancelled) {
          setActs(res.data.acts);
          setActsLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setActs([]);
          setActsLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [selectedState]);

  useEffect(() => {
    if (!selectedAct) return;
    let cancelled = false;
    setSectionsLoading(true);
    getSections(selectedAct.id)
      .then((data) => {
        if (!cancelled) {
          setSections(data);
          setSectionsLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setSections([]);
          setSectionsLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [selectedAct]);

  const q = search.toLowerCase();
  const filtered = sections.filter((s) => {
    // Text search filter
    if (search && !(
      (s.section_number?.toLowerCase().includes(q) ?? false) ||
      (s.section_title?.toLowerCase().includes(q) ?? false) ||
      (s.plain_language?.toLowerCase().includes(q) ?? false)
    )) return false;

    // Category / attribute filter
    if (activeFilter === "all") return true;
    if (activeFilter === "non-bailable") return s.is_bailable === false;
    if (activeFilter === "bailable") return s.is_bailable === true;
    if (activeFilter === "cognizable") return s.is_cognizable === true;
    // Category-based filters match against the selected act's category
    if (activeFilter === "criminal") return selectedAct?.category?.toLowerCase() === "criminal";
    if (activeFilter === "family") return selectedAct?.category?.toLowerCase() === "family";
    if (activeFilter === "cyber") return selectedAct?.category?.toLowerCase() === "cyber";
    return true;
  });

  // --- REMOVED DUPLICATE STATE ---


  useEffect(() => {
    if (search.length < 2 || selectedAct) {
      setSearchResults(null);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const { data } = await axios.get(`/api/sections/search?q=${encodeURIComponent(search)}`);
        setSearchResults(data.results);
      } catch (err) {
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [search, selectedAct]);

  return (
    <div className="min-h-screen bg-[#f6f2ea] paper-grain text-slate-900">
      <header className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/90 px-4 py-3.5 shadow-sm backdrop-blur-md">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 min-w-0">
            <Link
              href="/"
              className="flex items-center gap-2.5 shrink-0 rounded-lg outline-none ring-offset-2 hover:opacity-90 focus-visible:ring-2 focus-visible:ring-slate-400"
            >
              <div className="w-9 h-9 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg flex items-center justify-center shadow-md ring-1 ring-amber-500/20">
                <Scale className="w-4 h-4 text-amber-100" />
              </div>
              <span className="font-legal-serif font-semibold text-slate-900 text-sm hidden sm:inline">
                {t.nav.brand}
              </span>
            </Link>
            <ChevronRight className="w-4 h-4 text-slate-300 shrink-0" />
            <div className="flex items-center gap-1.5 text-slate-600 min-w-0">
              <Library className="w-4 h-4 text-slate-400 shrink-0" />
              <span className="text-sm font-medium truncate">
                {t.nav.browseLaws}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0 flex-wrap justify-end">
            <SiteLanguageToggle surface="light" />
            <Link
              href="/references"
              className="hidden sm:inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-sm hover:bg-slate-50"
            >
              {t.nav.references}
            </Link>
            <Link
              href="/#nyaya-chat"
              className="inline-flex items-center gap-1.5 rounded-full border border-amber-200/80 bg-gradient-to-r from-slate-900 to-slate-800 px-3 py-1.5 text-xs font-semibold text-amber-50 shadow-md transition-colors hover:from-slate-800 hover:to-slate-700"
            >
              <Search className="w-3.5 h-3.5" />
              {t.nav.askNyaya}
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {!selectedAct ? (
          <>
            <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
              <div className="max-w-2xl">
                <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
                  Browse legal acts
                </h1>
                <div className="flex items-center gap-4 mt-2">
                   <p className="text-sm text-slate-600 leading-relaxed">
                    Filter by jurisdiction:
                  </p>
                  <div className="flex gap-2">
                    {["Central", "Maharashtra", "Uttar Pradesh"].map(s => (
                      <button
                        key={s}
                        onClick={() => setSelectedState(s === "Central" ? null : s)}
                        className={`text-[10px] uppercase font-bold px-3 py-1 rounded-full border transition-all ${
                          (s === "Central" && !selectedState) || selectedState === s
                            ? "bg-slate-900 text-white border-slate-900"
                            : "bg-white text-slate-500 border-slate-200 hover:border-slate-300"
                        }`}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <div className="relative w-full md:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Search all acts (e.g. theft, 498A)..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10 h-10 rounded-xl border-slate-200 bg-white text-sm shadow-sm focus:border-amber-400"
                />
              </div>
            </div>

            {searchResults ? (
              <div className="space-y-4 mb-12">
                <div className="flex items-center justify-between">
                  <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                    <Search className="w-3 h-3" />
                    Search Results for "{search}"
                  </h2>
                  <button onClick={() => setSearch("")} className="text-xs text-blue-600 hover:underline">Clear search</button>
                </div>
                {isSearching ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-6 h-6 text-slate-300 animate-spin" />
                  </div>
                ) : searchResults.length === 0 ? (
                  <div className="py-12 text-center bg-white rounded-2xl border border-dashed border-slate-200">
                    <p className="text-sm text-slate-400">No sections found for your search.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {searchResults.map((s) => (
                      <article key={s.id} className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm hover:border-amber-200 transition-all">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="outline" className="font-mono text-[10px] tabular-nums">§ {s.section_number}</Badge>
                              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tight">{s.act_title}</span>
                            </div>
                            <h3 className="font-semibold text-slate-900 mb-1">{s.section_title}</h3>
                            <p className="text-xs text-slate-500 line-clamp-2">{s.plain_language}</p>
                          </div>
                          <button 
                            onClick={() => {
                              const act = acts.find(a => a.short_title === s.act_title);
                              if (act) setSelectedAct(act);
                            }}
                            className="p-2 hover:bg-slate-50 rounded-lg text-slate-400 hover:text-slate-900 transition-colors"
                          >
                            <ArrowRight className="w-4 h-4" />
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
                <div className="border-t border-slate-200 pt-8" />
              </div>
            ) : null}

            {actsLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-36 rounded-2xl bg-slate-200/60 animate-pulse"
                  />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {acts.map((act) => (
                  <button
                    key={act.id}
                    type="button"
                    onClick={() => setSelectedAct(act)}
                    className="group text-left rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm transition-all duration-200 hover:border-slate-300 hover:shadow-md hover:-translate-y-0.5"
                  >
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-600 group-hover:bg-slate-800 group-hover:text-white transition-colors">
                        <BookOpen className="w-5 h-5" />
                      </div>
                      <Badge
                        variant="outline"
                        className={`text-[10px] uppercase tracking-wide ${getCategoryColor(act.category)}`}
                      >
                        {getCategoryLabel(act.category)}
                      </Badge>
                    </div>
                    <p className="font-semibold text-[15px] text-slate-900 leading-snug pr-6">
                      {act.short_title}
                    </p>
                    <div className="mt-4 flex items-center justify-between text-xs text-slate-500">
                      <span>
                        {act.year ?? "—"} ·{" "}
                        <span className="font-medium text-slate-700">
                          {act.section_count}
                        </span>{" "}
                        sections
                      </span>
                      <ArrowRight className="w-4 h-4 text-slate-300 transition-transform group-hover:translate-x-0.5 group-hover:text-slate-500" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </>
        ) : (
          <>
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedAct(null);
                    setSections([]);
                    setSearch("");
                  }}
                  className="mb-2 inline-flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-slate-800"
                >
                  <span aria-hidden>←</span> All acts
                </button>
                <h1 className="text-xl font-semibold tracking-tight text-slate-900 sm:text-2xl">
                  {selectedAct.short_title}
                </h1>
                <p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600">
                  <span>{selectedAct.year ?? "—"}</span>
                  <span className="text-slate-300">·</span>
                  <Badge
                    variant="outline"
                    className={`text-xs ${getCategoryColor(selectedAct.category)}`}
                  >
                    {getCategoryLabel(selectedAct.category)}
                  </Badge>
                </p>
              </div>
              <Input
                placeholder="Filter sections…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full sm:w-72 rounded-xl border-slate-200 bg-white text-sm shadow-sm"
              />
            </div>

            {/* Filter row */}
            <div className="flex flex-wrap gap-2 mb-4">
              {SECTION_FILTERS.map((f) => (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => setActiveFilter(f.id)}
                  className={`text-xs px-3 py-1.5 rounded-full border transition-all font-medium ${
                    activeFilter === f.id
                      ? "bg-slate-900 text-white border-slate-900"
                      : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:border-slate-300"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {sectionsLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="h-24 rounded-2xl bg-slate-200/50 animate-pulse"
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {filtered.length === 0 && (
                  <p className="rounded-2xl border border-dashed border-slate-200 bg-white py-12 text-center text-sm text-slate-500">
                    No sections match your filter.
                  </p>
                )}
                {filtered.map((section) => (
                  <article
                    key={
                      section.id ??
                      `${section.section_number}-${section.section_title}`
                    }
                    className={`rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm transition-shadow hover:shadow-md ${getCategoryAccentBorder(selectedAct.category)}`}
                  >
                    <div>
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge
                            variant="outline"
                            className="font-mono text-xs tabular-nums"
                          >
                            § {section.section_number}
                          </Badge>
                          {section.is_bailable === false && (
                            <Badge className="bg-red-100 text-red-700 border-red-200 text-xs">
                              Non-Bailable
                            </Badge>
                          )}
                          {section.is_bailable === true && (
                            <Badge className="bg-green-100 text-green-700 border-green-200 text-xs">
                              Bailable
                            </Badge>
                          )}
                          {section.is_cognizable === true && (
                            <Badge className="bg-orange-100 text-orange-700 border-orange-200 text-xs">
                              Cognizable
                            </Badge>
                          )}
                        </div>
                        {section.relevant_court && (
                          <span className="hidden text-right text-[11px] text-slate-400 md:block max-w-[40%]">
                            {section.relevant_court}
                          </span>
                        )}
                      </div>
                      {section.section_title && (
                        <h2 className="mt-3 text-base font-semibold text-slate-900">
                          {section.section_title}
                        </h2>
                      )}
                      {section.plain_language && (
                        <p className="mt-2 text-sm leading-relaxed text-slate-600">
                          {section.plain_language}
                        </p>
                      )}
                      {section.punishment_summary && (
                        <p className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-slate-50 px-2.5 py-1.5 text-xs text-slate-600 ring-1 ring-slate-100">
                          <span aria-hidden>⚖️</span>
                          {section.punishment_summary}
                        </p>
                      )}
                      
                      {/* Expansion logic for bare text */}
                      {section.bare_text && (
                        <div className="mt-2">
                          <button type="button"
                            onClick={() => setExpandedSections(prev => {
                              const next = new Set(prev);
                              const key = section.id || 0;
                              next.has(key) ? next.delete(key) : next.add(key);
                              return next;
                            })}
                            className="text-[10px] text-blue-600 hover:text-blue-700 flex items-center gap-1"
                          >
                            <Scale className="w-2.5 h-2.5" />
                            {expandedSections.has(section.id || 0) ? "Hide" : "Show"} bare act text
                          </button>
                          {expandedSections.has(section.id || 0) && (
                            <div className="mt-2 bg-slate-50 border border-slate-100 rounded p-3">
                              <p className="text-xs text-slate-500 font-mono leading-relaxed whitespace-pre-wrap">
                                {section.bare_text}
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Amendment History Section */}
                      <AmendmentHistory sectionId={section.id} />
                    </div>
                  </article>

                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// --- Amendment History Component ---
function AmendmentHistory({ sectionId }: { sectionId?: number }) {
  const [amendments, setAmendments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const fetchAmendments = async () => {
    if (isOpen || !sectionId) {
      setIsOpen(!isOpen);
      return;
    }
    setLoading(true);
    setIsOpen(true);
    try {
      const { data } = await axios.get(`/api/amendments/section/${sectionId}`);
      setAmendments(data);
    } catch (err) {
      console.error("Failed to fetch amendments", err);
    } finally {
      setLoading(false);
    }
  };

  if (!sectionId) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-100">
      <button
        onClick={fetchAmendments}
        className="text-[10px] font-bold uppercase tracking-wider text-slate-400 hover:text-blue-600 flex items-center gap-1.5 transition-colors"
      >
        <History className="w-3 h-3" />
        Amendment History {amendments.length > 0 && `(${amendments.length})`}
        {loading && <Loader2 className="w-2.5 h-2.5 animate-spin" />}
      </button>

      {isOpen && !loading && (
        <div className="mt-3 space-y-3 pl-2 border-l-2 border-slate-100">
          {amendments.length === 0 ? (
            <p className="text-[10px] text-slate-400 italic">No amendments found for this section.</p>
          ) : (
            amendments.map((a, idx) => (
              <div key={idx} className="relative">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-bold text-blue-600">
                    {new Date(a.effective_date).getFullYear()}
                  </span>
                  <span className="text-[9px] text-slate-400">·</span>
                  <span className="text-[10px] font-medium text-slate-700">{a.amendment_act}</span>
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed">{a.notes}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

