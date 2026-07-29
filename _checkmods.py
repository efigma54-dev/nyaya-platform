import sys
from pathlib import Path
root = Path(__file__).resolve().parent
mods = {}
for name in [
    "fastapi", "pydantic", "sqlalchemy", "alembic", "asyncpg", "httpx",
    "redis", "qdrant_client", "numpy", "scipy", "sklearn", "rank_bm25",
    "sentence_transformers", "jose", "passlib", "email_validator",
    "typer", "rich", "dotenv", "orjson",
]:
    try:
        m = __import__(name)
        v = getattr(m, "__version__", "n/a")
        mods[name] = f"ok ({v})"
    except Exception as e:
        mods[name] = f"FAIL: {type(e).__name__}"
(root / "evidence" / "installed_modules.txt").write_text(
    "\n".join(f"{k:25s} {v}" for k, v in mods.items()) + "\n", encoding="utf-8")
sys.exit(0)
