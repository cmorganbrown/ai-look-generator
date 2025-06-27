# Data Persistence Guide

This guide explains how to maintain your TrendScraper data across deployments and prevent data loss.

## 🎯 Problem Solved

Previously, when you deployed to Railway, all your local data (looks, landing pages, uploads) would be lost because:
- Data directories weren't tracked in Git
- Railway creates a fresh environment on each deployment
- No backup system was in place

## ✅ Solutions Implemented

### 1. Git-Based Data Persistence (Primary Solution)

**What it does:**
- All data directories (`uploads/`, `landing_pages/`, `looks/`) are now tracked in Git
- Data persists across deployments automatically
- No manual intervention required

**How it works:**
- Modified `.gitignore` to include data directories
- All existing data has been committed to Git
- Future deployments will include all your data

### 2. Backup System (Secondary Solution)

**What it does:**
- Creates timestamped backups before deployments
- Allows manual backup/restore operations
- Provides additional data safety

**Usage:**
```bash
# Create a backup
python3 backup_data.py create [optional_name]

# List all backups
python3 backup_data.py list

# Restore from backup
python3 backup_data.py restore backup_name
```

### 3. Automated Deployment Script

**What it does:**
- Automatically creates a backup before deploying
- Handles git operations
- Ensures data safety during deployment

**Usage:**
```bash
./deploy.sh
```

## 📁 Data Directory Structure

```
TrendScraper/
├── uploads/           # Scraped data from Pinterest/Google
│   ├── *.json        # Pinterest product data
│   └── *.html        # Google Shopping data
├── landing_pages/     # Generated landing pages
│   └── *.html        # Individual landing pages
├── looks/            # AI-generated looks
│   ├── *.json        # Look data
│   ├── data/         # Look metadata
│   └── images/       # Generated hero images
├── backups/          # Local backups (not deployed)
│   └── backup_*/     # Timestamped backups
└── generated_images/ # Temporary generated images (not tracked)
```

## 🚀 Deployment Workflow

### Option 1: Automated Deployment (Recommended)
```bash
./deploy.sh
```

This will:
1. Create a backup of all data
2. Add changes to Git
3. Commit changes
4. Push to Railway
5. Deploy with all data intact

### Option 2: Manual Deployment
```bash
# Create backup first
python3 backup_data.py create

# Then deploy normally
git add .
git commit -m "Your commit message"
git push origin main
```

## 🔧 Maintenance

### Regular Backups
```bash
# Create a backup with custom name
python3 backup_data.py create "weekly_backup_$(date +%Y%m%d)"

# List all backups
python3 backup_data.py list
```

### Data Recovery
```bash
# Restore from a specific backup
python3 backup_data.py restore backup_20250627_143022
```

### Clean Up Old Backups
```bash
# Remove old backups (keep last 5)
ls -t backups/ | tail -n +6 | xargs -I {} rm -rf backups/{}
```

## ⚠️ Important Notes

1. **Generated Images**: The `generated_images/` directory is NOT tracked in Git to keep repository size manageable. These are temporary files that can be regenerated.

2. **Backup Size**: Backups can be large (several MB). Consider cleaning up old backups periodically.

3. **Railway Storage**: Railway has storage limits. Monitor your repository size and clean up if needed.

4. **API Keys**: Never commit API keys or sensitive data. They should remain in environment variables.

## 🆘 Troubleshooting

### Data Missing After Deployment
1. Check if data directories exist in Git: `git ls-files | grep -E "(uploads|landing_pages|looks)/"`
2. Verify data was committed: `git log --oneline --name-only`
3. Restore from backup if needed: `python3 backup_data.py restore latest_backup`

### Large Repository Size
1. Check what's taking space: `du -sh *`
2. Clean up generated images: `rm -rf generated_images/*`
3. Remove old backups: `rm -rf backups/backup_*`

### Backup Issues
1. Ensure you have write permissions: `ls -la backups/`
2. Check available disk space: `df -h`
3. Verify backup script works: `python3 backup_data.py create test_backup`

## 📊 Data Statistics

Your current data includes:
- **9 landing pages** (HTML files)
- **6 AI-generated looks** (JSON files)
- **14 upload files** (JSON/HTML scraped data)
- **Total size**: ~3.5MB of valuable data

All of this data is now safely persisted across deployments! 🎉 