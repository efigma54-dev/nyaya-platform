import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Nyaya AI — Legal Statutory Corpus Platform",
  description:
    "Indian statutory corpus with hybrid search (BM25 + BGE-M3 + cross-encoder), bidirectional IPC ↔ BNS mappings, knowledge graph, and benchmark harness.",
};

const NAV = [
  { href: "/", label: "Home" },
  { href: "/corpus", label: "Corpus" },
  { href: "/search", label: "Search" },
  { href: "/compare", label: "IPC ↔ BNS" },
  { href: "/benchmark", label: "Benchmark" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased font-sans">
        <div className="min-h-screen flex flex-col">
          <header className="sticky top-0 z-40 border-b border-white/5 bg-[#0b0818]/80 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
              <Link href="/" className="flex items-center gap-3 group">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-nyaya-500 to-sky-500 shadow-glow grid place-items-center font-black">
                  ন্যায়
                </div>
                <div className="leading-tight">
                  <div className="font-semibold tracking-tight text-white/95 group-hover:text-white">Nyaya AI</div>
                  <div className="text-[11px] uppercase tracking-widest text-nyaya-300/80">
                    Legal Corpus Platform
                  </div>
                </div>
              </Link>
              <nav className="hidden md:flex items-center gap-1 text-sm">
                {NAV.map((n) => (
                  <Link
                    key={n.href}
                    href={n.href}
                    className="px-3 py-2 rounded-lg text-white/70 hover:text-white hover:bg-white/5 transition"
                  >
                    {n.label}
                  </Link>
                ))}
              </nav>
              <div className="flex items-center gap-2">
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs px-3 py-2 rounded-lg border border-nyaya-500/30 bg-nyaya-500/10 text-nyaya-200 hover:bg-nyaya-500/20 transition"
                >
                  API Docs <span className="kbd ml-1">↗</span>
                </a>
              </div>
            </div>
          </header>
          <main className="flex-1">{children}</main>
          <footer className="border-t border-white/5 mt-24">
            <div className="max-w-7xl mx-auto px-6 py-8 text-xs text-white/40 flex flex-col sm:flex-row gap-4 sm:items-center sm:justify-between">
              <div>© {new Date().getFullYear()} Nyaya AI Engineering. v0.1.0.</div>
              <div className="flex items-center gap-4">
                <span>Stack: FastAPI · SQLAlchemy · Postgres · Qdrant · Redis · BGE-M3 · Next.js 14</span>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
