#!/usr/bin/env python3
"""
List all device types in NetBox
"""

import requests
import os
import json

NETBOX_URL = "https://nbupg.homelan.local"
VERIFY_SSL = False

def get_api_token():
    token = os.getenv("NETBOX_TOKEN")
    if token:
        return token
    
    token = input("API token: ").strip()
    if not token:
        exit(1)
    return token

api_token = get_api_token()

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

session = requests.Session()
session.headers.update(headers)
session.verify = VERIFY_SSL

print("Getting device types...")
resp = session.get(
    f"{NETBOX_URL}/api/dcim/device-types/",
    params={"limit": 1000}
)

types = resp.json()["results"]

print(f"\n{'Manufacturer':<20} {'Model':<30} {'ID':<8}")
print("-" * 60)

for dt in types[:20]:  # First 20
    mfg = dt.get('manufacturer', {}).get('name', 'N/A')
    model = dt.get('model', 'N/A')
    print(f"{mfg:<20} {model:<30} {dt['id']:<8}")

print(f"\n... and {len(types) - 20} more")
print(f"Total: {len(types)} device types")