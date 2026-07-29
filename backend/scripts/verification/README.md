# Production Verification Framework

Automated verification suite for the Nyaya Platform. Validates deployment readiness across all components.

## Quick Start

Run complete verification:
```bash
python backend/scripts/verification/verify_all.py
```

This executes all verifications and generates a comprehensive production acceptance report.

## Individual Verifiers

### Docker Verification
```bash
python backend/scripts/verification/verify_docker.py
```

Validates:
- Docker daemon running
- All containers healthy
- Port accessibility
- Docker images available
- docker-compose.yml validity

**Evidence:** `evidence/runtime/docker_runtime.md`

### API Verification
```bash
python backend/scripts/verification/verify_api.py
```

Validates:
- `/health` endpoint responding
- `/openapi.json` available
- `/docs` documentation accessible
- Chat endpoint functional
- Section search endpoint operational

**Evidence:** `evidence/runtime/api_runtime.md`

### Database Verification
```bash
python backend/scripts/verification/verify_database.py
```

Validates:
- PostgreSQL connectivity
- Database version
- Required tables exist (acts, sections, amendments)
- Indexes present
- Foreign keys configured
- Migrations applied

**Evidence:** `evidence/runtime/database_runtime.md`

### Qdrant Verification
```bash
python backend/scripts/verification/verify_qdrant.py
```

Validates:
- Qdrant health
- Collections exist
- Collection details and vector counts
- Qdrant version
- Search capability

**Evidence:** `evidence/runtime/qdrant_runtime.md`

### Chat Verification
```bash
python backend/scripts/verification/verify_chat.py
```

Tests real queries:
- "What is BNS Section 302?"
- "What is IPC 420 equivalent?"
- "Explain Section 351"
- "What is punishment for murder?"
- "What is an unknown fictional law?"

Validates:
- Response structure
- Citations present
- Confidence scores
- Grounding and no hallucination

**Evidence:** `evidence/runtime/chat_runtime.md`

### Performance Verification
```bash
python backend/scripts/verification/verify_performance.py
```

Measures:
- API health latency
- Chat endpoint latency (3 queries)
- Search latency (3 queries)
- System memory usage
- CPU usage

**Evidence:** `evidence/runtime/performance_runtime.md`

### Security Verification
```bash
python backend/scripts/verification/verify_security.py
```

Validates:
- Required environment variables present
- Debug mode disabled
- Secrets not exposed
- Security headers configured
- CORS configuration

**Evidence:** `evidence/runtime/security_runtime.md`

## Evidence Reports

All verification results are written to `evidence/runtime/`:

- `docker_runtime.md` - Docker infrastructure status
- `api_runtime.md` - API endpoint validation
- `database_runtime.md` - PostgreSQL health
- `qdrant_runtime.md` - Vector database status
- `chat_runtime.md` - Chat functionality results
- `performance_runtime.md` - Performance metrics
- `security_runtime.md` - Security posture
- `production_acceptance.md` - Comprehensive report

## Exit Codes

- `0` - All verifications passed, production ready
- `1` - One or more verifications failed
- `2` - Critical failure (cannot continue)

## Integration with CI/CD

Add to GitHub Actions workflow:

```yaml
- name: Production Verification
  run: |
    python backend/scripts/verification/verify_all.py
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    REDIS_URL: ${{ secrets.REDIS_URL }}
    QDRANT_URL: ${{ secrets.QDRANT_URL }}
```

## Production Acceptance Criteria

All of the following must be true:

✓ All containers healthy
✓ Docker Compose starts from scratch with one command
✓ No manual setup required
✓ Health endpoints return OK
✓ API functional (health, docs, openapi)
✓ Database connected and healthy
✓ Redis connected and healthy
✓ Qdrant connected and healthy
✓ Chat endpoint functional
✓ Citations returned and grounded
✓ No failing verification
✓ Security requirements met
✓ Performance within acceptable ranges

## Troubleshooting

### All verifications pass
Platform is production ready. Check `evidence/runtime/production_acceptance.md` for detailed results.

### Some verifications fail
1. Review the specific evidence report (e.g., `api_runtime.md`)
2. Check container logs: `docker compose logs <service>`
3. Address the root cause
4. Re-run the verification suite

### Timeout errors
Increase timeout in the individual verifier script if services are slow to respond in your environment.

### Connection refused errors
Ensure all services are running:
```bash
docker compose ps
docker compose up -d
```

## Requirements

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL running
- Redis running
- Qdrant running
- FastAPI backend running on port 8000
- Next.js frontend running on port 3005

## Dependencies

Install verification dependencies:
```bash
pip install requests psutil psycopg2-binary
```

Or use the main project requirements:
```bash
pip install -r backend/requirements.txt
```
