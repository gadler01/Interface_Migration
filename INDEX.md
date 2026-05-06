# NetBox Interface Migration Tool

**Complete documentation for device and interface migration with advanced filtering**

---

## 📋 Documentation Index

### Getting Started

- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** ← **START HERE if on Windows**
  - Git installation
  - Python setup
  - Virtual environment
  - GitHub integration
  - GitHub Desktop / VS Code guides

- **[SETUP.md](SETUP.md)** ← **START HERE if on Linux**
  - Quick start (5 minutes)
  - Virtual environment setup
  - Configuration
  - Basic usage examples

### Full Documentation

- **[README.md](README.md)** ← **COMPLETE REFERENCE**
  - Full operator documentation
  - All commands and options
  - Troubleshooting guide
  - Common use cases
  - Best practices

### Git & Version Control

- **[GIT_SETUP.md](GIT_SETUP.md)**
  - Git workflow commands
  - Remote repository options (GitHub, GitLab, etc.)
  - Collaboration guides
  - Backup procedures

---

## 🚀 Quick Start by Platform

### Windows PC

```powershell
# 1. Install Git and Python (see WINDOWS_SETUP.md)
# 2. Clone repository
git clone https://github.com/YOUR_USERNAME/netbox-interface-migration.git
cd netbox-interface-migration

# 3. Setup
python -m venv netbox_env
.\netbox_env\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Edit script with your API token
code netbox_json_migration_advanced.py

# 5. Run
python netbox_json_migration_advanced.py export "dci" "" export.json --cabled
```

### Linux Server

```bash
# 1. Clone repository
git clone /home/grahama/netbox-interface-migration
cd netbox-interface-migration

# 2. Setup
source netbox_env/bin/activate
pip install -r requirements.txt

# 3. Run
python3 netbox_json_migration_advanced.py export "dci" "" export.json --cabled
```

---

## 📁 Repository Structure

```
netbox-interface-migration/
│
├── README.md                              (Complete operator guide)
├── SETUP.md                               (Linux quick start)
├── WINDOWS_SETUP.md                       (Windows installation & setup)
├── GIT_SETUP.md                           (Git configuration & remotes)
├── INDEX.md                               (This file)
│
├── netbox_json_migration_advanced.py      (Main tool)
├── requirements.txt                       (Python dependencies)
│
├── .gitignore                             (Git ignore patterns)
└── .git/                                  (Git history)
```

---

## 🎯 Common Tasks

### Export Interfaces

```bash
# All interfaces
python netbox_json_migration_advanced.py export "dci" "" export.json

# Only cabled
python netbox_json_migration_advanced.py export "dci" "" export.json --cabled

# Specific device type
python netbox_json_migration_advanced.py export "dci" "" export.json --device-type "Switch"

# Specific tag
python netbox_json_migration_advanced.py export "dci" "" export.json --tag "production"
```

### Import Interfaces

```bash
python netbox_json_migration_advanced.py import export.json "target-site" "location"

# Only cabled interfaces
python netbox_json_migration_advanced.py import export.json "target-site" "location" --connected
```

### Manage Git

```bash
# View history
git log --oneline

# Make changes
git add .
git commit -m "Description of changes"

# Push to remote
git push

# View status
git status
```

---

## 🔐 Configuration

Edit `netbox_json_migration_advanced.py` around line 350:

```python
NETBOX_URL = "https://nbupg.homelan.local"
API_TOKEN = "nbt_YOUR_FULL_TOKEN_HERE"
VERIFY_SSL = False  # For self-signed certs
```

Get your API token from NetBox:
1. Log into NetBox UI
2. Admin → Users
3. Click your username
4. Scroll to "Auth tokens"
5. Copy the token (includes `nbt_` prefix)

---

## 📊 Features

✅ **Export filtering:**
- All interfaces
- Cabled interfaces only
- By device type
- By device tag
- Combinations of above

✅ **Accurate tracking:**
- Interface counts per device
- Total cabled interface counts
- Export summaries with percentages
- Detailed logging

✅ **Import options:**
- Full import
- Cabled interfaces only
- Safe error handling
- Duplicate detection

✅ **Logging:**
- Timestamped log files
- ASCII compatible (Windows friendly)
- Detailed error messages
- Easy troubleshooting

---

## 🛠️ Tech Stack

- **Language:** Python 3.6+
- **Dependencies:** `requests` library
- **Version Control:** Git
- **Target:** NetBox API v2.8+

---

## 📖 Which File to Read?

| Situation | Read This |
|-----------|-----------|
| I'm on Windows, first time setup | WINDOWS_SETUP.md |
| I'm on Linux, first time setup | SETUP.md |
| I need complete reference documentation | README.md |
| I want to push to GitHub/GitLab | GIT_SETUP.md |
| I'm confused about which file to read | This file (INDEX.md) |

---

## ✨ Key Features Explained

### Export Summary Example

```
======================================================================
EXPORT SUMMARY
======================================================================
File:                  export_cabled.json
Export Type:           cabled
Device Type Filter:    (none)
Tag Filter:            (none)
Total Devices:         48
Total Interfaces:      567
Cabled Interfaces:     567
======================================================================
```

**What this means:**
- 48 devices were processed
- 567 interfaces are in the export
- All 567 have cables attached (100%)

### Import Summary Example

```
======================================================================
IMPORT SUMMARY
======================================================================
Total:    567
Created:  523 [OK]
Skipped:  34 [SKIP]
Failed:   10 [FAIL]
======================================================================
```

**What this means:**
- 523 new interfaces created ✓
- 34 already existed ⊘
- 10 had errors ✗

---

## 🔗 External Resources

- **NetBox Documentation:** https://netbox.dev/
- **NetBox API Docs:** https://netbox.dev/api/
- **Python Requests:** https://requests.readthedocs.io/
- **Git Documentation:** https://git-scm.com/doc
- **GitHub Guides:** https://guides.github.com/

---

## 📞 Support

**For setup issues on Windows:** See WINDOWS_SETUP.md  
**For setup issues on Linux:** See SETUP.md  
**For usage questions:** See README.md  
**For git/version control:** See GIT_SETUP.md  
**For log file analysis:** Check `netbox_migration_*.log`

---

## 📝 Version Info

- **Tool Version:** 1.0 (Advanced Edition)
- **Last Updated:** May 5, 2026
- **Python:** 3.6+
- **NetBox:** 2.8+

---

## 🚀 Ready to Start?

**Choose your platform:**

- 🪟 **Windows:** Go to [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- 🐧 **Linux:** Go to [SETUP.md](SETUP.md)
- 📚 **Full Docs:** Go to [README.md](README.md)

---

**Let's migrate! 🎯**
