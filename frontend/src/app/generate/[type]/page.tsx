"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useLocale } from "@/components/LocaleProvider";
import { Scale, FileText, Download, Loader2, ChevronLeft } from "lucide-react";
import Link from "next/link";
import axios from "axios";

export default function GenericDocGenerator() {
  const { type } = useParams();
  const { t } = useLocale();
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    user_details: "",
    recipient_details: "",
    subject: "",
    facts: "",
    demands: "",
  });

  const getDocTitle = () => {
    switch (type) {
      case "rti": return "RTI Application";
      case "consumer": return "Consumer Complaint";
      case "notice": return "Legal Notice";
      default: return "Legal Document";
    }
  };

  const getFormLabels = () => {
    switch (type) {
      case "rti": return {
        user: "Applicant Details",
        recipient: "Public Information Officer (PIO) Details",
        subject: "Subject / Information Description",
        facts: "Background / Reason for request",
        demands: "Specific Information Points (be precise)"
      };
      case "consumer": return {
        user: "Complainant Details",
        recipient: "Opposite Party (Company/Service Provider)",
        subject: "Subject of Complaint",
        facts: "Facts of the Incident (chronological)",
        demands: "Relief Sought (Refund, Compensation, etc.)"
      };
      case "notice": return {
        user: "Sender Details",
        recipient: "Recipient (Individual/Entity)",
        subject: "Subject of Notice",
        facts: "Grounds for Notice",
        demands: "Specific Demands & Timeframe (e.g. 15 days)"
      };
      default: return { user: "User Details", recipient: "Recipient Details", subject: "Subject", facts: "Facts", demands: "Demands" };
    }
  };

  const labels = getFormLabels();

  const generateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.post("/api/generate/generate", {
        ...form,
        template_type: type
      });
      setDraft(data.draft);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to generate draft. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const downloadAsTxt = () => {
    if (!draft) return;
    const element = document.createElement("a");
    const file = new Blob([draft], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = `${getDocTitle().replace(" ", "_")}_${Date.now()}.txt`;
    document.body.appendChild(element);
    element.click();
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <Link href="/generate" className="p-2 hover:bg-slate-100 rounded-full transition-colors">
            <ChevronLeft className="w-5 h-5 text-slate-600" />
          </Link>
          <div className="flex items-center gap-2.5">
            <Scale className="w-5 h-5 text-slate-800" />
            <h1 className="font-bold text-lg text-slate-900">{getDocTitle()} Generator</h1>
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
                Document Details
              </h2>
              <form onSubmit={generateDraft} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{labels.user}</label>
                  <input
                    type="text" required
                    value={form.user_details}
                    onChange={e => setForm({ ...form, user_details: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                    placeholder="Full name, address, contact"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{labels.recipient}</label>
                  <input
                    type="text" required
                    value={form.recipient_details}
                    onChange={e => setForm({ ...form, recipient_details: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                    placeholder="Name/Title and Office Address"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{labels.subject}</label>
                  <input
                    type="text" required
                    value={form.subject}
                    onChange={e => setForm({ ...form, subject: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                    placeholder="Brief summary of the matter"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{labels.facts}</label>
                  <textarea
                    required rows={5}
                    value={form.facts}
                    onChange={e => setForm({ ...form, facts: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none"
                    placeholder="Detailed chronological facts of your case..."
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">{labels.demands}</label>
                  <textarea
                    rows={3}
                    value={form.demands}
                    onChange={e => setForm({ ...form, demands: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none"
                    placeholder="What specifically do you want? (Information, refund, apology, etc.)"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-slate-900 text-white font-semibold py-2.5 rounded-xl hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                  Generate {getDocTitle()}
                </button>
              </form>
            </div>
          </div>

          {/* Preview Section */}
          <div className="relative">
            {draft ? (
              <div className="bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden flex flex-col h-full max-h-[700px]">
                <div className="bg-slate-50 border-b border-slate-200 px-4 py-3 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Draft Preview</span>
                  <button
                    onClick={downloadAsTxt}
                    className="text-xs text-amber-600 font-semibold flex items-center gap-1 hover:text-amber-700"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download .txt
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto p-8 font-serif text-slate-800 leading-relaxed whitespace-pre-wrap bg-[url('https://www.transparenttextures.com/patterns/paper-fibers.png')]">
                  {draft}
                </div>
              </div>
            ) : (
              <div className="h-full min-h-[400px] border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-center p-8 bg-white/50">
                <FileText className="w-12 h-12 text-slate-200 mb-4" />
                <p className="text-slate-400 text-sm">Generate to see the formal {getDocTitle()} here.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
