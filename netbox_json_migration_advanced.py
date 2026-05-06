#!/usr/bin/env python3
"""
NetBox Device & Interface JSON Migration Tool with Advanced Filtering
Export: all interfaces, by device type, by tag, or by cable status
"""

import json
import sys
import requests
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


# Setup logging
log_file = f"netbox_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NetBoxJSONMigrator:
    """Export/import devices and interfaces as JSON with advanced filtering."""

    def __init__(self, base_url: str, api_token: str, verify_ssl: bool = True):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.verify_ssl = verify_ssl
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.verify = verify_ssl

    def test_connection(self) -> bool:
        """Test API connectivity."""
        try:
            resp = self.session.get(f"{self.base_url}/api/dcim/devices/?limit=1")
            resp.raise_for_status()
            logger.info("[OK] Connected to NetBox")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to NetBox: {e}")
            return False

    def get_devices_by_site_and_location(self, site_name: str, location_name: Optional[str] = None) -> List[Dict]:
        """Get all devices at a site and optionally a specific location."""
        try:
            params = {"site": site_name, "limit": 1000}
            if location_name:
                params["location"] = location_name
            
            resp = self.session.get(f"{self.base_url}/api/dcim/devices/", params=params)
            resp.raise_for_status()
            return resp.json()["results"]
        except Exception as e:
            logger.error(f"Error fetching devices: {e}")
            return []

    def get_interfaces_for_device(self, device_id: int) -> List[Dict]:
        """Get all interfaces for a device."""
        try:
            resp = self.session.get(
                f"{self.base_url}/api/dcim/interfaces/",
                params={"device_id": device_id, "limit": 1000}
            )
            resp.raise_for_status()
            return resp.json()["results"]
        except Exception as e:
            logger.error(f"Error fetching interfaces for device {device_id}: {e}")
            return []

    def filter_devices_by_type(self, devices: List[Dict], device_type: str) -> List[Dict]:
        """Filter devices by type name."""
        filtered = []
        for device in devices:
            dev_type = device.get("device_type", {}).get("display", "")
            if device_type.lower() in dev_type.lower():
                filtered.append(device)
        logger.info(f"Filtered {len(devices)} devices to {len(filtered)} with type matching '{device_type}'")
        return filtered

    def filter_devices_by_tag(self, devices: List[Dict], tag: str) -> List[Dict]:
        """Filter devices by tag."""
        filtered = []
        for device in devices:
            tags = [t.get("name", "") for t in device.get("tags", [])]
            if tag in tags:
                filtered.append(device)
        logger.info(f"Filtered {len(devices)} devices to {len(filtered)} with tag '{tag}'")
        return filtered

    def filter_interfaces_by_cable(self, interfaces: List[Dict]) -> List[Dict]:
        """Filter interfaces to only those with cables attached."""
        filtered = [iface for iface in interfaces if iface.get("cable")]
        logger.debug(f"Filtered {len(interfaces)} interfaces to {len(filtered)} with cables")
        return filtered

    def export_to_json(self, site_name: str, location_name: Optional[str] = None,
                       output_file: str = "export.json", 
                       export_type: str = "all",
                       device_type: Optional[str] = None,
                       tag: Optional[str] = None,
                       cabled_only: bool = False) -> str:
        """
        Export devices and interfaces from site/location to JSON.
        
        export_type: "all" (all interfaces), "cabled" (only with cables)
        device_type: filter by device type (optional)
        tag: filter by device tag (optional)
        cabled_only: only export interfaces with cables
        """
        msg = f"Exporting devices and interfaces from {site_name}"
        if location_name:
            msg += f" / {location_name}"
        msg += f" (type: {export_type}"
        if device_type:
            msg += f", device_type: {device_type}"
        if tag:
            msg += f", tag: {tag}"
        msg += ")"
        logger.info(msg)

        devices = self.get_devices_by_site_and_location(site_name, location_name)
        if not devices:
            logger.warning(f"No devices found at {site_name}" + (f" / {location_name}" if location_name else ""))
            return ""

        logger.info(f"Found {len(devices)} total devices")

        # Apply device filters
        if device_type:
            devices = self.filter_devices_by_type(devices, device_type)
        if tag:
            devices = self.filter_devices_by_tag(devices, tag)

        if not devices:
            logger.warning("No devices match the specified filters")
            return ""

        logger.info(f"Exporting {len(devices)} devices after filtering")

        # Build export structure
        export_data = {
            "source_site": site_name,
            "source_location": location_name,
            "export_type": export_type,
            "device_type_filter": device_type,
            "tag_filter": tag,
            "cabled_only": cabled_only,
            "export_date": datetime.now().isoformat(),
            "devices": [],
            "summary": {
                "total_devices": 0,
                "total_interfaces": 0,
                "cabled_interfaces": 0
            }
        }

        total_interface_count = 0
        total_cabled_count = 0

        for device in devices:
            device_data = {
                "id": device.get("id"),
                "name": device.get("name"),
                "site": device.get("site", {}).get("name"),
                "location": device.get("location", {}).get("name") if device.get("location") else None,
                "device_type": device.get("device_type", {}).get("display"),
                "status": device.get("status", {}).get("label") if isinstance(device.get("status"), dict) else device.get("status"),
                "tags": [t.get("name") for t in device.get("tags", [])],
                "interfaces": [],
                "interface_count": 0,
                "cabled_count": 0
            }

            # Get interfaces for this device
            interfaces = self.get_interfaces_for_device(device["id"])
            
            # Count cabled interfaces before filtering
            cabled_interfaces = [iface for iface in interfaces if iface.get("cable")]
            device_data["cabled_count"] = len(cabled_interfaces)
            total_cabled_count += len(cabled_interfaces)
            
            # Filter interfaces by cable status if requested
            if cabled_only or export_type == "cabled":
                interfaces = self.filter_interfaces_by_cable(interfaces)
            
            device_data["interface_count"] = len(interfaces)
            total_interface_count += len(interfaces)
            
            logger.info(f"  {device['name']}: {len(interfaces)} interfaces exported ({device_data['cabled_count']} cabled)")

            for iface in interfaces:
                interface_data = {
                    "id": iface.get("id"),
                    "name": iface.get("name"),
                    "type": iface.get("type", {}).get("value") if isinstance(iface.get("type"), dict) else iface.get("type"),
                    "enabled": iface.get("enabled"),
                    "mtu": iface.get("mtu"),
                    "description": iface.get("description"),
                    "mode": iface.get("mode", {}).get("value") if isinstance(iface.get("mode"), dict) else iface.get("mode"),
                    "untagged_vlan": iface.get("untagged_vlan", {}).get("name") if iface.get("untagged_vlan") else None,
                    "tagged_vlans": [v.get("name") for v in iface.get("tagged_vlans", [])] if iface.get("tagged_vlans") else [],
                    "has_cable": bool(iface.get("cable"))
                }
                device_data["interfaces"].append(interface_data)

            export_data["devices"].append(device_data)

        # Update summary
        export_data["summary"]["total_devices"] = len(devices)
        export_data["summary"]["total_interfaces"] = total_interface_count
        export_data["summary"]["cabled_interfaces"] = total_cabled_count

        # Write to JSON file
        try:
            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2)
            
            # Print summary to screen and log
            print("\n" + "=" * 70)
            print("EXPORT SUMMARY")
            print("=" * 70)
            print(f"File:                  {output_file}")
            print(f"Export Type:           {export_type}")
            if device_type:
                print(f"Device Type Filter:    {device_type}")
            if tag:
                print(f"Tag Filter:            {tag}")
            print(f"Total Devices:         {export_data['summary']['total_devices']}")
            print(f"Total Interfaces:      {export_data['summary']['total_interfaces']}")
            print(f"Cabled Interfaces:     {export_data['summary']['cabled_interfaces']}")
            print("=" * 70 + "\n")
            
            logger.info(f"✓ Exported to: {output_file}")
            logger.info(f"Export Summary: {export_data['summary']['total_devices']} devices, {export_data['summary']['total_interfaces']} interfaces ({export_data['summary']['cabled_interfaces']} cabled)")
            
            return output_file
        except Exception as e:
            logger.error(f"Error writing JSON: {e}")
            return ""

    def load_json(self, json_file: str) -> Dict:
        """Load JSON export file."""
        try:
            with open(json_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON: {e}")
            return {}

    def get_site_id(self, site_name: str) -> Optional[int]:
        """Get site ID by name or slug."""
        try:
            resp = self.session.get(
                f"{self.base_url}/api/dcim/sites/",
                params={"name": site_name}
            )
            resp.raise_for_status()
            results = resp.json()["results"]
            return results[0]["id"] if results else None
        except Exception as e:
            logger.error(f"Error looking up site: {e}")
            return None

    def get_location_id(self, site_name: str, location_name: str) -> Optional[int]:
        """Get location ID by name and site. Site name can be slug or display name."""
        try:
            # Try to get site ID - could be a slug or display name
            site_id = self.get_site_id(site_name)
            
            # If that didn't work, try looking up by slug directly
            if not site_id:
                try:
                    resp = self.session.get(
                        f"{self.base_url}/api/dcim/sites/",
                        params={"slug": site_name}
                    )
                    resp.raise_for_status()
                    results = resp.json()["results"]
                    site_id = results[0]["id"] if results else None
                except:
                    return None
            
            if not site_id:
                return None
            
            resp = self.session.get(
                f"{self.base_url}/api/dcim/locations/",
                params={"site_id": site_id, "name": location_name}
            )
            resp.raise_for_status()
            results = resp.json()["results"]
            logger.debug(f"Found location '{location_name}' at site ID {site_id}: {len(results)} results")
            return results[0]["id"] if results else None
        except Exception as e:
            logger.error(f"Error looking up location: {e}")
            return None

    def get_device_id(self, device_name: str, site_name: str) -> Optional[int]:
        """Get device ID by name and site. Site name can be slug or display name."""
        try:
            # Try to get site ID - could be a slug or display name
            site_id = self.get_site_id(site_name)
            
            # If that didn't work, try looking up by slug directly
            if not site_id:
                try:
                    resp = self.session.get(
                        f"{self.base_url}/api/dcim/sites/",
                        params={"slug": site_name}
                    )
                    resp.raise_for_status()
                    results = resp.json()["results"]
                    site_id = results[0]["id"] if results else None
                except:
                    return None
            
            if not site_id:
                return None
            
            resp = self.session.get(
                f"{self.base_url}/api/dcim/devices/",
                params={"name": device_name, "site_id": site_id}
            )
            resp.raise_for_status()
            results = resp.json()["results"]
            return results[0]["id"] if results else None
        except Exception as e:
            logger.error(f"Error looking up device: {e}")
            return None

    def import_from_json(self, json_file: str, target_site: str, 
                        target_location: Optional[str] = None, 
                        rename_devices: Optional[Dict[str, str]] = None,
                        only_connected: bool = False) -> Dict[str, int]:
        """
        Import devices and interfaces from JSON to target site/location.
        
        rename_devices: dict mapping old device names to new names
        only_connected: if True, only import interfaces that have cables attached
        """
        data = self.load_json(json_file)
        if not data:
            return {"total": 0, "created": 0, "failed": 0}

        msg = f"Importing to {target_site}"
        if target_location:
            msg += f" / {target_location}"
        if only_connected:
            msg += " (cabled interfaces only)"
        logger.info(msg)

        rename_devices = rename_devices or {}
        stats = {"total": 0, "created": 0, "failed": 0, "skipped": 0}

        # Get target location ID if specified
        target_location_id = None
        if target_location:
            target_location_id = self.get_location_id(target_site, target_location)
            if not target_location_id:
                logger.warning(f"Location not found: {target_location} @ {target_site}")
                response = input("Continue anyway? (yes/no): ").strip().lower()
                if response != "yes":
                    return stats

        for device_data in data.get("devices", []):
            source_device_name = device_data.get("name")
            target_device_name = rename_devices.get(source_device_name, source_device_name)

            # Check if device exists at target
            device_id = self.get_device_id(target_device_name, target_site)
            if not device_id:
                logger.error(f"[FAIL] Device not found: {target_device_name} @ {target_site}")
                stats["failed"] += 1
                continue

            # Create interfaces
            for interface_data in device_data.get("interfaces", []):
                # Filter interfaces with cables if requested
                if only_connected:
                    has_cable = interface_data.get("has_cable", False)
                    if not has_cable:
                        logger.info(f"Skipping interface {interface_data.get('name')} on {target_device_name} (no cable attached)")
                        stats["skipped"] += 1
                        continue

                interface_payload = {
                    "device": device_id,
                    "name": interface_data.get("name"),
                    "type": interface_data.get("type"),
                    "enabled": interface_data.get("enabled", True),
                }

                if interface_data.get("mtu"):
                    interface_payload["mtu"] = interface_data["mtu"]
                if interface_data.get("description"):
                    interface_payload["description"] = interface_data["description"]
                if interface_data.get("mode"):
                    interface_payload["mode"] = interface_data["mode"]

                # Handle VLANs
                if interface_data.get("untagged_vlan"):
                    vlan_name = interface_data["untagged_vlan"]
                    try:
                        vlan_resp = self.session.get(
                            f"{self.base_url}/api/ipam/vlans/",
                            params={"name": vlan_name}
                        )
                        vlan_results = vlan_resp.json()["results"]
                        if vlan_results:
                            interface_payload["untagged_vlan"] = vlan_results[0]["id"]
                    except:
                        logger.warning(f"VLAN not found: {vlan_name}")

                if interface_data.get("tagged_vlans"):
                    vlan_ids = []
                    for vlan_name in interface_data["tagged_vlans"]:
                        try:
                            vlan_resp = self.session.get(
                                f"{self.base_url}/api/ipam/vlans/",
                                params={"name": vlan_name}
                            )
                            vlan_results = vlan_resp.json()["results"]
                            if vlan_results:
                                vlan_ids.append(vlan_results[0]["id"])
                        except:
                            pass
                    if vlan_ids:
                        interface_payload["tagged_vlans"] = vlan_ids

                # Check if interface exists
                try:
                    check_resp = self.session.get(
                        f"{self.base_url}/api/dcim/interfaces/",
                        params={"device_id": device_id, "name": interface_data.get("name")}
                    )
                    if check_resp.json()["results"]:
                        logger.info(f"[SKIP] Skipped (exists): {interface_data.get('name')} on {target_device_name}")
                        stats["skipped"] += 1
                        continue
                except:
                    pass

                # Create interface
                try:
                    resp = self.session.post(
                        f"{self.base_url}/api/dcim/interfaces/",
                        json=interface_payload
                    )
                    resp.raise_for_status()
                    logger.info(f"[OK] Created {interface_data.get('name')} on {target_device_name}")
                    stats["created"] += 1
                except Exception as e:
                    logger.error(f"[FAIL] Failed to create {interface_data.get('name')} on {target_device_name}: {e}")
                    stats["failed"] += 1

            stats["total"] += len(device_data.get("interfaces", []))

        return stats


def main():
    """Main entry point."""
    
    # Configuration
    NETBOX_URL = "https://nbupg.homelan.local"
    API_TOKEN = "nbt_SA3YmWPeJzAv.<YOUR_TOKEN>"
    VERIFY_SSL = False

    # Parse arguments
    if len(sys.argv) < 2:
        print("""
NetBox Device & Interface JSON Migration Tool with Advanced Filtering

USAGE:
  python3 script.py <command> [args]

COMMANDS:

  export <site> [location] [output_file] [options]
    Export all devices and interfaces from site/location to JSON
    
    Options:
      --all              Export all interfaces (default)
      --cabled           Export only interfaces with cables attached
      --device-type NAME Filter by device type
      --tag NAME         Filter by device tag
    
    Examples:
      python3 script.py export "Site-A"
      python3 script.py export "Site-A" "Building-A" export.json --cabled
      python3 script.py export "Site-A" "" export.json --device-type "Switch"
      python3 script.py export "Site-A" "" export.json --tag "production"

  import <json_file> <target_site> [target_location] [--connected]
    Import devices and interfaces from JSON to target site/location
    
    --connected: Only import interfaces that have cables attached
    
    Examples:
      python3 script.py import export.json "Site-B"
      python3 script.py import export.json "Site-B" "Building-B"
      python3 script.py import export.json "Site-B" "Building-B" --connected

  help
    Show this help message
        """)
        sys.exit(0)

    command = sys.argv[1].lower()

    # Initialize migrator
    migrator = NetBoxJSONMigrator(NETBOX_URL, API_TOKEN, VERIFY_SSL)

    # Test connection
    logger.info("Testing NetBox connection...")
    if not migrator.test_connection():
        logger.error("Cannot connect to NetBox")
        sys.exit(1)

    # Export command
    if command == "export":
        if len(sys.argv) < 3:
            print("Usage: python3 script.py export <site> [location] [output_file] [options]")
            sys.exit(1)

        site = sys.argv[2]
        location = None
        output_file = f"export_{site}.json"
        export_type = "all"
        device_type = None
        tag = None
        cabled_only = False
        
        # Parse remaining arguments
        remaining_args = sys.argv[3:]
        i = 0
        while i < len(remaining_args):
            arg = remaining_args[i]
            if arg == "--all":
                export_type = "all"
            elif arg == "--cabled":
                export_type = "cabled"
                cabled_only = True
            elif arg == "--device-type" and i + 1 < len(remaining_args):
                device_type = remaining_args[i + 1]
                i += 1
            elif arg == "--tag" and i + 1 < len(remaining_args):
                tag = remaining_args[i + 1]
                i += 1
            elif not arg.startswith("--"):
                if location is None:
                    location = arg
                elif output_file == f"export_{site}.json":
                    output_file = arg
            i += 1

        migrator.export_to_json(site, location, output_file, export_type, device_type, tag, cabled_only)

    # Import command
    elif command == "import":
        if len(sys.argv) < 4:
            print("Usage: python3 script.py import <json_file> <target_site> [target_location] [--connected]")
            sys.exit(1)

        json_file = sys.argv[2]
        target_site = sys.argv[3]
        target_location = None
        only_connected = False
        
        # Parse remaining arguments
        for arg in sys.argv[4:]:
            if arg == "--connected":
                only_connected = True
            else:
                target_location = arg

        response = input(f"Import from {json_file} to {target_site}? (yes/no): ").strip().lower()
        if response != "yes":
            print("Aborted")
            sys.exit(0)

        stats = migrator.import_from_json(json_file, target_site, target_location, only_connected=only_connected)

        print("\n" + "=" * 70)
        print("IMPORT SUMMARY")
        print("=" * 70)
        print(f"Total:    {stats['total']}")
        print(f"Created:  {stats['created']} [OK]")
        print(f"Skipped:  {stats['skipped']} [SKIP]")
        print(f"Failed:   {stats['failed']} [FAIL]")
        print("=" * 70)

    elif command == "help":
        print("See usage above")
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        print("Run: python3 script.py help")
        sys.exit(1)


if __name__ == "__main__":
    main()