"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { useLocale } from "@/components/LocaleProvider";
import { 
  User, History, Bookmark, Settings, LogOut, 
  ChevronRight, Scale, ExternalLink, Shield, 
  MessageSquare, Loader2, AlertTriangle, Trash2, Share2
} from "lucide-react";
import Link from "next/link";
import { getSavedQueries, getSavedSections, deleteQuery, deleteSection } from "@/lib/api";

export default function UserDashboard() {
  const { user, logout, token, loading: authLoading } = useAuth();
  const { t } = useLocale();
  const [savedQueries, setSavedQueries] = useState<any[]>([]);
  const [savedSections, setSavedSections] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchData();
    } else if (!authLoading) {
      // Redirect or show login
    }
  }, [token, authLoading]);

  const fetchData = async () => {
    if (!token) return;
    try {
      const [queries, sections] = await Promise.all([
        getSavedQueries(token),
        getSavedSections(token)
      ]);
      setSavedQueries(queries);
      setSavedSections(sections);
    } catch (err) {
      console.error("Failed to fetch dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteQuery = async (id: number) => {
    if (!token) return;
    if (!confirm("Are you sure you want to delete this query?")) return;
    try {
      await deleteQuery(token, id);
      setSavedQueries(prev => prev.filter(q => q.id !== id));
    } catch (err) {
      alert("Failed to delete query");
    }
  };

  const handleDeleteSection = async (id: number) => {
    if (!token) return;
    if (!confirm("Are you sure you want to delete this section?")) return;
    try {
      await deleteSection(token, id);
      setSavedSections(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      alert("Failed to delete section");
    }
  };

  const handleShare = async (title: string, text: string) => {
    if (navigator.share) {
      try {
        await navigator.share({ title, text, url: window.location.href });
      } catch (err) {
        console.error("Share failed", err);
      }
    } else {
      await navigator.clipboard.writeText(`${title}\n\n${text}`);
      alert("Copied to clipboard!");
    }
  };

  if (authLoading || (loading && token)) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-slate-300 animate-spin" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 bg-white rounded-3xl flex items-center justify-center mb-6 shadow-sm">
          <Shield className="w-8 h-8 text-slate-300" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Access Denied</h1>
        <p className="text-slate-500 mb-8 max-w-sm">Please log in to view your personalized legal dashboard and saved resources.</p>
        <Link href="/" className="bg-slate-900 text-white font-bold px-8 py-3 rounded-2xl hover:bg-slate-800 transition-all">
          Return Home
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar Navigation */}
      <aside className="w-72 bg-white border-r border-slate-200 flex flex-col sticky top-0 h-screen hidden lg:flex">
        <div className="p-8 border-b border-slate-50">
          <Link href="/" className="flex items-center gap-2.5">
            <Scale className="w-6 h-6 text-slate-900" />
            <span className="font-bold text-xl tracking-tight text-slate-900">Nyaya</span>
          </Link>
        </div>
        
        <nav className="flex-1 p-6 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 bg-slate-900 text-white rounded-2xl font-bold shadow-lg shadow-slate-200 transition-all">
            <User className="w-4 h-4" />
            My Profile
          </button>
          <Link href="/amendments" className="w-full flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-50 rounded-2xl font-semibold transition-all">
            <History className="w-4 h-4" />
            Legal Timeline
          </Link>
          <Link href="/sections" className="w-full flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-50 rounded-2xl font-semibold transition-all">
            <Bookmark className="w-4 h-4" />
            Acts Library
          </Link>
        </nav>

        <div className="p-6 border-t border-slate-50">
          <button 
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-3 text-red-500 hover:bg-red-50 rounded-2xl font-bold transition-all"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="bg-white/80 backdrop-blur-md border-b border-slate-100 px-8 py-6 sticky top-0 z-10 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Personal Dashboard</h1>
            <p className="text-xs text-slate-400">Welcome back, {user.full_name}</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center text-slate-600 font-bold border border-slate-200">
              {user.full_name.charAt(0)}
            </div>
          </div>
        </header>

        <div className="p-10 max-w-6xl mx-auto space-y-10">
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm">
              <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600 mb-6">
                <MessageSquare className="w-6 h-6" />
              </div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Saved Queries</p>
              <p className="text-3xl font-black text-slate-900">{savedQueries.length}</p>
            </div>
            <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm">
              <div className="w-12 h-12 bg-amber-50 rounded-2xl flex items-center justify-center text-amber-600 mb-6">
                <Bookmark className="w-6 h-6" />
              </div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Bookmarked Sections</p>
              <p className="text-3xl font-black text-slate-900">{savedSections.length}</p>
            </div>
            <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm">
              <div className="w-12 h-12 bg-green-50 rounded-2xl flex items-center justify-center text-green-600 mb-6">
                <Shield className="w-6 h-6" />
              </div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Account Status</p>
              <p className="text-3xl font-black text-slate-900">Verified</p>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-10">
            {/* Recent Queries */}
            <section className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-slate-900">Recent AI Consultations</h2>
                <button className="text-xs font-bold text-slate-400 hover:text-slate-900 transition-colors uppercase tracking-widest">View All</button>
              </div>
              
              <div className="space-y-4">
                {savedQueries.length > 0 ? savedQueries.map((q) => (
                  <div key={q.id} className="bg-white border border-slate-100 rounded-3xl p-6 hover:shadow-md transition-all group">
                    <p className="text-sm font-bold text-slate-900 mb-3 group-hover:text-blue-600 transition-colors line-clamp-2 leading-relaxed">
                      {q.query_text}
                    </p>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                      <span>{new Date(q.created_at).toLocaleDateString()}</span>
                      <div className="flex items-center gap-3">
                        <button onClick={(e) => { e.preventDefault(); handleShare("Nyaya Legal Query", q.query_text); }} className="hover:text-blue-600">
                          <Share2 className="w-3.5 h-3.5" />
                        </button>
                        <button onClick={(e) => { e.preventDefault(); handleDeleteQuery(q.id); }} className="hover:text-red-500">
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                )) : (
                  <div className="py-12 text-center bg-slate-50/50 border border-dashed border-slate-200 rounded-3xl">
                    <MessageSquare className="w-10 h-10 text-slate-200 mx-auto mb-4" />
                    <p className="text-sm text-slate-400">No saved queries yet. Start a chat with Nyaya!</p>
                  </div>
                )}
              </div>
            </section>

            {/* Saved Sections */}
            <section className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-slate-900">Legal Reference Library</h2>
                <button className="text-xs font-bold text-slate-400 hover:text-slate-900 transition-colors uppercase tracking-widest">Explore Acts</button>
              </div>

              <div className="space-y-4">
                {savedSections.length > 0 ? savedSections.map((s) => (
                  <div key={s.id} className="bg-white border border-slate-100 rounded-3xl p-6 flex items-start justify-between group hover:shadow-md transition-all">
                    <div>
                      <h3 className="font-bold text-slate-900 mb-1 group-hover:text-amber-600 transition-colors">Section {s.section_number}</h3>
                      <p className="text-xs text-slate-400 font-medium mb-4">{s.act_title}</p>
                      <div className="flex gap-2">
                        <span className="text-[9px] bg-slate-50 text-slate-500 px-2 py-1 rounded-md font-bold uppercase tracking-widest border border-slate-100">Saved</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button 
                        onClick={() => handleShare(`Section ${s.section_number}`, s.act_title)}
                        className="p-3 bg-slate-50 rounded-2xl text-slate-400 hover:bg-blue-50 hover:text-blue-600 transition-all shadow-inner"
                      >
                        <Share2 className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDeleteSection(s.id)}
                        className="p-3 bg-slate-50 rounded-2xl text-slate-400 hover:bg-red-50 hover:text-red-600 transition-all shadow-inner"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <button className="p-3 bg-slate-50 rounded-2xl text-slate-400 hover:bg-slate-900 hover:text-white transition-all shadow-inner">
                        <ExternalLink className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )) : (
                  <div className="py-12 text-center bg-slate-50/50 border border-dashed border-slate-200 rounded-3xl">
                    <Bookmark className="w-10 h-10 text-slate-200 mx-auto mb-4" />
                    <p className="text-sm text-slate-400">Your legal library is empty. Save sections as you browse.</p>
                  </div>
                )}
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
