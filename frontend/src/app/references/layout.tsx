import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "References — Nyaya",
  description:
    "Official Constitution and Bare Acts, court portals, Law Commission, debates, and suggested law books.",
};

export default function ReferencesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
