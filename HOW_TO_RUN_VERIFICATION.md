# How to Run the Production Verification Framework

## Quick Reference

```bash
# Validate framework is installed correctly
python backend/scripts/validation_check.py

# Run complete production verification
python backend/scripts/verification/verify_all.py

# One-command quick start (includes Docker startup)
bash backend/scripts/verification/quick_start.sh

# Run individual verifier
python backend/scripts/verification/verify_docker.py
python backend/scripts/verification/verify_api.py
python backend/scripts/verification/verify_database.py
python backend/scripts/verification/verify_qdrant.py
python backend/scripts/verification/verify_chat.py
python backend/scripts/verification/verify_performance.py
python backend/scripts/verification/verify_security.py
```

## Prerequisites

### Required
- Docker and Docker Compose
- Python 3.9+
- All services running (or use quick_start.sh to start them)

### Dependencies
```bash
pip install requests psutil psycopg2-binary
```

Or from the requirements file:
```bash
pip install -r backend/scripts/verification/requirements.txt
```

## Step-by-Step

### 1. Check Installation
```bash
$ python backend/scripts/validation_check.py

FRAMEWORK VALIDATION
============================================================

Checking required files...
  ✓ backend/scripts/verification/__init__.py
  ✓ backend/scripts/verification/verify_docker.py
  ✓ backend/scripts/verification/verify_api.py
  ...

✓ FRAMEWORK VALIDATION PASSED
============================================================
```

### 2. Start Services (if needed)
```bash
docker compose up -d
docker compose ps  # Verify all running
```

### 3. Run Verification
```bash
$ python backend/scripts/verification/verify_all.py

============================================================
NYAYA PLATFORM PRODUCTION VERIFICATION
============================================================

Started at: 2025-01-15T10:30:00.123456

Running Docker Verification...
[1/5] Checking Docker daemon...
✓ PASS: Docker daemon is running
[2/5] Checking containers...
✓ PASS: nyaya_postgres is healthy
✓ PASS: nyaya_redis is healthy
... (all checks)

Running API Verification...
[1/5] Checking /health endpoint...
✓ PASS: Health endpoint responding (status 200)
... (all checks)

... (more verifiers) ...

============================================================
PRODUCTION VERIFICATION COMPLETE
============================================================

Verifications Passed: 7/7

Production Acceptance Report: evidence/runtime/production_acceptance.md

Status: PRODUCTION VERIFICATION PASSED - READY FOR DEPLOYMENT
```

### 4. Review Results
```bash
cat evidence/runtime/production_acceptance.md
```

## Output Examples

### Success Scenario (Exit Code: 0)
```
Verifications Passed: 7/7

Evidence reports generated:
  - docker_runtime.md (✓ PASS)
  - api_runtime.md (✓ PASS)
  - database_runtime.md (✓ PASS)
  - qdrant_runtime.md (✓ PASS)
  - chat_runtime.md (✓ PASS)
  - performance_runtime.md (✓ PASS)
  - security_runtime.md (✓ PASS)

Production Acceptance Report: evidence/runtime/production_acceptance.md

Status: PRODUCTION VERIFICATION PASSED - READY FOR DEPLOYMENT
```

### Failure Scenario (Exit Code: 1)
```
Verifications Passed: 5/7
Verifications Failed: API, Chat

Check failed reports:
- api_runtime.md (✗ FAIL)
- chat_runtime.md (✗ FAIL)

Review detailed reports for root cause analysis.
```

## Evidence Reports Location

All reports are generated in `evidence/runtime/`:

```
evidence/runtime/
├── docker_runtime.md          # Container health status
├── api_runtime.md             # API endpoint validation
├── database_runtime.md        # PostgreSQL health
├── qdrant_runtime.md          # Vector DB status
├── chat_runtime.md            # Chat functionality
├── performance_runtime.md     # Performance metrics
├── security_runtime.md        # Security posture
└── production_acceptance.md   # Summary + DoD checklist
```

Open these in any text editor or with `cat`:
```bash
cat evidence/runtime/production_acceptance.md
```

## Common Issues & Solutions

### Issue: "Connection refused to http://localhost:8000"
**Solution:** Start services first
```bash
docker compose up -d
sleep 10  # Wait for services to start
python backend/scripts/verification/verify_all.py
```

### Issue: "Database connection failed"
**Solution:** Check PostgreSQL is running
```bash
docker compose ps postgres
docker compose logs postgres
# If not running:
docker compose up -d postgres
```

### Issue: "psycopg2 ModuleNotFoundError"
**Solution:** Install dependencies
```bash
pip install psycopg2-binary requests psutil
```

### Issue: "Verification timeout"
**Solution:** Services may be slow. Give them more time or check logs
```bash
docker compose logs
# Or wait longer:
sleep 30
python backend/scripts/verification/verify_all.py
```

## Automated Execution

### Run on Schedule (Linux/Mac)
Add to crontab for daily verification at 2 AM:
```bash
0 2 * * * cd /opt/nyaya-platform && python backend/scripts/verification/verify_all.py
```

### Run in Docker
```bash
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  python:3.12 \
  bash -c "pip install -r backend/scripts/verification/requirements.txt && \
           python backend/scripts/verification/verify_all.py"
```

### Run with Docker Compose
```bash
docker compose exec api python backend/scripts/verification/verify_all.py
```

## Integration with CI/CD

### GitHub Actions (Already Configured)
The workflow is at `.github/workflows/production_verification.yml`

It automatically runs on:
- Push to main branch
- Pull requests
- Manual trigger via workflow_dispatch

View results:
1. Go to GitHub Actions tab
2. Click "Production Verification" workflow
3. View logs and artifacts

### Gitlab CI
```yaml
production-verification:
  stage: test
  script:
    - pip install -r backend/scripts/verification/requirements.txt
    - python backend/scripts/verification/verify_all.py
  artifacts:
    paths:
      - evidence/runtime/
    when: always
```

### Jenkins
```groovy
stage('Production Verification') {
    steps {
        sh 'pip install -r backend/scripts/verification/requirements.txt'
        sh 'python backend/scripts/verification/verify_all.py'
        archiveArtifacts artifacts: 'evidence/runtime/**/*.md'
    }
}
```

## Performance Expectations

### Typical Execution Times
- Docker verification: 5-10 seconds
- API verification: 10-15 seconds
- Database verification: 5-10 seconds
- Qdrant verification: 5-10 seconds
- Chat verification: 20-40 seconds (includes 5 real queries)
- Performance verification: 30-60 seconds (measures latency)
- Security verification: 5-10 seconds

**Total: ~90-180 seconds (1.5-3 minutes)**

## Next Steps After Verification Passes

1. **Review Reports**
   - Check `production_acceptance.md` for summary
   - Review specific component reports

2. **Monitor Metrics**
   - Note baseline performance numbers
   - Compare with future runs

3. **Deploy Confidently**
   - All checks have passed
   - Platform is production-ready
   - Use deployment runbook (DEPLOYMENT_RUNBOOK.md)

4. **Continue Production Hardening** (Optional)
   - Implement D1-D10 from the production loop
   - Use this verification framework after each change
   - Track progress with evidence reports

## Support

For detailed information:
- Framework guide: `backend/scripts/verification/README.md`
- Deployment procedures: `DEPLOYMENT_RUNBOOK.md`
- Architecture: `VERIFICATION_FRAMEWORK_SUMMARY.md`
- Complete docs: `PRODUCTION_VERIFICATION_FRAMEWORK_COMPLETE.md`

## Success Criteria

✓ Verification framework installed
✓ All services running
✓ verify_all.py executes without errors
✓ All 7 verifiers pass
✓ production_acceptance.md generated
✓ Exit code 0

You're ready for production deployment!
