#!/usr/bin/env python3
"""
verify_performance.py

Measures performance metrics across the platform.
- API latency
- Retrieval latency
- Embedding latency
- Memory usage
- CPU usage

Exit codes:
  0: All measurements successful
  1: Measurement failed
"""

import requests
import json
import sys
import time
import psutil
import os
from datetime import datetime
from pathlib import Path

API_BASE_URL = "http://localhost:8000"
EVIDENCE_DIR = Path("evidence/runtime")
TIMESTAMP = datetime.now().isoformat()


def http_post(endpoint: str, payload: dict, timeout: int = 30) -> tuple[float, int, dict | str]:
    """Make HTTP POST request and measure latency."""
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        latency = (time.time() - start_time) * 1000  # Convert to ms
        try:
            return latency, response.status_code, response.json()
        except json.JSONDecodeError:
            return latency, response.status_code, response.text
    except requests.exceptions.Timeout:
        latency = (time.time() - start_time) * 1000
        return latency, 0, f"Request timeout"
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        return latency, 0, str(e)


def get_system_metrics() -> dict:
    """Get current system resource metrics."""
    try:
        # Get current process
        process = psutil.Process(os.getpid())
        
        # Memory info (in MB)
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # CPU percent
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # System-wide metrics
        vm = psutil.virtual_memory()
        system_memory_percent = vm.percent
        
        return {
            "process_memory_mb": memory_mb,
            "process_cpu_percent": cpu_percent,
            "system_memory_percent": system_memory_percent,
            "system_memory_available_mb": vm.available / 1024 / 1024
        }
    except Exception as e:
        return {"error": str(e)}


def verify_performance() -> int:
    """Main performance verification logic."""
    print("=" * 60)
    print("PERFORMANCE VERIFICATION")
    print("=" * 60)
    
    evidence = {
        "timestamp": TIMESTAMP,
        "api_url": API_BASE_URL,
        "measurements": [],
        "system_metrics": {},
        "summary": {"passed": 0, "failed": 0}
    }
    
    # Get baseline system metrics
    print("\n[1/5] Capturing system metrics...")
    baseline_metrics = get_system_metrics()
    if "error" not in baseline_metrics:
        print(f"✓ PASS: System metrics captured")
        print(f"  Process Memory: {baseline_metrics['process_memory_mb']:.2f} MB")
        print(f"  Process CPU: {baseline_metrics['process_cpu_percent']:.2f}%")
        print(f"  System Memory: {baseline_metrics['system_memory_percent']:.2f}%")
        evidence["system_metrics"]["baseline"] = baseline_metrics
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not capture system metrics: {baseline_metrics.get('error')}")
        evidence["summary"]["failed"] += 1
    
    # Test 1: API health endpoint latency
    print("\n[2/5] Measuring API health latency...")
    latencies_health = []
    for i in range(3):
        latency, code, response = http_post("/health", {}, timeout=5)
        if code == 200:
            latencies_health.append(latency)
            print(f"  Request {i+1}: {latency:.2f}ms")
    
    if latencies_health:
        avg_latency = sum(latencies_health) / len(latencies_health)
        print(f"✓ PASS: Average health latency: {avg_latency:.2f}ms")
        evidence["measurements"].append({
            "measurement": "health_api_latency",
            "unit": "ms",
            "samples": latencies_health,
            "average": avg_latency,
            "min": min(latencies_health),
            "max": max(latencies_health)
        })
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not measure health latency")
        evidence["summary"]["failed"] += 1
    
    # Test 2: Chat endpoint latency
    print("\n[3/5] Measuring chat latency (3 queries)...")
    latencies_chat = []
    chat_queries = [
        "What is BNS Section 302?",
        "What is the punishment for theft?",
        "Explain Section 351"
    ]
    
    for query in chat_queries:
        latency, code, response = http_post("/chat", {"query": query}, timeout=30)
        if code == 200:
            latencies_chat.append(latency)
            print(f"  Query '{query[:30]}...': {latency:.2f}ms")
        else:
            print(f"  Query failed: HTTP {code}")
    
    if latencies_chat:
        avg_latency = sum(latencies_chat) / len(latencies_chat)
        print(f"✓ PASS: Average chat latency: {avg_latency:.2f}ms")
        evidence["measurements"].append({
            "measurement": "chat_latency",
            "unit": "ms",
            "samples": latencies_chat,
            "average": avg_latency,
            "min": min(latencies_chat),
            "max": max(latencies_chat)
        })
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not measure chat latency")
        evidence["summary"]["failed"] += 1
    
    # Test 3: Search latency
    print("\n[4/5] Measuring search latency (3 queries)...")
    latencies_search = []
    search_queries = [
        "punishment",
        "theft",
        "murder"
    ]
    
    for query in search_queries:
        latency, code, response = http_post(
            "/search/sections",
            {"query": query},
            timeout=15
        )
        if code == 200:
            latencies_search.append(latency)
            result_count = len(response.get("results", [])) if isinstance(response, dict) else 0
            print(f"  Query '{query}': {latency:.2f}ms ({result_count} results)")
        else:
            print(f"  Query failed: HTTP {code}")
    
    if latencies_search:
        avg_latency = sum(latencies_search) / len(latencies_search)
        print(f"✓ PASS: Average search latency: {avg_latency:.2f}ms")
        evidence["measurements"].append({
            "measurement": "search_latency",
            "unit": "ms",
            "samples": latencies_search,
            "average": avg_latency,
            "min": min(latencies_search),
            "max": max(latencies_search)
        })
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not measure search latency")
        evidence["summary"]["failed"] += 1
    
    # Test 4: Post-load system metrics
    print("\n[5/5] Capturing post-load system metrics...")
    postload_metrics = get_system_metrics()
    if "error" not in postload_metrics:
        print(f"✓ PASS: Post-load metrics captured")
        print(f"  Process Memory: {postload_metrics['process_memory_mb']:.2f} MB")
        print(f"  Process CPU: {postload_metrics['process_cpu_percent']:.2f}%")
        print(f"  System Memory: {postload_metrics['system_memory_percent']:.2f}%")
        evidence["system_metrics"]["postload"] = postload_metrics
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not capture post-load metrics")
        evidence["summary"]["failed"] += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"PERFORMANCE VERIFICATION: {evidence['summary']['passed']} passed, {evidence['summary']['failed']} failed")
    print("=" * 60)
    
    # Write evidence
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_file = EVIDENCE_DIR / "performance_runtime.md"
    with open(evidence_file, "w") as f:
        f.write(f"# Performance Runtime Verification\n\n")
        f.write(f"**Timestamp:** {TIMESTAMP}\n")
        f.write(f"**API Base URL:** {API_BASE_URL}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- **Passed:** {evidence['summary']['passed']}\n")
        f.write(f"- **Failed:** {evidence['summary']['failed']}\n\n")
        
        f.write(f"## System Metrics\n\n")
        if "baseline" in evidence["system_metrics"]:
            baseline = evidence["system_metrics"]["baseline"]
            f.write(f"### Baseline\n")
            f.write(f"- Process Memory: {baseline.get('process_memory_mb', 'N/A'):.2f} MB\n")
            f.write(f"- Process CPU: {baseline.get('process_cpu_percent', 'N/A'):.2f}%\n")
            f.write(f"- System Memory: {baseline.get('system_memory_percent', 'N/A'):.2f}%\n\n")
        
        if "postload" in evidence["system_metrics"]:
            postload = evidence["system_metrics"]["postload"]
            f.write(f"### Post-Load\n")
            f.write(f"- Process Memory: {postload.get('process_memory_mb', 'N/A'):.2f} MB\n")
            f.write(f"- Process CPU: {postload.get('process_cpu_percent', 'N/A'):.2f}%\n")
            f.write(f"- System Memory: {postload.get('system_memory_percent', 'N/A'):.2f}%\n\n")
        
        f.write(f"## Latency Measurements\n\n")
        for measurement in evidence["measurements"]:
            f.write(f"### {measurement['measurement'].replace('_', ' ').title()}\n\n")
            f.write(f"- **Unit:** {measurement['unit']}\n")
            f.write(f"- **Average:** {measurement['average']:.2f}\n")
            f.write(f"- **Min:** {measurement['min']:.2f}\n")
            f.write(f"- **Max:** {measurement['max']:.2f}\n")
            f.write(f"- **Samples:** {len(measurement['samples'])}\n\n")
    
    return 0 if evidence["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(verify_performance())
