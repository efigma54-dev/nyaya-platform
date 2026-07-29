import Link from "next/link";
import { api } from "@/lib/api";
import { SectionSummary } from "@/lib/types";

export const dynamic = "force-dynamic";

const STATUS_STYLE: Record<string, string> = {
  in_force: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  repealed: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  superseded: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  partially_repealed: "bg-orange-500/15 text-orange-300 border-orange-500/30",
};

function flag(title: string, on: boolean | null | undefined, positive: boolean) {
  if (on === undefined || on === null) return null;
  const good = positive ? on : !on;
  return (
    <span
      title={title}
      className={`text-[10px] px-2 py-0.5 rounded border ${
        good ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30" :
               "bg-rose-500/10 text-rose-300 border-rose-500/30"
      }`}
    >
      {title}
    </span>
  );
}

function SectionCard({ s }: { s: SectionSummary }) {
  return (
    <Link href={`/section/${s.id}`} className="group glass rounded-xl p-4 hover:shadow-glow transition">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="text-[11px] uppercase tracking-widest text-white/40">
            {s.act_short_title} · Sec {s.section_number}
          </div>
          <div className="mt-1 font-semibold text-white group-hover:text-nyaya-200 transition">{s.title}</div>
        </div>
        {s.act_year && (
          <div className="text-xs text-white/40 whitespace-nowrap">{s.act_year}</div>
        )}
      </div>
      {s.chapter && <div className="mt-1 text-xs text-nyaya-200/80">{s.chapter}</div>}
      {s.plain_language && (
        <p className="mt-3 text-sm text-white/65 line-clamp-2 leading-relaxed">{s.plain_language}</p>
      )}
      {Array.isArray(s.keywords) && s.keywords.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {s.keywords.slice(0, 6).map((k) => (
            <span key={k} className="text-[10px] px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white/60">
              #{k}
            </span>
          ))}
        </div>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-1.5">
        {flag("Cognizable", s.cognizable, true)}
        {flag("Bailable", s.bailable, false)}
        {flag("Compoundable", s.compoundable, true)}
        {s.death_penalty && flag("Death", true, false)}
        {s.life_imprisonment && flag("Life", true, false)}
        {typeof s.imprisonment_max_months === "number" && s.imprisonment_max_months > 0 && (
          <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white/60">
            Max {Math.round(s.imprisonment_max_months / 12)}y
          </span>
        )}
      </div>
    </Link>
  );
}

export default async function CorpusPage() {
  const acts = await api.listActs().catch(() => []);
  const sectionsByAct: Record<number, SectionSummary[]> = {};
  for (const a of acts) {
    sectionsByAct[a.id] = await api.sectionsForAct(a.id).catch(() => []);
  }
  const totalSections = Object.values(sectionsByAct).reduce((n, xs) => n + xs.length, 0);

  return (
    <div className="max-w-7xl mx-auto px-6 py-14">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-10">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-nyaya-300/70">Statutory Corpus</div>
          <h1 className="mt-2 text-4xl font-bold tracking-tight">
            {acts.length} Acts · {totalSections} Sections · 3 codes repealed in 2023
          </h1>
          <p className="mt-3 max-w-3xl text-white/65 leading-relaxed">
            Indian Penal Code (1860), CrPC (1973), Indian Evidence Act (1872) are
            <span className="ml-1 text-amber-300"> superseded</span> by the
            <span className="mx-1"> Bharatiya Nyaya Sanhita 2023, Bharatiya Nagarik Suraksha Sanhita 2023, </span>
            and <span>Bharatiya Sakshya Adhiniyam 2023</span> respectively (in force 1 Jul 2024).
            Click any section to view the plain-language summary, KG, and its IPC↔BNS counterpart.
          </p>
        </div>
        <Link
          href="/search"
          className="self-start md:self-end px-4 py-2 rounded-lg bg-nyaya-600/80 hover:bg-nyaya-600 transition text-white"
        >
          Search the corpus →
        </Link>
      </div>

      <div className="space-y-16">
        {acts.map((a) => (
          <section key={a.id} className="scroll-smooth-section">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-xl font-semibold">{a.short_title}</h2>
                  <span className={`text-xs px-2 py-1 rounded-md border ${STATUS_STYLE[a.status] ?? "bg-white/10 text-white/60 border-white/15"}`}>
                    {a.status.replaceAll("_", " ")}
                  </span>
                  <span className="text-xs text-white/40">{a.act_no ?? `Act of ${a.year}`}</span>
                </div>
                <p className="mt-1 text-sm text-white/55 max-w-3xl">{a.long_title}</p>
              </div>
              <div className="text-sm text-white/60">{sectionsByAct[a.id]?.length ?? 0} sections seeded</div>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(sectionsByAct[a.id] ?? []).map((s) => (
                <SectionCard key={s.id} s={s} />
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
