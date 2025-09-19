#!/usr/bin/env python3
"""
Simple test script to verify Firebase integration.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.services.firebase_service import firebase_admin_service
from app.core.config import settings

def test_firebase_config():
    """Test Firebase configuration."""
    print("=== Firebase Configuration Test ===")
    
    # Check if Firebase environment variables are set
    firebase_vars = [
        'FIREBASE_PROJECT_ID',
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL'
    ]
    
    print("Checking Firebase environment variables:")
    for var in firebase_vars:
        value = getattr(settings, var, None)
        if value:
            # Mask sensitive data
            if 'KEY' in var:
                masked_value = value[:20] + "..." if len(value) > 20 else "***"
                print(f"  ✓ {var}: {masked_value}")
            else:
                print(f"  ✓ {var}: {value}")
        else:
            print(f"  ✗ {var}: Not set")
    
    print()

def test_firebase_initialization():
    """Test Firebase Admin SDK initialization."""
    print("=== Firebase Initialization Test ===")
    
    try:
        initialized = firebase_admin_service.initialize()
        if initialized:
            print("  ✓ Firebase Admin SDK initialized successfully")
            return True
        else:
            print("  ✗ Firebase Admin SDK initialization failed (credentials not configured)")
            return False
    except Exception as e:
        print(f"  ✗ Firebase Admin SDK initialization error: {e}")
        return False

async def test_firebase_operations():
    """Test basic Firebase operations."""
    print("=== Firebase Operations Test ===")
    
    # Test with a dummy token (this will fail but shows the service is working)
    try:
        result = await firebase_admin_service.verify_id_token("dummy_token")
        print(f"  Token verification test: {result}")
    except Exception as e:
        print(f"  Token verification test (expected to fail): {type(e).__name__}")
    
    # Test user retrieval with dummy UID
    try:
        result = await firebase_admin_service.get_user("dummy_uid")
        print(f"  User retrieval test: {result}")
    except Exception as e:
        print(f"  User retrieval test (expected to fail): {type(e).__name__}")

def main():
    """Main test function."""
    print("Firebase Integration Test")
    print("=" * 50)
    
    # Test configuration
    test_firebase_config()
    
    # Test initialization
    initialized = test_firebase_initialization()
    
    if initialized:
        print("\n✓ Firebase integration is properly configured and ready!")
        print("\nTo use Firebase in production:")
        print("1. Set up your Firebase project")
        print("2. Download the service account key JSON")
        print("3. Set the environment variables in .env file")
        print("4. Update the frontend Firebase config with your project details")
    else:
        print("\n⚠ Firebase integration needs configuration:")
        print("1. Create a Firebase project at https://console.firebase.google.com")
        print("2. Generate a service account key")
        print("3. Set the Firebase environment variables")
        print("4. See .env.example for required variables")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()