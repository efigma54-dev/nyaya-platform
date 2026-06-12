"use client";
import { useLocale } from "./LocaleProvider";

interface Props {
  onSelectQuery: (query: string) => void;
}

export default function CategoryGrid({ onSelectQuery }: Props) {
  const { t } = useLocale();
  
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6">
      <p className="text-sm font-semibold text-slate-700 text-center mb-1">
        {t.categoryGrid.title}
      </p>
      <p className="text-xs text-slate-400 text-center mb-5" 
         dangerouslySetInnerHTML={{ __html: t.categoryGrid.subtitleHtml }} />
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Object.entries(t.categoryGrid.cats).map(([id, cat]) => (
          <button
            key={id}
            type="button"
            onClick={() => onSelectQuery(cat.example)}
            className="text-left p-3 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all duration-150 cursor-pointer group"
          >
            <div className="text-xl mb-2">{getCategoryIcon(id)}</div>
            <div className="font-medium text-sm text-slate-800 mb-0.5">{cat.label}</div>
            <div className="text-xs text-slate-500 mb-2 leading-snug">{cat.desc}</div>
            <div className="text-xs text-slate-400 group-hover:text-slate-600 font-medium uppercase tracking-wide">
              {t.categoryGrid.insertCta}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function getCategoryIcon(id: string): string {
  switch (id) {
    case "criminal": return "⚖️";
    case "constitutional": return "📜";
    case "consumer": return "🛒";
    case "family": return "👨👩👧";
    case "property": return "🏠";
    case "labour": return "💼";
    case "cyber": return "💻";
    default: return "📚";
  }
}

