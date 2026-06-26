
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
from ..evidence.save import save_evidence, get_sha256

def generate_json_report(
    results: List[Dict[str, Any]],
    output_dir: Path
) -> Dict[str, Any]:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_info": get_git_info(),
        "results": results,
        "status_counts": count_statuses(results),
        "overall_score": compute_score(results)
    }

    output_path = output_dir / "validation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return {
        "output_path": str(output_path),
        "sha256": get_sha256(output_path)
    }

def get_git_info() -> Dict[str, str]:
    from ..evidence.save import get_git_info as save_get_git_info
    return save_get_git_info()

def count_statuses(results: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"PASS": 0, "WARNING": 0, "FAIL": 0}
    for result in results:
        status = result.get("status", "UNKNOWN")
        if status in counts:
            counts[status] +=1
    return counts

def compute_score(results: List[Dict[str, Any]]) -> float:
    if not results:
        return 0.0

    total = len(results)
    pass_count = sum(1 for r in results if r.get("status") == "PASS")
    warning_count = sum(1 for r in results if r.get("status") == "WARNING")

    weighted = (pass_count * 100 + warning_count * 50) / total
    return weighted / 10  # convert to 10.0 scale
