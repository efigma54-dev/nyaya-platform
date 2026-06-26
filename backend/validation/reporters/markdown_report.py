
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone
from .json_report import count_statuses, compute_score
from ..evidence.save import get_sha256, get_git_info

def generate_markdown_report(
    results: List[Dict[str, Any]],
    output_dir: Path
) -> Dict[str, Any]:
    git_info = get_git_info()
    status_counts = count_statuses(results)
    score = compute_score(results)

    overall_status = "Production Candidate — Further Verification Required"
    if status_counts["FAIL"] ==0 and status_counts["WARNING"] ==0 and score >= 9.5:
        overall_status = "Production Ready (10/10)"
    elif status_counts["FAIL"] ==0 and score >= 9.0:
        overall_status = "Production Candidate (9.0–9.5/10)"

    markdown = f"# Nyaya AI — Enterprise Validation Report\n\n"
    markdown += f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
    markdown += f"Git Commit: {git_info.get('short_hash', 'unknown')}\n"
    markdown += f"Git Branch: {git_info.get('branch', 'unknown')}\n\n"
    markdown += f"---\n\n"
    markdown += f"## Overall Score: {score:.2f} / 10.0\n\n"
    markdown += f"## Overall Status: {overall_status}\n\n"

    markdown += "## Status Summary\n"
    markdown += "| Status | Count |\n"
    markdown += "|--------|-------|\n"
    for status, count in status_counts.items():
        markdown += f"| {status} | {count} |\n"

    markdown += "\n---\n\n"
    markdown += "## Component Results\n"
    markdown += "| Component | Status | Checks Passed | Evidence Files |\n"
    markdown += "|-----------|--------|---------------|----------------|\n"
    for result in results:
        component = result.get("component", "unknown")
        status = result.get("status", "UNKNOWN")
        checks_passed = sum(1 for c in result.get("checks", []) if c.get("status") == "PASS")
        evidence_count = len(result.get("evidence", []))
        markdown += f"| {component} | {status} | {checks_passed} | {evidence_count} |\n"

    markdown += "\n---\n\n"
    markdown += "## Evidence Hashes\n"
    for result in results:
        if "evidence" in result:
            for evidence_file in result["evidence"]:
                try:
                    sha = get_sha256(Path(evidence_file))
                    markdown += f"* `{Path(evidence_file).name}`: `{sha}`\n"
                except Exception:
                    pass

    output_path = output_dir / "validation.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    return {
        "output_path": str(output_path),
        "sha256": get_sha256(output_path)
    }
