import Link from "next/link";
import { api } from "@/lib/api";
import { IPCBNSCompare } from "@/lib/types";
import CitationHighlight from "@/components/CitationHighlight";
import clsx from "clsx";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "IPC ↔ BNS Side-by-Side · Nyaya AI",
  description: "Legacy IPC, CrPC, Evidence Act → 2023 Sanhitas bidirectional mapping and plain-language translation.",
};

type SearchParams = { a?: string; b?: string; kind?: string };

async function seedPairs(): Promise<IPCBNSCompare[]> {
  const all = await api.listIpcBnsCompare([
    // a few high-importance sections to seed the page
    ...[
      "Indian Penal Code, 1860:34",
      "Indian Penal Code, 1860:53",
      "Indian Penal Code, 1860:300",
      "Indian Penal Code, 1860:302",
      "Indian Penal Code, 1860:304",
      "Indian Penal Code, 1860:320",
      "Indian Penal Code, 1860:354",
      "Indian Penal Code, 1860:363",
      "Indian Penal Code, 1860:375",
      "Indian Penal Code, 1860:376",
      "Indian Penal Code, 1860:498A",
      "Indian Penal Code, 1860:304B",
      "Indian Penal Code, 1860:377",
      "Indian Penal Code, 1860:378",
      "Indian Penal Code, 1860:390",
      "Indian Penal Code, 1860:420",
    ].map((x) => {
      void x;
      return 0;
    }),
  ]);
  // Fall back to scanning all sections for BNS acts with mapping data:
  if (all.length === 0) {
    const acts = await api.listActs().catch(() => []);
    const bns = acts.find((a) => a.short_title.includes("Bharatiya Nyaya Sanhita"));
    const ipc = acts.find((a) => a.short_title.includes("Indian Penal Code"));
    if (bns) {
      const sections = await api.sectionsForAct(bns.id).catch(() => []);
      const out = await api.listIpcBnsCompare(sections.slice(0, 20).map((s) => s.id));
      void ipc;
      return out;
    }
  }
  return all;
}

function Panel({
  title, subtitle, s, badge, badgeStyle,
}: {
  title: string; subtitle: string; s: {
    id: number; section_number: string; title: string; chapter?: string | null;
    bare_text: string; plain_language?: string | null; act_short_title?: string | null;
    act_year?: number | null;
  }; badge?: string; badgeStyle?: string;
}) {
  return (
    <div className="glass rounded-2xl p-6 h-full flex flex-col">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="text-[11px] uppercase tracking-widest text-white/40">{subtitle}</div>
          <div className="mt-1 font-semibold">{title}</div>
        </div>
        {badge && (
          <span className={clsx("text-[10px] px-2 py-0.5 rounded-md border", badgeStyle)}>{badge}</span>
        )}
      </div>
      <div className="mt-3 flex items-center gap-2 text-sm text-white/60">
        <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10">§ {s.section_number}</span>
        {s.chapter && <span className="truncate">{s.chapter}</span>}
      </div>
      <Link href={`/section/${s.id}`} className="mt-2 text-lg font-semibold text-white hover:text-nyaya-200">
        {s.title}
      </Link>
      <div className="mt-4 text-sm text-white/80 leading-relaxed flex-1">
        <div className="text-[11px] uppercase tracking-widest text-white/40 mb-1">Bare Text</div>
        <CitationHighlight text={s.bare_text} className="markdown-body" />
      </div>
      {s.plain_language && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="text-[11px] uppercase tracking-widest text-nyaya-300/70 mb-1">Plain-Language</div>
          <p className="text-sm text-nyaya-100/90 leading-relaxed">{s.plain_language}</p>
        </div>
      )}
    </div>
  );
}

export default async function ComparePage({ searchParams }: { searchParams: SearchParams }) {
  const acts = await api.listActs().catch(() => []);
  const ipcAct = acts.find((a) => /Indian Penal Code/i.test(a.short_title));
  const bnsAct = acts.find((a) => /Bharatiya Nyaya Sanhita/i.test(a.short_title));

  let specific: IPCBNSCompare[] = [];
  if (searchParams.a) {
    specific = await api.ipcBnsForSection(Number(searchParams.a)).catch(() => []);
  }
  if (specific.length === 0 && searchParams.b) {
    specific = await api.ipcBnsForSection(Number(searchParams.b)).catch(() => []);
  }
  const featured: IPCBNSCompare[] = specific.length ? specific : await seedPairs();

  const ipcSections = ipcAct ? await api.sectionsForAct(ipcAct.id).catch(() => []) : [];
  const bnsSections = bnsAct ? await api.sectionsForAct(bnsAct.id).catch(() => []) : [];

  return (
    <div className="max-w-7xl mx-auto px-6 py-14 space-y-10">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-nyaya-300/70">Legacy ↔ New Codes</div>
          <h1 className="mt-2 text-4xl font-bold tracking-tight">IPC / CrPC / Evidence Act ↔ BNS / BNSS / BSA</h1>
          <p className="mt-3 text-white/65 max-w-3xl leading-relaxed">
            1 July 2024 repealed the Indian Penal Code, Code of Criminal Procedure, and Indian Evidence Act
            and replaced them with three new Sanhitas. Every Nyaya mapping stores the equivalence class
            (<em>exact</em>, <em>partial</em>, <em>expanded/narrowed/split/merged</em>) and notes for translators.
            Pick two sections below for a side-by-side plain-language view.
          </p>
        </div>
      </div>

      <form action="/compare" method="get" className="glass rounded-2xl p-5 grid md:grid-cols-3 gap-4">
        <div>
          <label className="text-xs uppercase tracking-widest text-white/40">Left Section</label>
          <select
            name="a"
            defaultValue={searchParams.a ?? ""}
            className="mt-1 w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-white focus:outline-none focus:border-nyaya-500/60"
          >
            <option value="">— Select a section —</option>
            <optgroup label="IPC 1860">
              {ipcSections.map((s) => (
                <option key={`ipc-${s.id}`} value={s.id}>§ {s.section_number} · {s.title}</option>
              ))}
            </optgroup>
            <optgroup label="BNS 2023">
              {bnsSections.map((s) => (
                <option key={`bns-${s.id}`} value={s.id}>§ {s.section_number} · {s.title}</option>
              ))}
            </optgroup>
          </select>
        </div>
        <div>
          <label className="text-xs uppercase tracking-widest text-white/40">Right Section</label>
          <select
            name="b"
            defaultValue={searchParams.b ?? ""}
            className="mt-1 w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-white focus:outline-none focus:border-nyaya-500/60"
          >
            <option value="">(auto via IPC↔BNS mapping if left selected)</option>
            <optgroup label="IPC 1860">
              {ipcSections.map((s) => (
                <option key={`ipc2-${s.id}`} value={s.id}>§ {s.section_number} · {s.title}</option>
              ))}
            </optgroup>
            <optgroup label="BNS 2023">
              {bnsSections.map((s) => (
                <option key={`bns2-${s.id}`} value={s.id}>§ {s.section_number} · {s.title}</option>
              ))}
            </optgroup>
          </select>
        </div>
        <div className="flex items-end">
          <button type="submit" className="w-full px-4 py-2 rounded-lg bg-gradient-to-br from-nyaya-600 to-sky-500 text-white font-medium">
            Compare
          </button>
        </div>
      </form>

      {featured.length === 0 && (
        <div className="glass rounded-2xl p-6 text-white/65">
          No IPC↔BNS mappings to display. Seed the backend corpus first.
        </div>
      )}

      <div className="space-y-10">
        {featured.map((p) => (
          <section key={p.mapping.id} className="scroll-smooth-section">
            <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
              <div className="flex items-center gap-2">
                <span className={`text-[11px] px-2.5 py-0.5 rounded-md border ${
                  p.mapping.mapping_kind === "ipc_to_bns"
                    ? "bg-amber-500/15 text-amber-200 border-amber-500/30"
                    : "bg-sky-500/15 text-sky-200 border-sky-500/30"
                }`}>
                  {p.mapping.mapping_kind}
                </span>
                <span className="text-[11px] px-2.5 py-0.5 rounded-md bg-white/5 border border-white/10 text-white/70">
                  equivalence: {p.mapping.equivalence}
                </span>
                {p.mapping.notes && (
                  <span className="text-xs text-white/55">· {p.mapping.notes}</span>
                )}
              </div>
              <div className="text-xs text-white/45">
                Mapping ID <span className="font-mono">#{p.mapping.id}</span>
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <Panel
                title={`${p.left.act_short_title ?? "—"} · ${p.left.act_year ?? ""}`}
                subtitle={p.mapping.mapping_kind === "ipc_to_bns" ? "Legacy (repealed or superseded)" : "New (in force)"}
                s={p.left as any}
                badge={/IPC|CrPC|Evidence/.test(p.left.act_short_title ?? "") ? "Legacy" : "New"}
                badgeStyle={/IPC|CrPC|Evidence/.test(p.left.act_short_title ?? "")
                  ? "bg-amber-500/15 text-amber-200 border-amber-500/30"
                  : "bg-emerald-500/15 text-emerald-200 border-emerald-500/30"}
              />
              <Panel
                title={`${p.right.act_short_title ?? "—"} · ${p.right.act_year ?? ""}`}
                subtitle={p.mapping.mapping_kind === "ipc_to_bns" ? "New (in force 1 Jul 2024)" : "Legacy (repealed)"}
                s={p.right as any}
                badge={/Nyaya|Nagarik|Sakshya/.test(p.right.act_short_title ?? "") ? "New" : "Legacy"}
                badgeStyle={/Nyaya|Nagarik|Sakshya/.test(p.right.act_short_title ?? "")
                  ? "bg-emerald-500/15 text-emerald-200 border-emerald-500/30"
                  : "bg-amber-500/15 text-amber-200 border-amber-500/30"}
              />
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
