import sys
from pathlib import Path
import importlib.metadata as md
root = Path(__file__).resolve().parent
(root / "evidence" / "installed_packages.txt").write_text(
    "\n".join(sorted(set(d.metadata['Name'] for d in md.distributions()))) + "\n", encoding="utf-8")
print("OK")
sys.exit(0)
