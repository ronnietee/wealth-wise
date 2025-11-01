#!/usr/bin/env python3
"""
Script to process subscription renewals via cron job.
This script authenticates with admin credentials and calls the renewal endpoint.

Usage:
    python scripts/process_renewals.py

Environment Variables Required:
    ADMIN_USERNAME - Admin username
    ADMIN_PASSWORD - Admin password
    APP_URL - Base URL of the application (default: http://localhost:5000)
"""

import os
import sys
import requests
from datetime import datetime

# Add parent directory to path to import app config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_admin_token(username, password, app_url):
    """Get admin JWT token by authenticating with admin credentials."""
    try:
        response = requests.post(
            f"{app_url}/admin/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            print(f"ERROR: Failed to authenticate. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to application: {e}")
        return None

def process_renewals(token, app_url):
    """Call the renewal processing endpoint."""
    try:
        response = requests.post(
            f"{app_url}/api/subscriptions/renewal/process",
            headers={"Authorization": f"Bearer {token}"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: {data.get('message', 'Renewals processed')}")
            print(f"Renewed: {data.get('renewed', 0)} subscriptions")
            failed = data.get('failed', [])
            if failed:
                print(f"Failed: {len(failed)} subscriptions")
                for failure in failed:
                    print(f"  - Subscription {failure.get('subscription_id')}: {failure.get('error')}")
            return True
        else:
            print(f"ERROR: Renewal processing failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to process renewals: {e}")
        return False

def main():
    """Main function to process renewals."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting renewal processing...")
    
    # Get configuration from environment
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    app_url = os.getenv('APP_URL', 'http://localhost:5000').rstrip('/')
    
    # Validate required environment variables
    if not admin_username:
        print("ERROR: ADMIN_USERNAME environment variable not set")
        sys.exit(1)
    
    if not admin_password:
        print("ERROR: ADMIN_PASSWORD environment variable not set")
        sys.exit(1)
    
    # Get admin token
    print("Authenticating with admin credentials...")
    token = get_admin_token(admin_username, admin_password, app_url)
    
    if not token:
        print("ERROR: Failed to obtain admin token")
        sys.exit(1)
    
    print("Admin token obtained successfully")
    
    # Process renewals
    print("Processing subscription renewals...")
    success = process_renewals(token, app_url)
    
    if success:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Renewal processing completed successfully")
        sys.exit(0)
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Renewal processing failed")
        sys.exit(1)

if __name__ == '__main__':
    main()

