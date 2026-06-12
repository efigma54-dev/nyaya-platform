// frontend/src/lib/api.ts
// ALL requests go through Next.js proxy at /api/*
// Never call backend directly from browser — avoids all CORS issues

import axios from "axios";

// Empty string = relative URL = goes through Next.js proxy
const API_BASE = "";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

export type StreamEvent = 
  | { type: "token"; data: string }
  | { type: "emergency"; data: any }
  | { type: "sections"; data: SectionCard[] }
  | { type: "meta"; data: { 
      category: string | null; 
      provider: string; 
      low_confidence: boolean; 
      web_sources: any[]; 
      judgments: any[];
    } }
  | { type: "done"; data?: { ipc_bns_note: boolean } }
  | { type: "error"; data: string };

export interface SectionCard {
  id?: number;
  act_title: string;
  section_number: string;
  section_title: string;
  plain_language: string;
  punishment_summary: string;
  is_bailable: boolean | null;
  is_cognizable: boolean | null;
  relevant_court: string;
  bare_text?: string;
  max_punishment?: string;
  act_id?: number;
}

export interface Lawyer {
  id: number;
  full_name: string;
  specialization: string;
  location: string;
  experience_years: number;
  is_verified: boolean;
  rating: number;
  phone?: string;
  email?: string;
  bio?: string;
}

export interface Amendment {
  id: number;
  section_number: string;
  act_title: string;
  effective_date: string;
  amendment_act: string;
  notes: string;
}

export interface AnalyticsSummary {
  total_queries: number;
  categories: Record<string, number>;
  languages: Record<string, number>;
  recent_queries: { query: string; time: string; category: string | null }[];
}

export interface ChatResponse {
  answer: string;
  sections: SectionCard[];
  judgments?: any[];
  web_sources?: any[];
  category: string | null;
  session_id: string | null;
  response_time_ms: number;
  ai_provider: string;
  emergency?: any;
  low_confidence?: boolean;
  ipc_bns_note?: boolean;
  lang: string;
}

export interface Act {
  id: number;
  short_title: string;
  year: number | null;
  category: string;
  act_type: string;
  section_count: number;
}

// --- API METHODS ---

export async function sendChatQuery(
  query: string,
  sessionId: string,
  lang: string = "en"
): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/api/chat", {
    query,
    session_id: sessionId,
    lang,
  });
  return data;
}

export async function* streamChatQuery(
  query: string,
  sessionId: string,
  lang: string = "en"
): AsyncGenerator<StreamEvent> {
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, session_id: sessionId, stream: true, lang }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text.slice(0, 200)}`);
  }
  if (!response.body) throw new Error("No response body");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const event = JSON.parse(line.slice(6)) as StreamEvent;
          yield event;
        } catch {
          // skip malformed
        }
      }
    }
  }
}

export async function getActs(state?: string): Promise<Act[]> {
  const url = state ? `/api/sections/acts/list?state=${state}` : `/api/sections/acts/list`;
  const { data } = await api.get<{ acts: Act[] }>(url);
  return data.acts;
}

export async function getSections(actId?: number, category?: string) {
  const params: Record<string, string | number> = { limit: 50 };
  if (actId) params.act_id = actId;
  if (category) params.category = category;
  const { data } = await api.get("/api/sections/", { params });
  return data.sections;
}

export async function getLawyers(city?: string, category?: string): Promise<Lawyer[]> {
  const { data } = await api.get("/api/lawyers", { params: { city, category } });
  return data.lawyers;
}

export async function getAmendments(sectionId: number): Promise<Amendment[]> {
  const { data } = await api.get(`/api/amendments/section/${sectionId}`);
  return data;
}

export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  const { data } = await api.get("/api/analytics/summary");
  return data;
}

export async function generateDocument(
  type: string,
  input: Record<string, unknown>
): Promise<{ draft: string }> {
  // FIR lives at POST /fir/generate (not /generate/fir)
  const path = type === "fir" ? "/api/fir/generate" : `/api/generate/${type}`;
  const { data } = await api.post<{ draft: string }>(path, input);
  return data;
}

// --- USER METHODS ---

export async function getSavedQueries(token: string) {
  const { data } = await api.get("/api/user/saved-queries", {
    headers: { Authorization: `Bearer ${token}` }
  });
  return data;
}

export async function saveQuery(token: string, query: string, answer: string) {
  const { data } = await api.post("/api/user/saved-queries", null, {
    params: { query, answer },
    headers: { Authorization: `Bearer ${token}` }
  });
  return data;
}

export async function deleteQuery(token: string, id: number) {
  const { data } = await api.delete(`/api/user/saved-queries/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return data;
}

export async function getSavedSections(token: string) {
  const { data } = await api.get("/api/user/saved-sections", {
    headers: { Authorization: `Bearer ${token}` }
  });
  return data;
}

export async function saveSection(token: string, section: SectionCard) {
  const { data } = await api.post("/api/user/saved-sections", null, {
    params: { 
      section_id: section.id, 
      act_title: section.act_title, 
      section_number: section.section_number 
    },
    headers: { Authorization: `Bearer ${token}` }
  });
  return data;
}

export async function deleteSection(token: string, id: number) {
  const { data } = await api.delete(`/api/user/saved-sections/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return data;
}

