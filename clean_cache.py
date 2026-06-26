
from pathlib import Path
import shutil

base_dir = Path(__file__).parent

for pycache in base_dir.rglob("__pycache__"):
    if pycache.is_dir():
        print(f"Deleting {pycache}")
        shutil.rmtree(pycache)

for pyc in base_dir.rglob("*.pyc"):
    print(f"Deleting {pyc}")
    pyc.unlink()

print("Done cleaning cache!")
