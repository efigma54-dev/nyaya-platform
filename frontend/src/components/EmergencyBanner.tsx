// frontend/src/components/EmergencyBanner.tsx
"use client";

import { Phone, AlertTriangle, X } from "lucide-react";
import { useState } from "react";

interface Contact {
  label: string;
  number: string;
}

interface Emergency {
  title: string;
  color: string;
  rights: string[];
  contacts: Contact[];
  sections: string[];
}

export default function EmergencyBanner({ emergency, onDismiss }: {
  emergency: Emergency;
  onDismiss: () => void;
}) {
  const isRed = emergency.color === "red";

  return (
    <div className={`
      rounded-xl border-2 p-4 mb-4 animate-in slide-in-from-top-2 duration-300
      ${isRed
        ? "bg-red-50 border-red-300"
        : "bg-orange-50 border-orange-300"
      }
    `}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className={`w-5 h-5 shrink-0 ${isRed ? "text-red-600" : "text-orange-600"}`} />
          <h3 className={`font-semibold text-sm ${isRed ? "text-red-800" : "text-orange-800"}`}>
            {emergency.title}
          </h3>
        </div>
        <button type="button" onClick={onDismiss} className="shrink-0">
          <X className="w-4 h-4 text-slate-400 hover:text-slate-600" />
        </button>
      </div>

      {/* Rights */}
      <ul className="space-y-1.5 mb-4">
        {emergency.rights.map((right, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
            <span className="shrink-0 font-bold text-slate-500">{i + 1}.</span>
            {right}
          </li>
        ))}
      </ul>

      {/* Emergency contacts */}
      <div className="flex flex-wrap gap-2">
        {emergency.contacts.map((contact, i) => (
          <a
            key={i}
            href={`tel:${contact.number}`}
            className={`
              flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
              ${isRed
                ? "bg-red-600 text-white hover:bg-red-700"
                : "bg-orange-600 text-white hover:bg-orange-700"
              }
            `}
          >
            <Phone className="w-3 h-3" />
            {contact.label}: {contact.number}
          </a>
        ))}
      </div>

      {/* Relevant sections */}
      {emergency.sections.length > 0 && (
        <p className="text-xs text-slate-500 mt-3">
          Relevant law: {emergency.sections.join(" · ")}
        </p>
      )}
    </div>
  );
}
