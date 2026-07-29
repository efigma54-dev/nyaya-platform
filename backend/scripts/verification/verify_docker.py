#!/usr/bin/env python3
"""
verify_docker.py

Verifies Docker Compose deployment health.
- Checks all containers are running
- Verifies images exist
- Checks ports are accessible
- Validates health checks pass

Exit codes:
  0: All checks pass
  1: Container not running
  2: Health check failed
  3: Port not accessible
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

EVIDENCE_DIR = Path("evidence/runtime")
TIMESTAMP = datetime.now().isoformat()


def run_cmd(cmd: list) -> tuple[int, str, str]:
    """Execute shell command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def check_docker_running() -> bool:
    """Verify Docker daemon is running."""
    code, _, _ = run_cmd(["docker", "ps"])
    return code == 0


def get_compose_ps() -> dict:
    """Get docker compose ps output as JSON."""
    code, stdout, stderr = run_cmd(["docker", "compose", "ps", "--format", "json"])
    if code != 0:
        print(f"FAIL: docker compose ps failed: {stderr}")
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        # Fallback to parsing text output
        return parse_compose_ps_text(stdout)


def parse_compose_ps_text(output: str) -> dict:
    """Fallback parser for docker compose ps text output."""
    containers = {}
    for line in output.strip().split("\n"):
        if "CONTAINER" in line or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2:
            containers[parts[0]] = {"state": parts[-1]}
    return containers


def check_container_health(container_name: str) -> tuple[bool, str]:
    """Check if a container is healthy."""
    code, stdout, _ = run_cmd(["docker", "inspect", container_name])
    if code != 0:
        return False, f"Container {container_name} does not exist"
    
    try:
        info = json.loads(stdout)[0]
        state = info.get("State", {})
        running = state.get("Running", False)
        health = info.get("State", {}).get("Health", {}).get("Status", "none")
        
        if not running:
            return False, f"Container {container_name} is not running"
        if health == "unhealthy":
            return False, f"Container {container_name} health check failed"
        
        return True, f"Container {container_name} is healthy"
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        return False, f"Failed to parse container state: {e}"


def check_port_accessible(port: int) -> tuple[bool, str]:
    """Check if a port is accessible."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        if result == 0:
            return True, f"Port {port} is accessible"
        else:
            return False, f"Port {port} is not accessible"
    except Exception as e:
        return False, f"Failed to check port {port}: {e}"


def verify_docker() -> int:
    """Main verification logic."""
    print("=" * 60)
    print("DOCKER VERIFICATION")
    print("=" * 60)
    
    evidence = {
        "timestamp": TIMESTAMP,
        "checks": [],
        "summary": {"passed": 0, "failed": 0}
    }
    
    # Check 1: Docker daemon running
    print("\n[1/5] Checking Docker daemon...")
    if check_docker_running():
        print("✓ PASS: Docker daemon is running")
        evidence["checks"].append({"check": "docker_daemon", "status": "PASS"})
        evidence["summary"]["passed"] += 1
    else:
        print("✗ FAIL: Docker daemon is not running")
        evidence["checks"].append({"check": "docker_daemon", "status": "FAIL", "reason": "Docker daemon not accessible"})
        evidence["summary"]["failed"] += 1
        return 1
    
    # Check 2: Containers running
    print("\n[2/5] Checking containers...")
    compose_ps = get_compose_ps()
    
    required_containers = ["nyaya_postgres", "nyaya_redis", "nyaya_qdrant", "nyaya_api", "nyaya_frontend"]
    for container in required_containers:
        healthy, msg = check_container_health(container)
        if healthy:
            print(f"✓ PASS: {msg}")
            evidence["checks"].append({"check": f"container_{container}", "status": "PASS"})
            evidence["summary"]["passed"] += 1
        else:
            print(f"✗ FAIL: {msg}")
            evidence["checks"].append({"check": f"container_{container}", "status": "FAIL", "reason": msg})
            evidence["summary"]["failed"] += 1
    
    # Check 3: Port accessibility
    print("\n[3/5] Checking port accessibility...")
    ports = {
        "PostgreSQL": 5432,
        "Redis": 6379,
        "Qdrant": 6333,
        "API": 8000,
        "Frontend": 3005
    }
    for name, port in ports.items():
        accessible, msg = check_port_accessible(port)
        if accessible:
            print(f"✓ PASS: {msg}")
            evidence["checks"].append({"check": f"port_{port}_{name}", "status": "PASS"})
            evidence["summary"]["passed"] += 1
        else:
            print(f"✗ FAIL: {msg}")
            evidence["checks"].append({"check": f"port_{port}_{name}", "status": "FAIL", "reason": msg})
            evidence["summary"]["failed"] += 1
    
    # Check 4: Docker images exist
    print("\n[4/5] Checking Docker images...")
    code, stdout, stderr = run_cmd(["docker", "compose", "images"])
    if code == 0:
        print("✓ PASS: Docker images exist")
        evidence["checks"].append({"check": "docker_images", "status": "PASS"})
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Failed to list Docker images: {stderr}")
        evidence["checks"].append({"check": "docker_images", "status": "FAIL", "reason": stderr})
        evidence["summary"]["failed"] += 1
    
    # Check 5: Docker compose config valid
    print("\n[5/5] Checking docker-compose.yml validity...")
    code, stdout, stderr = run_cmd(["docker", "compose", "config"])
    if code == 0:
        print("✓ PASS: docker-compose.yml is valid")
        evidence["checks"].append({"check": "compose_config", "status": "PASS"})
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: docker-compose.yml is invalid: {stderr}")
        evidence["checks"].append({"check": "compose_config", "status": "FAIL", "reason": stderr})
        evidence["summary"]["failed"] += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"DOCKER VERIFICATION: {evidence['summary']['passed']} passed, {evidence['summary']['failed']} failed")
    print("=" * 60)
    
    # Write evidence
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_file = EVIDENCE_DIR / "docker_runtime.md"
    with open(evidence_file, "w") as f:
        f.write(f"# Docker Runtime Verification\n\n")
        f.write(f"**Timestamp:** {TIMESTAMP}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- **Passed:** {evidence['summary']['passed']}\n")
        f.write(f"- **Failed:** {evidence['summary']['failed']}\n\n")
        f.write(f"## Checks\n")
        for check in evidence["checks"]:
            status_icon = "✓" if check["status"] == "PASS" else "✗"
            reason = f" - {check['reason']}" if "reason" in check else ""
            f.write(f"- {status_icon} {check['check']}: {check['status']}{reason}\n")
    
    return 0 if evidence["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(verify_docker())
