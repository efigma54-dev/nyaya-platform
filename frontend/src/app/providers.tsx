"use client";

import { LocaleProvider } from "@/components/LocaleProvider";
import { AuthProvider } from "@/lib/auth";
import FloatingLegalAssistant from "@/components/FloatingLegalAssistant";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <LocaleProvider>
        {children}
        <FloatingLegalAssistant />
      </LocaleProvider>
    </AuthProvider>
  );
}
