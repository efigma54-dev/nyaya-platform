"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { sendChatQuery, streamChatQuery, type StreamEvent, saveSection, saveQuery } from "@/lib/api";
import { type SectionCard } from "@/lib/api";
import { useLocale } from "@/components/LocaleProvider";
import CategoryGrid from "@/components/CategoryGrid";
import SiteLanguageToggle from "@/components/SiteLanguageToggle";
import { MessageCircle, Menu, X, Scale, ExternalLink, FileText, History, Users, BarChart3, BookOpen, Send, Loader2, AlertTriangle, ChevronRight, Info, Mic, MicOff, User, Library, Bookmark, Share2 } from "lucide-react";
import Link from "next/link";
import { generateSessionId } from "@/lib/utils";
import EmergencyBanner from "@/components/EmergencyBanner";
import ChatMarkdown from "@/components/ChatMarkdown";
import { useAuth } from "@/lib/auth";
import AuthModal from "@/components/auth/AuthModal";
import { getCategoryColor, getCategoryLabel } from "@/lib/utils";
import axios from "axios";

// ── Types ────────────────────────────────────────────────────
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
  sections?: SectionCard[];
  webSources?: any[];
  judgments?: any[];
  emergency?: any;
  category?: string | null;
  provider?: string;
  lowConfidence?: boolean;
  ipcBnsNote?: boolean;
  responseTimeMs?: number;
  lang?: string;
}

function getSessionId(): string {
  if (typeof window === "undefined") return generateSessionId();
  const key = "nyaya_session";
  const existing = sessionStorage.getItem(key);
  if (existing) return existing;
  const id = generateSessionId();
  sessionStorage.setItem(key, id);
  return id;
}

export default function Home() {
  const { t, lang } = useLocale();
  const { user, token, logout } = useAuth();
  const [authOpen, setAuthOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [summaries, setSummaries] = useState<Record<string, string>>({});
  const [summarizing, setSummarizing] = useState<string | null>(null);

  const handleSummarize = async (url: string, text: string) => {
    setSummarizing(url);
    try {
      const { data } = await axios.post("/api/kanoon/summarize", { text });
      setSummaries(prev => ({ ...prev, [url]: data.summary }));
    } catch (err) {
      console.error("Summarization failed", err);
    } finally {
      setSummarizing(null);
    }
  };
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const sessionId = useRef<string>("");

  useEffect(() => { sessionId.current = getSessionId(); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  }, [input]);

  const handleSelectExample = (query: string) => {
    setInput(query);
    // Focus textarea after selection
    setTimeout(() => textareaRef.current?.focus(), 100);
  };

  const handleStreamEvent = useCallback((event: StreamEvent, msgId: string, startTime: number) => {
    setMessages(prev => prev.map(m => {
      if (m.id !== msgId) return m;
      switch (event.type) {
        case "emergency": return { ...m, emergency: event.data };
        case "sections": return { ...m, sections: event.data };
        case "meta": return {
          ...m,
          category: event.data.category,
          provider: event.data.provider,
          lowConfidence: event.data.low_confidence,
          webSources: event.data.web_sources,
          judgments: event.data.judgments
        };
        case "token": return { ...m, content: m.content + event.data };
        case "done": return { ...m, streaming: false, responseTimeMs: Date.now() - startTime, ipcBnsNote: event.data?.ipc_bns_note };
        case "error": return { ...m, content: "Error: " + event.data, streaming: false };
        default: return m;
      }
    }));
  }, []);

  const sendMessage = useCallback(async (queryText?: string) => {
    const query = (queryText || input).trim();
    if (!query || streaming) return;
    setInput("");
    setError(null);

    const userMsgId = `u_${Date.now()}`;
    const asstMsgId = `a_${Date.now()}`;
    setMessages(prev => [...prev,
      { id: userMsgId, role: "user", content: query },
      { id: asstMsgId, role: "assistant", content: "", streaming: true, lang },
    ]);
    setStreaming(true);
    const startTime = Date.now();

    try {
      try {
        for await (const event of streamChatQuery(query, sessionId.current, lang)) {
          handleStreamEvent(event, asstMsgId, startTime);
        }
      } catch {
        const data = await sendChatQuery(query, sessionId.current, lang);
        const anyData = data as any;
        setMessages(prev => prev.map(m => m.id === asstMsgId ? {
          ...m, content: data.answer, sections: data.sections,
          category: data.category, provider: data.ai_provider,
          emergency: data.emergency, lowConfidence: data.low_confidence,
          webSources: anyData.web_sources,
          judgments: anyData.judgments,
          responseTimeMs: data.response_time_ms, streaming: false,
        } : m));
      }
    } catch (err: any) {
      console.error("Chat error:", err);
      const isConnectionError = err.message?.includes("connect") || err.message?.includes("Network Error");
      setError(isConnectionError 
        ? "The Nyaya API is currently offline. Please ensure the backend services are running."
        : (err.response?.data?.detail || err.message || "Something went wrong. Please try again."));
      setMessages(prev => prev.filter(m => m.id !== asstMsgId));
    } finally {
      setStreaming(false);
      setMessages(prev => prev.map(m => m.id === asstMsgId ? { ...m, streaming: false } : m));
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
  }, [input, streaming, handleStreamEvent, lang]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const OFFICIAL_SOURCES = [
    { label: "Constitution of India (official text)", url: "https://legislative.gov.in/constitution-of-india/" },
    { label: "India Code — central Bare Acts", url: "https://www.indiacode.nic.in/" },
    { label: "Supreme Court of India — judgments", url: "https://main.sci.gov.in/" },
    { label: "eCourts / High Court portals", url: "https://ecourts.gov.in/" },
    { label: "Law Commission of India — reports", url: "https://lawcommissionofindia.nic.in/" },
  ];

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* ── Mobile sidebar overlay ── */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/60"
          onClick={() => setSidebarOpen(false)}
        >
          <div
            className="w-72 h-full bg-slate-900 flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
              <div className="flex items-center gap-2">
                <Scale className="w-4 h-4 text-amber-400" />
                <span className="font-semibold text-white text-sm">{t.nav.brand}</span>
              </div>
              <button
                type="button"
                onClick={() => setSidebarOpen(false)}
                className="text-slate-400 hover:text-white"
                aria-label={lang === "hi" ? "साइडबार बंद करें" : "Close sidebar"}
                title={lang === "hi" ? "साइडबार बंद करें" : "Close sidebar"}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
              <p className="text-xs text-slate-400 leading-relaxed">
                {t.home.heroLead}
              </p>
              <div className="pt-2 border-t border-slate-700/50">
                <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider">{t.references.officialHeading}</p>
                {OFFICIAL_SOURCES.map(src => (
                  <a key={src.url} href={src.url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-2 text-xs text-slate-500 hover:text-slate-300 py-1.5 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3 shrink-0" />
                    {src.label}
                  </a>
                ))}
              </div>
            </div>

            <div className="px-4 py-3 border-t border-slate-700/50 flex flex-col gap-3">
              <Link href="/generate" className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5" onClick={() => setSidebarOpen(false)}>
                <FileText className="w-3.5 h-3.5 text-amber-400" />
                Legal Document Generator
              </Link>
              <Link href="/lawyers" className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5" onClick={() => setSidebarOpen(false)}>
                <Users className="w-3.5 h-3.5 text-green-400" />
                Verified Lawyer Directory
              </Link>
              <Link href="/admin/analytics" className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5" onClick={() => setSidebarOpen(false)}>
                <BarChart3 className="w-3.5 h-3.5 text-purple-400" />
                Analytics Dashboard
              </Link>
              <Link href="/sections" className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5" onClick={() => setSidebarOpen(false)}>
                <BookOpen className="w-3.5 h-3.5" />
                {t.nav.browseLaws}
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* ── Left Sidebar (Desktop) ── */}
      <aside className="w-72 bg-slate-900 text-white hidden md:flex md:flex-col shrink-0">
        <div className="px-6 py-5 border-b border-slate-700/50">
          <div className="flex items-center gap-2.5 mb-1">
            <div className="w-7 h-7 bg-white/10 rounded-lg flex items-center justify-center">
              <Scale className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-base tracking-tight">{t.nav.brand}</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">{t.home.heroTitle}</p>
        </div>

        <div className="px-5 py-4 border-b border-slate-700/50">
          <p className="text-xs text-slate-400 mb-3">{t.home.heroLead}</p>
          <div className="flex flex-wrap gap-2 mt-4">
            {[t.home.trustPill1, t.home.trustPill2].map(tag => (
              <span key={tag} className="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full">{tag}</span>
            ))}
          </div>
        </div>

        <div className="px-5 py-4 flex-1 overflow-y-auto space-y-4">
          <Link href="/generate" className="flex items-center gap-3 text-xs text-slate-400 hover:text-white transition-colors group">
            <FileText className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
            Document Generator
          </Link>
          <Link href="/lawyers" className="flex items-center gap-3 text-xs text-slate-400 hover:text-white transition-colors group">
            <Users className="w-4 h-4 text-green-400 group-hover:scale-110 transition-transform" />
            Lawyer Directory
          </Link>
          <Link href="/sections" className="flex items-center gap-3 text-xs text-slate-400 hover:text-white transition-colors group">
            <BookOpen className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
            Browse Bare Acts
          </Link>
        </div>

        <div className="px-5 py-4 border-t border-slate-700/50">
          <Link href="/admin/analytics" className="flex items-center gap-3 text-xs text-slate-500 hover:text-slate-300 transition-colors">
            <BarChart3 className="w-3.5 h-3.5" />
            Admin Analytics
          </Link>
        </div>

        <div className="mt-auto px-5 pt-6 pb-12 border-t border-slate-700/50 bg-slate-900/40">
          {user ? (
            <div className="space-y-3">
              <Link href="/dashboard" className="flex items-center justify-between p-2.5 bg-slate-800 rounded-xl hover:bg-slate-700 transition-all group border border-slate-700/50">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center text-slate-900 font-bold text-xs">
                    {user.full_name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-[10px] font-bold text-white truncate w-24">{user.full_name}</p>
                    <p className="text-[9px] text-slate-400">Dashboard</p>
                  </div>
                </div>
                <ChevronRight className="w-3 h-3 text-slate-500 group-hover:translate-x-1 transition-transform" />
              </Link>
              <button onClick={logout} className="w-full text-left px-2 text-[9px] font-bold text-red-500 hover:text-red-400 uppercase tracking-widest transition-colors">
                Sign Out
              </button>
            </div>
          ) : (
            <button 
              onClick={() => setAuthOpen(true)}
              className="w-full flex items-center gap-3 p-3 bg-white text-slate-900 rounded-xl font-bold shadow-lg hover:bg-slate-100 transition-all active:scale-[0.98]"
            >
              <User className="w-3.5 h-3.5" />
              <span className="text-xs">Sign In</span>
            </button>
          )}
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-slate-200 px-4 h-12 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="md:hidden w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100"
              aria-label={lang === "hi" ? "साइडबार खोलें" : "Open sidebar"}
              title={lang === "hi" ? "साइडबार खोलें" : "Open sidebar"}
            >
              <Menu className="w-4 h-4 text-slate-700" />
            </button>
            <div className="hidden md:flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${streaming ? "bg-amber-500 animate-pulse" : "bg-green-500"}`} />
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{streaming ? "Processing..." : "System Live"}</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <SiteLanguageToggle surface="light" />
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="max-w-3xl mx-auto px-4 py-8">
              <div className="text-center mb-8">
                <h1 className="text-2xl font-bold text-slate-900 mb-2">{t.home.heroTitle}</h1>
                <p className="text-sm text-slate-500 max-w-xl mx-auto">{t.home.heroLead}</p>
              </div>

              <CategoryGrid onSelectQuery={handleSelectExample} />

              <div className="mt-8 bg-white border border-slate-200 rounded-2xl p-5">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Official Portals</p>
                <div className="space-y-3">
                  {OFFICIAL_SOURCES.slice(0, 3).map(src => (
                    <a key={src.url} href={src.url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center justify-between group"
                    >
                      <span className="text-sm text-slate-600 group-hover:text-slate-900 transition-colors">{src.label.split(" (")[0]}</span>
                      <ExternalLink className="w-3.5 h-3.5 text-slate-300 group-hover:text-slate-500" />
                    </a>
                  ))}
                </div>
              </div>
            </div>
          ) : (

            /* Messages */
            <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
              {messages.map(msg => (
                <MessageBubble 
                  key={msg.id} 
                  message={msg} 
                  summaries={summaries}
                  summarizing={summarizing}
                  onSummarize={handleSummarize}
                  onAuthOpen={() => setAuthOpen(true)}
                  onSaveSection={async (sec) => {
                    if (token) await saveSection(token, sec);
                  }}
                  onSaveQuery={async (q, a) => {
                    if (token) await saveQuery(token, q, a);
                  }}
                />
              ))}
              {streaming && messages[messages.length - 1]?.content === "" && (
                <div className="flex items-center gap-2 text-slate-400 text-sm">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {t.home.loadingLine}
                </div>
              )}
              {error && (
                <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-sm text-red-600">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  {error}
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div id="nyaya-chat" className="bg-white border-t border-slate-200 px-4 py-3 shrink-0">
          <div className="max-w-3xl mx-auto">
            {messages.length > 0 && (
              <button type="button" onClick={() => { setMessages([]); setError(null); }}
                className="text-xs text-slate-400 hover:text-slate-600 mb-2 block">
                ← {t.home.newChat}
              </button>
            )}
            <div className="flex gap-2 items-end">
              <textarea id="nyaya-chat-input" ref={textareaRef} value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={messages.length > 0 ? t.home.composerPlaceholderFollowUp : t.home.composerPlaceholderEmpty}
                rows={1} disabled={streaming}
                className="flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:border-slate-300 focus:outline-none px-3 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 disabled:opacity-50 transition-colors"
              />
              <button type="button" onClick={() => sendMessage()}
                disabled={!input.trim() || streaming}
                className="w-10 h-10 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center shrink-0 transition-colors"
              >
                {streaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
              <VoiceButton onTranscript={(text) => setInput(prev => prev + " " + text)} />
            </div>
            <p className="text-xs text-slate-400 mt-2 text-center">
              {messages.length > 0 ? t.home.composerHintActive : t.home.composerHintEmpty}
            </p>
          </div>
        </div>
      </main>


      <AuthModal 
        isOpen={authOpen} 
        onClose={() => setAuthOpen(false)} 
      />
    </div>
  );
}

interface MessageBubbleProps {
  message: Message;
  summaries: Record<string, string>;
  summarizing: string | null;
  onSummarize: (url: string, text: string) => Promise<void>;
  onAuthOpen: () => void;
  onSaveSection: (section: SectionCard) => Promise<void>;
  onSaveQuery: (query: string, answer: string) => Promise<void>;
}

function sortSectionsForDisplay(
  sections: SectionCard[],
  emergency?: { type?: string } | null
): SectionCard[] {
  if (emergency?.type !== "domestic_violence") return sections;
  return [...sections].sort((a, b) => {
    const aPwdva = (a.act_title || "").toLowerCase().includes("domestic violence") ? 1 : 0;
    const bPwdva = (b.act_title || "").toLowerCase().includes("domestic violence") ? 1 : 0;
    return bPwdva - aPwdva;
  });
}

function MessageBubble({ message, summaries, summarizing, onSummarize, onAuthOpen, onSaveSection, onSaveQuery }: MessageBubbleProps) {
  const { t, lang } = useLocale();
  const { user } = useAuth();
  const [emergencyDismissed, setEmergencyDismissed] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set());
  const displaySections = message.sections
    ? sortSectionsForDisplay(message.sections, message.emergency)
    : [];

  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="bg-slate-800 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm max-w-[80%] leading-relaxed">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {message.emergency && !emergencyDismissed && (
        <EmergencyBanner emergency={message.emergency} onDismiss={() => setEmergencyDismissed(true)} />
      )}

      {(message.content || message.streaming) && (
        <div className="bg-white border border-slate-200 rounded-2xl px-5 py-4 shadow-sm">
          <div className="text-sm text-slate-700 leading-relaxed">
            <ChatMarkdown content={message.content} />
            {message.streaming && (
              <span className="inline-block w-0.5 h-4 bg-slate-400 animate-pulse ml-0.5 align-text-bottom" />
            )}
          </div>
          {!message.streaming && message.content && (
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 flex-wrap gap-2">
              <div className="flex items-center gap-2 flex-wrap">
                {message.category && (
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${getCategoryColor(message.category)}`}>
                    {getCategoryLabel(message.category)}
                  </span>
                )}
                {message.responseTimeMs && (
                  <span className="text-xs text-slate-400">{(message.responseTimeMs / 1000).toFixed(1)}s</span>
                )}
                {message.provider && (
                  <span className="text-xs text-slate-400">· {message.provider}</span>
                )}
              </div>
              <div className="flex items-center gap-3">
                <button 
                  onClick={() => {
                    const text = `${message.content}\n\nGenerated by Nyaya Platform`;
                    if (navigator.share) navigator.share({ title: "Nyaya Legal Advice", text });
                    else {
                      navigator.clipboard.writeText(text);
                      alert("Copied to clipboard!");
                    }
                  }}
                  className="text-[10px] text-slate-400 hover:text-blue-600 font-bold flex items-center gap-1"
                >
                  <Share2 className="w-3 h-3" />
                  {lang === "hi" ? "साझा करें" : "Share"}
                </button>
                <button 
                  onClick={() => {
                    if (!user) onAuthOpen();
                    else onSaveQuery(message.content, message.content);
                  }}
                  className="text-[10px] text-slate-400 hover:text-slate-600 font-bold flex items-center gap-1"
                >
                  <Bookmark className="w-3 h-3" />
                  {lang === "hi" ? "जवाब सहेजें" : "Save Answer"}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {message.lowConfidence && !message.streaming && (
        <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-xs text-amber-700">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
          {lang === "hi" ? "सीमित डेटाबेस कवरेज — योग्य वकील के साथ सत्यापित करें।" : "Limited database coverage — verify with a qualified lawyer."}
        </div>
      )}

      {message.ipcBnsNote && !message.streaming && (
        <div className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 text-xs text-blue-700">
          <Info className="w-3.5 h-3.5 shrink-0" />
          {lang === "hi" ? "दिखाई गई IPC धाराएं BNS 2023 समकक्ष (1 जुलाई, 2024 से प्रभावी) शामिल हैं" : "IPC sections shown include BNS 2023 equivalents (effective July 1, 2024)"}
        </div>
      )}

      {displaySections.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-2 ml-1">
            {displaySections.length} {displaySections.length === 1 ? t.chat.sectionsFoundOne : t.chat.sectionsFound}:
          </p>
          <div className="space-y-2">
            {displaySections.slice(0, 5).map((section, i) => (
              <div key={i} className="bg-white border border-slate-200 rounded-xl p-4 hover:border-slate-300 transition-colors">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs border border-slate-300 rounded px-1.5 py-0.5 text-slate-600">
                      § {section.section_number}
                    </span>
                    {section.is_bailable === false && (
                      <span className="text-xs bg-red-100 text-red-700 border border-red-200 rounded-full px-2 py-0.5">{lang === "hi" ? "गैर-जमानती" : "Non-Bailable"}</span>
                    )}
                    {section.is_bailable === true && (
                      <span className="text-xs bg-green-100 text-green-700 border border-green-200 rounded-full px-2 py-0.5">{lang === "hi" ? "जमानती" : "Bailable"}</span>
                    )}
                    {section.is_cognizable === true && (
                      <span className="text-xs bg-orange-100 text-orange-700 border border-orange-200 rounded-full px-2 py-0.5">{lang === "hi" ? "संज्ञेय" : "Cognizable"}</span>
                    )}
                  </div>
                  <span className="text-xs text-slate-400 shrink-0">#{i + 1}</span>
                </div>
                <p className="text-xs text-slate-500 mb-1">{section.act_title}</p>
                {section.section_title && (
                  <p className="font-medium text-sm text-slate-800 mb-2">{section.section_title}</p>
                )}
                {section.plain_language && (
                  <p className="text-sm text-slate-600 leading-relaxed mb-2">{section.plain_language}</p>
                )}
                {section.punishment_summary && (
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 bg-slate-50 rounded px-2 py-1.5 mb-2">
                    <span>⚖️</span>
                    <span>{section.punishment_summary}</span>
                  </div>
                )}
                {section.relevant_court && (
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <span>🏛</span>
                    <span>{section.relevant_court}</span>
                  </div>
                )}
                {section.bare_text && (
                  <div className="mt-2">
                    <button type="button"
                      onClick={() => setExpandedSections(prev => {
                        const next = new Set(prev);
                        next.has(i) ? next.delete(i) : next.add(i);
                        return next;
                      })}
                      className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                    >
                      <Scale className="w-3 h-3" />
                      {expandedSections.has(i) ? (lang === "hi" ? "छिपाएं" : "Hide") : (lang === "hi" ? "दिखाएं" : "Show")} {lang === "hi" ? "बेयर एक्ट पाठ" : "bare act text"}
                    </button>
                    {expandedSections.has(i) && (
                      <div className="mt-2 bg-slate-50 border border-slate-100 rounded p-3">
                        <p className="text-xs text-slate-500 font-mono leading-relaxed whitespace-pre-wrap">
                          {section.bare_text}
                        </p>
                      </div>
                    )}
                  </div>
                )}
                <div className="mt-3 flex justify-end gap-3">
                  <button 
                    onClick={() => {
                      const text = `Section ${section.section_number} of ${section.act_title}: ${section.plain_language}\n\nView more on Nyaya.`;
                      if (navigator.share) navigator.share({ title: `Section ${section.section_number}`, text });
                      else {
                        navigator.clipboard.writeText(text);
                        alert("Copied to clipboard!");
                      }
                    }}
                    className="text-[10px] text-slate-400 hover:text-blue-600 font-bold flex items-center gap-1"
                  >
                    <Share2 className="w-3 h-3" />
                    {lang === "hi" ? "साझा करें" : "Share"}
                  </button>
                  <button 
                    onClick={() => {
                      if (!user) onAuthOpen();
                      else onSaveSection(section);
                    }}
                    className="text-[10px] text-slate-400 hover:text-amber-600 font-bold flex items-center gap-1"
                  >
                    <Bookmark className="w-3 h-3" />
                    {lang === "hi" ? "सेक्शन सहेजें" : "Save Section"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {message.webSources && message.webSources.length > 0 && (
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 mb-4">
          <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1.5">
            <ExternalLink className="w-3.5 h-3.5" />
            {lang === "hi" ? "वेब स्रोत (रीयल-टाइम जानकारी के लिए)" : "Web Sources (for real-time info)"}
          </p>
          <div className="space-y-3">
            {message.webSources.map((src, i) => (
              <div key={i} className="text-xs">
                <a href={src.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium block mb-0.5">
                  {src.title}
                </a>
                <p className="text-slate-500 leading-relaxed line-clamp-2">{src.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {message.judgments && message.judgments.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 mb-4">
          <p className="text-xs font-semibold text-blue-700 mb-2 flex items-center gap-1.5">
            <Library className="w-3.5 h-3.5" />
            {lang === "hi" ? "कानूनी निर्णय (प्रीसिडेंट्स)" : "Legal Judgments (Precedents)"}
          </p>
          <div className="space-y-3">
            {message.judgments.map((j, i) => (
              <div key={i} className="text-xs">
                <a href={j.url} target="_blank" rel="noopener noreferrer" className="text-blue-700 hover:underline font-medium block mb-0.5">
                  {j.title}
                </a>
                <p className="text-blue-600/70 leading-relaxed line-clamp-2">{j.snippet}</p>
                <button 
                  onClick={() => onSummarize(j.url, j.snippet)}
                  disabled={summarizing === j.url}
                  className="mt-1 text-[10px] text-blue-800 font-bold hover:underline disabled:opacity-50"
                >
                  {summarizing === j.url ? "⌛ Summarizing..." : "✨ Summarize Judgment"}
                </button>
                {summaries[j.url] && (
                  <div className="mt-2 p-3 bg-white border border-blue-100 rounded-xl text-[11px] text-slate-700 leading-relaxed animate-in slide-in-from-top-1 duration-200">
                    {summaries[j.url]}
                  </div>
                )}
                <button 
                  onClick={() => {
                    if (!user) onAuthOpen();
                    else {
                      // Save logic here
                    }
                  }}
                  className="mt-1 ml-4 text-[10px] text-slate-500 font-bold hover:underline"
                >
                  <Bookmark className="w-3 h-3 inline mr-1" />
                  Save Reference
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Verify on trusted sources footer */}
      {!message.streaming && message.content && (
        <div className="flex flex-col gap-2 mt-3">
          <div className="flex items-center gap-2">
            <a
              href="https://www.indiacode.nic.in/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 border border-slate-200 rounded-lg px-3 py-1.5 hover:border-slate-300 transition-colors"
            >
              <BookOpen className="w-3 h-3" />
              {t.trustedPanel.chatToggle}
            </a>
          </div>
          
          {message.role === "assistant" && message.content.length > 300 && (
            <Link 
              href="/lawyers"
              className="group bg-green-50 border border-green-100 rounded-xl p-3 flex items-center justify-between hover:border-green-300 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 group-hover:scale-110 transition-transform">
                  <Users className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-[11px] font-bold text-green-800">Need expert legal representation?</p>
                  <p className="text-[10px] text-green-600">Connect with verified advocates in our directory.</p>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-green-400 group-hover:translate-x-1 transition-transform" />
            </Link>
          )}
        </div>
      )}
    </div>
  );
}

// ── Voice Button Component ───────────────────────────────────
function VoiceButton({ onTranscript }: { onTranscript: (text: string) => void }) {
  const [isListening, setIsListening] = useState(false);

  const toggleListen = () => {
    if (isListening) {
      setIsListening(false);
      return;
    }
    
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice recognition not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN"; // Supports English with Indian accent
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };
    recognition.start();
  };

  return (
    <button
      type="button"
      onClick={toggleListen}
      className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all ${isListening ? "bg-red-100 text-red-600 animate-pulse" : "bg-slate-100 text-slate-500 hover:bg-slate-200"}`}
    >
      {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
    </button>
  );
}

