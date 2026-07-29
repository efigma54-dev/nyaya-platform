"use client";

import clsx from "clsx";

type Props = {
  text: string;
  query?: string | null;
  validated?: boolean | null;
  similarity?: number | null;
  className?: string;
};

function normalize(s: string) {
  return s.toLowerCase().replace(/[\s\n\r\t\.\(\)\[\],;:!?।\-—'"]+/g, " ").trim();
}

export default function CitationHighlight({ text, query, validated, similarity, className }: Props) {
  const rendered = (() => {
    if (!query) return text;
    const qtoks = Array.from(new Set(normalize(query).split(" ").filter((t) => t.length >= 3)));
    if (qtoks.length === 0) return text;
    const escaped = qtoks.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const re = new RegExp(`(${escaped.join("|")})`, "gi");
    const parts = text.split(re);
    return parts.map((p, i) => {
      const match = re.test(p);
      re.lastIndex = 0;
      const isMatch = match;
      const hlClass =
        validated === true ? "hl-valid" :
        validated === false ? "hl-invalid" : "hl";
      return isMatch ? <mark key={i} className={hlClass}>{p}</mark> : <span key={i}>{p}</span>;
    });
  })();

  return (
    <div className={clsx("relative", className)}>
      {similarity !== null && similarity !== undefined && (
        <div className="absolute top-0 right-0 text-[10px] text-white/30 font-mono">
          cite-sim {(similarity * 100).toFixed(0)}%
        </div>
      )}
      <div className="markdown-body text-[15px] text-white/85 leading-relaxed">{rendered}</div>
    </div>
  );
}
