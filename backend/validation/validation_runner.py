
#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

from .collectors.docker import check_docker
from .collectors.git import check_git
from .collectors.security import check_security
from .reporters.json_report import generate_json_report
from .reporters.markdown_report import generate_markdown_report

def main():
    print("=" * 80)
    print("🚀 Starting Enterprise Validation Framework")
    print("=" * 80)
    print()

    output_dir = Path(__file__).parent.parent.parent
    results: List[Dict[str, Any]] = []

    collectors = [
        ("docker", check_docker),
        ("git", check_git),
        ("security", check_security)
    ]

    for name, collector in collectors:
        print(f"🔍 Running collector: {name}")
        try:
            result = collector()
            results.append(result)
            print(f"✅ {name} collector completed: {result.get('status')}")
            print()
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results.append({
                "component": name,
                "status": "FAIL",
                "error": str(e),
                "collected_at": datetime.now(timezone.utc).isoformat()
            })

    print()
    print("📊 Generating reports...")
    print()

    json_result = generate_json_report(results, output_dir)
    print(f"✅ JSON report: {json_result['output_path']} (SHA256: {json_result['sha256']})")

    md_result = generate_markdown_report(results, output_dir)
    print(f"✅ Markdown report: {md_result['output_path']} (SHA256: {md_result['sha256']})")

    print()
    print("=" * 80)
    print("✅ Validation complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
