#!/usr/bin/env python3

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Import the ZepCloudClient
from core.zep_cloud_client import ZepCloudClient
from core.zep_cloud_server import add_graph_data

def test_client_json_handling():
    """Test the client's JSON handling directly"""
    print("\n=== Testing ZepCloudClient JSON Handling ===")
    
    # Initialize the client - no parameters needed as it uses environment variables
    try:
        client = ZepCloudClient()
        user_id = "test_user_json_handling"
    except Exception as e:
        print(f"❌ Failed to initialize ZepCloudClient: {str(e)}")
        print("Make sure ZEP_API_KEY environment variable is set")
        return False
    
    # Test cases
    test_cases = [
        {
            "name": "Valid JSON object",
            "data": '{"name": "John", "age": 30, "city": "New York"}',
            "expected_success": True
        },
        {
            "name": "Valid JSON with nested object",
            "data": '{"person": {"name": "John", "age": 30}, "address": {"city": "New York", "zip": "10001"}}',
            "expected_success": True
        },
        {
            "name": "Valid JSON array",
            "data": '[{"name": "John"}, {"name": "Jane"}]',
            "expected_success": True
        },
        {
            "name": "JSON with extra quotes",
            "data": '"{"name": "John", "age": 30}"',
            "expected_success": True
        },
        {
            "name": "Python dict (not string)",
            "data": {"name": "John", "age": 30, "city": "New York"},
            "expected_success": True
        },
        {
            "name": "JSON with syntax error",
            "data": '{"name": "John", "age": 30, city: "New York"}',  # Missing quotes around city
            "expected_success": False
        },
        {
            "name": "Completely invalid data",
            "data": 'This is not JSON at all',
            "expected_success": False
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"Data: {test_case['data']}")
        
        try:
            result = client.add_graph_data(user_id, test_case['data'], "json")
            
            success = result.get("success", False)
            print(f"Result: {'✅ Success' if success else '❌ Failure'}")
            if not success:
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            if success == test_case["expected_success"]:
                print(f"✅ Test passed (got expected result: {success})")
                success_count += 1
            else:
                print(f"❌ Test failed (expected {test_case['expected_success']}, got {success})")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            if not test_case["expected_success"]:
                print(f"✅ Test actually passed (expected failure with exception)")
                success_count += 1
            else:
                print(f"❌ Test failed (unexpected exception)")
    
    print(f"\n=== Client Test Summary: {success_count}/{len(test_cases)} tests passed ===")
    return success_count == len(test_cases)

def test_server_json_handling():
    """Test the server's JSON handling via the tool function"""
    print("\n=== Testing Server Tool JSON Handling ===")
    
    user_id = "test_user_server_json"
    
    # Test cases
    test_cases = [
        {
            "name": "Valid JSON object",
            "data": '{"name": "John", "age": 30, "city": "New York"}',
            "expected_success": True
        },
        {
            "name": "JSON with extra quotes",
            "data": '"{"name": "John", "age": 30}"',
            "expected_success": True
        },
        {
            "name": "Single quotes instead of double",
            "data": "{'name': 'John', 'age': 30}",
            "expected_success": True
        },
        {
            "name": "JSON with Python-style trailing comma",
            "data": '{"name": "John", "age": 30,}',
            "expected_success": True
        },
        {
            "name": "JSON with syntax error",
            "data": '{"name": "John", "age": 30, city: "New York"}',  # Missing quotes around city
            "expected_success": False
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"Data: {test_case['data']}")
        
        try:
            result_json = add_graph_data(user_id, test_case['data'], "json")
            result = json.loads(result_json)
            
            success = result.get("success", False)
            print(f"Result: {'✅ Success' if success else '❌ Failure'}")
            if not success:
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            if success == test_case["expected_success"]:
                print(f"✅ Test passed (got expected result: {success})")
                success_count += 1
            else:
                print(f"❌ Test failed (expected {test_case['expected_success']}, got {success})")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            if not test_case["expected_success"]:
                print(f"✅ Test actually passed (expected failure with exception)")
                success_count += 1
            else:
                print(f"❌ Test failed (unexpected exception)")
    
    print(f"\n=== Server Test Summary: {success_count}/{len(test_cases)} tests passed ===")
    return success_count == len(test_cases)

def main():
    print("🧪 Testing JSON handling for Zep Graph Data")
    
    client_success = test_client_json_handling()
    server_success = test_server_json_handling()
    
    print("\n=== Final Results ===")
    print(f"Client Tests: {'✅ PASSED' if client_success else '❌ FAILED'}")
    print(f"Server Tests: {'✅ PASSED' if server_success else '❌ FAILED'}")
    
    if client_success and server_success:
        print("\n🎉 All tests passed! Your JSON handling is robust.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Review the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 