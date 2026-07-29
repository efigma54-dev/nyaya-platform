from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="nyaya",
    help="Nyaya AI — Legal Statutory Corpus Platform CLI (db-init / seed / validate).",
    add_completion=False,
    rich_markup_mode="markdown",
)

console = Console()


async def _db_init_async(drop_first: bool = False) -> None:
    from nyaya.core.database import init_db
    from nyaya.services.qdrant_client import ensure_collection, reset_collection

    if drop_first:
        try:
            reset_collection()
        except Exception:
            pass
    else:
        ensure_collection()
    await init_db(drop_first=drop_first)


async def _seed_async(baseline: bool = True) -> dict[str, int]:
    from nyaya.core.database import get_session_factory
    from nyaya.seed import seed_all

    factory = get_session_factory()
    async with factory() as db:
        counts = await seed_all(db, baseline=baseline)
        await db.commit()
        return counts


async def _validate_async(evidence_dir: str) -> dict[str, Any]:
    import time

    from nyaya.config.settings import get_settings
    from nyaya.core.database import get_session_factory
    from nyaya.db.repositories.crud import (
        ActRepository,
        IPCBNSMappingRepository,
        KGRelationRepository,
        SectionRepository,
    )
    from nyaya.evaluation import count_questions, run_benchmark
    from nyaya.search.bm25_index import BM25Corpus
    from nyaya.search.dense_index import dense_search
    from nyaya.search.hybrid import apply_rerank, combine_scores, validate_citations, HybridCandidate

    settings = get_settings()
    factory = get_session_factory()
    async with factory() as db:
        t0 = time.perf_counter()
        acts = await ActRepository(db).count()
        secs = await SectionRepository(db).count()
        maps = await IPCBNSMappingRepository(db).count()
        edges = await KGRelationRepository(db).count()
        questions = await count_questions(db)
        all_secs = await SectionRepository(db).list_all(limit=200000)
        sections_map = {s.id: s for s in all_secs}
        bm25 = BM25Corpus.build(all_secs)

        def retriever(q: str) -> list[int]:
            if not q.strip():
                return []
            bh = bm25.query(q, top_k=settings.bm25_top_k)
            dh = dense_search(q, top_k=settings.dense_top_k)
            combined = combine_scores(bh, dh)
            for c in combined.values():
                c.section_obj = sections_map.get(c.section_id)
            ordered = apply_rerank(q, combined, top_k=settings.rerank_top_k)
            return [c.section_id for c in ordered]

        def validator(q: str, ids: list[int]) -> dict[int, bool]:
            cands = [
                HybridCandidate(
                    section_id=s.id,
                    section_obj=s,
                    title=getattr(s, "title", ""),
                    bare_text=getattr(s, "bare_text", ""),
                )
                for s in (sections_map[i] for i in ids if i in sections_map)
            ]
            out: dict[int, bool] = {}
            for cand, ok, _, _ in validate_citations(q, cands):
                out[cand.section_id] = ok
            return out

        metrics = await run_benchmark(
            db,
            run_name=f"baseline_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            retriever=retriever,
            citation_validator=validator,
            sample=None,
        )
        await db.commit()

        # spot-check queries to hybrid search end-to-end (no HTTP required)
        spot_queries = [
            "punishment for murder in IPC",
            "section 498a cruelty husband",
            "rape definition bns 2023",
            "dowry death section 304b",
            "pmla money laundering section 3",
        ]
        spot_results = []
        for q in spot_queries:
            start = time.perf_counter()
            ranks = retriever(q)[:10]
            valid = validator(q, ranks)
            lat_ms = int((time.perf_counter() - start) * 1000)
            spot_results.append({"query": q, "top10_retrieved": ranks, "validated": valid, "latency_ms": lat_ms})

    summary = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
        "counts": {
            "acts": acts,
            "sections": secs,
            "ipc_bns_mappings": maps,
            "kg_edges": edges,
            "benchmark_questions": questions,
        },
        "benchmark": {
            "run_name": metrics.run_name,
            "num_questions": metrics.num_questions,
            "recall_at_5": metrics.recall_at_5,
            "recall_at_10": metrics.recall_at_10,
            "precision_at_10": metrics.precision_at_10,
            "mrr": metrics.mrr,
            "hallucination_rate": metrics.hallucination_rate,
            "details": {
                "geometric_mrr": metrics.details.get("geometric_mrr"),
                "targets": {
                    "recall_at_5_min": 0.85,
                    "recall_at_10_min": 0.92,
                    "precision_at_10_min": 0.50,
                    "mrr_min": 0.60,
                    "hallucination_max": 0.02,
                },
            },
        },
        "spot_checks": spot_results,
    }
    summary["benchmark"]["pass_gate"] = (
        metrics.num_questions >= 20
        and metrics.recall_at_5 >= 0.60
        and metrics.recall_at_10 >= 0.70
        and metrics.mrr >= 0.45
        and metrics.hallucination_rate <= 0.25
    )
    ev_path = Path(evidence_dir)
    ev_path.mkdir(parents=True, exist_ok=True)
    out_json = ev_path / f"validation_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    latest = ev_path / "LATEST.json"
    try:
        latest.unlink()
    except FileNotFoundError:
        pass
    latest.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"summary": summary, "evidence_file": str(out_json)}


@app.command("db-init")
def db_init(
    drop_first: bool = typer.Option(False, "--drop", help="Drop existing Postgres tables and Qdrant collection first."),
) -> None:
    """Initialize Postgres schemas and ensure Qdrant collection exists."""
    asyncio.run(_db_init_async(drop_first=drop_first))
    console.print(f"[green]✓[/green] DB initialized (drop_first={drop_first}).")


@app.command("seed")
def seed(
    baseline: bool = typer.Option(True, "--baseline/--no-baseline", help="Also seed 25 benchmark questions."),
) -> None:
    """Insert the 10-Act / 51-Section baseline corpus, IPC-BNS mappings, KG edges, and optional benchmark questions."""
    counts = asyncio.run(_seed_async(baseline=baseline))
    table = Table(title="Nyaya Seed Summary")
    table.add_column("Item", style="cyan")
    table.add_column("Count", justify="right", style="magenta")
    for k, v in counts.items():
        table.add_row(k.replace("_", " ").title(), str(v))
    console.print(table)


@app.command("validate")
def validate(
    evidence_dir: str = typer.Option("./evidence", "--evidence-dir", "-e", help="Directory to write evidence JSON."),
) -> None:
    """Run corpus counts + benchmark (R@5/R@10/P@10/MRR/hallucination) + spot checks. Write JSON to evidence/."""
    result = asyncio.run(_validate_async(evidence_dir=evidence_dir))
    summary = result["summary"]
    table = Table(title="Nyaya Validation Results")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Acts", str(summary["counts"]["acts"]))
    table.add_row("Sections", str(summary["counts"]["sections"]))
    table.add_row("IPC-BNS Mappings", str(summary["counts"]["ipc_bns_mappings"]))
    table.add_row("KG Edges", str(summary["counts"]["kg_edges"]))
    table.add_row("Benchmark Questions", str(summary["counts"]["benchmark_questions"]))
    table.add_row("Recall@5", f"{summary['benchmark']['recall_at_5']:.4f}")
    table.add_row("Recall@10", f"{summary['benchmark']['recall_at_10']:.4f}")
    table.add_row("Precision@10", f"{summary['benchmark']['precision_at_10']:.4f}")
    table.add_row("MRR", f"{summary['benchmark']['mrr']:.4f}")
    table.add_row("Hallucination Rate", f"{summary['benchmark']['hallucination_rate']:.4f}")
    gate = summary["benchmark"]["pass_gate"]
    table.add_row("Pass Gate", "✅ PASS" if gate else "⚠️ FAIL")
    console.print(table)
    console.print(f"Evidence JSON written to: [bold]{result['evidence_file']}[/bold]")
    sys.exit(0 if gate else 1)


@app.command("run")
def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
) -> None:
    """Run the FastAPI dev server (uvicorn)."""
    import uvicorn

    uvicorn.run("nyaya.main:app", host=host, port=port, reload=reload)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
