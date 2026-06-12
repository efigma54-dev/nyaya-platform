"use client";

import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";

interface Props {
  content: string;
  className?: string;
}

const components: Components = {
  p: ({ children }) => (
    <p className="my-1.5 leading-relaxed text-slate-700">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-slate-900">{children}</strong>
  ),
  em: ({ children }) => <em className="italic text-slate-600">{children}</em>,
  ul: ({ children }) => (
    <ul className="my-2 list-disc space-y-1 pl-5 text-slate-700">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="my-2 list-decimal space-y-1 pl-5 text-slate-700">{children}</ol>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  h1: ({ children }) => (
    <h3 className="mt-3 mb-1.5 text-base font-semibold text-slate-900">{children}</h3>
  ),
  h2: ({ children }) => (
    <h3 className="mt-3 mb-1.5 text-sm font-semibold text-slate-900">{children}</h3>
  ),
  h3: ({ children }) => (
    <h4 className="mt-2 mb-1 text-sm font-semibold text-slate-800">{children}</h4>
  ),
};

/** Renders assistant chat text with bold, lists, and headings (no typography plugin required). */
export default function ChatMarkdown({ content, className = "" }: Props) {
  return (
    <div className={`text-sm ${className}`}>
      <ReactMarkdown components={components}>{content}</ReactMarkdown>
    </div>
  );
}
