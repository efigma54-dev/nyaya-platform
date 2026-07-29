import Link from "next/link";
import { api } from "@/lib/api";
import { BenchmarkMetrics } from "@/lib/types";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Retrieval Benchmark · Nyaya AI",
  description: "Recall@5/10, Precision@10, MRR, and hallucination rate against 25+ retrieval questions.",
};

const TARGETS = {
  recall_at_5: { min: 0.60, prod: 0.85 },
  recall_at_10: { min: 0.70, prod: 0.92 },
  precision_at_10: { min: 0.35, prod: 0.50 },
  mrr: { min: 0.45, prod: 0.60 },
  hallucination_rate: { max: 0.25, prod: 0.02 },
};

function gauge(pct: number, color: string) {
  return (
    <div className="h-2 rounded-full bg-white/5 overflow-hidden">
      <div className={`h-full ${color}`} style={{ width: `${Math.min(100, pct)}%` }} />
    </div>
  );
}

function Metric({
  label, value, format, minTarget, prodTarget, direction = "up",
}: {
  label: string; value: number; format?: (n: number) => string;
  minTarget?: number; prodTarget?: number; direction?: "up" | "down";
}) {
  const fmt = format ?? ((n: number) => n.toFixed(2));
  const pct = (() => {
    if (direction === "up" && prodTarget) return (value / prodTarget) * 100;
    if (direction === "down" && prodTarget) return Math.max(0, 100 - (value / prodTarget) * 100);
    return value * 100;
  })();
  const color = (() => {
    if (direction === "up") {
      if (minTarget !== undefined && value < minTarget) return "bg-rose-500";
      if (prodTarget !== undefined && value < prodTarget) return "bg-amber-400";
      return "bg-emerald-400";
    }
    if (prodTarget !== undefined && value > prodTarget) return "bg-rose-500";
    if (minTarget !== undefined && value > minTarget) return "bg-amber-400";
    return "bg-emerald-400";
  })();
  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex items-center justify-between text-xs text-white/50 uppercase tracking-widest">
        <div>{label}</div>
        {minTarget !== undefined && (
          <div>Target: <span className="text-white/75">{direction === "up" ? "≥" : "≤"} {
            direction === "up" ? (prodTarget ?? minTarget).toFixed(2) : (prodTarget ?? minTarget).toFixed(2)
          }</span></div>
        )}
      </div>
      <div className="mt-3 flex items-end justify-between">
        <div className="text-4xl font-bold font-mono tracking-tight">{fmt(value)}</div>
      </div>
      <div className="mt-3">{gauge(pct, color)}</div>
    </div>
  );
}

export default async function BenchmarkPage() {
  const health = await api.health().catch(() => null);
  let result: BenchmarkMetrics | null = null;
  let err: string | null = null;
  try {
    result = await api.benchmark("frontend_on_demand", undefined);
  } catch (e: unknown) {
    err = (e as Error)?.message ?? "Benchmark request failed.";
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-14 space-y-10">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-nyaya-300/70">Evaluator Harness</div>
          <h1 className="mt-2 text-4xl font-bold tracking-tight">Retrieval Benchmark Dashboard</h1>
          <p className="mt-3 text-white/65 max-w-3xl leading-relaxed">
            Nyaya tracks five retrieval metrics across 25+ seeded statutory questions spanning Easy / Medium / Hard
            (see <code className="font-mono bg-white/5 px-1.5 py-0.5 rounded">backend/nyaya/seed/benchmark_questions.py</code>).
            Production readiness requires Recall@5 ≥ 0.85, Recall@10 ≥ 0.92, Precision@10 ≥ 0.50,
            MRR ≥ 0.60, and hallucination rate below 2% on a 1,000+ question set.
          </p>
        </div>
        {result && (
          <div className="self-start md:self-end glass rounded-xl px-4 py-3 text-xs">
            <div className="text-white/40">Run</div>
            <div className="font-mono text-white/90">{result.run_name}</div>
            <div className="text-white/50 mt-0.5">{result.num_questions} questions</div>
          </div>
        )}
      </div>

      {err && (
        <div className="rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-200 px-4 py-3 text-sm">
          Could not run live benchmark. {err}
        </div>
      )}

      {result && (
        <div className="grid md:grid-cols-5 gap-4">
          <Metric
            label="Recall @ 5"
            value={result.recall_at_5}
            format={(n) => (n * 100).toFixed(1) + "%"}
            minTarget={TARGETS.recall_at_5.min}
            prodTarget={TARGETS.recall_at_5.prod}
          />
          <Metric
            label="Recall @ 10"
            value={result.recall_at_10}
            format={(n) => (n * 100).toFixed(1) + "%"}
            minTarget={TARGETS.recall_at_10.min}
            prodTarget={TARGETS.recall_at_10.prod}
          />
          <Metric
            label="Precision @ 10"
            value={result.precision_at_10}
            format={(n) => (n * 100).toFixed(1) + "%"}
            minTarget={TARGETS.precision_at_10.min}
            prodTarget={TARGETS.precision_at_10.prod}
          />
          <Metric
            label="Mean Reciprocal Rank"
            value={result.mrr}
            format={(n) => n.toFixed(3)}
            minTarget={TARGETS.mrr.min}
            prodTarget={TARGETS.mrr.prod}
          />
          <Metric
            label="Hallucination Rate"
            value={result.hallucination_rate}
            format={(n) => (n * 100).toFixed(1) + "%"}
            minTarget={TARGETS.hallucination_rate.max}
            prodTarget={TARGETS.hallucination_rate.prod}
            direction="down"
          />
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-5">
        <div className="glass rounded-2xl p-5 lg:col-span-2">
          <h2 className="text-lg font-semibold mb-3">How we evaluate</h2>
          <ol className="list-decimal list-inside space-y-2 text-sm text-white/75 leading-relaxed">
            <li><strong>Question Bank</strong>: 25 baseline questions (Easy/Medium/Hard) spanning IPC 1860 legacy, BNS 2023 new codes, PMLA, SCST POA, IT Act, DVA.</li>
            <li><strong>Retriever</strong>: Hybrid BM25 (rank_bm25) + BGE-M3 dense (Qdrant) + min-max weighted fuse → Cross-Encoder top-200 rerank.</li>
            <li><strong>Citation Validator</strong>: Per-top-10 result we measure query/semantic similarity against its bare text + keywords. Any result that fails the 0.72 threshold AND is not in the ground-truth set increments the hallucination counter (with a 0.5× score penalty applied at retrieval time).</li>
            <li><strong>Metrics</strong>: Recall@5 / Recall@10 / Precision@10 / MRR / Hallucination Rate are persisted per run as <code className="font-mono bg-white/5 px-1 py-0.5 rounded">BenchmarkRun</code> rows.</li>
            <li><strong>Evidence</strong>: Every CLI run of <span className="kbd">nyaya validate</span> writes a JSON report to <code className="font-mono bg-white/5 px-1 py-0.5 rounded">evidence/</code>, including per-question metrics, latency, and five spot-check retrievals.</li>
          </ol>
        </div>
        <div className="glass rounded-2xl p-5">
          <h2 className="text-lg font-semibold mb-3">Corpus Inventory</h2>
          <dl className="space-y-2 text-sm">
            {[
              ["Acts", health?.acts_count ?? "—"],
              ["Sections", health?.sections_count ?? "—"],
              ["IPC↔BNS Mappings", health?.mappings_count ?? "—"],
              ["Benchmark Questions", health?.questions_count ?? "—"],
              ["Postgres", health?.postgres ?? "—"],
              ["Qdrant", health?.qdrant ?? "—"],
              ["Redis", health?.redis ?? "—"],
            ].map(([k, v]) => (
              <div key={k} className="flex items-center justify-between rounded-md bg-white/5 border border-white/10 px-3 py-2">
                <dt className="text-white/60">{k}</dt>
                <dd className="font-mono text-white/95">{String(v)}</dd>
              </div>
            ))}
          </dl>
          <div className="mt-5 text-xs text-white/50 leading-relaxed">
            Production readiness requires a 1,000+ question benchmark. Start by expanding
            <Link href="/corpus" className="text-nyaya-200 ml-1"> the corpus </Link>
            and adding more ground-truth relevant-section IDs.
          </div>
        </div>
      </div>
    </div>
  );
}
