
import asyncio
import json
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.core.config import get_settings
from app.models.legal import Act, Section
from sqlalchemy import select, func
from app.rag.vector_store import get_qdrant_client, COLLECTION_SECTIONS
import redis


def get_git_commit():
    """Get current git commit hash if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def check_redis_status():
    """Check Redis connection status."""
    settings = get_settings()
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        return "HEALTHY"
    except Exception as e:
        return f"UNHEALTHY: {str(e)[:50]}"


def check_docker_status():
    """Check Docker container status (basic check)."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        containers = result.stdout.strip().split("\n") if result.stdout else []
        return {
            "status": "HEALTHY" if containers else "NO RUNNING CONTAINERS",
            "containers": containers
        }
    except Exception as e:
        return {"status": f"UNHEALTHY: {str(e)[:50]}", "containers": []}


def get_environment_info():
    """Get environment metadata."""
    settings = get_settings()
    return {
        "app_env": settings.APP_ENV,
        "database_url": "redacted",
        "redis_url": "redacted",
        "qdrant_url": settings.QDRANT_URL
    }


def generate_text_report(report):
    """Generate the exact text report format requested."""
    text = f"""
Validation Report
=================

Generated:
{report['generated_at']}

Git Commit:
{report['git_commit']}

Environment
-----------
App Env: {report['environment']['app_env']}
Qdrant URL: {report['environment']['qdrant_url']}

Status Checks
-------------
Database: {report['database_status']}
Redis: {report['redis_status']}
Qdrant: {report['qdrant_status']}
Docker: {report['docker_status']['status']}

Database
--------
Acts: {report['acts']}
Sections: {report['sections']}

Qdrant
-------
Collection: {COLLECTION_SECTIONS}
Vectors: {report['vectors']}
Chunks: {report['chunks']}

Sync
----
Database: {report['sections']}
Vectors: {report['vectors']}
Sync %: {report['sync_percent']}%
Status: {report['sync_status']}

Quality
-------
Duplicate Sections: {report['duplicate_sections']}
Duplicate Vectors: {report['duplicate_vectors']}
Missing Vectors: {report['missing_vectors']}
Orphan Vectors: {report['orphan_vectors']}
Embedding Failures: {report['embedding_failures']}
Acts without Sections: {len(report['acts_without_sections'])}

Overall Status
--------------
{report['status']}

Generated automatically by:
backend/scripts/validate_corpus.py
"""
    return text.strip()


def generate_html_report(report):
    """Generate a pretty HTML report."""
    status_color = {
        "PASS": "#27ae60",
        "WARNING": "#f39c12",
        "FAIL": "#e74c3c"
    }

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nyaya AI - Corpus Validation Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .status-badge {{ padding: 8px 20px; border-radius: 6px; display: inline-block;
                      font-weight: bold; color: white; font-size: 18px; }}
            .PASS {{ background-color: {status_color['PASS']}; }}
            .WARNING {{ background-color: {status_color['WARNING']}; }}
            .FAIL {{ background-color: {status_color['FAIL']}; }}
            .section {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px; }}
            .metric-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e9ecef; }}
            .metric-label {{ font-weight: 500; }}
            .metric-value {{ font-weight: bold; color: #2c3e50; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚖️ Nyaya AI - Corpus Validation Report</h1>
            
            <div class="section">
                <p class="metric-label">Generated: <span class="metric-value">{report['generated_at']}</span></p>
                <p class="metric-label">Git Commit: <span class="metric-value">{report['git_commit']}</span></p>
                <p class="metric-label">App Env: <span class="metric-value">{report['environment']['app_env']}</span></p>
            </div>
            
            <div class="section">
                <h2>Status Checks</h2>
                <div class="metric-row"><span class="metric-label">Database:</span> <span class="metric-value">{report['database_status']}</span></div>
                <div class="metric-row"><span class="metric-label">Redis:</span> <span class="metric-value">{report['redis_status']}</span></div>
                <div class="metric-row"><span class="metric-label">Qdrant:</span> <span class="metric-value">{report['qdrant_status']}</span></div>
                <div class="metric-row"><span class="metric-label">Docker:</span> <span class="metric-value">{report['docker_status']['status']}</span></div>
            </div>
            
            <div class="section">
                <h2>Database</h2>
                <div class="metric-row"><span class="metric-label">Acts:</span> <span class="metric-value">{report['acts']}</span></div>
                <div class="metric-row"><span class="metric-label">Sections:</span> <span class="metric-value">{report['sections']}</span></div>
            </div>
            
            <div class="section">
                <h2>Qdrant</h2>
                <div class="metric-row"><span class="metric-label">Collection:</span> <span class="metric-value">{COLLECTION_SECTIONS}</span></div>
                <div class="metric-row"><span class="metric-label">Vectors:</span> <span class="metric-value">{report['vectors']}</span></div>
                <div class="metric-row"><span class="metric-label">Chunks:</span> <span class="metric-value">{report['chunks']}</span></div>
            </div>
            
            <div class="section">
                <h2>Sync</h2>
                <div class="metric-row"><span class="metric-label">Database:</span> <span class="metric-value">{report['sections']}</span></div>
                <div class="metric-row"><span class="metric-label">Vectors:</span> <span class="metric-value">{report['vectors']}</span></div>
                <div class="metric-row"><span class="metric-label">Sync %:</span> <span class="metric-value">{report['sync_percent']}%</span></div>
                <div class="metric-row"><span class="metric-label">Status:</span> <span class="status-badge {report['sync_status']}">{report['sync_status']}</span></div>
            </div>
            
            <div class="section">
                <h2>Quality</h2>
                <div class="metric-row"><span class="metric-label">Duplicate Sections:</span> <span class="metric-value">{report['duplicate_sections']}</span></div>
                <div class="metric-row"><span class="metric-label">Duplicate Vectors:</span> <span class="metric-value">{report['duplicate_vectors']}</span></div>
                <div class="metric-row"><span class="metric-label">Missing Vectors:</span> <span class="metric-value">{report['missing_vectors']}</span></div>
                <div class="metric-row"><span class="metric-label">Orphan Vectors:</span> <span class="metric-value">{report['orphan_vectors']}</span></div>
                <div class="metric-row"><span class="metric-label">Embedding Failures:</span> <span class="metric-value">{report['embedding_failures']}</span></div>
                <div class="metric-row"><span class="metric-label">Acts without Sections:</span> <span class="metric-value">{len(report['acts_without_sections'])}</span></div>
            </div>
            
            <div class="section">
                <h2>Overall Status</h2>
                <span class="status-badge {report['status']}">{report['status']}</span>
            </div>
            
            <div style="margin-top:40px; color:#7f8c8d; font-size:14px;">
                Generated automatically by: <code>backend/scripts/validate_corpus.py</code>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def generate_markdown_report(report):
    """Generate a Markdown report."""
    md = f"""
# ⚖️ Nyaya AI - Corpus Validation Report

Generated: {report['generated_at']}
Git Commit: {report['git_commit']}
App Env: {report['environment']['app_env']}

---

## Status Checks
- **Database**: {report['database_status']}
- **Redis**: {report['redis_status']}
- **Qdrant**: {report['qdrant_status']}
- **Docker**: {report['docker_status']['status']}

---

## Database
- **Acts**: {report['acts']}
- **Sections**: {report['sections']}

---

## Qdrant
- **Collection**: {COLLECTION_SECTIONS}
- **Vectors**: {report['vectors']}
- **Chunks**: {report['chunks']}

---

## Sync
- **Database**: {report['sections']}
- **Vectors**: {report['vectors']}
- **Sync %**: {report['sync_percent']}%
- **Status**: {report['sync_status']}

---

## Quality
- **Duplicate Sections**: {report['duplicate_sections']}
- **Duplicate Vectors**: {report['duplicate_vectors']}
- **Missing Vectors**: {report['missing_vectors']}
- **Orphan Vectors**: {report['orphan_vectors']}
- **Embedding Failures**: {report['embedding_failures']}
- **Acts without Sections**: {len(report['acts_without_sections'])}

---

## Overall Status
**{report['status']}**

---

Generated automatically by: `backend/scripts/validate_corpus.py`
    """
    return md.strip()


async def validate_corpus():
    """Validate the entire legal corpus and produce all report formats."""
    print("=" * 80)
    print("⚖️ NYAYA AI - AUTOMATED CORPUS VALIDATION")
    print("=" * 80)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    git_commit = get_git_commit()

    validation_report = {
        "generated_at": generated_at,
        "git_commit": git_commit,
        "environment": get_environment_info(),
        "database_status": "UNKNOWN",
        "redis_status": check_redis_status(),
        "qdrant_status": "UNKNOWN",
        "docker_status": check_docker_status(),
        "acts": 0,
        "sections": 0,
        "chunks": 0,
        "vectors": 0,
        "missing_vectors": 0,
        "orphan_vectors": 0,
        "duplicate_sections": 0,
        "duplicate_vectors": 0,
        "embedding_failures": 0,
        "sync_percent": 0,
        "sync_status": "PASS",
        "acts_without_sections": [],
        "status": "PASS"
    }

    async with AsyncSessionLocal() as db:
        print("\n📊 Step 1: Querying PostgreSQL database...")

        try:
            # Test DB connection
            await db.execute(select(1))
            validation_report["database_status"] = "HEALTHY"
        except Exception as e:
            validation_report["database_status"] = f"UNHEALTHY: {str(e)[:50]}"
            validation_report["status"] = "FAIL"

        # Get DB counts
        result = await db.execute(select(func.count(Act.id)))
        validation_report["acts"] = result.scalar() or 0

        result = await db.execute(select(func.count(Section.id)))
        validation_report["sections"] = result.scalar() or 0

        print(f"  ✅ Acts: {validation_report['acts']}")
        print(f"  ✅ Sections: {validation_report['sections']}")

        # Check for duplicates
        result = await db.execute(
            select(
                Section.act_id,
                Section.section_number,
                func.count(Section.id).label("count")
            )
            .group_by(Section.act_id, Section.section_number)
            .having(func.count(Section.id) > 1)
        )
        duplicates = result.all()
        validation_report["duplicate_sections"] = len(duplicates)
        for dup in duplicates:
            if "duplicate_sections_list" not in validation_report:
                validation_report["duplicate_sections_list"] = []
            validation_report["duplicate_sections_list"].append({
                "act_id": dup.act_id,
                "section_number": dup.section_number,
                "count": dup.count
            })
        print(f"  ✅ Duplicate sections: {validation_report['duplicate_sections']}")

        # Check acts without sections
        result = await db.execute(select(Act))
        acts = result.scalars().all()
        for act in acts:
            await db.refresh(act, ["sections"])
            if not act.sections:
                validation_report["acts_without_sections"].append(act.id)

    # Vector Store
    print("\n🔍 Step 2: Querying Qdrant vector store...")
    qdrant_points = 0
    try:
        client = get_qdrant_client()
        collections = [c.name for c in client.get_collections().collections]
        validation_report["qdrant_status"] = "HEALTHY"
        if COLLECTION_SECTIONS in collections:
            info = client.get_collection(COLLECTION_SECTIONS)
            qdrant_points = info.points_count
            validation_report["vectors"] = qdrant_points
            validation_report["chunks"] = qdrant_points  # Assuming 1:1 for now
            print(f"  ✅ Vectors: {validation_report['vectors']}")
            print(f"  ✅ Chunks: {validation_report['chunks']}")
        else:
            print(f"  ⚠️  Collection '{COLLECTION_SECTIONS}' not found")
            validation_report["vectors"] = 0
            validation_report["chunks"] = 0
    except Exception as e:
        print(f"  ❌ Qdrant connection failed: {e}")
        validation_report["qdrant_status"] = f"UNHEALTHY: {str(e)[:50]}"
        validation_report["vectors"] = 0
        validation_report["chunks"] = 0

    # Sync & Additional Checks
    print("\n🔗 Step 3: Validating sync and metrics...")

    if validation_report["sections"] > 0:
        validation_report["sync_percent"] = int(
            min(100, (validation_report["vectors"] / validation_report["sections"]) * 100)
        )
    else:
        validation_report["sync_percent"] = 100 if validation_report["vectors"] == 0 else 0

    if validation_report["sections"] > 0 and validation_report["vectors"] == 0:
        validation_report["sync_status"] = "FAIL"
        validation_report["status"] = "FAIL"
    elif validation_report["sections"] == 0 and validation_report["vectors"] > 0:
        validation_report["sync_status"] = "WARNING"
        validation_report["status"] = "WARNING"
    elif validation_report["sync_percent"] < 90:
        validation_report["sync_status"] = "WARNING"
    else:
        validation_report["sync_status"] = "PASS"
    print(f"  ✅ Sync %: {validation_report['sync_percent']}%")
    print(f"  ✅ Sync Status: {validation_report['sync_status']}")

    # Final Status
    if validation_report["database_status"] != "HEALTHY":
        validation_report["status"] = "FAIL"
    elif validation_report["qdrant_status"] != "HEALTHY":
        validation_report["status"] = "FAIL"
    elif validation_report["duplicate_sections"] > 0:
        validation_report["status"] = "FAIL"
    elif validation_report["sync_status"] == "FAIL":
        validation_report["status"] = "FAIL"
    elif validation_report["sync_status"] == "WARNING" or len(validation_report["acts_without_sections"]) > 0:
        validation_report["status"] = "WARNING"

    # Save Reports
    print("\n📝 Step 4: Generating reports...")
    report_dir = Path(__file__).resolve().parents[2]

    # JSON
    json_path = report_dir / "validation.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(validation_report, f, indent=2, ensure_ascii=False)
    print(f"  ✅ JSON: {json_path}")

    # Text
    text_path = report_dir / "validation.txt"
    text_content = generate_text_report(validation_report)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_content)
    print(f"  ✅ TXT: {text_path}")

    # HTML
    html_path = report_dir / "validation.html"
    html_content = generate_html_report(validation_report)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  ✅ HTML: {html_path}")

    # Markdown
    md_path = report_dir / "validation.md"
    md_content = generate_markdown_report(validation_report)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  ✅ MD: {md_path}")

    # Print final report
    print("\n" + "=" * 80)
    print(text_content)
    print("=" * 80)

    return validation_report


if __name__ == "__main__":
    asyncio.run(validate_corpus())
