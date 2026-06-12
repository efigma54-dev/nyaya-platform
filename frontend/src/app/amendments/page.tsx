"use client";

import { useState, useEffect } from "react";
import { useLocale } from "@/components/LocaleProvider";
import { Scale, History, Calendar, ArrowRight, Loader2, Info } from "lucide-react";
import Link from "next/link";
import axios from "axios";

interface Amendment {
  id: number;
  section_number: string;
  act_title: string;
  effective_date: string;
  amendment_act: string;
  notes: string;
  new_text_snippet: string;
}

export default function AmendmentsPage() {
  const { t, lang } = useLocale();
  const [amendments, setAmendments] = useState<Amendment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get("/api/amendments/recent")
      .then(res => {
        setAmendments(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5">
            <Scale className="w-5 h-5 text-slate-800" />
            <h1 className="font-bold text-lg text-slate-900">Amendment Timeline</h1>
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-12">
        <div className="flex items-center gap-4 mb-10">
          <div className="w-12 h-12 bg-amber-100 rounded-2xl flex items-center justify-center">
            <History className="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Recent Legal Changes</h2>
            <p className="text-sm text-slate-500">Track how Indian laws have evolved over time.</p>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-slate-300 animate-spin" />
          </div>
        ) : amendments.length === 0 ? (
          <div className="bg-white border border-dashed border-slate-200 rounded-3xl p-12 text-center">
            <Info className="w-12 h-12 text-slate-200 mx-auto mb-4" />
            <p className="text-slate-400">No recent amendments found in the database.</p>
          </div>
        ) : (
          <div className="space-y-8 relative before:absolute before:left-[19px] before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-200">
            {amendments.map((am) => (
              <div key={am.id} className="relative pl-12">
                <div className="absolute left-0 top-1 w-10 h-10 bg-white border-2 border-slate-200 rounded-full flex items-center justify-center z-10">
                  <Calendar className="w-4 h-4 text-slate-400" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:border-amber-300 transition-colors">
                  <div className="flex items-center justify-between gap-4 mb-4">
                    <span className="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-md">
                      Effective: {am.effective_date}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono uppercase tracking-widest">#{am.id}</span>
                  </div>
                  <h3 className="font-bold text-slate-900 mb-1 flex items-center gap-2">
                    {am.act_title} · § {am.section_number}
                  </h3>
                  <p className="text-xs font-semibold text-slate-500 mb-3">{am.amendment_act}</p>
                  <p className="text-sm text-slate-600 leading-relaxed mb-4 bg-slate-50 p-4 rounded-xl border border-slate-100 italic">
                    "{am.notes}"
                  </p>
                  <div className="flex items-center justify-between">
                    <Link href="/sections" className="text-xs font-bold text-slate-900 flex items-center gap-1 hover:gap-2 transition-all">
                      View Section Details
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
