#!/usr/bin/env python3
"""
Test script for the ZepCloudClient
"""

import sys
import time
import uuid

from zep_cloud_client import ZepCloudClient

def test_list_users():
    """Test listing users"""
    print("\n=== Testing List Users ===")
    
    try:
        client = ZepCloudClient()
        users = client.list_users()
        
        print(f"Found {len(users)} users")
        # Print first 5 users
        for i, user in enumerate(users[:5]):
            print(f"User {i+1}: {user['user_id']}")
            
        return True
    
    except Exception as e:
        print(f"Error listing users: {str(e)}")
        return False

def test_get_user(user_id: str):
    """Test getting a user"""
    print(f"\n=== Testing Get User: {user_id} ===")
    
    try:
        client = ZepCloudClient()
        user = client.get_user(user_id)
        
        if user:
            print(f"Found user: {user['user_id']}")
            print(f"Metadata: {user['metadata']}")
            return True
        else:
            print(f"User {user_id} not found")
            return False
    
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return False

def test_create_user():
    """Test creating a user"""
    # Generate a unique user ID
    test_user_id = f"test_user_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    print(f"\n=== Testing Create User: {test_user_id} ===")
    
    try:
        client = ZepCloudClient()
        
        # Create user with metadata
        metadata = {
            "test": True,
            "created_at": time.time(),
            "description": "Test user created by ZepCloudClient test script"
        }
        
        user = client.create_user(test_user_id, metadata)
        
        if user:
            print(f"Created user: {user['user_id']}")
            print(f"Metadata: {user['metadata']}")
            
            # Now test getting the user
            time.sleep(1)  # Brief pause to ensure user is created
            return test_get_user(test_user_id)
        else:
            print("Failed to create user")
            return False
    
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False

def test_update_user(user_id: str):
    """Test updating a user"""
    print(f"\n=== Testing Update User: {user_id} ===")
    
    try:
        client = ZepCloudClient()
        
        # Get current user
        user = client.get_user(user_id)
        if not user:
            print(f"User {user_id} not found for update test")
            return False
            
        # Update metadata
        metadata = user["metadata"].copy() if user["metadata"] else {}
        metadata.update({
            "updated_at": time.time(),
            "update_test": True
        })
        
        updated_user = client.update_user(user_id, metadata)
        
        if updated_user:
            print(f"Updated user: {updated_user['user_id']}")
            print(f"Updated metadata: {updated_user['metadata']}")
            return True
        else:
            print(f"Failed to update user {user_id}")
            return False
    
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        return False

def test_delete_user(user_id: str):
    """Test deleting a user"""
    print(f"\n=== Testing Delete User: {user_id} ===")
    
    try:
        client = ZepCloudClient()
        
        # Confirm user exists
        user = client.get_user(user_id)
        if not user:
            print(f"User {user_id} not found for delete test")
            return False
            
        # Delete user
        success = client.delete_user(user_id)
        
        if success:
            print(f"Successfully deleted user {user_id}")
            
            # Verify user is deleted
            time.sleep(1)  # Brief pause to ensure user is deleted
            deleted_user = client.get_user(user_id)
            
            if deleted_user:
                print(f"WARNING: User {user_id} still exists after deletion")
                return False
            else:
                print(f"Confirmed user {user_id} no longer exists")
                return True
        else:
            print(f"Failed to delete user {user_id}")
            return False
    
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n=== Running All Zep Cloud Client Tests ===\n")
    
    # Test listing users
    list_success = test_list_users()
    
    # Test creating a user
    create_success = test_create_user()
    
    # The rest of the tests depend on create_success
    if create_success:
        # Get the newly created user ID
        client = ZepCloudClient()
        users = client.list_users()
        test_users = [u for u in users if u["user_id"].startswith("test_user_")]
        
        if test_users:
            test_user_id = test_users[0]["user_id"]
            print(f"\nUsing test user: {test_user_id}")
            
            # Test updating user
            update_success = test_update_user(test_user_id)
            
            # Test deleting user
            delete_success = test_delete_user(test_user_id)
            
            # Report results
            print("\n=== Test Results ===")
            print(f"List Users: {'✅ SUCCESS' if list_success else '❌ FAILED'}")
            print(f"Create User: {'✅ SUCCESS' if create_success else '❌ FAILED'}")
            print(f"Update User: {'✅ SUCCESS' if update_success else '❌ FAILED'}")
            print(f"Delete User: {'✅ SUCCESS' if delete_success else '❌ FAILED'}")
            
            return list_success and create_success and update_success and delete_success
        else:
            print("No test users found after creation")
            return False
    else:
        # Report partial results
        print("\n=== Test Results ===")
        print(f"List Users: {'✅ SUCCESS' if list_success else '❌ FAILED'}")
        print(f"Create User: {'✅ SUCCESS' if create_success else '❌ FAILED'}")
        print("Update User: ❌ SKIPPED (Create failed)")
        print("Delete User: ❌ SKIPPED (Create failed)")
        
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 