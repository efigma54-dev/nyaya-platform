"use client";

import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { MessageCircle } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";

const CHAT_ANCHOR = "nyaya-chat";

export default function FloatingLegalAssistant() {
  const pathname = usePathname();
  const router = useRouter();
  const { t } = useLocale();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  // Home already has a persistent composer — floating CTA duplicates it
  if (pathname === "/") return null;

  const openChat = () => {
    if (pathname === "/") {
      const el = document.getElementById(CHAT_ANCHOR);
      el?.scrollIntoView({ behavior: "smooth", block: "center" });
      setTimeout(() => {
        document.getElementById("nyaya-chat-input")?.focus();
      }, 350);
    } else {
      router.push(`/#${CHAT_ANCHOR}`);
      setTimeout(() => {
        document.getElementById("nyaya-chat-input")?.focus();
      }, 400);
    }
  };

  return (
    <button
      type="button"
      onClick={openChat}
      className="fixed bottom-5 right-4 z-50 flex items-center gap-2 rounded-full border border-amber-400/40 bg-linear-to-r from-slate-900 via-slate-800 to-slate-900 pl-3 pr-4 py-2.5 text-sm font-semibold text-amber-50 shadow-[0_8px_30px_rgba(0,0,0,0.45)] ring-2 ring-amber-500/25 transition hover:ring-amber-400/50 hover:brightness-110 active:scale-[0.98] md:bottom-8 md:right-8"
      aria-label={t.home.floatingSr}
    >
      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-amber-400/20 text-amber-200">
        <MessageCircle className="w-5 h-5" aria-hidden />
      </span>
      <span className="pr-0.5">{t.home.floatingLabel}</span>
    </button>
  );
}
