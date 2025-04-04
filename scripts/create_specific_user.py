#!/usr/bin/env python3
"""
Script to create a specific user in Zep Cloud with the ID "16263830569_aprilx"
This will attempt to create the user directly in the Zep Cloud API without fallback mode
"""

import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv

# Try loading from both .env and .env.new
env_path = Path('.env.new')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment from .env.new")
else:
    load_dotenv()  # Fallback to default .env
    print(f"Loaded environment from .env")

# Import the Zep Cloud client
try:
    from zep_cloud_client import ZepCloudClient
    print("Successfully imported ZepCloudClient")
except ImportError:
    print("Failed to import ZepCloudClient. Make sure zep_cloud_client.py is in the current directory.")
    sys.exit(1)

# The specific user ID we want to create
USER_ID = "16263830569_aprilx"

def main():
    print(f"\n=== Creating specific user in Zep Cloud: {USER_ID} ===\n")
    
    # Create client
    try:
        client = ZepCloudClient()
        print(f"Successfully initialized ZepCloudClient")
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        sys.exit(1)
    
    # Create user with metadata
    metadata = {
        "created_at": time.time(),
        "description": "Test user created for production use",
        "source": "direct_api_call",
        "organization": "zep_cloud_test"
    }
    
    print(f"Attempting to create user {USER_ID} with metadata:")
    print(json.dumps(metadata, indent=2))
    
    # Try to create the user
    try:
        user = client.create_user(USER_ID, metadata)
        
        if user:
            print(f"\n✅ SUCCESS: Created user: {user['user_id']}")
            print(f"Metadata: {json.dumps(user['metadata'], indent=2)}")
            print("\nThe user should now be available in the Zep Cloud system.")
            return True
        else:
            print(f"\n❌ ERROR: Failed to create user {USER_ID}")
            return False
    except Exception as e:
        print(f"\n❌ ERROR: Exception while creating user: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 