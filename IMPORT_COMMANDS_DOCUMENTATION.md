# Import Commands Documentation

## Overview

The NetBox Interface Migration Tool supports **three types of imports**:

1. **Interface Import** - Create interfaces on existing devices
2. **Cable Import** - Create network cables in NetBox
3. **Combined Import** - Interfaces and cables together

---

## Import Command Syntax

```bash
python3 netbox_json_migration_advanced.py import <json_file> <target_site> [target_location] [options]
```

### Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `<json_file>` | Yes | Export JSON file | `export_cabled.json` |
| `<target_site>` | Yes | Destination site | `"LightEdge-Chaska"` or `"lightedge-chaska"` |
| `[target_location]` | No | Destination location | `"DCI"` or leave empty |
| `[options]` | No | Import modifiers | `--connected`, `--cables-only` |

### Options

| Option | Description | Use Case |
|--------|-------------|----------|
| `--connected` | Only import interfaces with cables | Safer production imports |
| `--cables-only` | Import only cables, skip interfaces | Cable-only migration |

---

## Import Examples

### Example 1: Basic Interface Import

```bash
python3 netbox_json_migration_advanced.py import export.json "LightEdge-Chaska" "DCI"
```

**What it does:**
- Reads `export.json`
- Creates interfaces on devices at `LightEdge-Chaska / DCI`
- Devices must already exist at target

**Output:**
```
Import from export.json to LightEdge-Chaska? (yes/no): yes

======================================================================
INTERFACE IMPORT SUMMARY
======================================================================
Total:    567
Created:  523 [OK]
Skipped:  34 [SKIP]
Failed:   10 [FAIL]
======================================================================
```

**What this means:**
- 567 interfaces to import
- 523 successfully created
- 34 already existed (skipped)
- 10 had errors (failed)

---

### Example 2: Import Only Cabled Interfaces

```bash
python3 netbox_json_migration_advanced.py import export.json "LightEdge-Chaska" "DCI" --connected
```

**What it does:**
- Only imports interfaces marked as having cables
- Skips virtual/loopback interfaces
- Safer for production environments

**Use case:** You only want physical connections, not management interfaces

---

### Example 3: Import Without Location

```bash
python3 netbox_json_migration_advanced.py import export.json "LightEdge-Chaska"
```

**What it does:**
- Imports to site-level (no location assignment)
- Useful if target doesn't have locations defined

---

### Example 4: Import Only Cables

```bash
python3 netbox_json_migration_advanced.py import export_with_cables.json "LightEdge-Chaska" --cables-only
```

**What it does:**
- Skips all interfaces
- Creates only network cables
- Perfect for cable inventory migration
- Ignores the location parameter

**Output:**
```
Import from export_with_cables.json to LightEdge-Chaska? (yes/no): yes

======================================================================
CABLE IMPORT SUMMARY
======================================================================
Total:    89
Created:  85 [OK]
Skipped:  2 [SKIP]
Failed:   2 [FAIL]
======================================================================
```

---

### Example 5: Combined - Interfaces and Cables

**Step 1: Export both**
```bash
python3 netbox_json_migration_advanced.py export "dci" "" export_all.json --cables
```

**Step 2: Import interfaces**
```bash
python3 netbox_json_migration_advanced.py import export_all.json "target-site" "location"
```

**Step 3: Import cables** (optional - run separately or together)
```bash
python3 netbox_json_migration_advanced.py import export_all.json "target-site" --cables-only
```

---

## Prerequisites for Successful Import

### For Interface Import

✅ **Devices must exist** at target site with same names  
✅ **Location must exist** (if importing to location)  
✅ **VLANs must exist** (if using tagged interfaces)  
✅ **Interface names unique** (not already present)  
✅ **Device API accessible** (read permissions)  

### For Cable Import

✅ **Cable types must exist** in NetBox  
✅ **No duplicate cable names** (cables are unique)  
✅ **Cable API accessible** (write permissions)  

### For Both

✅ **Valid API token** with write permissions  
✅ **Target site reachable** by NetBox API  
✅ **Export JSON valid** (from export command)  

---

## Import Summary Interpretation

### Interface Import Summary

```
Total:    567        Total interfaces to import
Created:  523 [OK]   Successfully created
Skipped:  34 [SKIP]  Already existed at target
Failed:   10 [FAIL]  Errors during creation
```

**Success rate:** 523/567 = 92%

### Cable Import Summary

```
Total:    89         Total cables to import
Created:  85 [OK]    Successfully created
Skipped:  2 [SKIP]   Already existed
Failed:   2 [FAIL]   Errors during creation
```

**Success rate:** 85/89 = 96%

---

## Logging

### Import Log Entries

The log file (`netbox_migration_*.log`) shows:

**For interfaces:**
```
2026-05-06 10:30:00 - INFO - Importing to lightedge-chaska / DCI
2026-05-06 10:30:01 - INFO - [OK] Created eth0 on router-1
2026-05-06 10:30:02 - INFO - [SKIP] Skipped (exists): eth1 on router-1
2026-05-06 10:30:03 - ERROR - [FAIL] Failed to create mgmt on switch-1: VLAN not found
```

**For cables:**
```
2026-05-06 10:30:00 - INFO - Importing 89 cables to lightedge-chaska
2026-05-06 10:30:01 - INFO - [OK] Created cable: UPLINK-CABLE-001
2026-05-06 10:30:02 - INFO - [SKIP] Cable already exists: CORE-CABLE-002
```

---

## Common Import Scenarios

### Scenario 1: Disaster Recovery Replication

**Goal:** Replicate production to DR site

```bash
# 1. Export from production
python3 ... export "production" "" prod_dr.json --cabled --cables

# 2. Create devices at DR (manually)

# 3. Import interfaces to DR
python3 ... import prod_dr.json "DR-Site" "DCI"

# 4. Import cables to DR
python3 ... import prod_dr.json "DR-Site" --cables-only
```

---

### Scenario 2: Network Switch Replacement

**Goal:** Migrate interfaces from old to new switch

```bash
# 1. Export old switch config
python3 ... export "dci" "" old_switch.json --device-type "Catalyst 6509"

# 2. Edit JSON: rename devices (old-sw → new-sw)

# 3. Import to new switches
python3 ... import old_switch.json "dci" "DCI"
```

---

### Scenario 3: Production-Only Migration

**Goal:** Migrate only production equipment

```bash
# 1. Export production tagged equipment + cables
python3 ... export "dci" "" prod.json --tag "production" --cabled --cables

# 2. Import to new site
python3 ... import prod.json "new-site" "location"

# 3. Verify all created
# Check log for failure count
```

---

### Scenario 4: Cable Inventory Migration

**Goal:** Migrate cable catalog between NetBox instances

```bash
# Export cables from source
python3 ... export "source-site" "" cables.json --cables

# Import to destination
python3 ... import cables.json "dest-site" --cables-only
```

---

## Troubleshooting Import Issues

### Issue: "Device not found at target site"

**Cause:** Device doesn't exist at destination

**Solution:**
1. Create device at target site first
2. Ensure exact name match (case-sensitive)
3. Check log for specific device names

**Command to check:**
```bash
grep "Device not found" netbox_migration_*.log
```

---

### Issue: "VLAN not found"

**Cause:** VLAN doesn't exist at target site

**Solution:**
1. Create VLAN at target site: Admin → VLANs
2. Script warns but continues
3. Manually assign VLAN after import

**To avoid:** Use `--connected` flag (skips VLAN issues)

---

### Issue: "Location not found"

**Cause:** Location doesn't exist at target site

**Solution:**
1. Create location at target: Admin → Locations
2. Or import without location parameter
3. Or answer "yes" when prompted to continue

---

### Issue: Import shows "0 created"

**Cause:** Interfaces already exist or devices not found

**Solution:**
1. Check log file for specific errors
2. Verify device names match
3. Use different devices for testing
4. Try `--connected` flag to skip problem devices

**Debug command:**
```bash
grep FAIL netbox_migration_*.log | head -20
```

---

### Issue: "Cable already exists"

**Cause:** Cable with same name exists at target

**Solution:**
1. Choose different cable names in export
2. Or use different target site
3. Or delete existing cables first

**To list existing:**
```bash
# In NetBox UI: Admin → Circuits → Cables
```

---

## Import vs Export Comparison

| Operation | Direction | Data | Time |
|-----------|-----------|------|------|
| Export | Source → JSON | Devices, interfaces, cables | 5-15s |
| Import | JSON → Target | Interfaces and/or cables | 5-30s |

### Typical Workflow

```
Export Site A (15s)
  ↓
Verify JSON (1m)
  ↓
Create devices at Site B (manual, 30m)
  ↓
Import interfaces (20s)
  ↓
Import cables (10s)
  ↓
Verify in NetBox (5m)
  ↓
DONE!
```

---

## Best Practices for Imports

### Before Import

- ✓ Backup target NetBox database
- ✓ Create all target devices
- ✓ Create all required VLANs
- ✓ Create all required locations
- ✓ Verify JSON file is valid
- ✓ Test on staging first

### During Import

- ✓ Monitor log file in real-time
- ✓ Watch for error patterns
- ✓ Run confirmation prompt shows target
- ✓ Check summary for fail count
- ✓ Don't close terminal

### After Import

- ✓ Verify in NetBox UI (sample check)
- ✓ Check interface counts match export
- ✓ Verify VLANs assigned correctly
- ✓ Test network connectivity
- ✓ Archive logs for audit trail

---

## Performance Metrics

### Import Times

```
100 interfaces:   ~10 seconds
500 interfaces:   ~30 seconds
1000 interfaces:  ~60 seconds
100 cables:       ~15 seconds
```

Add ~20% for API latency on remote NetBox instances.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (check log) |

Always check the log file for details!

---

## API Reference

### Import from Command Line

```bash
# Interfaces
python3 tool.py import export.json "site" "location" [--connected]

# Cables only
python3 tool.py import export.json "site" --cables-only

# Help
python3 tool.py help
```

### Import from Python

```python
from netbox_json_migration_advanced import NetBoxJSONMigrator

migrator = NetBoxJSONMigrator(url, token, verify_ssl)

# Import interfaces
stats = migrator.import_from_json(
    json_file="export.json",
    target_site="target-site",
    target_location="location",
    only_connected=False
)

# Import cables
cable_stats = migrator.import_cables_from_json(
    json_file="export.json",
    target_site="target-site"
)

# Check results
print(f"Created: {stats['created']}")
print(f"Failed: {stats['failed']}")
```

---

## Complete Import Reference

### All Import Commands

```bash
# Basic interface import
python3 ... import export.json "target-site"

# With location
python3 ... import export.json "target-site" "location"

# Only cabled interfaces (safer)
python3 ... import export.json "target-site" "location" --connected

# Only cables (skip interfaces)
python3 ... import export.json "target-site" --cables-only

# Cables without location
python3 ... import export.json "target-site" --cables-only

# Help
python3 ... help
```

---

## Summary

**Import Types:**
- Interface import → Creates interfaces on existing devices
- Cable import → Creates network cables in NetBox
- Combined → Run separately for both

**Options:**
- `--connected` → Only interfaces with cables
- `--cables-only` → Skip interfaces, cables only

**Prerequisites:**
- Devices must exist for interface import
- VLANs must exist for tagged interfaces
- Site must exist (any import type)

**Monitor:**
- Check log file for details
- Review import summary
- Verify in NetBox UI
- Test connectivity

---

**Ready to import?** See examples above for your use case!
