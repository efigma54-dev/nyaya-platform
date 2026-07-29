import sys, importlib, time, json, math, os, traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
EVD = ROOT / "evidence"
EVD.mkdir(exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
out = EVD / f"evidence_{stamp}.json"
text_log = EVD / f"run_{stamp}.log.txt"

captured = []
def P(s):
    captured.append(str(s))

_start = time.perf_counter()
REPORT = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "python_version": sys.version,
          "modules": {}, "schema": {}, "seed": {}, "metrics_smoke": {}, "hybrid_smoke": {}}

MODULES = [
    ("settings", "nyaya.config.settings"),
    ("security", "nyaya.core.security"),
    ("database", "nyaya.core.database"),
    ("dbmodels", "nyaya.db.models.schema"),
    ("repositories", "nyaya.db.repositories.crud"),
    ("schemas_pydantic", "nyaya.schemas"),
    ("qdrant_client_meta", "nyaya.services.qdrant_client"),
    ("redis_client_meta", "nyaya.services.redis_client"),
    ("embeddings_meta", "nyaya.services.embeddings"),
    ("bm25_index", "nyaya.search.bm25_index"),
    ("dense_index_meta", "nyaya.search.dense_index"),
    ("hybrid_pipeline", "nyaya.search.hybrid"),
    ("kg_service", "nyaya.search.kg_service"),
    ("evaluation", "nyaya.evaluation"),
    ("seed_acts", "nyaya.seed.acts"),
    ("seed_sections", "nyaya.seed.sections"),
    ("seed_ipc_bns_mappings", "nyaya.seed.ipc_bns_mappings"),
    ("seed_kg_relations", "nyaya.seed.kg_relations"),
    ("seed_benchmark_questions", "nyaya.seed.benchmark_questions"),
]

P("MODULE IMPORTS:")
all_import_ok = True
for key, imp in MODULES:
    t = time.perf_counter()
    try:
        importlib.import_module(imp)
        dt = time.perf_counter() - t
        REPORT["modules"][key] = {"ok": True, "import": imp, "elapsed_seconds": round(dt, 4)}
        P(f"  OK   {dt:7.4f}s  {imp}")
    except Exception as e:
        all_import_ok = False
        dt = time.perf_counter() - t
        tb = traceback.format_exc(limit=2)
        msg = f"{type(e).__name__}: {e}"
        REPORT["modules"][key] = {"ok": False, "import": imp, "elapsed_seconds": round(dt, 4),
                                  "error": msg, "traceback": tb}
        P(f"  FAIL {dt:7.4f}s  {imp}  {msg}")

P("")
P("SEED COUNTS:")
try:
    from nyaya.seed.acts import ACTS
    from nyaya.seed.sections import SECTIONS
    from nyaya.seed.ipc_bns_mappings import IPC_BNS_MAPPINGS
    from nyaya.seed.kg_relations import KG_EDGES
    from nyaya.seed.benchmark_questions import BENCHMARK_QUESTIONS
except Exception as e:
    P(f"  SEED IMPORT FAIL: {type(e).__name__}: {e}")
    ACTS, SECTIONS, IPC_BNS_MAPPINGS, KG_EDGES, BENCHMARK_QUESTIONS = [], [], [], [], []

REQUIRED_SECTION_FIELDS = (
    "section_number", "title", "bare_text", "plain_language", "keywords",
    "punishments", "bailable", "cognizable", "compoundable",
    "source_page", "checksum_sha256",
)
missing_by_field = {}
for i, s in enumerate(SECTIONS[:10]):
    for field in REQUIRED_SECTION_FIELDS:
        if field not in s:
            missing_by_field.setdefault(field, []).append(i)
schema_ok = len(missing_by_field) == 0
REPORT["schema"] = {"sampled": 10, "required": list(REQUIRED_SECTION_FIELDS),
                    "missing": {k: list(v) for k, v in missing_by_field.items()},
                    "all_constraints_satisfied": schema_ok}

import collections
difficulty_counter = collections.Counter(q[1] for q in BENCHMARK_QUESTIONS)
per_act = collections.Counter(s["act_short_title"] for s in SECTIONS)

seed_ok = (
    len(ACTS) == 10 and len(SECTIONS) >= 51
    and len(IPC_BNS_MAPPINGS) >= 17 and len(KG_EDGES) >= 15
    and len(BENCHMARK_QUESTIONS) >= 25 and schema_ok
)
REPORT["seed"] = {
    "acts": {"count": len(ACTS), "expected": 10, "titles": [a["short_title"] for a in ACTS]},
    "sections": {"count": len(SECTIONS), "expected_min": 51, "per_act": dict(per_act)},
    "ipc_bns_seed_pairs": {"count": len(IPC_BNS_MAPPINGS), "bidirectional_after_load": len(IPC_BNS_MAPPINGS) * 2},
    "kg_edges": {"count": len(KG_EDGES)},
    "benchmark_questions": {"count": len(BENCHMARK_QUESTIONS), "expected_min": 25,
                            "difficulties": dict(difficulty_counter)},
    "baseline_passed": seed_ok,
}
P(f"  Acts                    = {len(ACTS)}/10")
P(f"  Sections                = {len(SECTIONS)}/>=51")
P(f"  IPC-BNS seed pairs      = {len(IPC_BNS_MAPPINGS)} (x2 after bidirectional loader)")
P(f"  KG edges                = {len(KG_EDGES)}")
P(f"  Benchmark questions     = {len(BENCHMARK_QUESTIONS)}/>=25   "
  f"(easy/medium/hard={difficulty_counter.get('easy',0)}/{difficulty_counter.get('medium',0)}/{difficulty_counter.get('hard',0)})")
P(f"  Schema hard constraints = {'PASS' if schema_ok else f'FAIL: {list(missing_by_field.keys())}'}")

P("")
P("METRIC ARITHMETIC (synthetic ranked list):")
from nyaya.evaluation import recall_at_k, precision_at_k, reciprocal_rank
relevant = {2, 5, 9, 17, 21}
retrieved = [2, 55, 9, 3, 17, 8, 5, 10, 22, 4, 21, 30]
r5 = recall_at_k(relevant, retrieved, 5)
r10 = recall_at_k(relevant, retrieved, 10)
p10 = precision_at_k(relevant, retrieved, 10)
mrr = reciprocal_rank(relevant, retrieved)
EXPECTED = {"recall_at_5": 3/5, "recall_at_10": 4/5, "precision_at_10": 4/10, "mrr": 1.0}
validated_top10 = {2: True, 55: False, 9: True, 3: False, 17: True, 8: False, 5: True, 10: False, 22: False, 4: True}
hallucinated = sum(1 for rid in retrieved[:10] if rid not in relevant and validated_top10.get(rid, False) is False)
hall_q = 1.0 if hallucinated > 0 else 0.0
arithmetic_ok = (math.isclose(r5, EXPECTED["recall_at_5"]) and math.isclose(r10, EXPECTED["recall_at_10"])
                 and math.isclose(p10, EXPECTED["precision_at_10"]) and math.isclose(mrr, EXPECTED["mrr"]))
REPORT["metrics_smoke"] = {
    "relevant": sorted(relevant), "retrieved": retrieved,
    "recall_at_5": round(r5, 4), "recall_at_10": round(r10, 4),
    "precision_at_10": round(p10, 4), "mrr": round(mrr, 4),
    "hallucination_items": hallucinated, "hallucination_rate_q_level": round(hall_q, 4),
    "expected": {k: round(v, 4) for k, v in EXPECTED.items()},
    "arithmetic_exact_match": arithmetic_ok,
}
P(f"  Recall@5     = {r5:.4f}   expected {EXPECTED['recall_at_5']:.4f}   {'PASS' if math.isclose(r5, EXPECTED['recall_at_5']) else 'FAIL'}")
P(f"  Recall@10    = {r10:.4f}   expected {EXPECTED['recall_at_10']:.4f}   {'PASS' if math.isclose(r10, EXPECTED['recall_at_10']) else 'FAIL'}")
P(f"  Precision@10 = {p10:.4f}   expected {EXPECTED['precision_at_10']:.4f}   {'PASS' if math.isclose(p10, EXPECTED['precision_at_10']) else 'FAIL'}")
P(f"  MRR          = {mrr:.4f}   expected {EXPECTED['mrr']:.4f}        {'PASS' if math.isclose(mrr, EXPECTED['mrr']) else 'FAIL'}")
P(f"  Hallucinated items count = {hallucinated}")
P(f"  Arithmetic exact match   → {'PASS' if arithmetic_ok else 'FAIL'}")

P("")
P("BM25 + HYBRID + CITATION VALIDATOR SMOKE:")
from nyaya.search.bm25_index import BM25Corpus
from nyaya.search.hybrid import combine_scores, validate_citations, HybridCandidate
class FakeS:
    def __init__(self, sid, title, bare_text, keywords=None):
        self.id = sid; self.title = title; self.bare_text = bare_text
        self.keywords = keywords or []; self.plain_language = None
corpus = [
    FakeS(1, "Murder Punishment", "Whoever commits murder shall be punished with death or imprisonment for life.", ["murder","death","punishment","life"]),
    FakeS(2, "Culpable Homicide Not Amounting to Murder", "Culpable homicide not amounting to murder carries up to ten years imprisonment plus fine.", ["culpable","homicide","imprisonment"]),
    FakeS(3, "Theft Definition", "Dishonest taking of movable property out of possession without consent is theft.", ["theft","property","dishonest"]),
    FakeS(4, "Husband Cruelty 498A", "Cruelty by husband or his relatives includes dowry harassment and conduct likely to cause suicide.", ["cruelty","dowry","498a","suicide"]),
    FakeS(5, "Rape 376 Punishment", "Rape is punished with minimum ten years to life imprisonment and fine.", ["rape","imprisonment","376"]),
    FakeS(6, "Dowry Death 304B", "Where a woman dies within seven years of marriage after dowry harassment it is deemed dowry death.", ["dowry","death","304b","harassment"]),
    FakeS(7, "PMLA Section 3", "Any direct or indirect involvement in concealment or use of proceeds of crime is money-laundering.", ["pmla","money","laundering","proceeds","crime"]),
    FakeS(8, "BNS Murder 108", "Whoever commits murder shall be punished with death or imprisonment for life and fine.", ["bns","murder","death","life"]),
    FakeS(9, "SCST Atrocities 3", "Atrocities against SC/ST by non-SC/ST include tonsuring, garlanding chappals, gang rape.", ["scst","atrocity","poa","gang rape"]),
    FakeS(10, "IT Act 66", "Section 66 IT Act punishes dishonest and fraudulent computer misuse with 3 years or ₹5 lakh.", ["it act","66","hacking","dishonest"]),
]
bm25 = BM25Corpus.build(corpus)
bhits = bm25.query("murder death punishment", top_k=8)
dhits = [(1, 0.92), (8, 0.88), (5, 0.30), (2, 0.25), (3, 0.08), (7, 0.05)]
combined = combine_scores(bhits, dhits)
for c in combined.values():
    obj = next((x for x in corpus if x.id == c.section_id), None)
    c.section_obj = obj
    if obj:
        c.title = obj.title
        c.bare_text = obj.bare_text
ordered = sorted(combined.values(), key=lambda c: c.combined_score, reverse=True)
validated = validate_citations("murder death punishment", ordered)
hybrid_ok = (
    len(ordered) >= 2 and ordered[0].section_id == 1 and ordered[1].section_id == 8
    and sum(1 for _, ok, _, _ in validated if ok) >= 1
)
valid_rows = []
for c, ok, sim, snips in validated[:6]:
    valid_rows.append({"section_id": c.section_id, "title": c.title[:60], "combined": round(c.combined_score, 3),
                       "citation_validated": ok, "citation_similarity": round(sim, 3)})
REPORT["hybrid_smoke"] = {
    "query": "murder death punishment",
    "bm25_top": [[sid, round(sc, 3)] for sid, sc in bhits[:6]],
    "combined_ranked": [[c.section_id, c.title[:50], round(c.combined_score, 3)] for c in ordered[:6]],
    "validated_top6": valid_rows,
    "expected": {"rank_1_section_id": 1, "rank_2_section_id": 8, "at_least_1_validated": True},
    "expectations_met": hybrid_ok,
}
P(f"  BM25 top 5: {[[sid, round(sc, 2)] for sid, sc in bhits[:5]]}")
for i, c in enumerate(ordered[:6], start=1):
    marker = "  ★" if c.section_id in (1, 8) else ""
    P(f"    #{i}  id={c.section_id}  score={c.combined_score:.3f}  {c.title[:50]}{marker}")
P(f"  Rank 1 = Sec 1? {'✓' if ordered and ordered[0].section_id==1 else '✗'}")
P(f"  Rank 2 = Sec 8? {'✓' if len(ordered)>=2 and ordered[1].section_id==8 else '✗'}")
P(f"  ≥ 1 validated result?   {'✓' if any(ok for _,ok,_,_ in validated) else '✗'}")
P(f"  Hybrid expectations → {'PASS' if hybrid_ok else 'FAIL'}")

REPORT["elapsed_seconds"] = round(time.perf_counter() - _start, 3)
pass_gate = all([all_import_ok, seed_ok, arithmetic_ok, hybrid_ok])
REPORT["pass_gate"] = pass_gate
REPORT["pass_gate_breakdown"] = {
    "all_modules_import": all_import_ok,
    "baseline_seed_and_schema": seed_ok,
    "metric_arithmetic_exact": arithmetic_ok,
    "hybrid_rank_expectations": hybrid_ok,
}
P("")
P(f"OVERALL GATE → {'✅ PASS' if pass_gate else '⚠️ FAIL'}")

out.write_text(json.dumps(REPORT, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
latest = EVD / "LATEST.json"
try: latest.unlink()
except FileNotFoundError: pass
latest.write_text(json.dumps(REPORT, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
text_log.write_text("\n".join(captured) + f"\n\nEvidence JSON: {out}\nPass gate = {'PASS' if pass_gate else 'FAIL'}\n", encoding="utf-8")
# Also write exit code marker so we can read later
(EVD / "last_exit_code.txt").write_text("0" if pass_gate else "1")
sys.exit(0 if pass_gate else 1)
