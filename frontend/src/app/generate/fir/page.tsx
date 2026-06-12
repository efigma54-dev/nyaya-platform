"use client";

import { useState } from "react";
import { useLocale } from "@/components/LocaleProvider";
import { Scale, FileText, Download, Loader2, AlertTriangle, ChevronLeft } from "lucide-react";
import Link from "next/link";
import { generateDocument } from "@/lib/api";
import axios from "axios";

export default function FIRGenerator() {
  const { t, lang } = useLocale();
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    complainant_name: "",
    incident_date: "",
    incident_place: "",
    accused_details: "",
    narrative: "",
  });

  const generateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await generateDocument("fir", form);
      if (!result?.draft?.trim()) {
        setError("No draft returned from the server. Check GEMINI_API_KEY / GROQ_API_KEY in .env.");
        return;
      }
      setDraft(result.draft);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        setError(
          typeof detail === "string"
            ? detail
            : err.response?.status === 404
              ? "FIR endpoint not found — rebuild API and frontend."
              : err.message || "Failed to generate draft."
        );
      } else {
        setError(err instanceof Error ? err.message : "Failed to generate draft. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const downloadAsTxt = () => {
    if (!draft) return;
    const element = document.createElement("a");
    const file = new Blob([draft], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = `FIR_Draft_${Date.now()}.txt`;
    document.body.appendChild(element);
    element.click();
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 hover:bg-slate-100 rounded-full transition-colors">
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </Link>
          <div className="flex items-center gap-2.5">
            <Scale className="w-5 h-5 text-slate-800" />
            <h1 className="font-bold text-lg text-slate-900">{t.fir.title}</h1>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <h2 className="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
                <FileText className="w-4 h-4 text-amber-500" />
                {t.fir.subtitle}
              </h2>
              <form onSubmit={generateDraft} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{t.fir.formComplainant}</label>
                  <input
                    type="text"
                    required
                    value={form.complainant_name}
                    onChange={e => setForm({ ...form, complainant_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">{t.fir.formDate}</label>
                    <input
                      type="date"
                      required
                      value={form.incident_date}
                      onChange={e => setForm({ ...form, incident_date: e.target.value })}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">{t.fir.formPlace}</label>
                    <input
                      type="text"
                      required
                      value={form.incident_place}
                      onChange={e => setForm({ ...form, incident_place: e.target.value })}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{t.fir.formAccused}</label>
                  <input
                    type="text"
                    value={form.accused_details}
                    onChange={e => setForm({ ...form, accused_details: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{t.fir.formNarrative}</label>
                  <textarea
                    required
                    rows={6}
                    value={form.narrative}
                    onChange={e => setForm({ ...form, narrative: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-slate-900 text-white font-semibold py-2.5 rounded-xl hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                  {t.fir.formSubmit}
                </button>
              </form>
            </div>
            
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
              <p className="text-xs text-amber-800 leading-relaxed">
                {t.fir.disclaimer}
              </p>
            </div>

            {error && (
              <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                {error}
              </div>
            )}
          </div>

          {/* Preview Section */}
          <div className="relative">
            {draft ? (
              <div className="bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden flex flex-col h-full max-h-[700px]">
                <div className="bg-slate-50 border-b border-slate-200 px-4 py-3 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">{t.fir.preview}</span>
                  <button
                    onClick={downloadAsTxt}
                    className="text-xs text-amber-600 font-semibold flex items-center gap-1 hover:text-amber-700"
                  >
                    <Download className="w-3.5 h-3.5" />
                    {t.fir.download}
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto p-8 font-serif text-slate-800 leading-relaxed whitespace-pre-wrap bg-[url('https://www.transparenttextures.com/patterns/paper-fibers.png')]">
                  {draft}
                </div>
              </div>
            ) : (
              <div className="h-full min-h-[400px] border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-center p-8 bg-white/50">
                <FileText className="w-12 h-12 text-slate-200 mb-4" />
                <p className="text-slate-400 text-sm">Fill in the details and generate to see the formal FIR draft here.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
