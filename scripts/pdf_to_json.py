from __future__ import annotations

import json
from pathlib import Path

from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()

import importlib.util
from pathlib import Path as _Path
ingest_path = _Path(__file__).resolve().parent / "ingest_bare_acts.py"
spec = importlib.util.spec_from_file_location("ingest_bare_acts", str(ingest_path))
ingest_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingest_mod)
parse_bns_pdf = ingest_mod.parse_bns_pdf

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw"

FILES = [
    ("bns.pdf", "Bharatiya Nyaya Sanhita 2023", "The Bharatiya Nyaya Sanhita, 2023", 2023),
    ("bnss.pdf", "Bharatiya Nagarik Suraksha Sanhita 2023", "The Bharatiya Nagarik Suraksha Sanhita, 2023", 2023),
    ("bsa.pdf", "Bharatiya Sakshya Adhiniyam 2023", "The Bharatiya Sakshya Adhiniyam, 2023", 2023),
]


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for filename, short_title, full_title, year in FILES:
        path = RAW_DIR / filename
        if not path.exists():
            print(f"⚠️  Missing {path}, skipping")
            continue

        print(f"📄 Parsing {path}...")
        pdf_bytes = path.read_bytes()
        sections = parse_bns_pdf(pdf_bytes)
        print(f"  🔢 Got {len(sections)} sections")

        act_obj = {
            "act": {
                "short_title": short_title,
                "full_title": full_title,
                "year": year,
                "act_type": "CENTRAL",
                "category": "CRIMINAL",
            },
            "sections": [],
        }

        for s in sections:
            sec = {
                "number": s.get("section_number"),
                "title": s.get("section_title"),
                "bare_text": s.get("bare_text"),
                "plain_language": s.get("plain_language"),
                "is_bailable": s.get("is_bailable"),
                "is_cognizable": s.get("is_cognizable"),
                "punishment_summary": s.get("punishment_summary"),
                "max_punishment": s.get("max_punishment"),
                "min_punishment": s.get("min_punishment"),
                "fine_amount": s.get("fine_amount"),
                "relevant_court": s.get("relevant_court"),
            }
            act_obj["sections"].append(sec)

        out_file = DATA_DIR / (filename.replace('.pdf', '.json'))
        with out_file.open("w", encoding="utf-8") as fh:
            json.dump([act_obj], fh, ensure_ascii=False, indent=2)
        print(f"  ✅ Wrote {out_file} with {len(act_obj['sections'])} sections\n")


if __name__ == "__main__":
    main()
