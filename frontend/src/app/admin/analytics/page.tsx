"use client";

import { useState, useEffect } from "react";
import { Scale, BarChart3, Activity, PieChart, Clock, Loader2, RefreshCcw, TrendingUp } from "lucide-react";
import Link from "next/link";
import { getAnalyticsSummary, type AnalyticsSummary } from "@/lib/api";

export default function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = () => {
    setLoading(true);
    getAnalyticsSummary()
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 px-8 py-6 flex items-center justify-between sticky top-0 bg-slate-900/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 bg-amber-400 rounded-xl">
            <Scale className="w-6 h-6 text-slate-900" />
          </Link>
          <h1 className="text-xl font-bold tracking-tight">Nyaya Analytics Hub</h1>
        </div>
        <button 
          onClick={fetchData}
          className="p-2 hover:bg-slate-800 rounded-full transition-colors"
        >
          <RefreshCcw className={`w-5 h-5 text-slate-400 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </header>

      <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
        {loading && !data ? (
          <div className="flex items-center justify-center h-[60vh]">
            <Loader2 className="w-10 h-10 text-amber-400 animate-spin" />
          </div>
        ) : data ? (
          <div className="space-y-8">
            {/* Top Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6 shadow-lg">
                <div className="flex items-center gap-3 text-slate-400 mb-4">
                  <Activity className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase tracking-widest">Total Queries</span>
                </div>
                <p className="text-4xl font-bold text-white">{data.total_queries.toLocaleString()}</p>
                <p className="text-xs text-green-400 mt-2 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  Lifetime queries
                </p>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6 shadow-lg">
                <div className="flex items-center gap-3 text-slate-400 mb-4">
                  <PieChart className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase tracking-widest">Top Category</span>
                </div>
                <p className="text-4xl font-bold text-amber-400">
                  {Object.keys(data.categories)[0] || "N/A"}
                </p>
                <p className="text-xs text-slate-500 mt-2">Most queried legal area</p>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6 shadow-lg">
                <div className="flex items-center gap-3 text-slate-400 mb-4">
                  <Activity className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase tracking-widest">Hindi Adoption</span>
                </div>
                <p className="text-4xl font-bold text-white">
                  {Math.round(((data.languages["hi"] || 0) / data.total_queries) * 100) || 0}%
                </p>
                <p className="text-xs text-slate-500 mt-2">Bilingual usage share</p>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6 shadow-lg">
                <div className="flex items-center gap-3 text-slate-400 mb-4">
                  <Clock className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase tracking-widest">System Health</span>
                </div>
                <p className="text-4xl font-bold text-green-400">100%</p>
                <p className="text-xs text-slate-500 mt-2">Operational uptime</p>
              </div>
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Categories */}
              <div className="bg-slate-800 border border-slate-700 rounded-3xl p-8 shadow-lg">
                <div className="flex items-center justify-between mb-8">
                  <h3 className="text-lg font-bold flex items-center gap-3">
                    <BarChart3 className="w-5 h-5 text-amber-400" />
                    Query Distribution
                  </h3>
                </div>
                <div className="space-y-6">
                  {Object.entries(data.categories).map(([cat, count]) => (
                    <div key={cat}>
                      <div className="flex justify-between text-xs font-bold uppercase mb-2">
                        <span className="text-slate-400">{cat}</span>
                        <span>{count}</span>
                      </div>
                      <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-amber-400 rounded-full" 
                          style={{ width: `${(count / data.total_queries) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-slate-800 border border-slate-700 rounded-3xl p-8 shadow-lg">
                <h3 className="text-lg font-bold flex items-center gap-3 mb-8">
                  <RefreshCcw className="w-5 h-5 text-blue-400" />
                  Real-time Feed
                </h3>
                <div className="space-y-4">
                  {data.recent_queries.map((q, i) => (
                    <div key={i} className="flex gap-4 p-4 bg-slate-900/50 rounded-2xl border border-slate-700/50">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mt-1.5 shrink-0 animate-pulse" />
                      <div>
                        <p className="text-sm text-slate-200 line-clamp-1 mb-1">{q.query}</p>
                        <div className="flex items-center gap-3 text-[10px] text-slate-500 uppercase font-bold tracking-tight">
                          <span>{q.category || "General"}</span>
                          <span>·</span>
                          <span>{new Date(q.time).toLocaleTimeString()}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-20 text-center">
             <p className="text-slate-500">Failed to load analytics data.</p>
          </div>
        )}
      </main>
    </div>
  );
}
