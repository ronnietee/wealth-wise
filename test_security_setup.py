"""
Test script to verify security setup is working correctly.
Run this before starting the Flask application.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    success = True
    
    try:
        from flask_talisman import Talisman
        print("✅ Flask-Talisman imported successfully")
    except ImportError as e:
        print(f"❌ Flask-Talisman import error: {e}")
        print("   Run: pip install Flask-Talisman")
        success = False
    
    # Flask-WTF may have import issues with Werkzeug 3.x but works at runtime
    try:
        from flask_wtf.csrf import CSRFProtect, generate_csrf
        print("✅ Flask-WTF imported successfully")
    except (ImportError, AttributeError) as e:
        print(f"⚠️  Flask-WTF import warning: {e}")
        print("   This is a known compatibility issue with Werkzeug 3.x")
        print("   Flask-WTF will be tested during app initialization")
        # Don't fail - test at runtime instead
    
    # Flask-Limiter has compatibility issues with newer Werkzeug versions
    # But it may still work at runtime. Test it separately and don't fail if it has import issues
    try:
        from flask_limiter import Limiter
        print("✅ Flask-Limiter imported successfully")
    except (ImportError, AttributeError) as e:
        print(f"⚠️  Flask-Limiter import warning: {e}")
        print("   This is a known compatibility issue with Werkzeug 3.x")
        print("   The app may still work - rate limiting will be tested during app initialization")
        # Don't fail the test, just warn
    
    return success

def test_secret_keys():
    """Test that secret keys are set (or using dev defaults)."""
    print("\nTesting secret keys...")
    secret_key = os.environ.get('SECRET_KEY')
    jwt_secret = os.environ.get('JWT_SECRET_KEY')
    
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    if flask_env == 'production':
        if not secret_key or secret_key == 'your-secret-key-change-in-production':
            print("❌ SECRET_KEY must be set in production!")
            return False
        if not jwt_secret or jwt_secret == 'your-jwt-secret-key-change-in-production':
            print("❌ JWT_SECRET_KEY must be set in production!")
            return False
        print("✅ Production secret keys are set")
    else:
        if not secret_key or secret_key == 'your-secret-key-change-in-production':
            print("⚠️  SECRET_KEY not set, using development default")
        else:
            print("✅ SECRET_KEY is set")
        
        if not jwt_secret or jwt_secret == 'your-jwt-secret-key-change-in-production':
            print("⚠️  JWT_SECRET_KEY not set, using development default")
        else:
            print("✅ JWT_SECRET_KEY is set")
    
    return True

def test_app_initialization():
    """Test that the Flask app can be created with security features."""
    print("\nTesting app initialization...")
    try:
        from src import create_app
        
        # Try to create app
        app = create_app(os.environ.get('FLASK_ENV', 'default'))
        
        # Check that security extensions are initialized
        from src.extensions import csrf, limiter
        
        if csrf:
            print("✅ CSRF protection initialized")
        else:
            print("❌ CSRF protection not initialized")
            return False
        
        if limiter:
            print("✅ Rate limiter initialized")
        else:
            print("❌ Rate limiter not initialized")
            return False
        
        # Check config
        if app.config.get('WTF_CSRF_ENABLED'):
            print("✅ CSRF protection enabled in config")
        else:
            print("⚠️  CSRF protection not enabled in config")
        
        if app.config.get('SESSION_COOKIE_HTTPONLY'):
            print("✅ Session cookie HttpOnly enabled")
        else:
            print("⚠️  Session cookie HttpOnly not enabled")
        
        if app.config.get('SESSION_COOKIE_SAMESITE'):
            print(f"✅ Session cookie SameSite: {app.config.get('SESSION_COOKIE_SAMESITE')}")
        else:
            print("⚠️  Session cookie SameSite not set")
        
        print("✅ App initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ App initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csrf_token_generation():
    """Test that CSRF tokens can be generated."""
    print("\nTesting CSRF token generation...")
    try:
        from src import create_app
        from flask_wtf.csrf import generate_csrf
        from flask import request
        
        app = create_app(os.environ.get('FLASK_ENV', 'default'))
        
        # Need a test request context for CSRF token generation
        with app.test_request_context('/'):
            token = generate_csrf()
            if token and len(token) > 0:
                print(f"✅ CSRF token generated: {token[:20]}...")
                return True
            else:
                print("❌ CSRF token generation failed")
                return False
    except Exception as e:
        print(f"❌ CSRF token generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Security Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Secret Keys", test_secret_keys()))
    results.append(("App Initialization", test_app_initialization()))
    results.append(("CSRF Token Generation", test_csrf_token_generation()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ All tests passed! Security setup is correct.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

