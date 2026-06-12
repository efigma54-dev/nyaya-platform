"use client";

import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "nyaya_ref_bookmarks";
const MAX = 48;

export type ReferenceBookmark = {
  id: string;
  title: string;
  href: string;
  savedAt: number;
};

function load(): ReferenceBookmark[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter(
        (x): x is ReferenceBookmark =>
          typeof x === "object" &&
          x !== null &&
          typeof (x as ReferenceBookmark).href === "string" &&
          typeof (x as ReferenceBookmark).title === "string"
      )
      .slice(0, MAX);
  } catch {
    return [];
  }
}

function persist(list: ReferenceBookmark[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, MAX)));
  } catch {
    /* ignore */
  }
}

export function useReferenceBookmarks() {
  const [list, setList] = useState<ReferenceBookmark[]>([]);

  useEffect(() => {
    setList(load());
  }, []);

  const isSaved = useCallback(
    (href: string) => list.some((x) => x.href === href),
    [list]
  );

  const toggle = useCallback((item: { id: string; title: string; href: string }) => {
    setList((prev) => {
      const exists = prev.some((x) => x.href === item.href);
      let next: ReferenceBookmark[];
      if (exists) {
        next = prev.filter((x) => x.href !== item.href);
      } else {
        next = [
          {
            id: item.id,
            title: item.title,
            href: item.href,
            savedAt: Date.now(),
          },
          ...prev.filter((x) => x.href !== item.href),
        ].slice(0, MAX);
      }
      persist(next);
      return next;
    });
  }, []);

  const remove = useCallback((href: string) => {
    setList((prev) => {
      const next = prev.filter((x) => x.href !== href);
      persist(next);
      return next;
    });
  }, []);

  return { list, isSaved, toggle, remove };
}
