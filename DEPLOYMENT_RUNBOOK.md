# Production Deployment Runbook

## Pre-Deployment Checklist

### 1. Verify Code Quality
- [ ] All tests passing: `pytest backend/tests/`
- [ ] No linting errors: `pylint backend/`
- [ ] Type checking passes: `mypy backend/`
- [ ] Code coverage > 80%

### 2. Review Changes
- [ ] Git commit messages follow convention
- [ ] No hardcoded secrets in code
- [ ] No debug statements left in code
- [ ] Dependencies pinned to specific versions

### 3. Database Migrations
- [ ] All migrations created (if needed)
- [ ] Migration rollback tested locally
- [ ] Data backup performed

### 4. Security Review
- [ ] Environment variables documented
- [ ] Secrets stored in secure vault (not git)
- [ ] CORS settings appropriate
- [ ] Rate limiting configured
- [ ] API authentication verified

## Pre-Production Deployment

### Step 1: Pull Latest Code
```bash
cd /opt/nyaya-platform
git pull origin main
git checkout <release-tag>
```

### Step 2: Review Configuration
```bash
# Review environment variables
cp .env.example .env
# Edit .env with production values
vim .env

# Validate configuration
docker compose config
```

### Step 3: Backup Current State
```bash
# Backup database
python backend/scripts/backup.py

# Backup Qdrant collections
docker compose exec qdrant curl -X POST http://localhost:6333/snapshots
```

### Step 4: Build and Pull Images
```bash
# Build application images
docker compose build

# Pull base images
docker compose pull
```

### Step 5: Start Services
```bash
# Start in detached mode
docker compose up -d

# Wait for services to become healthy
sleep 30
docker compose ps
```

### Step 6: Run Verification Suite
```bash
# Execute complete verification
python backend/scripts/verification/verify_all.py

# Check report
cat evidence/runtime/production_acceptance.md
```

### Step 7: Manual Smoke Tests
```bash
# Test API health
curl http://localhost:8000/health

# Test frontend access
curl http://localhost:3005/

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is BNS Section 302?"}'
```

## Post-Deployment Validation

### Verify All Services
```bash
# List running containers
docker compose ps

# Check logs for errors
docker compose logs --tail=50

# Verify persistence
docker compose ps -a
```

### Performance Baseline
```bash
# Run performance tests
python backend/scripts/verification/verify_performance.py

# Monitor resource usage
docker stats

# Check database performance
docker compose exec postgres psql -U nyaya_user -d nyaya_db \
  -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### Data Validation
```bash
# Verify data integrity
python backend/scripts/verification/verify_database.py

# Check Qdrant indices
docker compose exec qdrant curl http://localhost:6333/collections
```

### Endpoint Testing
```bash
# Test all critical endpoints
python backend/scripts/verification/verify_api.py

# Test chat functionality
python backend/scripts/verification/verify_chat.py
```

## Monitoring Setup

### Enable Metrics Collection
```bash
# Start monitoring stack (if configured)
docker compose -f docker-compose.monitoring.yml up -d
```

### Configure Alerts
```bash
# Check alert configuration
docker compose logs prometheus
docker compose logs grafana
```

### Review Dashboards
- Navigate to http://localhost:3001 (Grafana)
- Verify all panels showing data
- Check error rates and latencies

## Rollback Procedure

If verification fails or issues are detected:

### Step 1: Stop Current Deployment
```bash
docker compose down
```

### Step 2: Restore Previous Version
```bash
git checkout previous-tag
docker compose build
docker compose up -d
```

### Step 3: Restore Database
```bash
python backend/scripts/restore.py
```

### Step 4: Re-run Verification
```bash
python backend/scripts/verification/verify_all.py
```

### Step 5: Investigate Root Cause
```bash
# Review logs
docker compose logs -f api
docker compose logs -f postgres

# Check error events
docker compose events --filter type=container --filter status=die
```

## Troubleshooting

### Container won't start
```bash
# Check container logs
docker compose logs <service>

# Inspect container
docker inspect <container>

# Check resource limits
docker stats
```

### Database connection failed
```bash
# Test connectivity
docker compose exec api python -c \
  "import psycopg2; psycopg2.connect(os.getenv('DATABASE_URL'))"

# Check database status
docker compose exec postgres pg_isready

# Review migrations
docker compose exec postgres psql -U nyaya_user -d nyaya_db \
  -c "SELECT * FROM alembic_version;"
```

### API endpoint returning errors
```bash
# Check API logs
docker compose logs api --tail=100

# Test endpoint directly
curl -v http://localhost:8000/health

# Review environment variables
docker compose exec api env | grep -E "DATABASE|REDIS|QDRANT"
```

### Performance degradation
```bash
# Check resource usage
docker stats

# Monitor database
docker compose exec postgres psql -U nyaya_user -d nyaya_db \
  -c "SELECT * FROM pg_stat_activity;"

# Check Redis memory
docker compose exec redis redis-cli info memory
```

## Maintenance

### Regular Backups
```bash
# Manual backup
python backend/scripts/backup.py

# Verify backup
ls -lh nyaya_backup.sql
```

### Log Rotation
```bash
# Check log size
du -sh $(docker inspect --format='{{.LogPath}}' nyaya_api)

# Configure log rotation (docker-compose.yml)
```

### Health Checks
```bash
# Daily verification
python backend/scripts/verification/verify_all.py

# Weekly performance review
python backend/scripts/verification/verify_performance.py
```

### Security Updates
```bash
# Check for updates
docker compose pull

# Update base images in Dockerfile
vim backend/Dockerfile
vim frontend/Dockerfile

# Rebuild and test
docker compose build
python backend/scripts/verification/verify_all.py
```

## Incident Response

### Service Down
1. Check service status: `docker compose ps`
2. Review logs: `docker compose logs <service>`
3. Restart service: `docker compose up -d <service>`
4. Verify recovery: `python backend/scripts/verification/verify_all.py`

### High Latency
1. Check CPU/Memory: `docker stats`
2. Review slow queries: Check database logs
3. Scale resources if needed
4. Monitor improvement

### Data Corruption
1. Stop services: `docker compose down`
2. Restore from backup: `python backend/scripts/restore.py`
3. Verify data integrity: `python backend/scripts/verification/verify_database.py`
4. Resume services: `docker compose up -d`

## Documentation

- [Production Verification Framework](backend/scripts/verification/README.md)
- [Docker Compose Setup](docker-compose.yml)
- [Environment Configuration](.env.example)
- [API Documentation](http://localhost:8000/docs)

## Support

For issues or questions:
1. Review logs: `docker compose logs`
2. Check verification reports: `evidence/runtime/`
3. Review this runbook
4. Contact platform team
