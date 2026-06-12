#!/usr/bin/env python3
"""
Run full Nyaya seed + embed pipeline in order.
Usage (repo root, with Postgres/Qdrant up):
  python scripts/run_seed_pipeline.py

Docker:
  docker compose run --rm api bash -c "export PYTHONPATH=/app NYAYA_BACKEND_PATH=/app && python /scripts/run_seed_pipeline.py"
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ORDER = [
    "seed_acts_metadata.py",
    "seed_bns_sections.py",
    "seed_corpus_v2.py",
    "embed_sections.py",
]


def main() -> int:
    print("Nyaya seed pipeline")
    print("=" * 50)
    for name in ORDER:
        path = SCRIPTS_DIR / name
        if not path.is_file():
            print(f"❌ Missing {path}")
            return 1
        print(f"\n▶ {name}")
        rc = subprocess.call([sys.executable, str(path)])
        if rc != 0:
            print(f"⚠️  {name} exited {rc} (continuing if idempotent)")
    print("\n✅ Pipeline finished. Verify Qdrant with:")
    print(
        '  docker compose run --rm api python -c "'
        "from app.rag.vector_store import get_qdrant_client, COLLECTION_NAME; "
        "c=get_qdrant_client(); print('vectors:', c.get_collection(COLLECTION_NAME).vectors_count)\""
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
