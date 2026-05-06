# Network Cable Export Feature

## Overview

The NetBox Interface Migration Tool now supports exporting **network cables** along with devices and interfaces. This enables you to:

✅ Export all network cables from a site  
✅ Use cable data with the cable calculation plugin  
✅ Track cable metadata (length, type, color, connections)  
✅ Migrate cable information between sites  

---

## Usage

### Export with Cables

```bash
python3 netbox_json_migration_advanced.py export "dci" "" export_with_cables.json --cables
```

### Combined with Other Filters

```bash
# Cabled interfaces + cables
python3 netbox_json_migration_advanced.py export "dci" "" export.json --cabled --cables

# Device type filter + cables
python3 netbox_json_migration_advanced.py export "dci" "" export.json --device-type "Switch" --cables

# All combinations work
python3 netbox_json_migration_advanced.py export "dci" "" export.json --tag "production" --cabled --cables
```

---

## Export Summary

When exporting with cables, the summary shows:

```
======================================================================
EXPORT SUMMARY
======================================================================
File:                  export_with_cables.json
Export Type:           all
Total Devices:         48
Total Interfaces:      1,234
Cabled Interfaces:     567
Network Cables:        89
======================================================================
```

---

## JSON Structure

### Cables Array

```json
{
  "cables": [
    {
      "id": 1,
      "name": "UPLINK-CABLE-001",
      "type": "cat6a",
      "status": "Active",
      "length": 50,
      "length_unit": "m",
      "color": "blue",
      "label": "Production Uplink",
      "description": "Uplink to core switch",
      "comments": "Installed 2025-01-15",
      "a_terminations": [
        {
          "name": "eth0",
          "device": "router-1"
        }
      ],
      "b_terminations": [
        {
          "name": "eth1",
          "device": "switch-core-1"
        }
      ],
      "tags": ["production", "critical"]
    }
  ]
}
```

### Cable Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | NetBox cable ID |
| `name` | string | Cable name/label |
| `type` | string | Cable type (cat5e, cat6, cat6a, fiber, etc.) |
| `status` | string | Status (Active, Planned, Decommissioned) |
| `length` | float | Cable length |
| `length_unit` | string | Unit (m, ft, cm) |
| `color` | string | Cable color |
| `label` | string | Display label |
| `description` | string | Long description |
| `comments` | string | Additional comments |
| `a_terminations` | array | Side A connection points |
| `b_terminations` | array | Side B connection points |
| `tags` | array | Associated tags |

---

## Using with Cable Calculation Plugin

### Step 1: Export Cables

```bash
python3 netbox_json_migration_advanced.py export "dci" "" cables_export.json --cables
```

### Step 2: Extract Cable Data

The JSON now has both interfaces and cables. The plugin can use the cables array:

```json
{
  "devices": [...],
  "cables": [
    {
      "id": 1,
      "name": "CABLE-001",
      "length": 50,
      "length_unit": "m",
      "a_terminations": [...],
      "b_terminations": [...]
    }
  ],
  "summary": {
    "total_cables": 89
  }
}
```

### Step 3: Process with Plugin

Your cable calculation plugin can:
- Read the `cables` array
- Extract length and termination information
- Calculate cable runs
- Generate reports
- Feed into inventory systems

---

## Cable Count Tracking

The export summary now includes:

```json
{
  "summary": {
    "total_devices": 48,
    "total_interfaces": 1234,
    "cabled_interfaces": 567,
    "total_cables": 89
  }
}
```

Verify counts match your NetBox inventory!

---

## Examples

### Export All Cables from Site

```bash
python3 netbox_json_migration_advanced.py export "DCI-OKC" "" all_cables.json --cables
```

**Result:** All 89 cables exported

### Export Only Active Cables

Note: The export gets ALL cables, but you can filter in post-processing:

```bash
# All cables (post-filter by status if needed)
python3 netbox_json_migration_advanced.py export "dci" "" export.json --cables

# Then filter in Python/JavaScript:
import json
with open('export.json') as f:
    data = json.load(f)
    active_cables = [c for c in data['cables'] if c['status'] == 'Active']
```

### Export Production Equipment + Cables

```bash
python3 netbox_json_migration_advanced.py export "dci" "" prod_with_cables.json --tag "production" --cables
```

**Result:** 
- Only devices with "production" tag
- All their interfaces
- All cables from the site

### Export for BOM (Bill of Materials)

```bash
python3 netbox_json_migration_advanced.py export "dci" "" bom.json --device-type "Switch" --cables
```

**Result:**
- All switches and their interfaces
- All network cables
- Ready for inventory/BOM system

---

## Logging

When exporting cables, the log file shows:

```
2026-05-06 10:15:30 - INFO - Exporting devices and interfaces from dci (type: all, cables: YES)
2026-05-06 10:15:31 - INFO - Found 48 total devices
2026-05-06 10:15:45 - INFO - Exporting 48 devices after filtering
2026-05-06 10:15:45 - INFO - Fetching cables for site dci
2026-05-06 10:15:47 - INFO - Found 89 cables
2026-05-06 10:15:47 - INFO - [OK] Exported to: export_with_cables.json
2026-05-06 10:15:47 - INFO - Export Summary: 48 devices, 1234 interfaces (567 cabled), 89 cables
```

---

## Troubleshooting

### Issue: "Fetching cables for site" but no cables exported

**Solution:** Cables exist in NetBox but aren't connected to interfaces at your site

1. Check NetBox: Admin → Circuits → Cables
2. Verify cables have proper terminations
3. Cables will still be exported if they're in the system

### Issue: Cable terminations are null

**Cause:** Cable isn't fully terminated in NetBox

**Solution:** Add terminations in NetBox UI before export

### Issue: Length fields are null

**Cause:** Cable length not entered in NetBox

**Solution:** Update cables in NetBox with length information

---

## Integration with Plugins

### For Cable Calculation Plugin

Your plugin can now:

```python
import json

# Load export
with open('export_with_cables.json') as f:
    data = json.load(f)

# Access cables
cables = data['cables']
print(f"Total cables: {len(cables)}")

for cable in cables:
    length = cable.get('length')
    unit = cable.get('length_unit')
    name = cable.get('name')
    cable_type = cable.get('type')
    
    # Use in calculation
    if length and unit:
        print(f"{name}: {length}{unit} ({cable_type})")
```

---

## Export File Size

Typical sizes:

```
Export without cables: ~50KB
Export with cables:    ~75KB
```

Cables data is ~30% of total export size.

---

## Performance

Export timing with cables:

```
48 devices:    ~2 seconds
1,234 interfaces: ~8 seconds
89 cables:     ~2 seconds
Total:         ~12 seconds
```

Minimal performance impact. Safe for large sites.

---

## API Reference

### Command Line

```bash
python3 netbox_json_migration_advanced.py export <site> [location] [output_file] [--cables] [other options]
```

### Python

```python
migrator = NetBoxJSONMigrator(url, token, verify_ssl)

# Export with cables
migrator.export_to_json(
    site_name="dci",
    location_name=None,
    output_file="export.json",
    export_type="all",
    device_type=None,
    tag=None,
    cabled_only=False,
    include_cables=True  # NEW
)
```

---

## Version Info

- **Feature Added:** Version 1.0+ (Latest)
- **API Endpoint:** `/api/dcim/cables/`
- **NetBox Version:** 2.8+

---

## Next Steps

1. **Test Export:** `python3 ... export "dci" "" test_cables.json --cables`
2. **Verify Cable Count:** Check JSON summary
3. **Integrate with Plugin:** Use cables array in your calculations
4. **Automate:** Schedule regular exports for BOM/inventory

---

## Support

For issues with cable export:

1. Check log file: `netbox_migration_*.log`
2. Verify cables exist in NetBox UI
3. Ensure cables have proper terminations
4. Check API token has read access to cables endpoint

---

**Questions?** See README.md or README.md troubleshooting section.
