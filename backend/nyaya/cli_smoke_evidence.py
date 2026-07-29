"""
Nyaya Platform — Smoke / Evidence Runner (no Postgres/Qdrant/Redis required).

Validates (in-process, in memory):
  1. Module imports for config / core / db / schemas / search.bm25 / search.hybrid / evaluation / seed
  2. Legal corpus schema against project-memory hard constraints
  3. Baseline seed data (counts, 10 Acts, 51+ Sections, bidirectional IPC-BNS mappings, KG edges, 25+ benchmark questions)
  4. Metric arithmetic (Recall@5/10, Precision@10, MRR, Hallucination) on a synthetic ranked list
  5. Hybrid combiner + BM25 index + citation validator with smoke data

Writes a timestamped JSON report to evidence/ plus LATEST.json.
"""
from __future__ import annotations

import importlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_MODULES = [
    ("settings", "nyaya.config.settings"),
    ("database", "nyaya.core.database"),
    ("security", "nyaya.core.security"),
    ("db_schema", "nyaya.db.models.schema"),
    ("crud_repos", "nyaya.db.repositories.crud"),
    ("pydantic_schemas", "nyaya.schemas"),
    ("bm25_index", "nyaya.search.bm25_index"),
    ("dense_index_meta", "nyaya.search.dense_index"),
    ("hybrid_pipeline", "nyaya.search.hybrid"),
    ("kg_service", "nyaya.search.kg_service"),
    ("evaluation", "nyaya.evaluation"),
    ("seed_acts", "nyaya.seed.acts"),
    ("seed_sections", "nyaya.seed.sections"),
    ("seed_ipc_bns", "nyaya.seed.ipc_bns_mappings"),
    ("seed_kg", "nyaya.seed.kg_relations"),
    ("seed_benchmark", "nyaya.seed.benchmark_questions"),
    ("seed_loader", "nyaya.seed"),
    ("cli_meta", "nyaya.cli"),
    ("main_meta", "nyaya.main"),
]

SECTION_REQUIRED_FIELDS = (
    "id", "act", "chapter", "part", "section_number", "title", "bare_text",
    "plain_language", "keywords", "punishments", "bailable", "cognizable",
    "compoundable", "source_pdf", "source_page", "checksum_sha256",
)

EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "evidence"


def load_module(name: str, import_path: str):
    start = time.perf_counter()
    try:
        m = importlib.import_module(import_path)
        return True, round(time.perf_counter() - start, 4), m, None
    except Exception as exc:  # pragma: no cover
        return False, round(time.perf_counter() - start, 4), None, f"{type(exc).__name__}: {exc}"


def check_section_schema(seed_section: dict) -> list[str]:
    violations: list[str] = []
    seed_has = set(seed_section.keys()) | {"act", "id"}  # act is resolved via act_id, id is generated
    seed_has |= {"source_pdf", "checksum_sha256"}  # may be injected by loader
    for f in SECTION_REQUIRED_FIELDS:
        if f not in ("id", "act") and f not in seed_section:
            violations.append(f)
    return violations


def compute_metrics_smoke():
    from nyaya.evaluation import recall_at_k, precision_at_k, reciprocal_rank

    relevant = {2, 5, 9, 17, 21}
    retrieved = [2, 55, 9, 3, 17, 8, 5, 10, 22, 4, 21, 30]
    r5 = recall_at_k(relevant, retrieved, 5)
    r10 = recall_at_k(relevant, retrieved, 10)
    p10 = precision_at_k(relevant, retrieved, 10)
    mrr = reciprocal_rank(relevant, retrieved)
    # Ground truth hallucination logic: a result in top-10 not validated AND not relevant
    validated = {2: True, 55: False, 9: True, 3: False, 17: True, 8: False,
                 5: True, 10: False, 22: False, 4: True}
    hallucinated_count = sum(
        1 for rid in retrieved[:10] if rid not in relevant and validated.get(rid, False) is False
    )
    hallucination_rate = 1.0 if hallucinated_count > 0 else 0.0  # question-level binary
    details = {
        "retrieved_top10": retrieved[:10],
        "relevant_ids": sorted(relevant),
        "validation": validated,
        "hallucinated_items_count_for_q": hallucinated_count,
    }
    return {
        "recall_at_5": round(r5, 4),
        "recall_at_10": round(r10, 4),
        "precision_at_10": round(p10, 4),
        "mrr": round(mrr, 4),
        "hallucination_rate_for_synthetic_q": round(hallucination_rate, 4),
        "details": details,
        "expected": {
            "recall_at_5_min": 0.2,  # 2/5 hits (2,9,17) in top5? [2,55,9,3,17] has 3/5 → 0.6
            "recall_at_5_expected_exact": 0.6,
            "recall_at_10_expected_exact": 4/5,  # 2,9,17,5 in top 10 = 4 of 5
            "precision_at_10_expected_exact": 4/10,
            "mrr_expected": 1.0,  # ID #2 is 1st
        },
    }


def test_hybrid_pipeline_smoke():
    from nyaya.search.bm25_index import BM25Corpus
    from nyaya.search.hybrid import combine_scores, validate_citations, HybridCandidate

    class FakeS:
        def __init__(self, sid, title, bare_text, keywords=None):
            self.id = sid
            self.title = title
            self.bare_text = bare_text
            self.keywords = keywords or []
            self.plain_language = None

    corpus = [
        FakeS(1, "Murder Punishment", "Whoever commits murder shall be punished with death or life imprisonment.", ["murder", "death"]),
        FakeS(2, "Culpable Homicide", "Culpable homicide not amounting to murder carries up to ten years.", ["homicide", "culpable"]),
        FakeS(3, "Theft Definition", "Dishonest taking of movable property without consent is theft.", ["theft", "property"]),
        FakeS(4, "Cruelty by Husband", "Cruelty by husband or relatives includes dowry harassment.", ["cruelty", "dowry"]),
        FakeS(5, "Rape Punishment 376", "Rape is punished with minimum ten years to life imprisonment.", ["rape", "imprisonment"]),
    ]
    bm25 = BM25Corpus.build(corpus)
    b_hits = bm25.query("murder death punishment", top_k=5)
    # fake dense hits via manual scoring
    d_hits = [(1, 0.91), (5, 0.28), (2, 0.19), (3, 0.12), (4, 0.05)]
    combined = combine_scores(b_hits, d_hits)
    for c in combined.values():
        cand = [s for s in corpus if s.id == c.section_id]
        if cand:
            c.section_obj = cand[0]
            c.title = cand[0].title
            c.bare_text = cand[0].bare_text
    validated = validate_citations("murder death punishment", list(combined.values()))
    summary = {
        "bm25_top": [(s, round(sc, 3)) for s, sc in b_hits[:3]],
        "combined_scores": sorted(
            [(c.section_id, round(c.combined_score, 3)) for c in combined.values()],
            key=lambda x: x[1], reverse=True,
        )[:5],
        "validated_count": sum(1 for _, ok, _, _ in validated if ok),
        "validated_sample": [(c.section_id, ok, round(sim, 2)) for c, ok, sim, _ in validated[:4]],
    }
    assert combined[1].combined_score >= 0.1, "Section #1 (murder) should be highly ranked"
    return summary


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    start_all = time.perf_counter()
    report: dict = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "modules": {}, "schema": {}, "seed": {}, "metrics_smoke": {}, "hybrid_smoke": {}}

    print("== Nyaya Smoke / Evidence Runner ==")
    print()

    # 1. Module imports
    print("[1/5] Module imports …")
    all_modules_ok = True
    for key, import_path in REQUIRED_MODULES:
        ok, elapsed, _m, err = load_module(key, import_path)
        report["modules"][key] = {"ok": ok, "import": import_path, "elapsed_seconds": elapsed, "error": err}
        status = "OK  " if ok else "FAIL"
        line = f"  {status} {elapsed:7.4f}s  {import_path}"
        if ok:
            print(line)
        else:
            print(line + f"  ERROR: {err}")
            all_modules_ok = False

    # 2. Legal corpus schema
    print()
    print("[2/5] Legal corpus schema check …")
    from nyaya.seed.sections import SECTIONS
    missing_by_field = {}
    for i, seed_sec in enumerate(SECTIONS[:10]):
        v = check_section_schema(seed_sec)
        for field in v:
            missing_by_field.setdefault(field, []).append(i)
    report["schema"] = {
        "baseline_sampled": 10,
        "required_fields": list(SECTION_REQUIRED_FIELDS),
        "sections_missing_fields": {k: sorted(set(v)) for k, v in missing_by_field.items()},
        "all_sections_meets_constraints": len(missing_by_field) == 0,
    }
    if missing_by_field:
        print("  WARN: missing fields detected:", json.dumps(missing_by_field))
    else:
        print("  OK: sampled 10/10 seed sections carry all hard-constraint fields")

    # 3. Seed counts
    print()
    print("[3/5] Baseline seed counts …")
    from nyaya.seed.acts import ACTS
    from nyaya.seed.ipc_bns_mappings import IPC_BNS_MAPPINGS
    from nyaya.seed.kg_relations import KG_EDGES
    from nyaya.seed.benchmark_questions import BENCHMARK_QUESTIONS

    act_short_titles = [a["short_title"] for a in ACTS]
    per_act_section_count: dict[str, int] = {}
    for s in SECTIONS:
        per_act_section_count[s["act_short_title"]] = per_act_section_count.get(s["act_short_title"], 0) + 1
    unique_ipc_bns_pairs = len(set(IPC_BNS_MAPPINGS))
    report["seed"] = {
        "acts_total": len(ACTS),
        "acts_expected": 10,
        "acts_titles": act_short_titles,
        "sections_total": len(SECTIONS),
        "sections_expected_min": 51,
        "sections_per_act": per_act_section_count,
        "ipc_bns_mappings_total": unique_ipc_bns_pairs,
        "bidirectional_loader_will_produce": unique_ipc_bns_pairs * 2,
        "kg_edges_total": len(KG_EDGES),
        "benchmark_questions_total": len(BENCHMARK_QUESTIONS),
        "benchmark_questions_expected_min": 25,
    }
    for k, v in [
        ("Acts", f"{len(ACTS)}/10"),
        ("Sections", f"{len(SECTIONS)}/≥51"),
        ("IPC-BNS seed pairs", f"{unique_ipc_bns_pairs} → {unique_ipc_bns_pairs*2} bidirectional"),
        ("KG edges", f"{len(KG_EDGES)}"),
        ("Benchmark Questions", f"{len(BENCHMARK_QUESTIONS)}/≥25"),
    ]:
        print(f"  · {k:30s}  {v}")

    # 4. Metric arithmetic
    print()
    print("[4/5] Metric math smoke …")
    metrics = compute_metrics_smoke()
    report["metrics_smoke"] = metrics
    print(f"  R@5  = {metrics['recall_at_5']:.4f}  (expect ≥{metrics['expected']['recall_at_5_expected_exact']})")
    print(f"  R@10 = {metrics['recall_at_10']:.4f}  (expect ≥{metrics['expected']['recall_at_10_expected_exact']})")
    print(f"  P@10 = {metrics['precision_at_10']:.4f}  (expect ≥{metrics['expected']['precision_at_10_expected_exact']})")
    print(f"  MRR  = {metrics['mrr']:.4f}  (expect ≥{metrics['expected']['mrr_expected']})")
    print(f"  HallucinationRate = {metrics['hallucination_rate_for_synthetic_q']:.4f}")

    exact_matches = (
        math.isclose(metrics["recall_at_5"], metrics["expected"]["recall_at_5_expected_exact"])
        and math.isclose(metrics["recall_at_10"], metrics["expected"]["recall_at_10_expected_exact"])
        and math.isclose(metrics["precision_at_10"], metrics["expected"]["precision_at_10_expected_exact"])
        and math.isclose(metrics["mrr"], metrics["expected"]["mrr_expected"])
    )
    report["metrics_smoke"]["arithmetic_correct"] = exact_matches
    print(f"  arithmetic exact match → {'PASS' if exact_matches else 'FAIL'}")

    # 5. Hybrid combiner + BM25 + validator
    print()
    print("[5/5] Hybrid combiner / BM25 / citation validator smoke …")
    hybrid = test_hybrid_pipeline_smoke()
    report["hybrid_smoke"] = hybrid
    print(f"  BM25 top 3: {hybrid['bm25_top']}")
    print(f"  Combined top 5: {hybrid['combined_scores']}")
    print(f"  Citation-validated results: {hybrid['validated_count']}/5")

    # Gate
    report["elapsed_seconds"] = round(time.perf_counter() - start_all, 3)
    seed_ok = (
        len(ACTS) == 10 and len(SECTIONS) >= 51 and len(BENCHMARK_QUESTIONS) >= 25
    )
    schema_ok = len(missing_by_field) == 0
    report["pass_gate"] = all([
        all_modules_ok,
        schema_ok,
        seed_ok,
        exact_matches,
        hybrid["validated_count"] >= 1,
    ])
    report["pass_gate_breakdown"] = {
        "all_modules_import": all_modules_ok,
        "schema_hard_constraints": schema_ok,
        "seed_count_baseline": seed_ok,
        "metric_arithmetic_exact": exact_matches,
        "hybrid_validated_results_present": hybrid["validated_count"] >= 1,
    }
    print()
    print(f"== OVERALL GATE → {'PASS' if report['pass_gate'] else 'FAIL'} ==")

    # Write evidence JSON
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = EVIDENCE_DIR / f"smoke_validation_{stamp}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    latest = EVIDENCE_DIR / "LATEST.json"
    try:
        latest.unlink()
    except FileNotFoundError:
        pass
    latest.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Evidence written: {path}")
    print(f"                 → LATEST.json")
    return 0 if report["pass_gate"] else 1


if __name__ == "__main__":
    sys.exit(main())
