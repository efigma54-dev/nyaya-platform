// frontend/src/components/SectionCard.tsx
"use client";

import { SectionCard as SectionCardType } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Scale, Gavel, Building } from "lucide-react";
import { useState } from "react";

interface Props {
  section: SectionCardType;
  index: number;
}

export default function SectionCard({ section, index }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="border border-slate-200 hover:border-slate-300 transition-colors">
      <CardHeader className="pb-2 pt-4 px-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="font-mono text-xs">
              § {section.section_number}
            </Badge>
            {section.is_bailable === false && (
              <Badge className="bg-red-100 text-red-700 border-red-200 text-xs">
                Non-Bailable
              </Badge>
            )}
            {section.is_bailable === true && (
              <Badge className="bg-green-100 text-green-700 border-green-200 text-xs">
                Bailable
              </Badge>
            )}
            {section.is_cognizable === true && (
              <Badge className="bg-orange-100 text-orange-700 border-orange-200 text-xs">
                Cognizable
              </Badge>
            )}
          </div>
          <span className="text-xs text-slate-400 shrink-0">#{index + 1}</span>
        </div>
        <p className="text-xs text-slate-500 mt-1">{section.act_title}</p>
        {section.section_title && (
          <p className="font-medium text-sm text-slate-800 mt-1">
            {section.section_title}
          </p>
        )}
      </CardHeader>

      <CardContent className="px-4 pb-4 space-y-3">
        {section.plain_language && (
          <p className="text-sm text-slate-600 leading-relaxed">
            {section.plain_language}
          </p>
        )}

        {section.punishment_summary && (
          <div className="flex items-start gap-2 bg-slate-50 rounded-md p-2">
            <Gavel className="w-3.5 h-3.5 text-slate-500 mt-0.5 shrink-0" />
            <span className="text-xs text-slate-600">
              {section.punishment_summary}
            </span>
          </div>
        )}

        {section.relevant_court && (
          <div className="flex items-center gap-2">
            <Building className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-500">{section.relevant_court}</span>
          </div>
        )}

        {section.bare_text && (
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            <Scale className="w-3 h-3" />
            {expanded ? "Hide" : "Show"} bare act text
          </button>
        )}

        {expanded && section.bare_text && (
          <div className="bg-slate-50 border border-slate-100 rounded p-3 mt-2">
            <p className="text-xs text-slate-500 font-mono leading-relaxed whitespace-pre-wrap">
              {section.bare_text}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
