// frontend/src/components/ChatMessage.tsx
"use client";

import type { ChatResponse } from "@/lib/api";
import SectionCard from "@/components/SectionCard";
import TrustedReferencesPanel from "@/components/TrustedReferencesPanel";
import EmergencyBanner from "@/components/EmergencyBanner";
import ChatMarkdown from "@/components/ChatMarkdown";
import { Badge } from "@/components/ui/badge";
import { getCategoryColor, getCategoryLabel } from "@/lib/utils";
import { useLocale } from "@/components/LocaleProvider";
import { Bot, User, Clock, Zap, AlertTriangle } from "lucide-react";
import { useState } from "react";

export interface ChatMessageModel {
  role: "user" | "assistant";
  content: string;
  data?: ChatResponse;
  timestamp: Date;
}

interface Props {
  message: ChatMessageModel;
}

export default function ChatMessage({ message }: Props) {
  const { t } = useLocale();
  const isUser = message.role === "user";
  const [emergencyDismissed, setEmergencyDismissed] = useState(false);

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="flex items-start gap-2 max-w-[85%]">
          <div className="rounded-2xl rounded-tr-sm border border-amber-200/80 bg-gradient-to-br from-amber-50 to-white px-4 py-2.5 text-sm text-slate-900 shadow-md">
            {message.content}
          </div>
          <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center shrink-0 mt-0.5 ring-2 ring-amber-400/30">
            <User className="w-4 h-4 text-amber-100" />
          </div>
        </div>
      </div>
    );
  }

  const data = message.data;

  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start gap-3 max-w-[94%] w-full">
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center shrink-0 mt-0.5 ring-2 ring-amber-500/25 shadow-md">
          <Bot className="w-4 h-4 text-amber-200" />
        </div>

        <div className="flex-1 space-y-3 min-w-0">
          {/* Emergency banner - shown first if present */}
          {!emergencyDismissed && data?.emergency && (
            <EmergencyBanner
              emergency={data.emergency}
              onDismiss={() => setEmergencyDismissed(true)}
            />
          )}

          <div className="rounded-2xl rounded-tl-sm border border-slate-200/90 bg-white px-4 py-3 shadow-md ring-1 ring-slate-900/[0.03]">
            <ChatMarkdown content={message.content} />

            {data && (
              <div className="flex items-center gap-2 mt-3 pt-3 border-t border-slate-100 flex-wrap">
                {data.category && (
                  <Badge
                    variant="outline"
                    className={`text-xs ${getCategoryColor(data.category)}`}
                  >
                    {getCategoryLabel(data.category)}
                  </Badge>
                )}
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <Clock className="w-3 h-3" />
                  {(data.response_time_ms / 1000).toFixed(1)}s
                </span>
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <Zap className="w-3 h-3" />
                  {data.ai_provider}
                </span>
              </div>
            )}
          </div>

          {/* Low confidence warning */}
          {data?.low_confidence && (
            <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-xs text-amber-700">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              Limited coverage — this area may not be fully indexed yet. Verify with a lawyer.
            </div>
          )}

          {/* IPC to BNS note */}
          {data?.ipc_bns_note && (
            <div className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 text-xs text-blue-700">
              ℹ️ IPC sections shown include BNS equivalents (effective July 1, 2024)
            </div>
          )}

          {data?.sections && data.sections.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-500 mb-2 ml-1 uppercase tracking-wide">
                {data.sections.length === 1
                  ? `1 ${t.chat.sectionsFoundOne}`
                  : `${data.sections.length} ${t.chat.sectionsFound}`}
                :
              </p>
              <div className="grid gap-2">
                {data.sections.slice(0, 4).map((section, i) => (
                  <SectionCard
                    key={`${section.act_title}-${section.section_number}-${i}`}
                    section={section}
                    index={i}
                  />
                ))}
              </div>
            </div>
          )}

          <TrustedReferencesPanel variant="chat" />
        </div>
      </div>
    </div>
  );
}
