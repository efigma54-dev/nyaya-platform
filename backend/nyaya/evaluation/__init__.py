from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Callable, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nyaya.db.models.schema import BenchmarkQuestion, BenchmarkRun


@dataclass
class EvalMetrics:
    run_name: str
    num_questions: int
    recall_at_5: float
    recall_at_10: float
    precision_at_10: float
    mrr: float
    hallucination_rate: float
    details: dict


def recall_at_k(relevant: set[int], retrieved: Sequence[int], k: int) -> float:
    if not relevant:
        return 1.0 if not retrieved else 0.0
    top = set(retrieved[:k])
    return float(len(top & relevant)) / float(len(relevant))


def precision_at_k(relevant: set[int], retrieved: Sequence[int], k: int) -> float:
    if k <= 0:
        return 0.0
    top = list(retrieved[:k])
    if not top:
        return 0.0
    return float(len(set(top) & relevant)) / float(len(top))


def reciprocal_rank(relevant: set[int], retrieved: Sequence[int]) -> float:
    for i, rid in enumerate(retrieved, start=1):
        if rid in relevant:
            return 1.0 / float(i)
    return 0.0


async def retrieve_benchmark_questions(db: AsyncSession, limit: int | None = None) -> list[BenchmarkQuestion]:
    stmt = select(BenchmarkQuestion).order_by(BenchmarkQuestion.id.asc())
    if limit is not None:
        stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def count_questions(db: AsyncSession) -> int:
    res = await db.execute(select(func.count(BenchmarkQuestion.id)))
    return int(res.scalar_one())


async def run_benchmark(
    db: AsyncSession,
    run_name: str,
    retriever: Callable[[str], list[int]],
    citation_validator: Callable[[str, list[int]], dict[int, bool]] | None = None,
    sample: int | None = None,
) -> EvalMetrics:
    questions = await retrieve_benchmark_questions(db, limit=sample)
    if not questions:
        return EvalMetrics(
            run_name=run_name,
            num_questions=0,
            recall_at_5=0.0,
            recall_at_10=0.0,
            precision_at_10=0.0,
            mrr=0.0,
            hallucination_rate=0.0,
            details={"error": "no_benchmark_questions"},
        )
    r5_sum = 0.0
    r10_sum = 0.0
    p10_sum = 0.0
    rr_sum = 0.0
    hallucinated = 0
    per_q: list[dict] = []
    for q in questions:
        rel = set(int(x) for x in q.relevant_section_ids)
        retrieved = retriever(q.query)
        r5 = recall_at_k(rel, retrieved, 5)
        r10 = recall_at_k(rel, retrieved, 10)
        p10 = precision_at_k(rel, retrieved, 10)
        rr = reciprocal_rank(rel, retrieved)
        r5_sum += r5
        r10_sum += r10
        p10_sum += p10
        rr_sum += rr
        hallucinated_count = 0
        if citation_validator is not None:
            validation = citation_validator(q.query, retrieved[:10])
            for rid, ok in validation.items():
                if not ok and rid not in rel:
                    hallucinated_count += 1
        if hallucinated_count > 0:
            hallucinated += 1
        per_q.append({"qid": q.id, "r5": r5, "r10": r10, "p10": p10, "rr": rr, "hallucinated": hallucinated_count})
    n = len(questions)
    metrics = EvalMetrics(
        run_name=run_name,
        num_questions=n,
        recall_at_5=round(r5_sum / n, 4) if n else 0.0,
        recall_at_10=round(r10_sum / n, 4) if n else 0.0,
        precision_at_10=round(p10_sum / n, 4) if n else 0.0,
        mrr=round(rr_sum / n, 4) if n else 0.0,
        hallucination_rate=round(hallucinated / n, 4) if n else 0.0,
        details={
            "per_question": per_q,
            "geometric_mrr": round(math.exp(sum(math.log1p(x["rr"]) for x in per_q) / n) - 1, 4),
        },
    )
    obj = BenchmarkRun(
        run_name=run_name,
        recall_at_5=metrics.recall_at_5,
        recall_at_10=metrics.recall_at_10,
        precision_at_10=metrics.precision_at_10,
        mrr=metrics.mrr,
        hallucination_rate=metrics.hallucination_rate,
        num_questions=metrics.num_questions,
        details={"details": metrics.details},
    )
    db.add(obj)
    await db.flush()
    return metrics
