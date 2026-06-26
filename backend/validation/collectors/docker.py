
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone
from ..evidence.save import save_evidence

def check_docker() -> Dict[str, Any]:
    component = "docker"
    evidence_dir = Path(__file__).parent.parent.parent.parent / "evidence"
    checks: List[Dict[str, Any]] = []
    evidence_files: List[str] = []

    try:
        docker_ps_output = subprocess.check_output(
            ["docker", "compose", "ps", "--format", "json"],
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent
        )
        evidence = save_evidence(evidence_dir, component, "docker_ps.json", docker_ps_output)
        evidence_files.append(evidence["file_path"])

        containers = [json.loads(line) for line in docker_ps_output.strip().split("\n") if line]
        overall_status = "PASS"

        for container in containers:
            name = container.get("Name", "unknown")
            status = container.get("Status", "unknown")
            container_status = "PASS" if "Up" in status else "FAIL"
            if container_status == "FAIL":
                overall_status = "FAIL"
            checks.append({
                "name": name,
                "status": container_status,
                "details": status
            })

        return {
            "component": component,
            "status": overall_status,
            "checks": checks,
            "evidence": evidence_files,
            "collected_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        evidence = save_evidence(
            evidence_dir,
            component,
            "docker_error.txt",
            str(e)
        )
        return {
            "component": component,
            "status": "FAIL",
            "checks": [],
            "error": str(e),
            "evidence": [evidence["file_path"]],
            "collected_at": datetime.now(timezone.utc).isoformat()
        }
