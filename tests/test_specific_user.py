#!/usr/bin/env python3
"""
Comprehensive test script for all operations on a specific user in Zep Cloud
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Configure the specific user ID to test
USER_ID = "16263830569_aprilx"

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

def check_user_exists(client, user_id, verbose=True):
    """Check if a user exists in Zep Cloud"""
    if verbose:
        print(f"\n=== Checking if user exists: {user_id} ===\n")
    
    try:
        user = client.get_user(user_id)
        
        if user:
            if verbose:
                print(f"✅ User exists: {user['user_id']}")
                print(f"Metadata: {json.dumps(user['metadata'], indent=2)}")
            return user
        else:
            if verbose:
                print(f"❌ User {user_id} does not exist")
            return None
    except Exception as e:
        if verbose:
            print(f"❌ Error checking user: {str(e)}")
        return None

def create_user(client, user_id, metadata=None):
    """Create a user in Zep Cloud"""
    print(f"\n=== Creating user: {user_id} ===\n")
    
    # Default metadata
    if metadata is None:
        metadata = {
            "created_at": time.time(),
            "description": "Test user created for production use",
            "source": "direct_api_call",
            "organization": "zep_cloud_test"
        }
    
    print(f"Attempting to create user with metadata:")
    print(json.dumps(metadata, indent=2))
    
    try:
        user = client.create_user(user_id, metadata)
        
        if user:
            print(f"\n✅ SUCCESS: Created user: {user['user_id']}")
            print(f"Metadata: {json.dumps(user['metadata'], indent=2)}")
            return user
        else:
            print(f"\n❌ ERROR: Failed to create user {user_id}")
            return None
    except Exception as e:
        print(f"\n❌ ERROR: Exception while creating user: {str(e)}")
        return None

def update_user(client, user_id, metadata):
    """Update a user in Zep Cloud"""
    print(f"\n=== Updating user: {user_id} ===\n")
    
    print(f"Attempting to update user with metadata:")
    print(json.dumps(metadata, indent=2))
    
    try:
        user = client.update_user(user_id, metadata)
        
        if user:
            print(f"\n✅ SUCCESS: Updated user: {user['user_id']}")
            print(f"Metadata: {json.dumps(user['metadata'], indent=2)}")
            return user
        else:
            print(f"\n❌ ERROR: Failed to update user {user_id}")
            return None
    except Exception as e:
        print(f"\n❌ ERROR: Exception while updating user: {str(e)}")
        return None

def delete_user(client, user_id):
    """Delete a user from Zep Cloud"""
    print(f"\n=== Deleting user: {user_id} ===\n")
    
    try:
        result = client.delete_user(user_id)
        
        if result:
            print(f"\n✅ SUCCESS: Deleted user: {user_id}")
            return True
        else:
            print(f"\n❌ ERROR: Failed to delete user {user_id}")
            return False
    except Exception as e:
        print(f"\n❌ ERROR: Exception while deleting user: {str(e)}")
        return False

def restore_user(client, user_id, metadata=None):
    """Restore a user if it was deleted"""
    # Default metadata
    if metadata is None:
        metadata = {
            "created_at": time.time(),
            "description": "Restored user",
            "source": "restore_operation",
            "organization": "zep_cloud_test"
        }
    
    return create_user(client, user_id, metadata)

def run_test_with_metadata(metadata=None):
    """Run a test with the specified metadata"""
    # Create client
    try:
        client = ZepCloudClient()
        print(f"Successfully initialized ZepCloudClient")
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        return False
    
    # Check if user exists
    original_user = check_user_exists(client, USER_ID)
    had_user_initially = original_user is not None
    
    if had_user_initially:
        print(f"\nUser {USER_ID} already exists. Will create, update, and preserve it.")
    else:
        print(f"\nUser {USER_ID} does not exist. Will create, update, and then delete it.")
    
    # Create the user if it doesn't exist
    if not had_user_initially:
        created_user = create_user(client, USER_ID, metadata)
        if not created_user:
            print("Failed to create user. Aborting test.")
            return False
    
    # Update the user with new metadata
    update_metadata = {
        "updated_at": time.time(),
        "description": "Updated test user",
        "test_operation": "update",
        "organization": "zep_cloud_test"
    }
    
    updated_user = update_user(client, USER_ID, update_metadata)
    if not updated_user:
        print("Failed to update user.")
        if not had_user_initially:
            print("Cleaning up by deleting the user we created.")
            delete_user(client, USER_ID)
        return False
    
    # Verify the user exists with updated metadata
    verified_user = check_user_exists(client, USER_ID)
    if not verified_user:
        print("Failed to verify user after update.")
        if not had_user_initially:
            print("Cleaning up by deleting the user we created.")
            delete_user(client, USER_ID)
        return False
    
    # Delete the user if we created it
    if not had_user_initially:
        deleted = delete_user(client, USER_ID)
        if not deleted:
            print("Failed to delete user.")
            return False
        
        # Verify the user is gone
        deleted_check = check_user_exists(client, USER_ID)
        if deleted_check:
            print("User still exists after deletion attempt.")
            return False
    else:
        # Restore the original user
        if original_user and "metadata" in original_user:
            restore_user(client, USER_ID, original_user["metadata"])
        else:
            # If we had a user but couldn't get its metadata, create with default metadata
            restore_user(client, USER_ID)
    
    print("\n✅ All operations completed successfully!")
    return True

def run_test_with_null_metadata():
    """Run a test with null metadata"""
    print("\n=== Testing with NULL metadata ===")
    return run_test_with_metadata(None)

def run_test_with_empty_metadata():
    """Run a test with empty dict metadata"""
    print("\n=== Testing with EMPTY DICT metadata ===")
    return run_test_with_metadata({})

def run_test_with_actual_metadata():
    """Run a test with actual metadata"""
    print("\n=== Testing with ACTUAL metadata ===")
    metadata = {
        "created_at": time.time(),
        "description": "Test user with actual metadata",
        "source": "direct_api_call",
        "test_case": "actual_metadata",
        "organization": "zep_cloud_test"
    }
    return run_test_with_metadata(metadata)

def main():
    print(f"\n=== Comprehensive Test for Zep Cloud User: {USER_ID} ===\n")
    
    parser = argparse.ArgumentParser(description='Test Zep Cloud user operations')
    parser.add_argument('--test-case', type=str, choices=['null', 'empty', 'actual', 'all'],
                       default='all', help='Test case to run (default: all)')
    
    args = parser.parse_args()
    
    if args.test_case == 'null' or args.test_case == 'all':
        test_null = run_test_with_null_metadata()
        if not test_null and args.test_case != 'all':
            return False
            
    if args.test_case == 'empty' or args.test_case == 'all':
        test_empty = run_test_with_empty_metadata()
        if not test_empty and args.test_case != 'all':
            return False
            
    if args.test_case == 'actual' or args.test_case == 'all':
        test_actual = run_test_with_actual_metadata()
        if not test_actual and args.test_case != 'all':
            return False
    
    print("\n=== Test Summary ===")
    if args.test_case == 'all':
        print("All test cases completed.")
    else:
        print(f"Test case '{args.test_case}' completed.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 