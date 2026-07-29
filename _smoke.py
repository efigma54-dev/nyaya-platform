from pathlib import Path
import sys, datetime
p = Path(__file__).resolve().parent / "evidence" / "smoke_check.txt"
p.parent.mkdir(exist_ok=True)
p.write_text(f"Hello from Python!\n{sys.version}\n{datetime.datetime.utcnow().isoformat()}\n", encoding="utf-8")
sys.exit(0)
