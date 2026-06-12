"use client";

import { useLocale } from "@/components/LocaleProvider";
import { FileText, ChevronRight, Scale, Info, ShieldAlert, Book } from "lucide-react";
import Link from "next/link";

const TEMPLATES = [
  { id: "fir", title: "FIR Draft", desc: "Police complaint for criminal incidents like theft, assault, or fraud.", icon: <ShieldAlert className="w-6 h-6 text-red-500" /> },
  { id: "rti", title: "RTI Application", desc: "Request information from government departments under the RTI Act.", icon: <Info className="w-6 h-6 text-blue-500" /> },
  { id: "consumer", title: "Consumer Complaint", desc: "For defective products, poor service, or unfair trade practices.", icon: <Scale className="w-6 h-6 text-amber-500" /> },
  { id: "notice", title: "Legal Notice", desc: "Formal demand letter to an individual or company for recovery or performance.", icon: <FileText className="w-6 h-6 text-slate-500" /> },
];

export default function GenerateHub() {
  const { t } = useLocale();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5">
            <Scale className="w-5 h-5 text-slate-800" />
            <h1 className="font-bold text-lg text-slate-900">Legal Document Generator</h1>
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900 mb-3">Professional Legal Drafting</h2>
          <p className="text-slate-500 max-w-xl mx-auto">
            Choose a template below. Describe your situation and our AI will generate a formal draft formatted for Indian legal procedures.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {TEMPLATES.map(tmp => (
            <Link key={tmp.id} href={tmp.id === "fir" ? "/generate/fir" : `/generate/${tmp.id}`}
              className="bg-white border border-slate-200 rounded-2xl p-6 hover:border-amber-400 hover:shadow-lg transition-all group relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <ChevronRight className="w-5 h-5 text-amber-500" />
              </div>
              <div className="w-12 h-12 bg-slate-50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-amber-50 transition-colors">
                {tmp.icon}
              </div>
              <h3 className="font-bold text-slate-900 mb-2">{tmp.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                {tmp.desc}
              </p>
            </Link>
          ))}
        </div>

        <div className="mt-16 bg-slate-900 rounded-3xl p-8 text-white relative overflow-hidden">
          <div className="relative z-10">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Book className="w-5 h-5 text-amber-400" />
              Need help understanding the law first?
            </h3>
            <p className="text-slate-400 text-sm mb-6 max-w-md">
              Before you draft a document, you can chat with Nyaya to find the exact sections and laws that apply to your case.
            </p>
            <Link href="/" className="inline-flex items-center gap-2 bg-amber-400 text-amber-950 font-bold px-6 py-3 rounded-xl hover:bg-amber-300 transition-colors">
              Go to Chat Assistant
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
          <Scale className="absolute -bottom-10 -right-10 w-64 h-64 text-white/5 rotate-12" />
        </div>
      </main>
    </div>
  );
}
