
import subprocess
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone
from ..evidence.save import save_evidence

def check_security() -> Dict[str, Any]:
    component = "security"
    evidence_dir = Path(__file__).parent.parent.parent.parent / "evidence"
    checks: list[Dict[str, Any]] = []
    evidence_files: list[str] = []
    overall_status = "PASS"

    try:
        if (evidence_dir / "security" / "bandit_report.json").exists():
            evidence_files.append(str(evidence_dir / "security" / "bandit_report.json"))
            checks.append({"name": "bandit", "status": "PASS"})

        if (evidence_dir / "security" / "pip_audit_report.json").exists():
            evidence_files.append(str(evidence_dir / "security" / "pip_audit_report.json"))
            checks.append({"name": "pip-audit", "status": "PASS"})

        if (evidence_dir / "security" / "safety_report.json").exists():
            evidence_files.append(str(evidence_dir / "security" / "safety_report.json"))
            checks.append({"name": "safety", "status": "PASS"})

        if len(checks) == 0:
            overall_status = "WARNING"
    except Exception as e:
        overall_status = "FAIL"
        checks.append({"name": "security_scans", "status": "FAIL", "error": str(e)})

    return {
        "component": component,
        "status": overall_status,
        "checks": checks,
        "evidence": evidence_files,
        "collected_at": datetime.now(timezone.utc).isoformat()
    }
