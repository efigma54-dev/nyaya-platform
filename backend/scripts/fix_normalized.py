
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_NORMALIZED = BASE_DIR / "data" / "normalized"

# Fix BNS
bns_path = DATA_NORMALIZED / "bharatiya_nyaya_sanhita_2023.json"
with bns_path.open("r", encoding="utf-8") as f:
    bns = json.load(f)

# Find the first duplicate section 1 and cut off there
sections = []
seen_numbers = set()
for sec in bns["sections"]:
    num = sec["section"]
    if num in seen_numbers:
        break
    seen_numbers.add(num)
    sections.append(sec)

bns["sections"] = sections
with bns_path.open("w", encoding="utf-8") as f:
    json.dump(bns, f, indent=2, ensure_ascii=False)

print("Fixed BNS! Now has", len(sections), "sections")
