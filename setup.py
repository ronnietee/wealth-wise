#!/usr/bin/env python3
"""
Setup script for Wealth Wise
"""

import os
import sys
import subprocess

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False
    return True

def create_database():
    """Create PostgreSQL database"""
    print("\nDatabase setup:")
    print("Please ensure PostgreSQL is installed and running.")
    print("Create a database named 'wealthwise' and update the DATABASE_URL in config.py")
    print("Example: postgresql://username:password@localhost/wealthwise")
    
    # Check if we can connect to the database
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        print("Please check your database connection and try again.")
        return False
    return True

def main():
    """Main setup function"""
    print("Wealth Wise Setup")
    print("================")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create database
    if not create_database():
        print("\nSetup incomplete. Please fix the database connection and run again.")
        sys.exit(1)
    
    print("\n✓ Setup completed successfully!")
    print("\nTo run the application:")
    print("  python app.py")
    print("\nThen open your browser to: http://localhost:5000")

if __name__ == "__main__":
    main()
