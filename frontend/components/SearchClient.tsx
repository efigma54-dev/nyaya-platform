"use client";

import { useEffect, useMemo, useState } from "react";
import { SearchHit, SearchResponse } from "@/lib/types";
import { api } from "@/lib/api";
import CitationHighlight from "./CitationHighlight";
import Link from "next/link";
import clsx from "clsx";

function scoreBar(bm25: number | null | undefined, dense: number | null | undefined,
                 rerank: number, combined: number) {
  const norm = (x: number | null | undefined) => Math.max(0, Math.min(1, x ?? 0));
  return (
    <div className="flex flex-col gap-1 w-40">
      <ScoreRow label="BM25" value={norm(bm25)} color="bg-sky-500" />
      <ScoreRow label="Dense" value={norm(dense)} color="bg-fuchsia-500" />
      <ScoreRow label="Rerank" value={norm(rerank)} color="bg-amber-400" />
      <ScoreRow label="Combined" value={norm(combined)} color="bg-emerald-400" />
    </div>
  );
}

function ScoreRow({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2 text-[10px] text-white/50">
      <div className="w-12 text-right">{label}</div>
      <div className="flex-1 h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div className={clsx("h-full rounded-full", color)} style={{ width: `${value * 100}%` }} />
      </div>
      <div className="w-8 text-right font-mono text-white/60">{(value * 100).toFixed(0)}</div>
    </div>
  );
}

function HitCard({ hit, query }: { hit: SearchHit; query: string }) {
  const sec = hit.section;
  const valid = hit.citation_validated;
  return (
    <div className={clsx(
      "glass rounded-2xl p-5 transition",
      valid ? "border-l-4 border-l-emerald-400/70" : "border-l-4 border-l-rose-400/60"
    )}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white/60">
              #{hit.rank}
            </span>
            {sec?.act_short_title && (
              <span className="text-xs text-nyaya-200">
                {sec.act_short_title} · Sec {sec.section_number}
                {sec.act_year ? ` · ${sec.act_year}` : ""}
              </span>
            )}
            {sec?.chapter && (
              <span className="text-xs text-white/50">{sec.chapter}</span>
            )}
            {valid ? (
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                ✓ Cited by corpus
              </span>
            ) : (
              <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/30">
                ✗ Hallucination risk
              </span>
            )}
          </div>
          <h3 className="mt-2 font-semibold text-lg text-white">
            <Link href={`/section/${hit.section_id}`} className="hover:text-nyaya-200">
              {sec?.title ?? `Section ${hit.section_id}`}
            </Link>
          </h3>
        </div>
        {scoreBar(hit.bm25_score, hit.dense_score, hit.rerank_score ?? hit.combined_score, hit.combined_score)}
      </div>
      <div className="mt-4 grid lg:grid-cols-2 gap-4">
        <div>
          <div className="text-[11px] uppercase tracking-widest text-white/40 mb-1">Bare Text</div>
          <CitationHighlight
            text={sec?.bare_text ?? ""}
            query={query}
            validated={valid}
            similarity={hit.citation_similarity}
            className="text-white/80"
          />
        </div>
        <div>
          <div className="text-[11px] uppercase tracking-widest text-white/40 mb-1">Plain Language</div>
          <CitationHighlight
            text={sec?.plain_language ?? "No plain-language summary in seed corpus yet."}
            query={query}
            validated={valid}
            className="text-white/80"
          />
          {hit.snippets && hit.snippets.length > 0 && (
            <div className="mt-3">
              <div className="text-[11px] uppercase tracking-widest text-white/40 mb-1">Snippets</div>
              <ul className="space-y-1.5">
                {hit.snippets.map((s, i) => (
                  <li key={i} className="text-sm text-white/70 bg-white/5 border border-white/10 rounded-lg px-3 py-2">
                    <CitationHighlight text={s} query={query} validated={valid} />
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SearchClient() {
  const [q, setQ] = useState("punishment for murder ipc");
  const [k, setK] = useState(10);
  const [rr, setRr] = useState(true);
  const [loading, setLoading] = useState(false);
  const [resp, setResp] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(query: string, topK: number, rerank: boolean) {
    setLoading(true);
    setError(null);
    try {
      const r = await api.search(query, topK, rerank);
      setResp(r);
    } catch (e: unknown) {
      setError((e as Error)?.message ?? "Search request failed.");
      setResp(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void run(q, k, rr);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const stats = useMemo(() => {
    if (!resp) return null;
    const validated = resp.results.filter((r) => r.citation_validated).length;
    const avgScore = resp.results.length
      ? resp.results.reduce((a, b) => a + (b.combined_score ?? 0), 0) / resp.results.length
      : 0;
    return { validated, total: resp.results.length, avgScore, latencyMs: resp.latency_ms };
  }, [resp]);

  return (
    <div className="space-y-6">
      <form
        className="glass rounded-2xl p-4 md:p-5"
        onSubmit={(e) => {
          e.preventDefault();
          void run(q, k, rr);
        }}
      >
        <div className="flex flex-col md:flex-row md:items-center gap-3">
          <div className="flex-1 relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40">🔎</span>
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Try: “dowry death 304b”, “rape bns 65”, “pmla section 3”, “498a cruelty”…"
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-nyaya-500/60 focus:outline-none focus:ring-2 focus:ring-nyaya-500/20 text-white placeholder:text-white/35"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-white/60 flex items-center gap-1.5">
              Top-K
              <select
                value={k}
                onChange={(e) => setK(parseInt(e.target.value, 10))}
                className="bg-white/5 border border-white/10 rounded-md px-2 py-1.5 text-white focus:outline-none"
              >
                {[5, 10, 25, 50, 100].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </label>
            <label className="text-xs text-white/60 flex items-center gap-1.5">
              <input type="checkbox" checked={rr} onChange={(e) => setRr(e.target.checked)} />
              Rerank
            </label>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-br from-nyaya-600 to-sky-500 text-white font-medium disabled:opacity-60"
            >
              {loading ? "Searching…" : "Search"}
            </button>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {[
            "punishment for murder in IPC",
            "section 498a cruelty husband",
            "rape definition bns 2023",
            "dowry death section 304b",
            "pmla money laundering section 3",
            "bailable cognizable theft ipc",
          ].map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => { setQ(s); void run(s, k, rr); }}
              className="text-xs px-2.5 py-1 rounded-md bg-white/5 border border-white/10 text-white/65 hover:bg-nyaya-500/10 hover:text-white hover:border-nyaya-500/40"
            >
              “{s}”
            </button>
          ))}
        </div>
      </form>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
          <Stat k="Latency" v={`${stats.latencyMs} ms`} />
          <Stat k="Returned" v={`${stats.total}`} />
          <Stat k="Cited ✓" v={`${stats.validated} (${((stats.validated / Math.max(1, stats.total)) * 100).toFixed(0)}%)`} />
          <Stat k="Avg Score" v={(stats.avgScore * 100).toFixed(1)} />
          <Stat k="Target Recall@10" v="≥ 0.92" />
        </div>
      )}

      {error && <div className="rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-200 px-4 py-3">{error}</div>}

      {loading && !resp && (
        <div className="grid md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="glass rounded-2xl p-5 animate-pulse">
              <div className="h-3 w-24 bg-white/10 rounded mb-3" />
              <div className="h-5 w-3/4 bg-white/10 rounded mb-4" />
              <div className="space-y-2">
                <div className="h-3 bg-white/5 rounded w-full" />
                <div className="h-3 bg-white/5 rounded w-11/12" />
              </div>
            </div>
          ))}
        </div>
      )}

      {resp && (
        <div className="grid gap-4">
          {resp.results.length === 0 && (
            <div className="glass rounded-2xl p-6 text-white/60">
              No results. Try broader keywords or check the <Link href="/corpus" className="text-nyaya-200">corpus list</Link>.
            </div>
          )}
          {resp.results.map((h) => (
            <HitCard key={h.section_id} hit={h} query={resp.query} />
          ))}
        </div>
      )}
    </div>
  );
}

function Stat({ k, v }: { k: string; v: string }) {
  return (
    <div className="glass rounded-xl px-4 py-3 flex items-center justify-between">
      <div className="text-xs text-white/50 uppercase tracking-wider">{k}</div>
      <div className="font-mono text-white">{v}</div>
    </div>
  );
}
