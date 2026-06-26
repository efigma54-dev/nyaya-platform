
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_NORMALIZED = BASE_DIR / "data" / "normalized"

for json_file in DATA_NORMALIZED.glob("*.json"):
    print(f"\nChecking {json_file.name}")
    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    sections = data["sections"]
    seen_numbers = {}
    for i, sec in enumerate(sections):
        num = sec["section"]
        if num in seen_numbers:
            print(f"  Duplicate {num} at index {i} (first at {seen_numbers[num]})")
        else:
            seen_numbers[num] = i

print("\nDone")
