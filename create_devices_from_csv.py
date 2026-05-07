#!/usr/bin/env python3
"""
Create NetBox devices from CSV export - as unracked at target site
"""

import csv
import requests
import sys
import argparse

# Configuration
NETBOX_URL = "https://nbupg.homelan.local"
API_TOKEN = "nbt_SA3YmWPeJzAv.YOUR_TOKEN_HERE"  # Update this
VERIFY_SSL = False

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
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
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
            except Exception as e:
                print(f"❌ {device_name}: {str(e)[:80]}")
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
    parser.add_argument("csv_file", help="CSV file with devices")
    parser.add_argument("target_site", help="Target NetBox site")
    
    args = parser.parse_args()
    
    create_devices(args.csv_file, args.target_site)