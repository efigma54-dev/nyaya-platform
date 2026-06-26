
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_NORMALIZED = BASE_DIR / "data" / "normalized"
file_path = DATA_NORMALIZED / "bharatiya_nyaya_sanhita_2023.json"

with file_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

for i in [0, 184, 185, 455, 456]:
    print(f"\n--- Index {i} ---")
    print(f"Section: {data['sections'][i]['section']}")
    print(f"Title: {data['sections'][i]['title']}")
    print("--- First 500 chars ---")
    print(data['sections'][i]['body'][:500])
