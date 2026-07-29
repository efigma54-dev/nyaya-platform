#!/usr/bin/env python3
"""
verify_api.py

Verifies FastAPI backend health and endpoints.
- Checks /health endpoint
- Validates /openapi.json
- Checks /docs availability
- Tests chat endpoint
- Tests section search endpoint

Exit codes:
  0: All checks pass
  1: API not responding
  2: Health endpoint failed
  3: OpenAPI invalid
"""

import requests
import json
import sys
from datetime import datetime
from pathlib import Path

API_BASE_URL = "http://localhost:8000"
EVIDENCE_DIR = Path("evidence/runtime")
TIMESTAMP = datetime.now().isoformat()


def http_get(endpoint: str, timeout: int = 5) -> tuple[int, dict | str]:
    """Make HTTP GET request and return status code and response."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=timeout)
        try:
            return response.status_code, response.json()
        except json.JSONDecodeError:
            return response.status_code, response.text
    except requests.exceptions.ConnectionError:
        return 0, f"Connection refused to {API_BASE_URL}{endpoint}"
    except requests.exceptions.Timeout:
        return 0, f"Request timeout to {API_BASE_URL}{endpoint}"
    except Exception as e:
        return 0, str(e)


def http_post(endpoint: str, payload: dict, timeout: int = 10) -> tuple[int, dict | str]:
    """Make HTTP POST request and return status code and response."""
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        try:
            return response.status_code, response.json()
        except json.JSONDecodeError:
            return response.status_code, response.text
    except requests.exceptions.ConnectionError:
        return 0, f"Connection refused to {API_BASE_URL}{endpoint}"
    except requests.exceptions.Timeout:
        return 0, f"Request timeout to {API_BASE_URL}{endpoint}"
    except Exception as e:
        return 0, str(e)


def verify_api() -> int:
    """Main API verification logic."""
    print("=" * 60)
    print("API VERIFICATION")
    print("=" * 60)
    
    evidence = {
        "timestamp": TIMESTAMP,
        "api_url": API_BASE_URL,
        "checks": [],
        "summary": {"passed": 0, "failed": 0}
    }
    
    # Check 1: Health endpoint
    print("\n[1/5] Checking /health endpoint...")
    code, response = http_get("/health")
    if code == 200:
        print(f"✓ PASS: Health endpoint responding (status {code})")
        print(f"  Response: {response}")
        evidence["checks"].append({"check": "health_endpoint", "status": "PASS", "code": code})
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Health endpoint failed (status {code})")
        print(f"  Response: {response}")
        evidence["checks"].append({"check": "health_endpoint", "status": "FAIL", "code": code, "reason": str(response)})
        evidence["summary"]["failed"] += 1
    
    # Check 2: OpenAPI schema
    print("\n[2/5] Checking /openapi.json...")
    code, response = http_get("/openapi.json")
    if code == 200 and isinstance(response, dict):
        print(f"✓ PASS: OpenAPI schema available (status {code})")
        print(f"  Title: {response.get('info', {}).get('title', 'Unknown')}")
        print(f"  Version: {response.get('info', {}).get('version', 'Unknown')}")
        evidence["checks"].append({"check": "openapi_schema", "status": "PASS", "code": code})
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: OpenAPI schema failed (status {code})")
        evidence["checks"].append({"check": "openapi_schema", "status": "FAIL", "code": code, "reason": "Invalid or missing schema"})
        evidence["summary"]["failed"] += 1
    
    # Check 3: Docs endpoint
    print("\n[3/5] Checking /docs endpoint...")
    code, response = http_get("/docs")
    if code == 200:
        print(f"✓ PASS: API documentation available (status {code})")
        evidence["checks"].append({"check": "docs_endpoint", "status": "PASS", "code": code})
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: API documentation failed (status {code})")
        evidence["checks"].append({"check": "docs_endpoint", "status": "FAIL", "code": code, "reason": "Docs not accessible"})
        evidence["summary"]["failed"] += 1
    
    # Check 4: Chat endpoint
    print("\n[4/5] Checking POST /chat endpoint...")
    chat_payload = {"query": "What is BNS Section 302?"}
    code, response = http_post("/chat", chat_payload)
    if code == 200 and isinstance(response, dict):
        print(f"✓ PASS: Chat endpoint responding (status {code})")
        print(f"  Response keys: {list(response.keys())}")
        evidence["checks"].append({
            "check": "chat_endpoint",
            "status": "PASS",
            "code": code,
            "response_keys": list(response.keys())
        })
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Chat endpoint failed (status {code})")
        print(f"  Response: {response}")
        evidence["checks"].append({
            "check": "chat_endpoint",
            "status": "FAIL",
            "code": code,
            "reason": str(response)
        })
        evidence["summary"]["failed"] += 1
    
    # Check 5: Section search endpoint
    print("\n[5/5] Checking POST /search/sections endpoint...")
    search_payload = {"query": "punishment"}
    code, response = http_post("/search/sections", search_payload)
    if code == 200 and isinstance(response, dict):
        print(f"✓ PASS: Search endpoint responding (status {code})")
        result_count = len(response.get("results", []))
        print(f"  Results: {result_count}")
        evidence["checks"].append({
            "check": "search_sections_endpoint",
            "status": "PASS",
            "code": code,
            "result_count": result_count
        })
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Search endpoint failed (status {code})")
        evidence["checks"].append({
            "check": "search_sections_endpoint",
            "status": "FAIL",
            "code": code,
            "reason": str(response)
        })
        evidence["summary"]["failed"] += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"API VERIFICATION: {evidence['summary']['passed']} passed, {evidence['summary']['failed']} failed")
    print("=" * 60)
    
    # Write evidence
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_file = EVIDENCE_DIR / "api_runtime.md"
    with open(evidence_file, "w") as f:
        f.write(f"# API Runtime Verification\n\n")
        f.write(f"**Timestamp:** {TIMESTAMP}\n")
        f.write(f"**API Base URL:** {API_BASE_URL}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- **Passed:** {evidence['summary']['passed']}\n")
        f.write(f"- **Failed:** {evidence['summary']['failed']}\n\n")
        f.write(f"## Checks\n")
        for check in evidence["checks"]:
            status_icon = "✓" if check["status"] == "PASS" else "✗"
            f.write(f"- {status_icon} **{check['check']}**: {check['status']} (HTTP {check.get('code', 'N/A')})\n")
            if "reason" in check:
                f.write(f"  - Reason: {check['reason']}\n")
            if "response_keys" in check:
                f.write(f"  - Response keys: {check['response_keys']}\n")
            if "result_count" in check:
                f.write(f"  - Results: {check['result_count']}\n")
    
    return 0 if evidence["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(verify_api())
