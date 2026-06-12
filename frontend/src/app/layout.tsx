import type { Metadata } from "next";
import { DM_Sans, Libre_Baskerville } from "next/font/google";
import "./globals.css";
import { AppProviders } from "./providers";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
});

const libreBaskerville = Libre_Baskerville({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-libre-baskerville",
});

export const metadata: Metadata = {
  title: "Nyaya — Indian legal information & research",
  description:
    "Describe your situation in your own words; get database-grounded acts, sections, and process hints. Official references for Constitution, Bare Acts, courts, and exams.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${dmSans.variable} ${libreBaskerville.variable} h-full antialiased`}
    >
      <body
        className={`${dmSans.className} min-h-full flex flex-col bg-slate-950 text-slate-900`}
      >
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
