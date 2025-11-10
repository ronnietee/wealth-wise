#!/usr/bin/env python
"""
Script to generate a hashed password for the admin portal.

Usage:
    python generate_admin_password.py
    python generate_admin_password.py "your-password-here"
"""

import sys
from werkzeug.security import generate_password_hash
import getpass

def main():
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        print("Admin Password Hash Generator")
        print("=" * 40)
        password = getpass.getpass("Enter admin password: ")
        password_confirm = getpass.getpass("Confirm admin password: ")
        
        if password != password_confirm:
            print("\n❌ Passwords do not match!")
            sys.exit(1)
    
    if not password:
        print("\n❌ Password cannot be empty!")
        sys.exit(1)
    
    # Generate the hash
    password_hash = generate_password_hash(password)
    
    print("\n✅ Password hash generated successfully!")
    print("\n" + "=" * 40)
    print("Add this to your .env file:")
    print("=" * 40)
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print("=" * 40)
    print("\nAlso set your admin username (if different from default):")
    print("ADMIN_USERNAME=admin")
    print("\n⚠️  Keep this hash secure and never commit it to version control!")

if __name__ == '__main__':
    main()

