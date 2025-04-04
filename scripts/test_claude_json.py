#!/usr/bin/env python3
"""
Script to test JSON formatting issues that Claude might encounter
This simulates different ways Claude might format JSON data
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Try loading environment variables
env_path = Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment from .env")
else:
    load_dotenv()  # Fallback to default .env
    print(f"Loaded environment from .env")

# User ID to test with
USER_ID = "16263830569"

# Import the Zep Cloud client
try:
    # Try to import from the core directory
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.zep_cloud_client import ZepCloudClient
    print("Successfully imported ZepCloudClient")
except ImportError as e:
    print(f"Failed to import ZepCloudClient: {str(e)}")
    print("Make sure zep_cloud_client.py is accessible.")
    sys.exit(1)

def test_claude_json_handling():
    """Test various JSON formatting scenarios that Claude might use"""
    print(f"\n=== Testing Claude JSON Handling for user: {USER_ID} ===")
    
    # Create client
    try:
        client = ZepCloudClient()
        print(f"Successfully initialized ZepCloudClient")
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        sys.exit(1)
    
    # Test scenarios simulating how Claude might format JSON data
    test_scenarios = [
        {
            "name": "Standard JSON Object", 
            "json_data": {"name": "Test User", "age": 30, "active": True},
            "expected_success": True
        },
        {
            "name": "JSON with nested quotes", 
            "json_data": '{"name": "Test User", "message": "Hello, this is a \"quoted\" message"}',
            "expected_success": True,
            "is_string": True
        },
        {
            "name": "JSON with extra quotes",
            "json_data": '\'{"name": "Extra Quotes Test", "age": 30}\'',
            "expected_success": False,
            "is_string": True
        },
        {
            "name": "JSON with formatted string",
            "json_data": """
            {
                "name": "Formatted JSON",
                "description": "JSON with newlines and indentation",
                "items": [1, 2, 3]
            }
            """,
            "expected_success": True,
            "is_string": True
        },
        {
            "name": "JSON with escaped backslashes",
            "json_data": '{"path": "C:\\\\Users\\\\Documents"}',
            "expected_success": True,
            "is_string": True
        },
        {
            "name": "Using JSON Object With String Value",
            "json_data": {"data": '{"nested": "value"}'},
            "expected_success": False
        }
    ]
    
    # Run each test scenario
    for scenario in test_scenarios:
        print(f"\n== Testing: {scenario['name']} ==")
        
        data = scenario["json_data"]
        is_string = scenario.get("is_string", False)
        
        if not is_string:
            try:
                data = json.dumps(data)
            except Exception as e:
                print(f"❌ Error converting to JSON string: {str(e)}")
                continue
        
        print(f"JSON data: {data}")
        print(f"Type: {type(data)}")
        print(f"Expected success: {scenario['expected_success']}")
        
        # Try adding to graph
        try:
            result = client.add_graph_data(USER_ID, data, "json")
            
            if result and result.get("success"):
                success = True
                uuid = result.get("response", {}).get("uuid", "unknown")
                print(f"✅ Success! Added JSON data to graph. UUID: {uuid}")
            else:
                success = False
                error = result.get("error", "Unknown error") if result else "Empty result"
                print(f"❌ Failed: {error}")
            
            if success == scenario["expected_success"]:
                print(f"✓ Result matches expected outcome")
            else:
                print(f"✗ Result differs from expected outcome")
                
        except Exception as e:
            print(f"❌ Exception during test: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Test modifying the client implementation to handle potential issues
    print("\n== Testing modified client approach ==")
    
    test_data = '{"name": "Modified Client Test", "value": "This tests a more robust implementation"}'
    print(f"Test data: {test_data}")
    
    try:
        # Try to fix common JSON formatting issues that Claude might introduce
        if isinstance(test_data, str):
            # Handle potential extra quotes that Claude might add
            if test_data.startswith("'") and test_data.endswith("'"):
                test_data = test_data[1:-1]
            elif test_data.startswith('"') and test_data.endswith('"'):
                test_data = test_data[1:-1]
                
            # Check if it's already valid JSON
            try:
                # Just validate, but keep as string
                json.loads(test_data)
                valid_json = True
            except json.JSONDecodeError:
                valid_json = False
                print(f"Warning: Invalid JSON string format")
                
            if not valid_json:
                # Try to fix common issues
                try:
                    # If it looks like a Python dict literal, try to eval it safely
                    if test_data.strip().startswith("{") and test_data.strip().endswith("}"):
                        import ast
                        obj = ast.literal_eval(test_data)
                        test_data = json.dumps(obj)
                        print(f"Fixed with ast.literal_eval: {test_data}")
                except Exception as e:
                    print(f"Could not fix JSON format: {str(e)}")
        
        # Now try adding to graph
        result = client.add_graph_data(USER_ID, test_data, "json")
        
        if result and result.get("success"):
            print(f"✅ Successfully added with modified approach")
        else:
            error = result.get("error", "Unknown error") if result else "Empty result"
            print(f"❌ Failed with modified approach: {error}")
            
    except Exception as e:
        print(f"❌ Exception during modified test: {str(e)}")
    
    # Final summary
    print("\n=== Test Summary ===")
    print("Completed testing of Claude JSON handling scenarios")
    print("Based on these results, we can update the client implementation to handle Claude's JSON format better")

if __name__ == "__main__":
    test_claude_json_handling() 