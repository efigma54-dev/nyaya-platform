
#!/usr/bin/env python3
"""
RAG Evaluation Suite for Nyaya AI.
Measures retrieval quality (recall, precision) and response quality.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx
from app.core.config import settings
from app.models.legal import Section
from sqlalchemy import select
from app.core.database import AsyncSessionLocal


class RAGEvaluator:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        
        # Sample benchmark dataset
        self.benchmark_questions = [
            {
                "id": "bns_theft",
                "question": "What is the punishment for theft under BNS?",
                "expected_section_numbers": ["304"],
                "expected_act": "Bharatiya Nyaya Sanhita"
            },
            {
                "id": "bns_assault",
                "question": "What is the definition of assault under BNS?",
                "expected_section_numbers": ["221"],
                "expected_act": "Bharatiya Nyaya Sanhita"
            },
            {
                "id": "bnss_arrest",
                "question": "When can a police officer arrest without a warrant under BNSS?",
                "expected_section_numbers": ["41"],
                "expected_act": "Bharatiya Nagarik Suraksha Sanhita"
            },
            {
                "id": "constitution_fundamental_right",
                "question": "What is Article 19 of the Indian Constitution?",
                "expected_section_numbers": ["19"],
                "expected_act": "Constitution of India"
            },
            {
                "id": "bsa_evidence",
                "question": "What is hearsay evidence under BSA?",
                "expected_section_numbers": ["60"],
                "expected_act": "Bharatiya Sakshya Adhiniyam"
            }
        ]
        
        self.results = []
    
    async def get_section_by_number(self, section_number: str):
        """Get section from database by number for verification."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Section).where(Section.section_number == section_number)
            )
            return result.scalar_one_or_none()
    
    async def evaluate_single_question(self, question: Dict) -> Dict:
        """Evaluate a single question against the API."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/",
                    json={"query": question["question"], "session_id": f"eval-{question['id']}"}
                )
                response.raise_for_status()
                chat_data = response.json()
            
            latency = (time.time() - start_time) * 1000
            retrieved_sections = chat_data.get("sections", [])
            retrieved_section_numbers = [s.get("section_number") for s in retrieved_sections]
            
            # Calculate recall@k
            expected = set(question["expected_section_numbers"])
            retrieved = set(retrieved_section_numbers)
            
            recall_at_1 = float(list(expected)[0] in retrieved_section_numbers[:1]) if len(expected) > 0 else 0
            recall_at_5 = float(len(expected & retrieved) > 0) if len(expected) > 0 else 0
            precision = len(expected & retrieved) / len(retrieved) if len(retrieved) > 0 else 0
            
            # Check if answer is provided
            has_answer = "answer" in chat_data and chat_data["answer"] and len(chat_data["answer"]) > 50
            
            return {
                "question_id": question["id"],
                "question": question["question"],
                "latency_ms": round(latency, 1),
                "retrieved_sections_count": len(retrieved_sections),
                "retrieved_section_numbers": retrieved_section_numbers,
                "expected_section_numbers": question["expected_section_numbers"],
                "recall@1": recall_at_1,
                "recall@5": recall_at_5,
                "precision": round(precision, 2),
                "has_answer": has_answer,
                "passed": recall_at_5 == 1 and has_answer
            }
        
        except Exception as e:
            return {
                "question_id": question["id"],
                "question": question["question"],
                "error": str(e),
                "passed": False
            }
    
    async def run_evaluation(self) -> Dict:
        """Run full evaluation on all benchmark questions."""
        print("=" * 60)
        print("Nyaya AI - RAG Evaluation")
        print("=" * 60)
        
        for question in self.benchmark_questions:
            print(f"\nEvaluating: {question['question']}")
            result = await self.evaluate_single_question(question)
            self.results.append(result)
            
            status = "✅ PASS" if result.get("passed") else "❌ FAIL"
            print(f"  Status: {status}")
            if "latency_ms" in result:
                print(f"  Latency: {result['latency_ms']:.1f}ms")
                print(f"  Recall@1: {result['recall@1']:.0%}")
                print(f"  Recall@5: {result['recall@5']:.0%}")
        
        # Calculate aggregate metrics
        total = len(self.results)
        passed = len([r for r in self.results if r.get("passed")])
        avg_latency = sum(r["latency_ms"] for r in self.results if "latency_ms" in r) / total if total > 0 else 0
        avg_recall1 = sum(r["recall@1"] for r in self.results if "recall@1" in r) / total if total > 0 else 0
        avg_recall5 = sum(r["recall@5"] for r in self.results if "recall@5" in r) / total if total > 0 else 0
        avg_precision = sum(r["precision"] for r in self.results if "precision" in r) / total if total > 0 else 0
        
        aggregate = {
            "total_questions": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1),
            "avg_latency_ms": round(avg_latency, 1),
            "avg_recall@1": round(avg_recall1 * 100, 1),
            "avg_recall@5": round(avg_recall5 * 100, 1),
            "avg_precision": round(avg_precision * 100, 1),
            "question_results": self.results
        }
        
        return aggregate
    
    def generate_report(self, aggregate: Dict) -> str:
        """Generate markdown report from results."""
        md = []
        md.append("# Nyaya AI - RAG Evaluation Report")
        md.append("\n## Aggregate Metrics")
        md.append(f"- **Total Questions:** {aggregate['total_questions']}")
        md.append(f"- **Passed:** {aggregate['passed']} ({aggregate['pass_rate']}%)")
        md.append(f"- **Average Latency:** {aggregate['avg_latency_ms']}ms")
        md.append(f"- **Average Recall@1:** {aggregate['avg_recall@1']}%")
        md.append(f"- **Average Recall@5:** {aggregate['avg_recall@5']}%")
        md.append(f"- **Average Precision:** {aggregate['avg_precision']}%")
        
        md.append("\n## Question Breakdown")
        for res in aggregate['question_results']:
            status = "✅ PASS" if res.get("passed") else "❌ FAIL"
            md.append(f"\n### {res['question_id']}")
            md.append(f"- **Question:** {res['question']}")
            md.append(f"- **Status:** {status")
            if "error" not in res:
                md.append(f"- **Latency:** {res['latency_ms']}ms")
                md.append(f"- **Recall@1:** {res['recall@1']*100:.0f}%")
                md.append(f"- **Recall@5:** {res['recall@5']*100:.0f}%")
        
        return "\n".join(md)


async def main():
    evaluator = RAGEvaluator()
    aggregate = await evaluator.run_evaluation()
    
    # Save JSON report
    with open("rag_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2)
    print("\n✅ Saved rag_evaluation.json")
    
    # Save markdown report
    report_md = evaluator.generate_report(aggregate)
    with open("RAG_EVALUATION.md", "w", encoding="utf-8") as f:
        f.write(report_md)
    print("✅ Saved RAG_EVALUATION.md")
    
    print("\n" + "=" * 60)
    print(f"Overall Pass Rate: {aggregate['pass_rate']}%")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
