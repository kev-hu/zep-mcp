#!/usr/bin/env python3
"""
Script to test the exact scenario from the Claude error message
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Import the ZepCloudClient
from core.zep_cloud_server import add_graph_data

def test_claude_error_scenario():
    """Test the exact scenario that failed in Claude"""
    print("\n=== Testing Exact Claude Error Scenario ===")
    
    # This is the exact data structure from the error message
    user_id = "anthony_ant2"
    data = {
        "datetime": "2025-01-01T00:00:00Z", 
        "text": "Omg, today I had an orange pie and it was so good! I think I'm going to try baking orange pies from now on. Oh and I loved how crunchy it was."
    }
    data_type = "json"
    
    print(f"User ID: {user_id}")
    print(f"Data: {data}")
    print(f"Data Type: {data_type}")
    
    # Try calling the tool function directly
    try:
        result_json = add_graph_data(user_id, data, data_type)
        result = json.loads(result_json)
        
        success = result.get("success", False)
        print(f"\nResult: {'✅ Success' if success else '❌ Failure'}")
        if not success:
            print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print("✅ Successfully processed the exact error scenario data!")
            print(f"Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Also try with a JSON-escaped string (which is what the error showed)
    print("\n== Testing with JSON-escaped string ==")
    escaped_json = '{\"datetime\": \"2025-01-01T00:00:00Z\", \"text\": \"Omg, today I had an orange pie and it was so good! I think I\\\'m going to try baking orange pies from now on. Oh and I loved how crunchy it was.\"}'
    
    try:
        result_json = add_graph_data(user_id, escaped_json, data_type)
        result = json.loads(result_json)
        
        success = result.get("success", False)
        print(f"Result: {'✅ Success' if success else '❌ Failure'}")
        if not success:
            print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print("✅ Successfully processed the escaped JSON data!")
    except Exception as e:
        print(f"❌ Exception with escaped JSON: {str(e)}")
    
    print("\n=== Test Complete ===")
    print("If both tests passed, the issue should be resolved!")

if __name__ == "__main__":
    test_claude_error_scenario() 