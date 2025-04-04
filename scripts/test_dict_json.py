#!/usr/bin/env python3
"""
Script to test adding Python dictionaries directly as JSON data
This will help verify our fixes for Claude's JSON handling
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Import the necessary components
from core.zep_cloud_client import ZepCloudClient
from core.zep_cloud_server import add_graph_data

def test_direct_dictionary_handling():
    """Test adding a Python dictionary directly as JSON data"""
    print("\n=== Testing Python Dictionary as JSON Data ===")
    
    # Initialize the client
    try:
        client = ZepCloudClient()
        user_id = "test_dict_json_user"
        print("✅ Successfully initialized ZepCloudClient")
    except Exception as e:
        print(f"❌ Failed to initialize ZepCloudClient: {str(e)}")
        return False
    
    # Test data that simulates what Claude might send
    test_data = {
        "datetime": "2025-01-01T00:00:00Z", 
        "text": "Omg, today I had an orange pie and it was so good! I think I'm going to try baking orange pies from now on. Oh and I loved how crunchy it was."
    }
    
    print(f"\n📝 Test: Python Dictionary Object")
    print(f"Data type: {type(test_data)}")
    print(f"Data content: {test_data}")
    
    # Test with client directly
    try:
        result = client.add_graph_data(user_id, test_data, "json")
        
        success = result.get("success", False)
        print(f"\nClient Result: {'✅ Success' if success else '❌ Failure'}")
        if not success:
            print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print("✅ Successfully added dictionary data through client")
    except Exception as e:
        print(f"❌ Exception in client test: {str(e)}")
    
    # Test with server tool function
    print("\n== Testing Server Tool Function ==")
    try:
        # Convert the result to a string since that's what the tool returns
        result_json = add_graph_data(user_id, test_data, "json")
        result = json.loads(result_json)
        
        success = result.get("success", False)
        print(f"Server Result: {'✅ Success' if success else '❌ Failure'}")
        if not success:
            print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print("✅ Successfully added dictionary data through server tool")
    except Exception as e:
        print(f"❌ Exception in server test: {str(e)}")
    
    # Test exact scenario from user's error
    print("\n== Testing Exact User Scenario ==")
    escaped_json_string = '{\"datetime\": \"2025-01-01T00:00:00Z\", \"text\": \"Omg, today I had an orange pie and it was so good! I think I\'m going to try baking orange pies from now on. Oh and I loved how crunchy it was.\"}'
    
    print(f"Data (escaped JSON string): {escaped_json_string}")
    
    try:
        result_json = add_graph_data(user_id, escaped_json_string, "json")
        result = json.loads(result_json)
        
        success = result.get("success", False)
        print(f"Result with escaped string: {'✅ Success' if success else '❌ Failure'}")
        if not success:
            print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print("✅ Successfully handled escaped JSON string")
    except Exception as e:
        print(f"❌ Exception in escaped JSON test: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_direct_dictionary_handling() 