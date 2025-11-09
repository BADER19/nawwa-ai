# Database Operations Scripts

This directory contains scripts for database backup, restore, monitoring, and testing.

## Scripts Overview

### 1. `backup-database.sh`
**Purpose:** Create compressed PostgreSQL backups automatically

**Usage:**
```bash
cd /d/aiVisualizer/infra
./scripts/backup-database.sh
```

**Features:**
- Creates compressed backups in `infra/backups/`
- Automatic retention (deletes backups older than 30 days)
- Logs backup history to `backup_log.json`
- Safe to run multiple times (won't conflict)

**Scheduling (Daily at 2 AM):**
```bash
# Edit crontab
crontab -e

# Add this line:
0 2 * * * /d/aiVisualizer/infra/scripts/backup-database.sh >> /var/log/db-backup.log 2>&1
```

---

### 2. `restore-database.sh`
**Purpose:** Restore database from backup file

**Usage:**
```bash
cd /d/aiVisualizer/infra
./scripts/restore-database.sh backups/instantviz_backup_20250102_020000.sql.gz
```

**Safety Features:**
- Requires typing "YES" to confirm (destructive operation)
- Creates pre-restore backup automatically
- Shows list of available backups if no argument provided

**⚠️ WARNING:** This will DELETE all current data and replace with backup!

---

### 3. `test-backup-restore.sh`
**Purpose:** Verify backup integrity by restoring to a test database

**Usage:**
```bash
cd /d/aiVisualizer/infra
./scripts/test-backup-restore.sh
```

**What it does:**
1. Creates a backup from current database
2. Restores to temporary test database
3. Compares row counts to verify data integrity
4. Cleans up test database

**Run this weekly** to ensure backups actually work!

**Expected output:**
```
✓ BACKUP/RESTORE TEST PASSED
All data restored correctly!
```

---

### 4. `monitor-database.sh`
**Purpose:** Show database health and statistics

**Usage:**
```bash
cd /d/aiVisualizer/infra
./scripts/monitor-database.sh
```

**Shows:**
- Database connectivity status
- Database and table sizes
- Row counts per table
- Active connections (total, active, idle)
- Recent activity (last 10 minutes)
- Backup age and status

**Use for:**
- Quick health check
- Debugging connection issues
- Monitoring disk space
- Verifying backups are running

---

## Environment Variables

All scripts support these environment variables:

```bash
# Database container name (default: infra-db-1)
export DB_CONTAINER=infra-db-1

# Database name (default: instantviz)
export DB_NAME=instantviz

# Database user (default: user)
export DB_USER=user

# Backup directory (default: /backups)
export BACKUP_DIR=/backups

# Backup retention in days (default: 30)
export RETENTION_DAYS=30
```

## File Permissions

Make scripts executable:

```bash
cd /d/aiVisualizer/infra/scripts
chmod +x *.sh
```

## Troubleshooting

### "Permission denied" when running scripts
```bash
chmod +x /d/aiVisualizer/infra/scripts/*.sh
```

### "Container not found" errors
Check container name:
```bash
docker ps --format "{{.Names}}" | grep db
```

Update `DB_CONTAINER` environment variable if different.

### Backup file too large
Backups are gzip-compressed. A 100MB database typically compresses to ~10-20MB.

If backups are still too large:
```bash
# Delete old backups manually
find /d/aiVisualizer/infra/backups -name "*.sql.gz" -mtime +7 -delete
```

### Restore takes too long
Large databases (>1GB) may take several minutes to restore. This is normal.

Progress is shown in real-time during restore.

---

## Production Checklist

Before deploying to production:

- [ ] Set up daily backup cron job
- [ ] Test restore procedure at least once
- [ ] Run `test-backup-restore.sh` to verify backups work
- [ ] Set up off-site backup copies (S3, external drive)
- [ ] Document who has access to restore backups
- [ ] Add monitoring script to health checks
- [ ] Configure alerts for backup failures

---

## Quick Reference

```bash
# Backup now
./scripts/backup-database.sh

# Restore latest backup
./scripts/restore-database.sh $(ls -t backups/*.sql.gz | head -1)

# Test backups work
./scripts/test-backup-restore.sh

# Check database health
./scripts/monitor-database.sh

# View backup logs
cat backups/backup_log.json | jq
```
