# NetBox Interface Migration Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![NetBox 2.8+](https://img.shields.io/badge/NetBox-2.8+-green.svg)](https://netbox.dev/)

**Advanced device and interface migration tool for NetBox with filtering, tracking, and logging.**

## 🎯 What It Does

Export devices and interfaces from one NetBox site to JSON, then import them to another site with:

- ✅ Advanced filtering (device type, tags, cabled status)
- ✅ Interface count tracking and summaries
- ✅ Accurate import reporting (created, skipped, failed)
- ✅ Detailed logging for troubleshooting
- ✅ Windows and Linux compatible

**Perfect for:**
- Disaster recovery (DR) replication
- Site migrations
- Device replacements
- Testing and staging environments
- Infrastructure as Code (IaC) workflows

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Export Guide](#export-guide)
6. [Import Guide](#import-guide)
7. [Logging & Monitoring](#logging--monitoring)
8. [Common Use Cases](#common-use-cases)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)
11. [Contributing](#contributing)

---

## 🚀 Quick Start

### Linux/Mac (5 minutes)

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/netbox-interface-migration.git
cd netbox-interface-migration
python3 -m venv netbox_env
source netbox_env/bin/activate
pip install -r requirements.txt

# Configure
nano netbox_json_migration_advanced.py
# Update: NETBOX_URL, API_TOKEN, VERIFY_SSL

# Run
python3 netbox_json_migration_advanced.py export "dci" "" export.json --cabled
python3 netbox_json_migration_advanced.py import export.json "target-site" "location"
```

### Windows (10 minutes)

See **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** for detailed instructions including:
- Git installation
- Python setup
- GitHub Desktop guide
- VS Code integration

---

## 💾 Installation

### Prerequisites

- **Python 3.6+** ([download](https://www.python.org/downloads/))
- **Git** ([download](https://git-scm.com/))
- **NetBox 2.8+** with API access
- **NetBox API token**

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/netbox-interface-migration.git
cd netbox-interface-migration
```

### Step 2: Create Virtual Environment

**Linux/Mac:**
```bash
python3 -m venv netbox_env
source netbox_env/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv netbox_env
.\netbox_env\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Get NetBox API Token

1. Log into NetBox UI: `https://your-netbox:8000`
2. Click your **username** (bottom left)
3. Scroll to **Auth tokens** section
4. Copy the token (includes `nbt_` prefix)

---

## ⚙️ Configuration

Edit `netbox_json_migration_advanced.py` and update these lines (around line 350):

```python
# Configuration
NETBOX_URL = "https://<YUPR_SERVER_URL>" #
API_TOKEN = "nbt_<YOUR_KEY>.<YOUR_FULL_TOKEN>"
VERIFY_SSL = True  # Set to False if using Self-Signed SSL cert
```

### Verify Configuration

```bash
python3 netbox_json_migration_advanced.py export --help
```

Should show help menu without errors.

---

## 🎬 Usage

### Display Help

```bash
python3 netbox_json_migration_advanced.py help
```

### Export Command

```bash
python3 netbox_json_migration_advanced.py export <site> [location] [output_file] [options]
```

### Import Command

```bash
python3 netbox_json_migration_advanced.py import <json_file> <target_site> [target_location] [--connected]
```

---

## 📤 Export Guide

### Export All Interfaces

```bash
python3 netbox_json_migration_advanced.py export "DCI-OKC" "" export_all.json
```

**Output:**
```
======================================================================
EXPORT SUMMARY
======================================================================
File:                  export_all.json
Export Type:           all
Total Devices:         48
Total Interfaces:      1,234
Cabled Interfaces:     567
======================================================================
```

**Use for:** Complete infrastructure backups, disaster recovery

---

### Export Only Cabled Interfaces

```bash
python3 netbox_json_migration_advanced.py export "DCI-OKC" "" export_cabled.json --cabled
```

**Output:**
```
======================================================================
EXPORT SUMMARY
======================================================================
File:                  export_cabled.json
Export Type:           cabled
Total Devices:         48
Total Interfaces:      567
Cabled Interfaces:     567
======================================================================
```

**Use for:** Production interfaces only, skip virtual/loopback

---

### Export by Device Type

```bash
python3 netbox_json_migration_advanced.py export "DCI-OKC" "" export_switches.json --device-type "Switch"
```

**Use for:** Device replacement, network upgrades

---

### Export by Tag

```bash
python3 netbox_json_migration_advanced.py export "DCI-OKC" "" export_prod.json --tag "production"
```

**Use for:** Production migrations, tag-based deployments

---

### Export Specific Location

```bash
python3 netbox_json_migration_advanced.py export "DCI-OKC" "Building-A/Floor-2" export_floor2.json
```

**Use for:** Floor migrations, location-specific backups

---

### Combine Filters

```bash
python3 netbox_json_migration_advanced.py export "DCI-OKC" "" export_prod_switches.json --device-type "Switch" --tag "production" --cabled
```

**Export:** Production switches with cables only

---

## 📥 Import Guide

### Basic Import

```bash
python3 netbox_json_migration_advanced.py import export_all.json "LightEdge-Chaska" "DCI"
```

**Output:**
```
============================================================
IMPORT SUMMARY
============================================================
Total:    1,234
Created:  1,100 [OK]
Skipped:  100 [SKIP]
Failed:   34 [FAIL]
============================================================
```

---

### Import Only Cabled Interfaces

```bash
python3 netbox_json_migration_advanced.py import export_all.json "LightEdge-Chaska" "DCI" --connected
```

Skips interfaces without cables (safer for production)

---

### Import Without Location

```bash
python3 netbox_json_migration_advanced.py import export.json "LightEdge-Chaska"
```

Import to site-level (no location assignment)

---

### Prerequisites for Import

✅ **Devices must exist** at target site with same names  
✅ **Location must exist** (if importing to location)  
✅ **VLANs must exist** (if using tagged interfaces)  
✅ **Interface names must be unique** (not already present)

---

## 📊 Logging & Monitoring

### Log File Location

```
netbox_migration_20260505_143022.log
```

Logs are created in working directory with timestamps.

### View Logs

```bash
# View latest log
tail -f netbox_migration_*.log

# Search for errors
grep ERROR netbox_migration_*.log

# Search for specific device
grep "router-1" netbox_migration_*.log
```

### Log Entries

```
[OK]   Successfully created interface
[SKIP] Interface already exists
[FAIL] Error creating interface
```

### Key Metrics

```
2026-05-05 14:30:22 - INFO - Found 48 total devices
2026-05-05 14:30:23 - INFO - Filtered 12 devices by type "Switch"
2026-05-05 14:30:25 - INFO - Found location 'DCI': 1 results
2026-05-05 14:30:26 - INFO - [OK] Created eth0 on router-1
```

---

## 🎯 Common Use Cases

### Use Case 1: Disaster Recovery Replication

**Goal:** Replicate production to DR site

```bash
# 1. Export production
python3 netbox_json_migration_advanced.py export "Production" "" prod_backup.json --cabled

# 2. Verify export
cat netbox_migration_*.log | grep "EXPORT SUMMARY"

# 3. Create devices at DR site (manual or script)

# 4. Import to DR
python3 netbox_json_migration_advanced.py import prod_backup.json "DR-Site" "DCI"

# 5. Verify import
cat netbox_migration_*.log | grep "IMPORT SUMMARY"
```

---

### Use Case 2: Network Switch Replacement

**Goal:** Migrate interfaces from old to new switch

```bash
# 1. Export old switch
python3 netbox_json_migration_advanced.py export "DCI-OKC" "" old_switch.json --device-type "Catalyst 6509"

# 2. Edit JSON to rename devices (old-sw-1 → new-sw-1)
nano old_switch.json

# 3. Import to same site
python3 netbox_json_migration_advanced.py import old_switch.json "DCI-OKC" "DCI"
```

---

### Use Case 3: Production-Only Migration

**Goal:** Export and migrate only production

```bash
# 1. Tag devices as "production" in NetBox

# 2. Export production only
python3 netbox_json_migration_advanced.py export "DCI-OKC" "" prod_export.json --tag "production" --cabled

# 3. Import to test environment
python3 netbox_json_migration_advanced.py import prod_export.json "Staging" "Test-Lab"
```

---

### Use Case 4: Location Migration

**Goal:** Move all devices from one floor to another

```bash
# Export specific floor
python3 netbox_json_migration_advanced.py export "DCI-OKC" "Building-A/Floor-2" floor2.json

# Import to new floor
python3 netbox_json_migration_advanced.py import floor2.json "DCI-OKC" "Building-B/Floor-3"
```

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to NetBox"

**Cause:** API token invalid or URL wrong

**Solution:**
```bash
# Verify URL format
curl -H "Authorization: Bearer nbt_YOUR_TOKEN" https://your-netbox:8000/api/status/

# Check token has correct prefix (nbt_)
# Verify firewall allows connection
```

---

### Issue: "No devices found"

**Cause:** Site name incorrect or empty site

**Solution:**
```bash
# Use site slug instead of display name
export "dci" "" export.json    # slug
# instead of
export "DCI-OKC" "" export.json  # display name might fail

# Check site exists
python3 -c "import requests; resp = requests.get('https://your-netbox:8000/api/dcim/sites/', verify=False, headers={'Authorization': 'Bearer nbt_TOKEN'}); [print(f\"{s['name']} ({s['slug']})\" ) for s in resp.json()['results']]"
```

---

### Issue: "Location not found"

**Cause:** Location doesn't exist at target site

**Solution:**
```bash
# Create location in NetBox first: Admin → Locations → New

# Or answer "yes" when prompted to continue anyway
# Or import without location
python3 netbox_json_migration_advanced.py import export.json "LightEdge-Chaska"
```

---

### Issue: "Device not found at target"

**Cause:** Devices don't exist at destination

**Solution:**
```bash
# Create devices at target site first
# Must have exact same names as source

# Verify device names match
grep '"name"' export.json | head -5
```

---

### Issue: "VLAN not found"

**Cause:** VLAN doesn't exist at target

**Solution:**
```bash
# Create VLAN at target: Admin → VLANs → New
# Script warns but continues
# Manually assign VLAN after if needed
```

---

### Issue: Import shows "0 created"

**Cause:** Interfaces already exist or devices not found

**Solution:**
1. Check log file for specific errors
2. Verify device names at target
3. Check if interfaces already exist
4. Use `--connected` flag to skip problem devices

```bash
# Check log
grep FAIL netbox_migration_*.log
```

---

### Issue: SSL Certificate Error

**Cause:** Self-signed certificate on NetBox

**Solution:**
Edit script and set:
```python
VERIFY_SSL = False
```

---

## ✅ Best Practices

### Before Export

- ✓ Backup NetBox database
- ✓ Verify source devices exist
- ✓ Test on staging first
- ✓ Check API token permissions

### During Export

- ✓ Review export summary
- ✓ Verify JSON file created
- ✓ Spot-check JSON content
- ✓ Check device and interface counts

### Before Import

- ✓ Create target devices
- ✓ Create target VLANs
- ✓ Create target locations
- ✓ Verify interface names are unique

### During Import

- ✓ Use `--connected` flag first
- ✓ Review import summary
- ✓ Monitor log file
- ✓ Check error patterns

### After Import

- ✓ Verify in NetBox UI
- ✓ Test network connectivity
- ✓ Archive logs for audit trail
- ✓ Document any manual fixes

---

## 📚 Command Reference

### Export Options

| Option | Description | Example |
|--------|-------------|---------|
| `--all` | Export all interfaces (default) | `export dci "" export.json --all` |
| `--cabled` | Only with cables | `export dci "" export.json --cabled` |
| `--device-type NAME` | Filter by type | `export dci "" export.json --device-type "Switch"` |
| `--tag NAME` | Filter by tag | `export dci "" export.json --tag "production"` |

### Import Options

| Option | Description | Example |
|--------|-------------|---------|
| `--connected` | Only cabled interfaces | `import export.json dci dci --connected` |

### File Naming Convention

```
export_all.json              # Export type
export_cabled.json           # Cabled only
export_switches.json         # Device type filter
export_production.json       # Tag filter
netbox_migration_*.log       # Log files (auto)
```

---

## 📦 What Gets Exported

### ✅ Included

- Device name, type, status, tags, location
- Interface name, type, MTU, description, mode
- VLAN assignments (tagged and untagged)
- Cable attachment status
- Enabled/disabled status

### ✗ Not Included

- Device physical attributes (serial, asset tag)
- MAC addresses
- Cable routing/connections
- Power information
- IP addresses
- DNS names

---

## 🔐 Security

### API Token

- Never commit tokens to git
- Use `.gitignore` to exclude local config
- Store securely on your system
- Rotate tokens periodically

### Best Practices

```bash
# Don't do this:
git add netbox_json_migration_advanced.py  # Has token!

# Do this instead:
git add netbox_json_migration_advanced.py  # Token in .gitignore
# or use environment variables
export NETBOX_TOKEN="nbt_YOUR_TOKEN"
```

---

## 🤝 Contributing

### Report Issues

1. Check [Troubleshooting](#troubleshooting) section
2. Review log file for errors
3. Search existing issues
4. Create new issue with:
   - Error message
   - Steps to reproduce
   - Log file excerpt
   - NetBox version

### Suggest Improvements

1. Open an issue with `[Enhancement]` label
2. Describe the improvement
3. Include examples
4. Link to any related docs

### Submit Code

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Test thoroughly
5. Commit with clear message
6. Push: `git push -u origin feature/my-feature`
7. Create Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📚 Documentation

- **[INDEX.md](INDEX.md)** - Documentation navigation
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** - Windows installation guide
- **[SETUP.md](SETUP.md)** - Linux quick start
- **[GIT_SETUP.md](GIT_SETUP.md)** - Git configuration and remotes

---

## 🆘 Support

### Common Errors

| Error | Fix |
|-------|-----|
| `403 Forbidden` | Check API token |
| `400 Bad Request` | Use correct site name |
| `Device not found` | Create device first |
| `VLAN not found` | Create VLAN first |
| `SSL error` | Set `VERIFY_SSL = False` |

### Get Help

1. Check **[Troubleshooting](#troubleshooting)** section above
2. Review **[README.md](README.md)** (this file)
3. Check log file: `netbox_migration_*.log`
4. Open an issue on GitHub

---

## 🚀 Quick Links

- **GitHub:** https://github.com/YOUR_USERNAME/netbox-interface-migration
- **NetBox Docs:** https://netbox.dev/
- **NetBox API:** https://netbox.dev/api/
- **Python Requests:** https://requests.readthedocs.io/

---

## 📊 Status

| Component | Status |
|-----------|--------|
| Export | ✅ Production Ready |
| Import | ✅ Production Ready |
| Filtering | ✅ Production Ready |
| Logging | ✅ Production Ready |
| Documentation | ✅ Complete |
| Windows Support | ✅ Full |
| Linux Support | ✅ Full |

---

## 🙏 Acknowledgments

Built for NetBox administrators and infrastructure teams managing complex device migrations.

---

## 📝 Changelog

### Version 1.0 (May 2026)

- Initial release
- Export filtering (device type, tags, cabled)
- Interface count tracking
- Detailed logging
- Windows/Linux compatibility
- Comprehensive documentation
- Git integration ready

---

**Last Updated:** May 5, 2026

**Questions?** See [INDEX.md](INDEX.md) for navigation or check [Troubleshooting](#troubleshooting) above.

**Ready to get started?** Pick your platform:
- 🪟 [Windows Setup](WINDOWS_SETUP.md)
- 🐧 [Linux Setup](SETUP.md)
