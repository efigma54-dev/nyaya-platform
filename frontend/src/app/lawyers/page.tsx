"use client";

import { useState, useEffect } from "react";
import { useLocale } from "@/components/LocaleProvider";
import { Scale, Users, MapPin, Briefcase, Star, ShieldCheck, Loader2, MessageSquare, X } from "lucide-react";
import Link from "next/link";
import axios from "axios";

import { getLawyers, type Lawyer } from "@/lib/api";

export default function LawyerDirectory() {
  const { t } = useLocale();
  const [lawyers, setLawyers] = useState<Lawyer[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLawyer, setSelectedLawyer] = useState<Lawyer | null>(null);
  const [inquiryForm, setInquiryForm] = useState({ name: "", phone: "", summary: "" });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    getLawyers()
      .then(data => {
        setLawyers(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleInquiry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLawyer) return;
    setSubmitting(true);
    try {
      // Use centralized api client if we had an inquiry method, 
      // but for now I'll just keep the axios call or add it to api.ts
      await axios.post("/api/lawyers/inquiry", {
        lawyer_id: selectedLawyer.id,
        user_name: inquiryForm.name,
        user_phone: inquiryForm.phone,
        query_summary: inquiryForm.summary
      });
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setSelectedLawyer(null);
        setInquiryForm({ name: "", phone: "", summary: "" });
      }, 3000);
    } catch (err) {
      alert("Failed to send inquiry. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5">
            <Scale className="w-5 h-5 text-slate-800" />
            <h1 className="font-bold text-lg text-slate-900">{t.lawyers.title}</h1>
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-12">
        <div className="mb-10">
          <h2 className="text-3xl font-bold text-slate-900 mb-2">{t.lawyers.title}</h2>
          <p className="text-slate-500">{t.lawyers.subtitle}</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-slate-300 animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {lawyers.map((l) => (
              <div key={l.id} className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center">
                    <Users className="w-8 h-8 text-slate-400" />
                  </div>
                  {l.is_verified && (
                    <div className="bg-green-50 text-green-700 text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1 border border-green-100">
                      <ShieldCheck className="w-3 h-3" />
                      {t.lawyers.verified}
                    </div>
                  )}
                </div>
                <h3 className="font-bold text-slate-900 text-lg mb-1">{l.full_name}</h3>
                <p className="text-amber-600 text-sm font-semibold mb-4">{l.specialization}</p>
                
                <div className="space-y-2 mb-6">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <MapPin className="w-3.5 h-3.5" />
                    {l.location}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Briefcase className="w-3.5 h-3.5" />
                    {l.experience_years}+ {t.lawyers.exp}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-amber-500 font-bold">
                    <Star className="w-3.5 h-3.5 fill-amber-500" />
                    {l.rating?.toFixed(1) || "5.0"} / 5.0
                  </div>
                </div>

                <p className="text-sm text-slate-600 line-clamp-3 mb-6 leading-relaxed italic">
                  "{l.bio || "Verified legal expert ready to assist."}"
                </p>

                <button
                  onClick={() => setSelectedLawyer(l)}
                  className="w-full bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-slate-800 transition-colors flex items-center justify-center gap-2"
                >
                  <MessageSquare className="w-4 h-4" />
                  {t.lawyers.connect}
                </button>
              </div>
            ))}
          </div>
        )}
      </main>


      {/* Inquiry Modal */}
      {selectedLawyer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="bg-white rounded-3xl w-full max-w-md p-8 relative shadow-2xl animate-in fade-in zoom-in duration-200">
            <button onClick={() => setSelectedLawyer(null)} className="absolute top-6 right-6 p-2 hover:bg-slate-100 rounded-full">
              <X className="w-5 h-5 text-slate-400" />
            </button>

            {success ? (
              <div className="py-12 text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <ShieldCheck className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{t.lawyers.successTitle}</h3>
                <p className="text-slate-500 text-sm">{t.lawyers.successBody}</p>
              </div>
            ) : (
              <>
                <h2 className="text-xl font-bold text-slate-900 mb-1">{t.lawyers.modalTitle}</h2>
                <p className="text-slate-500 text-sm mb-6">{t.lawyers.modalSubtitle}</p>

                <form onSubmit={handleInquiry} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">{t.lawyers.formName}</label>
                    <input
                      type="text" required
                      value={inquiryForm.name}
                      onChange={e => setInquiryForm({ ...inquiryForm, name: e.target.value })}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">{t.lawyers.formPhone}</label>
                    <input
                      type="tel" required
                      value={inquiryForm.phone}
                      onChange={e => setInquiryForm({ ...inquiryForm, phone: e.target.value })}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">{t.lawyers.formSummary}</label>
                    <textarea
                      required rows={4}
                      value={inquiryForm.summary}
                      onChange={e => setInquiryForm({ ...inquiryForm, summary: e.target.value })}
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full bg-amber-400 text-amber-950 font-bold py-3 rounded-xl hover:bg-amber-300 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : t.lawyers.formSubmit}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
