# NetBox Interface Migration Tool - Setup Guide

## Quick Start

### 1. Clone Repository

```bash
cd /home/<your_home>
git clone netbox-interface-migration
cd netbox-interface-migration
```

### 2. Create Virtual Environment

```bash
python3 -m venv netbox_env
source netbox_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Token

Edit `netbox_json_migration_advanced.py` and update:

```python
NETBOX_URL = "http://localhost:8000"
API_TOKEN = "nbt_YOUR_FULL_TOKEN_HERE"
VERIFY_SSL = True
```

### 5. Test Connection

```bash
python3 netbox_json_migration_advanced.py export --help
```

## Basic Usage

### Export All Interfaces

```bash
python3 netbox_json_migration_advanced.py export "dci" "" export.json
```

### Export Only Cabled

```bash
python3 netbox_json_migration_advanced.py export "dci" "" export_cabled.json --cabled
```

### Import to New Site

```bash
python3 netbox_json_migration_advanced.py import export_cabled.json "lightedge-chaska" "dci"
```

## Documentation

See `README.md` for complete operator documentation.

## Git Workflow

### First Time Setup

```bash
cd /~/netbox-interface-migration
git config user.email "your@email.com"
git config user.name "Your Name"
```

### Add Changes

```bash
git add netbox_json_migration_advanced.py
git commit -m "Update: Add new filtering option"
git log --oneline
```

### View History

```bash
git log --oneline
git show <commit-hash>
git diff HEAD~1
```

## Support

For issues, check the log files:

```bash
tail -f netbox_migration_*.log
```

For usage help:

```bash
python3 netbox_json_migration_advanced.py help
```
