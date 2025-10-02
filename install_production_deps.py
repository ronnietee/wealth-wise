#!/usr/bin/env python3
"""
Install production dependencies for STEWARD
Run this script to install Flask-WTF for CSRF protection
"""

import subprocess
import sys
import os

def install_requirements():
    """Install requirements from requirements.txt"""
    try:
        print("Installing production dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 STEWARD Production Setup")
    print("=" * 40)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    # Install dependencies
    if install_requirements():
        print("\n✅ Production setup complete!")
        print("\n📋 Next steps:")
        print("1. Run: python app.py")
        print("2. Test the login functionality")
        print("3. Deploy to your production server")
        print("\n🔒 Security features added:")
        print("- CSRF protection enabled")
        print("- Session management for Remember Me")
        print("- Secure login/logout endpoints")
        return True
    else:
        print("❌ Setup failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

