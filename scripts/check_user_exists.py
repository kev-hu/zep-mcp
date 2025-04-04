#!/usr/bin/env python3
"""
Script to check if a specific user exists in Zep Cloud
"""

import os
import sys
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

def check_user_exists(user_id):
    """Check if a user exists in Zep Cloud"""
    print(f"\n=== Checking if user exists in Zep Cloud: {user_id} ===\n")
    
    # Create client
    try:
        client = ZepCloudClient()
        print(f"Successfully initialized ZepCloudClient")
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        return False
    
    # Check if user exists
    try:
        user = client.get_user(user_id)
        
        if user:
            print(f"✅ User exists: {user['user_id']}")
            print(f"Metadata: {json.dumps(user['metadata'], indent=2)}")
            return True
        else:
            print(f"❌ User {user_id} does not exist")
            return False
    except Exception as e:
        print(f"❌ Error checking user: {str(e)}")
        return False

if __name__ == "__main__":
    # Get user ID from command line or use default
    user_id = sys.argv[1] if len(sys.argv) > 1 else "16263830569_aprilx"
    check_user_exists(user_id) 