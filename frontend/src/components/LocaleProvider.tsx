"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { getStrings, type Lang, type UiStrings } from "@/lib/ui-strings";

const STORAGE_KEY = "nyaya_ui_lang";

type Ctx = {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: UiStrings;
};

const LocaleContext = createContext<Ctx | null>(null);

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw === "hi" || raw === "en") {
        setLangState(raw);
        document.documentElement.lang = raw;
      }
    } catch {
      /* ignore */
    }
  }, []);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try {
      localStorage.setItem(STORAGE_KEY, l);
      document.documentElement.lang = l;
    } catch {
      /* ignore */
    }
  }, []);

  const t = useMemo(() => getStrings(lang), [lang]);

  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t]);

  return (
    <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>
  );
}

export function useLocale(): Ctx {
  const v = useContext(LocaleContext);
  if (!v) {
    throw new Error("useLocale must be used within LocaleProvider");
  }
  return v;
}

/** Safe for components that may render outside provider (fallback English). */
export function useLocaleOptional(): Ctx | null {
  return useContext(LocaleContext);
}
