# Database Setup & Operations Guide

## Production-Ready PostgreSQL Configuration

This document covers database operations, backups, migrations, security, and disaster recovery.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Security](#security)
3. [Migrations](#migrations)
4. [Backups & Recovery](#backups--recovery)
5. [Monitoring](#monitoring)
6. [Performance](#performance)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Initial Setup

1. **Set Database Password** (CRITICAL - Do this first!)

Edit `infra/.env` and change the default password:

```env
# Database Configuration
POSTGRES_USER=user
POSTGRES_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD  # ← CHANGE THIS!
POSTGRES_DB=instantviz
DATABASE_URL=postgresql+psycopg://user:YOUR_PASSWORD_HERE@db:5432/instantviz
```

**Generate a strong password:**
```bash
# On Linux/Mac:
openssl rand -base64 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

2. **Start Database**

```bash
cd infra
docker compose up -d db
```

3. **Run Migrations**

```bash
# Inside backend container or locally:
cd backend
alembic upgrade head
```

---

## Security

### ✅ IMPLEMENTED

1. **Database Only Accessible from Localhost**
   - Port mapping: `127.0.0.1:5432:5432`
   - Cannot be accessed from external networks

2. **Password in Environment Variable**
   - Never hardcoded in code
   - Stored in `.env` (git-ignored)

3. **Constraints Enforced at DB Level**
   - UNIQUE constraints on emails, Stripe IDs
   - CHECK constraints on usage counts, subscription statuses
   - Foreign key cascades for data integrity

4. **Connection Pooling**
   - Max 30 connections (10 persistent + 20 overflow)
   - Connections recycled every hour
   - Pre-ping to detect stale connections

### 🔒 ADDITIONAL SECURITY RECOMMENDATIONS

When deploying to production:

1. **Enable SSL/TLS**
   ```env
   DATABASE_URL=postgresql+psycopg://user:pass@db:5432/instantviz?sslmode=require
   ```

2. **Create Read-Only User** (for analytics)
   ```sql
   CREATE ROLE readonly_user WITH LOGIN PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE instantviz TO readonly_user;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;
   ```

3. **Rotate Passwords Quarterly**
   - Update `POSTGRES_PASSWORD` in `.env`
   - Restart database container
   - Update application connection strings

---

## Migrations

### Why Alembic?

- **Version Control**: Every schema change is tracked
- **Rollback**: Can undo migrations if something breaks
- **History**: See what changed and when
- **Team Collaboration**: Migrations are code - reviewable and mergeable

### Common Migration Commands

```bash
cd backend

# Create a new migration (after changing models)
alembic revision --autogenerate -m "Add user profile fields"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history --verbose

# Rollback to specific version
alembic downgrade <revision_id>
```

### Migration Workflow

1. **Modify SQLAlchemy Models** (`backend/models/*.py`)
2. **Generate Migration**:
   ```bash
   alembic revision --autogenerate -m "Descriptive message"
   ```
3. **Review Generated Migration** (`alembic/versions/XXX_*.py`)
   - Check for correctness
   - Add data migrations if needed
4. **Test Locally**:
   ```bash
   alembic upgrade head
   ```
5. **Commit to Git**:
   ```bash
   git add alembic/versions/
   git commit -m "Add migration: descriptive message"
   ```
6. **Deploy to Production**:
   ```bash
   # Run migrations before deploying new code
   alembic upgrade head
   ```

### Migration Best Practices

✅ **DO:**
- Always review auto-generated migrations
- Test migrations on a copy of production data
- Add both `upgrade()` and `downgrade()` functions
- Make backward-compatible changes when possible
- Run migrations before deploying new code

❌ **DON'T:**
- Edit applied migrations (create new ones instead)
- Delete migrations from git history
- Run migrations directly in production without testing
- Make breaking schema changes without a rollback plan

---

## Backups & Recovery

### Automated Daily Backups

**Setup Cron Job:**

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * /d/aiVisualizer/infra/scripts/backup-database.sh >> /var/log/db-backup.log 2>&1
```

**Manual Backup:**

```bash
cd /d/aiVisualizer/infra
./scripts/backup-database.sh
```

**Backup Location:** `infra/backups/instantviz_backup_YYYYMMDD_HHMMSS.sql.gz`

**Retention:** 30 days (configurable in script)

### Restore from Backup

```bash
cd /d/aiVisualizer/infra

# List available backups
ls -lh backups/

# Restore (DESTRUCTIVE - creates pre-restore backup automatically)
./scripts/restore-database.sh backups/instantviz_backup_20250102_020000.sql.gz
```

### Test Backup Integrity

**Run this weekly to ensure backups actually work:**

```bash
cd /d/aiVisualizer/infra
./scripts/test-backup-restore.sh
```

This script:
1. Creates a backup
2. Restores it to a test database
3. Compares row counts to verify integrity
4. Cleans up test database

**Expected output:**
```
✓ BACKUP/RESTORE TEST PASSED
All data restored correctly!
```

### Disaster Recovery Plan

**Scenario: Database Corrupted / Laptop Died / Accidental DELETE**

1. **Don't Panic** - Backups exist
2. **Find Latest Backup**:
   ```bash
   ls -lt /d/aiVisualizer/infra/backups/ | head
   ```
3. **Restore**:
   ```bash
   ./scripts/restore-database.sh backups/instantviz_backup_LATEST.sql.gz
   ```
4. **Verify**:
   ```bash
   docker exec -it infra-db-1 psql -U user -d instantviz -c "SELECT COUNT(*) FROM users;"
   ```
5. **Restart Application**:
   ```bash
   docker compose restart backend
   ```

**Recovery Time Objective (RTO):** < 15 minutes
**Recovery Point Objective (RPO):** Last backup (up to 24 hours of data loss)

### Off-Site Backups (Recommended for Production)

Currently backups are stored on the same machine. For production:

**Option 1: Cloud Storage (AWS S3)**
```bash
# After backup, upload to S3
aws s3 cp /d/aiVisualizer/infra/backups/ s3://my-backup-bucket/instantviz/ --recursive
```

**Option 2: External Drive**
```bash
# Mount external drive
mount /dev/sdb1 /mnt/backups

# Copy backups
rsync -av /d/aiVisualizer/infra/backups/ /mnt/backups/instantviz/
```

---

## Monitoring

### Health Check

```bash
# Check if database is running
docker exec infra-db-1 pg_isready -U user -d instantviz

# Check connection from backend
curl http://localhost:18001/health | jq
```

### Connection Pool Status

```bash
# Inside backend container
docker exec -it infra-backend-1 python -c "
from services.db import engine
print(f'Pool size: {engine.pool.size()}')
print(f'Checked out: {engine.pool.checkedout()}')
print(f'Overflow: {engine.pool.overflow()}')
"
```

### Slow Query Log

Edit `infra/docker-compose.yml` to enable slow query logging:

```yaml
db:
  environment:
    POSTGRES_LOG_MIN_DURATION_STATEMENT: "1000"  # Log queries > 1 second
```

View logs:
```bash
docker logs infra-db-1 | grep "duration:"
```

### Disk Usage

```bash
# Check database size
docker exec infra-db-1 psql -U user -d instantviz -c "
SELECT pg_size_pretty(pg_database_size('instantviz'));"

# Check table sizes
docker exec infra-db-1 psql -U user -d instantviz -c "
SELECT tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Active Connections

```bash
docker exec infra-db-1 psql -U user -d instantviz -c "
SELECT COUNT(*), state
FROM pg_stat_activity
WHERE datname = 'instantviz'
GROUP BY state;"
```

---

## Performance

### Indexes (Already Implemented)

✅ All critical indexes added:
- `users.email` (UNIQUE, for login lookups)
- `users.stripe_customer_id` (UNIQUE, for webhook lookups)
- `users.created_at` (for sorting users by signup date)
- `workspaces.owner_id, created_at` (composite, for "my recent workspaces")
- `projects.owner_id, updated_at` (composite, for "my recently edited projects")
- `project_visualizations.project_id, slide_number` (composite, for ordered retrieval)

### Query Optimization Tips

**Check if a query is using indexes:**
```sql
EXPLAIN ANALYZE
SELECT * FROM workspaces WHERE owner_id = 123 ORDER BY created_at DESC LIMIT 10;
```

Look for:
- ✅ "Index Scan" or "Index Only Scan" (good)
- ❌ "Seq Scan" on large tables (bad - add index)

**Find slow queries:**
```sql
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Connection Pool Tuning

Current settings (`backend/services/db.py`):
- `pool_size=10` (persistent connections)
- `max_overflow=20` (burst capacity)
- `pool_timeout=30` (wait time)
- `pool_recycle=3600` (refresh hourly)

Adjust based on load:
- **High traffic**: Increase `pool_size` to 20-30
- **Connection errors**: Increase `max_overflow`
- **Stale connection errors**: Decrease `pool_recycle`

---

## Troubleshooting

### "Too many connections" Error

**Cause:** Connection pool exhausted

**Fix:**
1. Check for connection leaks in code
2. Increase `POSTGRES_MAX_CONNECTIONS` in docker-compose.yml
3. Increase `max_overflow` in `backend/services/db.py`

**Immediate relief:**
```bash
# Kill idle connections
docker exec infra-db-1 psql -U user -d instantviz -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND state_change < NOW() - INTERVAL '5 minutes';"
```

### Migration Conflicts

**Error:** `FAILED: Multiple head revisions are present`

**Fix:**
```bash
# Merge migration branches
alembic merge heads -m "Merge migration branches"
alembic upgrade head
```

### Constraint Violation Errors

**Error:** `duplicate key value violates unique constraint "ix_users_email"`

**Cause:** Trying to insert duplicate email

**Fix:** This is expected behavior - handle in application code with try/catch

**Error:** `new row for relation "users" violates check constraint "check_usage_count_non_negative"`

**Cause:** Trying to set usage_count to negative number

**Fix:** Application bug - usage_count should never go below 0

### Backup Restore Fails

**Error:** `pg_restore: error: could not execute query: ERROR: role "someuser" does not exist`

**Cause:** Backup contains role ownership information

**Fix:** Already handled with `--no-owner --no-acl` flags in restore script

---

## Database Schema Overview

### Users Table
- **Primary Key:** `id`
- **Unique:** `email`, `stripe_customer_id`, `stripe_subscription_id`
- **Indexes:** `email`, `stripe_customer_id`, `stripe_subscription_id`, `created_at`, `(subscription_tier, subscription_status)`
- **Constraints:**
  - `usage_count >= 0`
  - `subscription_status IN ('active', 'canceled', 'past_due', ...)`
- **Cascade Deletes:** When user deleted, all workspaces/projects deleted

### Workspaces Table
- **Primary Key:** `id`
- **Foreign Key:** `owner_id` → `users.id` (ON DELETE CASCADE)
- **Indexes:** `owner_id`, `(owner_id, created_at)`, `(owner_id, updated_at)`
- **JSONB:** `data` (visualization state)

### Projects Table
- **Primary Key:** `id`
- **Foreign Key:** `owner_id` → `users.id` (ON DELETE CASCADE)
- **Indexes:** `owner_id`, `(owner_id, created_at)`, `(owner_id, updated_at)`
- **JSONB:** `context_metadata`, `topics`

### Project Visualizations Table
- **Primary Key:** `id`
- **Foreign Key:** `project_id` → `projects.id` (ON DELETE CASCADE)
- **Unique:** `(project_id, slide_number)` (no duplicate slide numbers)
- **Constraint:** `slide_number >= 1`
- **Indexes:** `project_id`, `(project_id, slide_number)`
- **JSONB:** `data`, `annotations`

---

## Checklist: Is Your Database Production-Ready?

- [x] Backups working and tested
- [x] Transactions on money/critical flows
- [x] Constraints in DB (not just app)
- [x] Indexes on main queries
- [x] Migrations versioned
- [x] Access control (localhost only)
- [x] Connection pooling configured
- [x] Monitoring enabled
- [x] Documented restore procedure
- [ ] Off-site backups configured (TODO)
- [ ] Alerting set up (disk space, connection errors) (TODO)
- [ ] SSL/TLS enabled (TODO - for production deployment)

---

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Database Best Practices](https://github.com/ankane/pgsync)

---

**Last Updated:** 2025-11-02
**Maintained By:** Development Team
