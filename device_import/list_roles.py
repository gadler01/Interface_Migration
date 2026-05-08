#!/usr/bin/env python3
"""
List all device roles in NetBox
"""

import requests
import os

NETBOX_URL = "https://nbupg.homelan.local"
VERIFY_SSL = False

def get_api_token():
    """Get API token from user"""
    token = os.getenv("NETBOX_TOKEN")
    if token:
        return token
    
    print("NetBox API Token required")
    token = input("Enter your NetBox API token (nbt_...): ").strip()
    
    if not token:
        print("❌ Token required")
        exit(1)
    
    return token

def list_roles():
    """List all roles"""
    
    api_token = get_api_token()
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    session.verify = VERIFY_SSL
    
    try:
        resp = session.get(
            f"{NETBOX_URL}/api/dcim/device-roles/",
            params={"limit": 1000}
        )
        resp.raise_for_status()
        roles = resp.json()["results"]
        
        print("")
        print("=" * 70)
        print("NetBox Device Roles")
        print("=" * 70)
        print(f"{'Name':<30} {'ID':<10} {'Color':<10}")
        print("-" * 70)
        
        for role in roles:
            print(f"{role['name']:<30} {role['id']:<10} {role.get('color', 'N/A'):<10}")
        
        print("=" * 70)
        print(f"Total: {len(roles)} roles")
        print("")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_roles()
