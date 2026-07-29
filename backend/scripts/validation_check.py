#!/usr/bin/env python3
"""
Framework validation test.

Validates that the Production Verification Framework is properly installed
and all components are accessible.

Run this to ensure the framework is ready to use.
"""

import sys
import os
from pathlib import Path

def check_files_exist():
    """Verify all required files exist."""
    print("Checking required files...")
    
    required_files = [
        "backend/scripts/verification/__init__.py",
        "backend/scripts/verification/utils.py",
        "backend/scripts/verification/verify_docker.py",
        "backend/scripts/verification/verify_api.py",
        "backend/scripts/verification/verify_database.py",
        "backend/scripts/verification/verify_qdrant.py",
        "backend/scripts/verification/verify_chat.py",
        "backend/scripts/verification/verify_performance.py",
        "backend/scripts/verification/verify_security.py",
        "backend/scripts/verification/verify_all.py",
        "backend/scripts/verification/README.md",
        "backend/scripts/verification/requirements.txt",
        "backend/scripts/verification/quick_start.sh",
        ".github/workflows/production_verification.yml",
        ".env.example",
        "DEPLOYMENT_RUNBOOK.md",
        "VERIFICATION_FRAMEWORK_SUMMARY.md",
    ]
    
    missing = []
    for file in required_files:
        file_path = Path(file)
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file}")
            missing.append(file)
    
    return len(missing) == 0, missing


def check_python_imports():
    """Verify required Python packages can be imported."""
    print("\nChecking Python dependencies...")
    
    required_packages = [
        ("requests", "requests"),
        ("psutil", "psutil"),
        ("psycopg2", "psycopg2"),
        ("subprocess", None),
        ("json", None),
        ("sys", None),
    ]
    
    missing = []
    for import_name, pip_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✓ {import_name}")
        except ImportError:
            if pip_name:
                print(f"  ✗ {import_name} (install: pip install {pip_name})")
                missing.append(pip_name)
            else:
                print(f"  ✗ {import_name}")
    
    return len(missing) == 0, missing


def check_executables():
    """Verify required executables are available."""
    print("\nChecking executables...")
    
    required_executables = ["docker", "python"]
    
    missing = []
    for executable in required_executables:
        result = os.system(f"which {executable} > /dev/null 2>&1")
        if result == 0:
            print(f"  ✓ {executable}")
        else:
            print(f"  ✗ {executable}")
            missing.append(executable)
    
    return len(missing) == 0, missing


def check_docker_compose():
    """Verify docker-compose.yml is valid."""
    print("\nChecking Docker Compose configuration...")
    
    result = os.system("docker compose config > /dev/null 2>&1")
    if result == 0:
        print("  ✓ docker-compose.yml is valid")
        return True, []
    else:
        print("  ✗ docker-compose.yml is invalid")
        return False, ["docker-compose.yml validation failed"]


def check_framework_structure():
    """Verify the framework structure is correct."""
    print("\nChecking framework structure...")
    
    checks = [
        ("Evidence directory exists", Path("evidence").is_dir()),
        ("Scripts directory exists", Path("backend/scripts").is_dir()),
        ("Verification directory exists", Path("backend/scripts/verification").is_dir()),
        ("GitHub workflows directory exists", Path(".github/workflows").is_dir()),
    ]
    
    all_pass = True
    for check_name, result in checks:
        if result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_pass = False
    
    return all_pass, []


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("PRODUCTION VERIFICATION FRAMEWORK VALIDATION")
    print("=" * 60)
    print()
    
    all_checks = [
        ("Files", check_files_exist),
        ("Python Imports", check_python_imports),
        ("Executables", check_executables),
        ("Docker Compose", check_docker_compose),
        ("Framework Structure", check_framework_structure),
    ]
    
    results = []
    for check_name, check_func in all_checks:
        try:
            passed, issues = check_func()
            results.append((check_name, passed, issues))
        except Exception as e:
            print(f"\n✗ Error during {check_name} check: {e}")
            results.append((check_name, False, [str(e)]))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_checks = len(results)
    passed_checks = sum(1 for _, passed, _ in results if passed)
    
    print(f"\nTotal Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}\n")
    
    for check_name, passed, issues in results:
        icon = "✓" if passed else "✗"
        status = "PASS" if passed else "FAIL"
        print(f"{icon} {check_name}: {status}")
        if issues:
            for issue in issues:
                print(f"   - {issue}")
    
    print("\n" + "=" * 60)
    
    if passed_checks == total_checks:
        print("✓ FRAMEWORK VALIDATION PASSED")
        print("\nFramework is ready to use:")
        print("  python backend/scripts/verification/verify_all.py")
        print("=" * 60)
        return 0
    else:
        print("✗ FRAMEWORK VALIDATION FAILED")
        print("\nPlease fix the issues above and try again.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
