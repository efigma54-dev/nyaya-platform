import Link from "next/link";
import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import CitationHighlight from "@/components/CitationHighlight";
import KGVisualization from "@/components/KGVisualization";
import { IPCBNSCompare } from "@/lib/types";
import clsx from "clsx";

export const dynamic = "force-dynamic";

function SectionHeader({ s }: { s: {
  id: number; title: string; section_number: string; chapter?: string | null; part?: string | null;
  act_short_title?: string | null; act_year?: number | null; source_page?: number | null;
  checksum_sha256?: string | null; source_pdf?: string | null;
} }) {
  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex flex-wrap items-center gap-2 text-xs text-white/50">
        <span className="px-2 py-0.5 rounded-md bg-nyaya-500/15 text-nyaya-200 border border-nyaya-500/30">
          {s.act_short_title}{s.act_year ? ` · ${s.act_year}` : ""}
        </span>
        <span>§ {s.section_number}</span>
        {s.chapter && <span>· {s.chapter}</span>}
        {s.part && <span>· Part: {s.part}</span>}
        {s.source_page && <span className="font-mono">p.{s.source_page}</span>}
        {s.source_pdf && (
          <a href={s.source_pdf} target="_blank" rel="noreferrer" className="text-nyaya-200 hover:underline">
            source PDF ↗
          </a>
        )}
        {s.checksum_sha256 && (
          <span className="font-mono text-[10px] text-white/40 truncate max-w-[28ch]" title={s.checksum_sha256}>
            sha256:{s.checksum_sha256.slice(0, 12)}…
          </span>
        )}
      </div>
      <h1 className="mt-3 text-3xl md:text-4xl font-bold tracking-tight">{s.title}</h1>
      <div className="mt-5 flex gap-2 flex-wrap">
        <Link href="/corpus" className="px-3 py-1.5 rounded-md text-sm bg-white/5 hover:bg-white/10 border border-white/10 text-white/80">
          ← Back to Corpus
        </Link>
        <Link href={`/compare?a=${s.id}`} className="px-3 py-1.5 rounded-md text-sm bg-nyaya-500/20 hover:bg-nyaya-500/30 border border-nyaya-500/40 text-nyaya-100">
          ⇄ IPC ↔ BNS compare
        </Link>
        <a href={`/search?q=${encodeURIComponent(s.title)}`} className="px-3 py-1.5 rounded-md text-sm bg-white/5 hover:bg-white/10 border border-white/10 text-white/80">
          Search similar
        </a>
      </div>
    </div>
  );
}

function PunishmentsBox({ s }: { s: {
  punishments?: string | null; bailable?: boolean | null; cognizable?: boolean | null; compoundable?: boolean | null;
  fine_min?: number | null; fine_max?: number | null; imprisonment_min_months?: number | null;
  imprisonment_max_months?: number | null; death_penalty?: boolean; life_imprisonment?: boolean;
  keywords?: string[] | null;
} }) {
  const chip = (t: string, v: boolean | undefined | null, good: boolean) => {
    if (v === undefined || v === null) return null;
    const ok = good ? v : !v;
    return (
      <span className={clsx(
        "text-xs px-2.5 py-1 rounded-md border",
        ok ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30" :
             "bg-rose-500/10 text-rose-300 border-rose-500/30"
      )}>{t}</span>
    );
  };
  return (
    <div className="glass rounded-2xl p-5">
      <div className="text-xs uppercase tracking-widest text-white/40">Punishment & Process</div>
      <p className="mt-2 text-sm text-white/80 leading-relaxed">{s.punishments ?? "Punishment is defined under the parent section's cross-reference."}</p>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <Stat k="Min Custody" v={s.imprisonment_min_months ? `${Math.round(s.imprisonment_min_months/12)}y ${s.imprisonment_min_months%12}m` : "—"} />
        <Stat k="Max Custody" v={s.imprisonment_max_months ? `${Math.round(s.imprisonment_max_months/12)}y` : "—"} />
        <Stat k="Fine Min" v={s.fine_min != null ? `₹${s.fine_min.toLocaleString("en-IN")}` : "—"} />
        <Stat k="Fine Max" v={s.fine_max != null ? `₹${s.fine_max.toLocaleString("en-IN")}` : "—"} />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {chip("Cognizable", s.cognizable, true)}
        {chip("Bailable", s.bailable, false)}
        {chip("Compoundable", s.compoundable, true)}
        {s.death_penalty && chip("Death", true, false)}
        {s.life_imprisonment && chip("Life", true, false)}
      </div>
      {Array.isArray(s.keywords) && s.keywords.length > 0 && (
        <div className="mt-5">
          <div className="text-xs uppercase tracking-widest text-white/40 mb-2">Keywords</div>
          <div className="flex flex-wrap gap-1.5">
            {s.keywords.map((k) => (
              <span key={k} className="text-xs px-2 py-1 rounded-md bg-white/5 border border-white/10 text-white/75">
                #{k}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ k, v }: { k: string; v: string }) {
  return (
    <div className="rounded-lg bg-white/5 border border-white/10 px-3 py-2 flex items-center justify-between">
      <div className="text-xs text-white/50">{k}</div>
      <div className="font-medium text-white/90 font-mono">{v}</div>
    </div>
  );
}

function CompareCard({ pair, side }: { pair: IPCBNSCompare; side: "left" | "right" }) {
  const s = side === "left" ? pair.left : pair.right;
  return (
    <div className="glass rounded-2xl p-5 h-full">
      <div className="flex items-center justify-between mb-2">
        <div className="text-[11px] uppercase tracking-widest text-white/40">
          {s.act_short_title}{s.act_year ? ` · ${s.act_year}` : ""}
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white/70">
          § {s.section_number}
        </span>
      </div>
      <Link href={`/section/${s.id}`} className="block font-semibold text-white/95 hover:text-nyaya-200">
        {s.title}
      </Link>
      <div className="mt-3 text-sm text-white/80 leading-relaxed markdown-body">
        <CitationHighlight text={s.bare_text ?? ""} className="text-sm text-white/80" />
      </div>
      {s.plain_language && (
        <div className="mt-3 pt-3 border-t border-white/5 text-sm text-nyaya-100/90 leading-relaxed">
          <div className="text-[11px] uppercase tracking-widest text-nyaya-300/70 mb-1">Plain language</div>
          {s.plain_language}
        </div>
      )}
    </div>
  );
}

export default async function SectionPage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  if (!Number.isFinite(id) || id <= 0) return notFound();
  const section = await api.section(id).catch(() => null);
  if (!section) return notFound();
  const pairs = await api.ipcBnsForSection(id).catch(() => [] as IPCBNSCompare[]);
  const kg = await api.kgSubgraph(id, 2).catch(() => null);

  return (
    <div className="max-w-7xl mx-auto px-6 py-12 space-y-8">
      <SectionHeader s={section as any} />

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass rounded-2xl p-6">
            <div className="text-xs uppercase tracking-widest text-white/40">Bare Statutory Text</div>
            <div className="mt-3">
              <CitationHighlight text={section.bare_text ?? ""} />
            </div>
          </div>
          {section.plain_language && (
            <div className="glass rounded-2xl p-6 border-l-4 border-l-nyaya-500">
              <div className="text-xs uppercase tracking-widest text-nyaya-300/80">Plain-Language Summary</div>
              <div className="mt-3 text-white/90 leading-relaxed markdown-body">
                {section.plain_language}
              </div>
            </div>
          )}
          {kg && (
            <KGVisualization subgraph={kg} rootId={section.id} />
          )}
        </div>

        <div className="space-y-6">
          <PunishmentsBox s={section as any} />

          {pairs.length > 0 && (
            <div className="glass rounded-2xl p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="text-xs uppercase tracking-widest text-white/40">IPC ↔ BNS Mappings</div>
                <Link href={`/compare?a=${section.id}`} className="text-xs text-nyaya-200 hover:underline">
                  Full compare →
                </Link>
              </div>
              <div className="space-y-3">
                {pairs.map((p) => (
                  <div key={p.mapping.id} className="rounded-xl border border-white/10 bg-white/5 p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-md border ${
                        p.mapping.mapping_kind === "ipc_to_bns" ? "bg-amber-500/10 text-amber-200 border-amber-500/30" :
                          "bg-sky-500/10 text-sky-200 border-sky-500/30"
                      }`}>{p.mapping.mapping_kind}</span>
                      <span className="text-[10px] text-white/50">{p.mapping.equivalence}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-1 text-xs">
                      <div className="rounded bg-white/5 px-2 py-1">
                        <div className="text-white/40">Left</div>
                        <Link href={`/section/${p.left.id}`} className="text-white/85 hover:text-white">
                          {p.left.act_short_title} § {p.left.section_number}
                        </Link>
                      </div>
                      <div className="rounded bg-white/5 px-2 py-1 text-right">
                        <div className="text-white/40">Right</div>
                        <Link href={`/section/${p.right.id}`} className="text-white/85 hover:text-white">
                          {p.right.act_short_title} § {p.right.section_number}
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {pairs.length > 0 && (
        <section>
          <h2 className="text-xl font-semibold mb-4">Side-by-side legacy ↔ new code comparisons</h2>
          <div className="space-y-6">
            {pairs.map((p) => (
              <div key={`side-${p.mapping.id}`}>
                <div className="flex items-center justify-between mb-3 text-xs">
                  <div className="inline-flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded-md bg-amber-500/15 text-amber-200 border border-amber-500/30">
                      {p.mapping.mapping_kind.toUpperCase()}
                    </span>
                    <span className="text-white/50">equivalence: <span className="text-white/80">{p.mapping.equivalence}</span></span>
                    {p.mapping.notes && <span className="text-white/50">· {p.mapping.notes}</span>}
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-6">
                  <CompareCard pair={p} side="left" />
                  <CompareCard pair={p} side="right" />
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
