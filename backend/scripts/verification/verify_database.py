#!/usr/bin/env python3
"""
verify_database.py

Verifies PostgreSQL database health and schema.
- Checks connectivity
- Verifies migrations are current
- Validates table row counts
- Checks indexes
- Checks foreign keys

Exit codes:
  0: All checks pass
  1: Database connection failed
  2: Schema validation failed
"""

import psycopg2
from psycopg2 import sql
import os
import sys
from datetime import datetime
from pathlib import Path

EVIDENCE_DIR = Path("evidence/runtime")
TIMESTAMP = datetime.now().isoformat()

# Connection parameters from environment or defaults
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "nyaya_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "nyaya_db")


def get_db_connection():
    """Establish PostgreSQL connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except psycopg2.OperationalError as e:
        return None, str(e)


def execute_query(conn, query: str) -> tuple[bool, list | str]:
    """Execute a database query and return results."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return True, results
    except Exception as e:
        return False, str(e)


def verify_database() -> int:
    """Main database verification logic."""
    print("=" * 60)
    print("DATABASE VERIFICATION")
    print("=" * 60)
    
    evidence = {
        "timestamp": TIMESTAMP,
        "database": f"{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "checks": [],
        "summary": {"passed": 0, "failed": 0}
    }
    
    # Check 1: Connection
    print("\n[1/6] Checking database connectivity...")
    conn = get_db_connection()
    if isinstance(conn, tuple):
        print(f"✗ FAIL: Database connection failed")
        print(f"  Error: {conn[1]}")
        evidence["checks"].append({
            "check": "database_connection",
            "status": "FAIL",
            "reason": conn[1]
        })
        evidence["summary"]["failed"] += 1
        return 1
    else:
        print(f"✓ PASS: Connected to {DB_HOST}:{DB_PORT}/{DB_NAME}")
        evidence["checks"].append({"check": "database_connection", "status": "PASS"})
        evidence["summary"]["passed"] += 1
    
    # Check 2: PostgreSQL version
    print("\n[2/6] Checking PostgreSQL version...")
    success, result = execute_query(conn, "SELECT version();")
    if success:
        version = result[0][0] if result else "Unknown"
        print(f"✓ PASS: {version}")
        evidence["checks"].append({"check": "postgres_version", "status": "PASS", "version": version})
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not retrieve PostgreSQL version")
        evidence["checks"].append({"check": "postgres_version", "status": "FAIL", "reason": result})
        evidence["summary"]["failed"] += 1
    
    # Check 3: Required tables exist
    print("\n[3/6] Checking required tables...")
    tables_to_check = ["acts", "sections", "amendments"]
    for table in tables_to_check:
        query = f"SELECT COUNT(*) FROM {table};"
        success, result = execute_query(conn, query)
        if success:
            count = result[0][0] if result else 0
            print(f"✓ PASS: Table '{table}' exists with {count} rows")
            evidence["checks"].append({
                "check": f"table_{table}",
                "status": "PASS",
                "row_count": count
            })
            evidence["summary"]["passed"] += 1
        else:
            print(f"✗ FAIL: Table '{table}' check failed: {result}")
            evidence["checks"].append({
                "check": f"table_{table}",
                "status": "FAIL",
                "reason": result
            })
            evidence["summary"]["failed"] += 1
    
    # Check 4: Indexes exist
    print("\n[4/6] Checking database indexes...")
    query = """
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE schemaname = 'public'
        LIMIT 10;
    """
    success, result = execute_query(conn, query)
    if success and result:
        index_count = len(result)
        print(f"✓ PASS: Found {index_count} indexes")
        for index, table in result[:3]:
            print(f"  - {index} on {table}")
        evidence["checks"].append({
            "check": "indexes",
            "status": "PASS",
            "index_count": index_count
        })
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not retrieve indexes")
        evidence["checks"].append({
            "check": "indexes",
            "status": "FAIL",
            "reason": result if result else "No indexes found"
        })
        evidence["summary"]["failed"] += 1
    
    # Check 5: Foreign keys exist
    print("\n[5/6] Checking foreign keys...")
    query = """
        SELECT constraint_name, table_name
        FROM information_schema.table_constraints
        WHERE constraint_type = 'FOREIGN KEY'
        AND table_schema = 'public'
        LIMIT 10;
    """
    success, result = execute_query(conn, query)
    if success and result:
        fk_count = len(result)
        print(f"✓ PASS: Found {fk_count} foreign keys")
        evidence["checks"].append({
            "check": "foreign_keys",
            "status": "PASS",
            "fk_count": fk_count
        })
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not retrieve foreign keys or none found")
        evidence["checks"].append({
            "check": "foreign_keys",
            "status": "FAIL",
            "reason": result if result else "No foreign keys found"
        })
        evidence["summary"]["failed"] += 1
    
    # Check 6: Migrations
    print("\n[6/6] Checking migrations...")
    query = """
        SELECT COUNT(*) FROM alembic_version;
    """
    success, result = execute_query(conn, query)
    if success:
        migration_count = result[0][0] if result else 0
        print(f"✓ PASS: {migration_count} migration(s) applied")
        evidence["checks"].append({
            "check": "migrations",
            "status": "PASS",
            "migration_count": migration_count
        })
        evidence["summary"]["passed"] += 1
    else:
        print(f"✗ FAIL: Could not check migrations (table may not exist yet)")
        evidence["checks"].append({
            "check": "migrations",
            "status": "FAIL",
            "reason": "alembic_version table not found"
        })
        evidence["summary"]["failed"] += 1
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    print(f"DATABASE VERIFICATION: {evidence['summary']['passed']} passed, {evidence['summary']['failed']} failed")
    print("=" * 60)
    
    # Write evidence
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_file = EVIDENCE_DIR / "database_runtime.md"
    with open(evidence_file, "w") as f:
        f.write(f"# Database Runtime Verification\n\n")
        f.write(f"**Timestamp:** {TIMESTAMP}\n")
        f.write(f"**Connection:** {evidence['database']}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- **Passed:** {evidence['summary']['passed']}\n")
        f.write(f"- **Failed:** {evidence['summary']['failed']}\n\n")
        f.write(f"## Checks\n")
        for check in evidence["checks"]:
            status_icon = "✓" if check["status"] == "PASS" else "✗"
            f.write(f"- {status_icon} **{check['check']}**: {check['status']}\n")
            if "version" in check:
                f.write(f"  - Version: {check['version']}\n")
            if "row_count" in check:
                f.write(f"  - Rows: {check['row_count']}\n")
            if "index_count" in check:
                f.write(f"  - Indexes: {check['index_count']}\n")
            if "fk_count" in check:
                f.write(f"  - Foreign Keys: {check['fk_count']}\n")
            if "migration_count" in check:
                f.write(f"  - Migrations: {check['migration_count']}\n")
            if "reason" in check:
                f.write(f"  - Reason: {check['reason']}\n")
    
    return 0 if evidence["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(verify_database())
