"use client";

import { useMemo } from "react";
import { KGSubgraph } from "@/lib/types";
import Link from "next/link";

export default function KGVisualization({ subgraph, rootId }: { subgraph: KGSubgraph; rootId: number }) {
  const positions = useMemo(() => {
    const nodes = subgraph.nodes;
    const n = nodes.length;
    if (n === 0) return {} as Record<number, { x: number; y: number }>;
    const cx = 360, cy = 260;
    const ring1 = 140;
    const ring2 = 220;
    const pos: Record<number, { x: number; y: number }> = {};
    const rootIdx = nodes.findIndex((nd) => nd.id === rootId);
    const others = [...nodes.slice(0, rootIdx), ...nodes.slice(rootIdx + 1)];
    pos[rootId] = { x: cx, y: cy };
    others.forEach((nd, i) => {
      const total = others.length;
      const angle = (i / total) * Math.PI * 2 - Math.PI / 2;
      const r = i % 2 === 0 ? ring1 : ring2;
      pos[nd.id] = { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r };
    });
    return pos;
  }, [subgraph, rootId]);

  const kindColor: Record<string, string> = {
    replaces: "#f43f5e",
    replaced_by: "#f43f5e",
    amended_by: "#f59e0b",
    interpreted_by: "#a78bfa",
    cited_in: "#38bdf8",
    related_section: "#34d399",
    analogous_to: "#fb923c",
  };

  return (
    <div className="glass rounded-2xl p-5 overflow-hidden">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">Knowledge Graph (depth=2)</h3>
        <div className="text-xs text-white/50">{subgraph.nodes.length} nodes · {subgraph.edges.length} edges</div>
      </div>
      <svg viewBox="0 0 720 520" className="w-full h-[520px] bg-[#120b26] rounded-xl border border-white/5">
        <defs>
          {Object.entries(kindColor).map(([k, c]) => (
            <marker key={k} id={`arrow-${k}`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill={c} />
            </marker>
          ))}
        </defs>
        {subgraph.edges.map((e, i) => {
          const a = positions[e.source_section_id];
          const b = positions[e.target_section_id];
          if (!a || !b) return null;
          const color = kindColor[e.relation_type] ?? "#ffffff55";
          const mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - Math.hypot(b.x - a.x, b.y - a.y) * 0.1 };
          const d = `M ${a.x} ${a.y} Q ${mid.x} ${mid.y} ${b.x} ${b.y}`;
          return (
            <g key={i}>
              <path d={d} stroke={color} strokeWidth={e.weight ? 1 + e.weight : 1.5} fill="none" opacity={0.75}
                markerEnd={`url(#arrow-${e.relation_type})`} />
              <title>{e.relation_type} — {e.evidence ?? ""}</title>
            </g>
          );
        })}
        {subgraph.nodes.map((n) => {
          const p = positions[n.id];
          if (!p) return null;
          const isRoot = n.id === rootId;
          return (
            <g key={n.id}>
              <circle cx={p.x} cy={p.y} r={isRoot ? 26 : 18} fill={isRoot ? "#7d4bff" : "#241b42"}
                stroke={isRoot ? "#c4b5fd" : "#ffffff30"} strokeWidth={isRoot ? 2 : 1} />
              <text x={p.x} y={p.y + 4} textAnchor="middle" fontSize={isRoot ? 13 : 10} fill="#fff" fontWeight={isRoot ? 700 : 500}>
                Sec {n.section_number}
              </text>
              <text x={p.x} y={p.y + 22} textAnchor="middle" fontSize={8} fill="#ffffff80" maxWidth={80}>
                {truncate(n.act_short_title ?? "", 28)}
              </text>
              <Link href={`/section/${n.id}`} style={{ cursor: "pointer" }}>
                <title>{n.act_short_title} § {n.section_number} — {n.title}</title>
                <circle cx={p.x} cy={p.y} r={isRoot ? 30 : 22} fill="transparent" />
              </Link>
            </g>
          );
        })}
      </svg>
      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
        {Object.entries(kindColor).map(([k, c]) => (
          <span key={k} className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-white/5 border border-white/10">
            <span className="w-2 h-2 rounded-full" style={{ background: c }} />
            {k}
          </span>
        ))}
      </div>
    </div>
  );
}

function truncate(s: string, n: number) {
  return s.length <= n ? s : s.slice(0, n - 1) + "…";
}
