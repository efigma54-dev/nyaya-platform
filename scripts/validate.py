
#!/usr/bin/env python3
"""
Automated validation script for Nyaya AI.
Runs all checks and generates validation reports.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.legal import Section, Act
from app.rag.vector_store import get_qdrant_client, COLLECTION_SECTIONS
from sqlalchemy import func, select


class ValidationResult:
    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.results = {}
        self.overall_status = "PASS"

    def add_check(self, name: str, passed: bool, metrics: dict = None, error: str = None):
        self.results[name] = {
            "passed": passed,
            "metrics": metrics or {},
            "error": error,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        if not passed:
            self.overall_status = "FAIL"

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "overall_status": self.overall_status,
            "results": self.results
        }

    def to_markdown(self):
        md = []
        md.append("# NYAYA AI - COMPLETE LOCAL VALIDATION REPORT")
        md.append(f"\n**Date:** {self.timestamp}")
        md.append(f"**Environment:** Docker Compose (Local Development)")
        md.append(f"**Status:** {'✅ ALL VALIDATION STEPS PASSED' if self.overall_status == 'PASS' else '❌ SOME VALIDATION STEPS FAILED'}")
        md.append("\n---\n")

        for name, result in self.results.items():
            status_emoji = "✅" if result["passed"] else "❌"
            md.append(f"## {name} {status_emoji}")
            if result["metrics"]:
                md.append("\n| Metric | Value |")
                md.append("|--------|-------|")
                for key, value in result["metrics"].items():
                    md.append(f"| {key} | {value} |")
            if result["error"]:
                md.append(f"\n**Error:** {result['error']}")
            md.append("\n---\n")

        md.append("\n## Corpus Statistics")
        if "PostgreSQL Database" in self.results:
            metrics = self.results["PostgreSQL Database"]["metrics"]
            md.append(f"\n- **Total Acts:** {metrics.get('Total Acts', 'N/A')}")
            md.append(f"\n- **Total Sections:** {metrics.get('Total Sections', 'N/A')}")
            md.append(f"\n- **Active Sections:** {metrics.get('Active Sections', 'N/A')}")

        if "Qdrant Vector Store" in self.results:
            qdrant_metrics = self.results["Qdrant Vector Store"]["metrics"]
            md.append(f"\n- **Vectors Indexed:** {qdrant_metrics.get('Points Count', 'N/A')}")

        return "\n".join(md)


async def check_database(result: ValidationResult):
    print("\n[1/7] Checking PostgreSQL...")
    try:
        async with AsyncSessionLocal() as db:
            total_sections = await db.execute(select(func.count(Section.id)))
            total_sections = total_sections.scalar_one()

            active_sections = await db.execute(select(func.count(Section.id)).where(Section.is_active == True))
            active_sections = active_sections.scalar_one()

            total_acts = await db.execute(select(func.count(Act.id)))
            total_acts = total_acts.scalar_one()

            result.add_check(
                "PostgreSQL Database",
                True,
                {
                    "Total Sections": total_sections,
                    "Active Sections": active_sections,
                    "Total Acts": total_acts
                }
            )
            print("✅ PostgreSQL checks passed!")
    except Exception as e:
        result.add_check("PostgreSQL Database", False, error=str(e))
        print(f"❌ PostgreSQL check failed: {e}")


async def check_qdrant(result: ValidationResult):
    print("\n[2/7] Checking Qdrant...")
    try:
        client = get_qdrant_client()
        info = client.get_collection(COLLECTION_SECTIONS)
        points_count = info.points_count
        vectors_count = info.vectors_count

        result.add_check(
            "Qdrant Vector Store",
            True,
            {
                "Points Count": points_count,
                "Vectors Count": vectors_count,
                "Status": info.status.value
            }
        )
        print("✅ Qdrant checks passed!")
    except Exception as e:
        result.add_check("Qdrant Vector Store", False, error=str(e))
        print(f"❌ Qdrant check failed: {e}")


async def check_sync(result: ValidationResult):
    print("\n[3/7] Checking Database ↔ Qdrant Sync...")
    try:
        async with AsyncSessionLocal() as db:
            db_count = await db.execute(select(func.count(Section.id)).where(Section.is_active == True))
            db_count = db_count.scalar_one()

        client = get_qdrant_client()
        qdrant_info = client.get_collection(COLLECTION_SECTIONS)
        qdrant_count = qdrant_info.points_count

        sync_status = db_count == qdrant_count
        sync_percent = (qdrant_count / db_count * 100) if db_count > 0 else 0

        result.add_check(
            "Database ↔ Qdrant Sync",
            sync_status,
            {
                "Database Sections": db_count,
                "Qdrant Vectors": qdrant_count,
                "Sync Percentage": f"{sync_percent:.1f}%"
            }
        )
        if sync_status:
            print("✅ Sync check passed (100%)!")
        else:
            print(f"⚠️ Sync check: {sync_percent:.1f}%")
    except Exception as e:
        result.add_check("Database ↔ Qdrant Sync", False, error=str(e))
        print(f"❌ Sync check failed: {e}")


async def check_api_health(result: ValidationResult):
    print("\n[4/7] Checking API Health...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8000/health")
            response.raise_for_status()
            health_data = response.json()

            result.add_check(
                "API Health",
                health_data.get("status") == "ok",
                health_data
            )
            if health_data.get("status") == "ok":
                print("✅ API health check passed!")
            else:
                print("⚠️ API health check warning!")
    except Exception as e:
        result.add_check("API Health", False, error=str(e))
        print(f"❌ API health check failed: {e}")


async def check_redis(result: ValidationResult):
    print("\n[5/7] Checking Redis...")
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        pong = r.ping()

        result.add_check(
            "Redis Cache",
            pong,
            {"Status": "Connected" if pong else "Disconnected"}
        )
        if pong:
            print("✅ Redis check passed!")
    except Exception as e:
        result.add_check("Redis Cache", False, error=str(e))
        print(f"❌ Redis check failed: {e}")


async def check_docker_containers(result: ValidationResult):
    print("\n[6/7] Checking Docker Containers...")
    try:
        import subprocess

        containers = ["nyaya_postgres", "nyaya_redis", "nyaya_qdrant", "nyaya_api", "nyaya_frontend"]
        container_statuses = {}

        for container in containers:
            try:
                output = subprocess.check_output(
                    ["docker", "inspect", "-f", "{{.State.Health.Status}}", container],
                    text=True
                ).strip()
                container_statuses[container] = output
            except subprocess.CalledProcessError:
                try:
                    output = subprocess.check_output(
                        ["docker", "inspect", "-f", "{{.State.Status}}", container],
                        text=True
                    ).strip()
                    container_statuses[container] = output
                except:
                    container_statuses[container] = "Not Found"

        all_passed = all(status in ["healthy", "running"] for status in container_statuses.values())

        result.add_check(
            "Docker Containers",
            all_passed,
            container_statuses
        )
        if all_passed:
            print("✅ Docker containers check passed!")
        else:
            print("⚠️ Some containers have issues!")
    except Exception as e:
        result.add_check("Docker Containers", False, error=str(e))
        print(f"❌ Docker containers check failed: {e}")


async def check_rag_query(result: ValidationResult):
    print("\n[7/7] Checking RAG Query...")
    try:
        start_time = time.time()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/chat/",
                json={"query": "What is the punishment for theft under BNS?", "session_id": "validation-test"}
            )
            response.raise_for_status()
            chat_data = response.json()

        latency = (time.time() - start_time) * 1000

        has_answer = "answer" in chat_data and chat_data["answer"]
        has_sections = "sections" in chat_data and len(chat_data["sections"]) > 0

        result.add_check(
            "RAG Query",
            has_answer and has_sections,
            {
                "Latency (ms)": f"{latency:.1f}",
                "Sections Retrieved": len(chat_data.get("sections", [])),
                "Has Answer": has_answer
            }
        )
        if has_answer and has_sections:
            print("✅ RAG query check passed!")
        else:
            print("⚠️ RAG query check warning!")
    except Exception as e:
        result.add_check("RAG Query", False, error=str(e))
        print(f"❌ RAG query check failed: {e}")


async def main():
    print("=" * 60)
    print("Nyaya AI - Automated Validation")
    print("=" * 60)

    result = ValidationResult()

    await check_database(result)
    await check_qdrant(result)
    await check_sync(result)
    await check_api_health(result)
    await check_redis(result)
    await check_docker_containers(result)
    await check_rag_query(result)

    print("\n" + "=" * 60)
    print("Generating reports...")

    # Save JSON report
    with open("validation.json", "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)
    print("✅ Generated validation.json")

    # Save Markdown report
    with open("LOCAL_VALIDATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(result.to_markdown())
    print("✅ Generated LOCAL_VALIDATION_REPORT.md")

    print("=" * 60)
    print(f"Overall Status: {result.overall_status}")
    print("=" * 60)

    return 0 if result.overall_status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
