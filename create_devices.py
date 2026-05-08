#!/usr/bin/env python3
"""
Create NetBox devices - interactive version
"""

import csv
import requests
import os
import json

NETBOX_URL = "https://nbupg.homelan.local"
VERIFY_SSL = False

def get_api_token():
    token = os.getenv("NETBOX_TOKEN")
    if token:
        return token
    token = input("API token (nbt_...): ").strip()
    if not token:
        exit(1)
    return token

def get_site_id(session, site_name):
    resp = session.get(f"{NETBOX_URL}/api/dcim/sites/", params={"name": site_name})
    results = resp.json()["results"]
    return results[0]["id"] if results else None

def get_device_type_id(session, device_type_name):
    resp = session.get(
        f"{NETBOX_URL}/api/dcim/device-types/",
        params={"model": device_type_name, "limit": 1}
    )
    results = resp.json()["results"]
    return results[0]["id"] if results else None

def get_role_id(session, role_name, all_roles):
    role_lower = role_name.lower().strip()
    for role in all_roles:
        if role['name'].lower() == role_lower:
            return role['id']
    return None

# Header
print("=" * 60)
print("NetBox Device Creator")
print("=" * 60)
print("")

# Get API token
api_token = get_api_token()

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

session = requests.Session()
session.headers.update(headers)
session.verify = VERIFY_SSL

# Get CSV file
print("\nAvailable CSV files:")
csv_files = [f for f in os.listdir(".") if f.endswith(".csv")]

if csv_files:
    for i, f in enumerate(csv_files, 1):
        print(f"  {i}. {f}")
    print("")
    choice = input("Select CSV (number or filename): ").strip()
    try:
        idx = int(choice) - 1
        csv_file = csv_files[idx] if 0 <= idx < len(csv_files) else choice
    except ValueError:
        csv_file = choice
else:
    csv_file = input("CSV filename: ").strip()

if not os.path.exists(csv_file):
    print(f"❌ File not found: {csv_file}")
    exit(1)

print(f"✅ Selected: {csv_file}")

# Get target site
print("\nEnter target NetBox site name:")
target_site = input("Site: ").strip()

if not target_site:
    print("❌ Site name required")
    exit(1)

# Get site ID
print(f"\nGetting site '{target_site}'...")
site_id = get_site_id(session, target_site)
if not site_id:
    print(f"❌ Site not found: {target_site}")
    exit(1)
print(f"✅ Site ID: {site_id}")

# Get roles
print("Getting roles...")
resp = session.get(f"{NETBOX_URL}/api/dcim/device-roles/", params={"limit": 1000})
all_roles = resp.json()["results"]
print(f"✅ Found {len(all_roles)} roles")

# Confirm
print("")
print(f"CSV File: {csv_file}")
print(f"Target Site: {target_site}")
print("")
confirm = input("Proceed? (yes/no): ").strip().lower()
if confirm != "yes":
    print("Aborted")
    exit(0)

print(f"\nReading: {csv_file}")
print("")

created = 0
failed = 0
skipped = 0

with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get('Name', '').strip()
        type_name = row.get('Type', '').strip()
        role_name = row.get('Role', '').strip()
        
        if not name:
            continue
        
        # Check if exists
        try:
            resp = session.get(
                f"{NETBOX_URL}/api/dcim/devices/",
                params={"name": name, "site_id": site_id}
            )
            if resp.json()["results"]:
                print(f"⊘ {name}: Exists")
                skipped += 1
                continue
        except:
            pass
        
        # Get device type ID
        type_id = get_device_type_id(session, type_name) if type_name else None
        if not type_id:
            print(f"❌ {name}: Type '{type_name}' not found")
            failed += 1
            continue
        
        # Get role ID
        role_id = get_role_id(session, role_name, all_roles) if role_name else None
        if not role_id:
            print(f"❌ {name}: Role '{role_name}' not found")
            failed += 1
            continue
        
        # Create device
        payload = {
            "name": name,
            "site": site_id,
            "device_type": type_id,
            "role": role_id,
        }
        
        try:
            resp = session.post(
                f"{NETBOX_URL}/api/dcim/devices/",
                json=payload
            )
            resp.raise_for_status()
            print(f"✅ {name}")
            created += 1
        except Exception as e:
            try:
                print(f"❌ {name}: {resp.json()}")
            except:
                print(f"❌ {name}: {e}")
            failed += 1

print("")
print("=" * 60)
print(f"Created: {created}")
print(f"Failed:  {failed}")
print(f"Skipped: {skipped}")
print("=" * 60)
