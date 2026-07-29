import Link from "next/link";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Home() {
  let health = null;
  try {
    health = await api.health();
  } catch {
    /* ignore */
  }

  return (
    <div className="relative">
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-14">
        <div className="grid lg:grid-cols-5 gap-10 items-center">
          <div className="lg:col-span-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-nyaya-500/30 bg-nyaya-500/10 px-3 py-1 text-xs text-nyaya-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Baseline Verified · 10 Acts · 51 Sections · 34 IPC↔BNS Mappings · 25 Benchmark Questions
            </div>
            <h1 className="mt-6 text-5xl md:text-6xl font-bold tracking-tight leading-[1.05]">
              <span className="gradient-text">Nyaya AI</span>
              <br />
              Indian Statutory Corpus,
              <br className="hidden md:block" /> Reimagined.
            </h1>
            <p className="mt-6 text-lg text-white/70 max-w-2xl leading-relaxed">
              Hybrid retrieval over the Indian statutory corpus — BM25 + BGE-M3 dense + cross-encoder rerank + citation validator.
              Bidirectional legacy IPC 1860 ↔ Bharatiya Nyaya Sanhita 2023 mapping, a knowledge graph of
              amendments/citations/interpretations, and a benchmark harness measuring R@5/10, P@10, MRR, and hallucinations.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href="/search"
                className="px-5 py-3 rounded-xl bg-gradient-to-br from-nyaya-600 to-sky-500 hover:shadow-glow transition text-white font-medium"
              >
                Try Hybrid Search →
              </Link>
              <Link
                href="/compare"
                className="px-5 py-3 rounded-xl border border-white/15 hover:border-nyaya-500/60 hover:bg-nyaya-500/10 transition"
              >
                IPC ↔ BNS Side-by-Side
              </Link>
              <Link href="/corpus" className="px-5 py-3 rounded-xl text-white/70 hover:text-white transition">
                Browse Corpus
              </Link>
            </div>
            <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl">
              {[
                { k: "Retrieval", v: "Hybrid BM25 + Dense", s: "w/ Cross-Encoder rerank" },
                { k: "Schema", v: "IPC-BNS Mapping", s: "bidirectional, 17+ pairs" },
                { k: "Graph", v: "KG Edges", s: "replaces / cited_in / related" },
                { k: "Eval", v: "R@5 / R@10 / MRR", s: "hallucination < 2% target" },
              ].map((x) => (
                <div key={x.k} className="glass rounded-xl p-4">
                  <div className="text-[11px] uppercase tracking-widest text-white/40">{x.k}</div>
                  <div className="mt-1 font-semibold text-white">{x.v}</div>
                  <div className="text-xs text-white/50">{x.s}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="glass rounded-2xl p-6 shadow-glow">
              <div className="flex items-center justify-between mb-4">
                <div className="text-sm text-white/60">Platform Health</div>
                <div className={`text-xs px-2 py-1 rounded-md ${
                  health?.status === "ok" ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30" :
                  "bg-amber-500/15 text-amber-300 border border-amber-500/30"
                }`}>
                  {health?.status ?? "unreachable"}
                </div>
              </div>
              <dl className="grid grid-cols-2 gap-3 text-sm">
                {[
                  ["Postgres", health?.postgres ?? "—"],
                  ["Qdrant", health?.qdrant ?? "—"],
                  ["Redis", health?.redis ?? "—"],
                  ["Acts", health?.acts_count ?? 0],
                  ["Sections", health?.sections_count ?? 0],
                  ["IPC↔BNS", health?.mappings_count ?? 0],
                  ["Benchmark Qs", health?.questions_count ?? 0],
                ].map(([k, v]) => (
                  <div key={k as string} className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2">
                    <dt className="text-white/50 text-xs">{k as string}</dt>
                    <dd className="font-medium text-white/90">{String(v)}</dd>
                  </div>
                ))}
              </dl>
              <div className="mt-5 pt-4 border-t border-white/5 text-xs text-white/40 leading-relaxed">
                <p>Press <span className="kbd">s</span> anywhere to jump to search.</p>
                <p className="mt-2">Tip: on search results, a green bar = citation validated (<span className="text-emerald-300">✓</span>), red = hallucination risk (<span className="text-rose-300">✗</span>).</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 pt-6 pb-20">
        <h2 className="text-2xl font-semibold mb-6">How retrieval works</h2>
        <div className="grid md:grid-cols-4 gap-4">
          {[
            { n: 1, t: "BM25", d: "Token-level inverted index search (rank_bm25). English + Devanagari tokenizer with stopword removal." },
            { n: 2, t: "BGE-M3 Dense", d: "1024-dim dense vectors via BAAI/bge-m3. Qdrant HNSW + cosine distance." },
            { n: 3, t: "Cross-Encoder Rerank", d: "ms-marco-MiniLM reranks combined candidates (top 200). Final hybrid weighted scoring." },
            { n: 4, t: "Citation Validator", d: "Per-result query/semantic similarity gating; 0.5× score penalty for hallucination-risk passages." },
          ].map((x) => (
            <div key={x.n} className="glass rounded-xl p-5">
              <div className="w-9 h-9 rounded-lg bg-nyaya-500/20 border border-nyaya-500/40 grid place-items-center font-bold">
                {x.n}
              </div>
              <div className="mt-3 font-semibold">{x.t}</div>
              <p className="mt-1 text-sm text-white/60 leading-relaxed">{x.d}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
