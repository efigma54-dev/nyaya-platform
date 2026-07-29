#!/usr/bin/env python3
"""
verify_all.py

Master orchestrator for production verification.

Runs all verification scripts in sequence:
  1. verify_docker.py
  2. verify_api.py
  3. verify_database.py
  4. verify_qdrant.py
  5. verify_chat.py
  6. verify_performance.py
  7. verify_security.py

Generates comprehensive production_acceptance.md report.

Exit codes:
  0: All verifications pass
  1: One or more verifications failed
  2: Critical failure (cannot continue)

Usage:
  python backend/scripts/verification/verify_all.py
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
EVIDENCE_DIR = Path("evidence/runtime")
TIMESTAMP = datetime.now().isoformat()

# List of verification scripts to run in order
VERIFIERS = [
    ("Docker", "verify_docker.py"),
    ("API", "verify_api.py"),
    ("Database", "verify_database.py"),
    ("Qdrant", "verify_qdrant.py"),
    ("Chat", "verify_chat.py"),
    ("Performance", "verify_performance.py"),
    ("Security", "verify_security.py"),
]


def run_verifier(name: str, script: str) -> tuple[int, str]:
    """Run a verifier script and capture output."""
    script_path = SCRIPT_DIR / script
    
    print(f"\n{'='*60}")
    print(f"Running {name} Verification...")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=SCRIPT_DIR.parent.parent.parent  # Project root
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}", file=sys.stderr)
        
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        error_msg = f"✗ TIMEOUT: {name} verification timed out after 120 seconds"
        print(error_msg)
        return 1, error_msg
    except Exception as e:
        error_msg = f"✗ ERROR: Failed to run {name} verification: {e}"
        print(error_msg)
        return 1, error_msg


def load_evidence_reports() -> dict:
    """Load all generated evidence reports."""
    evidence = {}
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    
    for report_file in EVIDENCE_DIR.glob("*_runtime.md"):
        try:
            with open(report_file, "r") as f:
                evidence[report_file.stem] = f.read()
        except Exception as e:
            print(f"Warning: Could not load {report_file}: {e}")
    
    return evidence


def generate_production_acceptance_report(
    results: dict,
    evidence: dict
) -> Path:
    """Generate comprehensive production acceptance report."""
    report_path = EVIDENCE_DIR / "production_acceptance.md"
    
    # Calculate overall status
    failed_checks = [name for name, code in results.items() if code != 0]
    total_checks = len(results)
    passed_checks = total_checks - len(failed_checks)
    
    overall_status = "✓ PASS" if len(failed_checks) == 0 else "✗ FAIL"
    
    with open(report_path, "w") as f:
        f.write("# Production Acceptance Report\n\n")
        f.write(f"**Generated:** {TIMESTAMP}\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"**Overall Status:** {overall_status}\n\n")
        f.write(f"**Verifications Passed:** {passed_checks}/{total_checks}\n\n")
        
        if failed_checks:
            f.write("**Failed Verifications:**\n")
            for name in failed_checks:
                f.write(f"- {name}\n")
            f.write("\n")
        
        # Definition of Done Checklist
        f.write("## Definition of Done\n\n")
        checks = [
            ("All containers healthy", results.get("Docker", 1) == 0),
            ("Docker Compose starts from scratch", results.get("Docker", 1) == 0),
            ("API health endpoint OK", results.get("API", 1) == 0),
            ("OpenAPI documentation available", results.get("API", 1) == 0),
            ("PostgreSQL connected and healthy", results.get("Database", 1) == 0),
            ("Redis connected and healthy", results.get("Docker", 1) == 0),
            ("Qdrant connected and healthy", results.get("Qdrant", 1) == 0),
            ("Chat endpoint functional", results.get("Chat", 1) == 0),
            ("Citations and grounding verified", results.get("Chat", 1) == 0),
            ("Security checks passed", results.get("Security", 1) == 0),
            ("No failing verification", len(failed_checks) == 0),
        ]
        
        for check_name, status in checks:
            icon = "✓" if status else "✗"
            f.write(f"- {icon} {check_name}\n")
        
        f.write("\n")
        
        # Verification Results
        f.write("## Verification Results\n\n")
        for name, code in results.items():
            icon = "✓" if code == 0 else "✗"
            status = "PASS" if code == 0 else "FAIL"
            f.write(f"### {icon} {name}\n\n")
            f.write(f"**Status:** {status} (exit code: {code})\n\n")
        
        # Detailed Reports
        f.write("## Detailed Reports\n\n")
        for name, code in results.items():
            report_key = f"{name.lower()}_runtime"
            if report_key in evidence:
                f.write(f"### {name} Details\n\n")
                f.write(evidence[report_key])
                f.write("\n\n")
        
        # Deployment Instructions
        f.write("## Deployment Instructions\n\n")
        if len(failed_checks) == 0:
            f.write("Platform is **PRODUCTION READY**.\n\n")
            f.write("### Pre-deployment Steps\n\n")
            f.write("1. Review all verification reports\n")
            f.write("2. Validate performance metrics meet SLOs\n")
            f.write("3. Confirm security requirements are met\n")
            f.write("4. Execute backup and restore procedures\n\n")
            f.write("### Deployment\n\n")
            f.write("```bash\n")
            f.write("cd /path/to/nyaya-platform\n")
            f.write("docker compose up -d\n")
            f.write("python backend/scripts/verification/verify_all.py\n")
            f.write("```\n\n")
        else:
            f.write("Platform has **FAILED VERIFICATIONS**. Cannot proceed to production.\n\n")
            f.write("### Troubleshooting\n\n")
            for name in failed_checks:
                f.write(f"- **{name}**: Review detailed report above\n")
            f.write("\n")
        
        # Next Steps
        f.write("## Next Steps\n\n")
        if len(failed_checks) == 0:
            f.write("1. Configure monitoring and alerting\n")
            f.write("2. Set up automated backups\n")
            f.write("3. Enable CI/CD pipeline\n")
            f.write("4. Configure log aggregation\n")
            f.write("5. Set up incident response procedures\n")
        else:
            f.write("1. Review failed verification reports\n")
            f.write("2. Address root causes\n")
            f.write("3. Re-run verification framework\n")
            f.write("4. Iterate until all checks pass\n")
    
    return report_path


def main() -> int:
    """Main orchestrator logic."""
    print("=" * 60)
    print("NYAYA PLATFORM PRODUCTION VERIFICATION")
    print("=" * 60)
    print(f"\nStarted at: {TIMESTAMP}")
    print(f"Verifications to run: {len(VERIFIERS)}")
    print()
    
    results = {}
    
    # Run each verifier
    for name, script in VERIFIERS:
        exit_code, output = run_verifier(name, script)
        results[name] = exit_code
    
    # Load all evidence reports
    print("\n" + "=" * 60)
    print("LOADING EVIDENCE REPORTS")
    print("=" * 60)
    evidence = load_evidence_reports()
    print(f"Loaded {len(evidence)} evidence reports")
    
    # Generate production acceptance report
    print("\n" + "=" * 60)
    print("GENERATING PRODUCTION ACCEPTANCE REPORT")
    print("=" * 60)
    report_path = generate_production_acceptance_report(results, evidence)
    print(f"Report generated: {report_path}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("PRODUCTION VERIFICATION COMPLETE")
    print("=" * 60)
    
    failed = [name for name, code in results.items() if code != 0]
    passed = len(results) - len(failed)
    
    print(f"\nVerifications Passed: {passed}/{len(results)}")
    if failed:
        print(f"Verifications Failed: {', '.join(failed)}")
    
    print(f"\nProduction Acceptance Report: {report_path}\n")
    
    # Exit code
    if failed:
        print("Status: PRODUCTION VERIFICATION FAILED")
        return 1
    else:
        print("Status: PRODUCTION VERIFICATION PASSED - READY FOR DEPLOYMENT")
        return 0


if __name__ == "__main__":
    sys.exit(main())
