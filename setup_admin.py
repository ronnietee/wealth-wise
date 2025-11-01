"""
Helper script to set up admin credentials in .env file.
Run this script to add admin credentials to your .env file.
"""

import os
from pathlib import Path

def setup_admin_credentials():
    """Add admin credentials to .env file."""
    env_path = Path('.env')
    
    # Check if .env exists
    if not env_path.exists():
        print("⚠️  .env file not found. Creating from env.example...")
        example_path = Path('env.example')
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
        else:
            # Create basic .env
            with open(env_path, 'w') as f:
                f.write("# STEWARD Environment Variables\n")
            print("✅ Created new .env file")
    
    # Read current .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Check if admin credentials already exist
    if 'ADMIN_USERNAME' in content or 'ADMIN_PASSWORD' in content:
        print("ℹ️  Admin credentials already exist in .env file.")
        response = input("Do you want to update them? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping admin credential setup.")
            return
        
        # Remove existing admin credentials
        lines = content.split('\n')
        new_lines = []
        skip_next = False
        for line in lines:
            if line.strip().startswith('# Admin Portal Credentials'):
                skip_next = True
                continue
            if skip_next and (line.strip().startswith('ADMIN_USERNAME') or line.strip().startswith('ADMIN_PASSWORD')):
                continue
            if skip_next and line.strip() == '':
                skip_next = False
            new_lines.append(line)
        content = '\n'.join(new_lines)
    
    # Get admin credentials from user
    print("\n🔐 Admin Portal Credential Setup")
    print("=" * 50)
    username = input("Enter admin username [default: admin]: ").strip() or 'admin'
    
    password = input("Enter admin password (required): ").strip()
    if not password:
        print("❌ Password is required!")
        return
    
    # Confirm password
    password_confirm = input("Confirm admin password: ").strip()
    if password != password_confirm:
        print("❌ Passwords do not match!")
        return
    
    # Add admin credentials to .env
    admin_section = f"""
# Admin Portal Credentials (REQUIRED for admin access)
# Set these to secure your admin portal. DO NOT use defaults in production.
ADMIN_USERNAME={username}
ADMIN_PASSWORD={password}
"""
    
    # Append to .env
    with open(env_path, 'a') as f:
        f.write(admin_section)
    
    print("\n✅ Admin credentials added to .env file!")
    print(f"\n📝 Summary:")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    print(f"\n🔗 Access admin portal at: http://localhost:5000/admin")
    print("\n⚠️  IMPORTANT: Never commit .env file to version control!")

if __name__ == '__main__':
    try:
        setup_admin_credentials()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

