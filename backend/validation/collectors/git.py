
import json
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone
from ..evidence.save import save_evidence, get_git_info

def check_git() -> Dict[str, Any]:
    component = "git"
    evidence_dir = Path(__file__).parent.parent.parent.parent / "evidence"

    git_info = get_git_info()
    evidence = save_evidence(
        evidence_dir,
        component,
        "git_info.json",
        json.dumps(git_info, indent=2)
    )
    return {
        "component": component,
        "status": "PASS",
        "checks": [
            {
                "name": "commit_hash",
                "status": "PASS" if git_info["commit_hash"] != "unknown" else "FAIL",
                "details": git_info["commit_hash"]
            },
            {
                "name": "branch",
                "status": "PASS",
                "details": git_info["branch"]
            }
        ],
        "git_info": git_info,
        "evidence": [evidence["file_path"]],
        "collected_at": datetime.now(timezone.utc).isoformat()
    }
