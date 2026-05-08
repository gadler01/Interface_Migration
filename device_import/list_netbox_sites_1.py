#!/usr/bin/env python3
"""
Create NetBox devices from CSV export - as unracked at target site

CSV FORMAT REQUIRED:
Required columns:
  - Name: Device name (required)
  - Site: Source site name (ignored, uses target site)
  - Status: Active/Offline/Planned
  - Manufacturer: Device manufacturer
  - Type: Device type/model
  - Role: Device role (Server/Switch/Router/etc)

Optional columns:
  - Serial number
  - Any other columns (ignored)

USAGE:
  python3 create_devices_from_csv.py
  (will prompt for CSV file and target site)

  OR with arguments:
  python3 create_devices_from_csv.py OKC_Devices.csv "vsol-test"
"""

import csv
import requests
import sys
import argparse
import os

# Configuration
NETBOX_URL = "https://nbupg.homelan.local"
API_TOKEN = None  # Will be prompted or from env var
VERIFY_SSL = False

def get_api_token():
    """Get API token from user or environment"""
    import os
    
    # Check environment variable first
    token = os.getenv("NETBOX_TOKEN")
    if token:
        return token
    
    # Prompt user
    print("NetBox API Token required")
    print("Get token from: https://nbupg.homelan.local/user/api-tokens/")
    print("")
    token = input("Enter your NetBox API token (nbt_...): ").strip()
    
    if not token:
        print("❌ Token required")
        sys.exit(1)
    
    return token

def get_site_id(session, site_name):
    """Get site ID by name"""
    try:
        resp = session.get(
            f"{NETBOX_URL}/api/dcim/sites/",
            params={"name": site_name}
        )
        resp.raise_for_status()
        results = resp.json()["results"]
        if results:
            return results[0]["id"]
        else:
            print(f"❌ Site not found: {site_name}")
            return None
    except Exception as e:
        print(f"❌ Error getting site: {e}")
        return None

def get_device_type_id(session, manufacturer, type_name):
    """Get device type ID"""
    try:
        resp = session.get(
            f"{NETBOX_URL}/api/dcim/device-types/",
            params={"manufacturer": manufacturer, "model": type_name}
        )
        resp.raise_for_status()
        results = resp.json()["results"]
        if results:
            return results[0]["id"]
        return None
    except:
        return None

def get_device_role_id(session, role_name):
    """Get device role ID"""
    try:
        resp = session.get(
            f"{NETBOX_URL}/api/dcim/device-roles/",
            params={"name": role_name}
        )
        resp.raise_for_status()
        results = resp.json()["results"]
        if results:
            return results[0]["id"]
        return None
    except:
        return None

def create_devices(csv_file, target_site):
    """Create devices from CSV"""
    
    # Get API token
    api_token = get_api_token()
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    session.verify = VERIFY_SSL
    
    # Get target site ID
    site_id = get_site_id(session, target_site)
    if not site_id:
        print(f"❌ Cannot proceed without site ID")
        sys.exit(1)
    
    print(f"✅ Target site ID: {site_id}")
    print("")
    
    # Read CSV
    created = 0
    failed = 0
    skipped = 0
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            device_name = row.get('Name', '').strip()
            manufacturer = row.get('Manufacturer', '').strip()
            device_type = row.get('Type', '').strip()
            role = row.get('Role', '').strip()
            status = row.get('Status', 'Active').strip().lower()
            
            if not device_name:
                continue
            
            # Check if device already exists
            try:
                check_resp = session.get(
                    f"{NETBOX_URL}/api/dcim/devices/",
                    params={"name": device_name, "site_id": site_id}
                )
                if check_resp.json()["results"]:
                    print(f"⊘ {device_name}: Already exists")
                    skipped += 1
                    continue
            except:
                pass
            
            # Build payload - UNRACKED (no rack)
            payload = {
                "name": device_name,
                "site": site_id,
                "status": status,
            }
            
            # Add device type if found
            if device_type and manufacturer:
                type_id = get_device_type_id(session, manufacturer, device_type)
                if type_id:
                    payload["device_type"] = type_id
            
            # Add role if found
            if role:
                role_id = get_device_role_id(session, role)
                if role_id:
                    payload["device_role"] = role_id
            
            # Create device
            try:
                resp = session.post(
                    f"{NETBOX_URL}/api/dcim/devices/",
                    json=payload
                )
                resp.raise_for_status()
                print(f"✅ {device_name}: Created")
                created += 1
            except requests.exceptions.HTTPError as e:
                # Show full error response
                try:
                    error_detail = resp.json()
                    print(f"❌ {device_name}: {error_detail}")
                except:
                    print(f"❌ {device_name}: {e}")
                failed += 1
            except Exception as e:
                print(f"❌ {device_name}: {str(e)}")
                failed += 1
    
    print("")
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create NetBox devices from CSV (unracked at target site)"
    )
    parser.add_argument("csv_file", nargs="?", help="CSV file with devices")
    parser.add_argument("target_site", nargs="?", help="Target NetBox site")
    
    args = parser.parse_args()
    
    # Interactive mode if no arguments
    if not args.csv_file:
        print("=" * 60)
        print("NetBox Device Creator - Interactive Mode")
        print("=" * 60)
        print("")
        
        # List CSV files in current directory
        csv_files = [f for f in os.listdir(".") if f.endswith(".csv")]
        
        if csv_files:
            print("Available CSV files:")
            for i, f in enumerate(csv_files, 1):
                print(f"  {i}. {f}")
            print("")
            
            choice = input("Select CSV file (enter number or filename): ").strip()
            
            # Handle numeric choice
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(csv_files):
                    csv_file = csv_files[idx]
                else:
                    csv_file = choice
            except ValueError:
                csv_file = choice
        else:
            csv_file = input("Enter CSV filename: ").strip()
        
        # Check if file exists
        if not os.path.exists(csv_file):
            print(f"❌ File not found: {csv_file}")
            sys.exit(1)
        
        print(f"✅ Selected: {csv_file}")
        print("")
        
        # Get target site
        target_site = input("Enter target NetBox site name (e.g., vsol-test): ").strip()
        
        if not target_site:
            print("❌ Site name required")
            sys.exit(1)
        
        print("")
    else:
        csv_file = args.csv_file
        target_site = args.target_site
    
    # Verify CSV exists
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)
    
    # Show what we're about to do
    print(f"CSV File: {csv_file}")
    print(f"Target Site: {target_site}")
    print("")
    
    confirm = input("Proceed? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Aborted")
        sys.exit(0)
    
    print("")
    create_devices(csv_file, target_site)