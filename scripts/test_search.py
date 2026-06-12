# scripts/test_search.py
# Semantic smoke tests after embed_sections.py

from __future__ import annotations

from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()

from app.rag.embedder import embed_text
from app.rag.vector_store import search_sections

TEST_QUERIES: list[tuple[str, str | None]] = [
    ("murder case what section applies", None),
    ("someone beat me up and I got injured", None),
    ("my husband is harassing me for dowry", None),
    ("I was cheated online lost money fraud", None),
    ("my fundamental rights were violated by police arrested without reason", None),
    ("consumer complaint against company defective product", "consumer"),
    ("mujhe ghar se nikala ja raha hai", None),
]


def run_tests() -> None:
    print("🔍 Nyaya Semantic Search Test")
    print("=" * 60)

    for query, category_filter in TEST_QUERIES:
        print(f"\n📝 Query: '{query}'")
        if category_filter:
            print(f"   Filter: category={category_filter}")

        try:
            vector = embed_text(query)
            results = search_sections(
                query_vector=vector,
                top_k=3,
                act_category=category_filter,
            )

            if not results:
                print("   ❌ No results returned")
                continue

            for i, r in enumerate(results, 1):
                p = r["payload"]
                b = p.get("is_bailable")
                bailable = (
                    "✅ Bailable"
                    if b is True
                    else "🔴 Non-Bailable"
                    if b is False
                    else "—"
                )
                title = (p.get("act_title") or "")[:30]
                sec = p.get("section_number") or ""
                st = (p.get("section_title") or "")[:40]
                score = float(r["score"])
                print(
                    f"   {i}. [{score:.3f}] {title} § {sec} — {st} {bailable}"
                )

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("If scores are above 0.4 for relevant queries → RAG is working.")
    print("Scores above 0.6 → strong semantic match.")


if __name__ == "__main__":
    run_tests()
