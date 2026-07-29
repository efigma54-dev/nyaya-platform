import SearchClient from "@/components/SearchClient";

export const metadata = {
  title: "Hybrid Search · Nyaya AI",
  description: "BM25 + BGE-M3 dense + cross-encoder rerank + citation validator.",
};

export default function SearchPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-14">
      <div className="mb-8">
        <div className="text-xs uppercase tracking-[0.3em] text-nyaya-300/70">Hybrid Retrieval</div>
        <h1 className="mt-2 text-4xl font-bold tracking-tight">Search the statutory corpus</h1>
        <p className="mt-2 text-white/65 max-w-3xl">
          Searches are routed through a four-stage pipeline: BM25 (lexical) + BGE-M3 dense (semantic)
          → combined with learned weights → ms-marco-MiniLM cross-encoder rerank →
          citation validator flags hallucination-risk results with a 0.5× score penalty.
        </p>
      </div>
      <SearchClient />
    </div>
  );
}
