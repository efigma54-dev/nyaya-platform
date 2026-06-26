
import hashlib
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

def get_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()

def save_evidence(
    evidence_dir: Path,
    component: str,
    file_name: str,
    content: str | bytes,
    file_mode: str = "w"
) -> Dict[str, Any]:
    component_dir = evidence_dir / component
    component_dir.mkdir(parents=True, exist_ok=True)
    file_path = component_dir / file_name

    with open(file_path, file_mode) as f:
        if file_mode == "w":
            f.write(content)
        else:
            f.write(content)

    return {
        "file_path": str(file_path),
        "component": component,
        "file_name": file_name,
        "sha256": get_sha256(file_path),
        "saved_at": datetime.now(timezone.utc).isoformat()
    }

def get_git_info() -> Dict[str, str]:
    try:
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        ).strip()
        short_hash = commit_hash[:7]
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        ).strip()
        return {"commit_hash": commit_hash, "short_hash": short_hash, "branch": branch}
    except Exception as e:
        return {"commit_hash": "unknown", "short_hash": "unknown", "branch": "unknown", "error": str(e)}
