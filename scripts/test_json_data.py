#!/usr/bin/env python3
"""
Script to specifically test adding JSON data to the Zep Cloud graph
This will help diagnose issues with JSON formatting and handling
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

def test_json_data_addition():
    """Test specifically adding JSON data to the graph with detailed diagnostics"""
    print(f"\n=== Testing JSON data addition for user: {USER_ID} ===")
    
    # Create client
    try:
        client = ZepCloudClient()
        print(f"Successfully initialized ZepCloudClient")
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        sys.exit(1)
    
    # Test different JSON payloads of increasing complexity
    json_test_data = [
        # Simple JSON object
        {
            "name": "Simple Test",
            "description": "A simple JSON object",
            "value": 42
        },
        
        # More complex JSON with nested objects
        {
            "user": {
                "name": "John Smith",
                "age": 35,
                "contact": {
                    "email": "john@example.com",
                    "phone": "555-1234"
                }
            },
            "preferences": {
                "theme": "dark",
                "notifications": True
            },
            "tags": ["test", "json", "data"]
        },
        
        # JSON with special characters
        {
            "title": "JSON with special chars: ✓, é, ñ",
            "content": "This includes quotes: \" and escaped chars \\ and new\nlines"
        }
    ]
    
    # Try each JSON payload
    for index, test_data in enumerate(json_test_data):
        print(f"\n== Test {index+1}: {test_data.get('name', 'JSON data')} ==")
        
        # Convert to JSON string
        try:
            # First try with standard JSON dumps
            json_string = json.dumps(test_data)
            print(f"JSON string (length: {len(json_string)}): {json_string[:100]}{'...' if len(json_string) > 100 else ''}")
        except Exception as e:
            print(f"❌ Error serializing JSON: {str(e)}")
            continue
        
        # Try adding to graph
        print("Adding JSON data to graph...")
        try:
            # Debug: Print the exact arguments being passed
            print(f"Debug - Arguments to add_graph_data:")
            print(f"  user_id: {USER_ID}")
            print(f"  data_type: json")
            print(f"  data: {json_string}")
            
            # Call the add_graph_data method with extensive error handling
            try:
                result = client.add_graph_data(USER_ID, json_string, "json")
                
                if result and result.get("success"):
                    uuid = result.get("response", {}).get("uuid", "unknown")
                    print(f"✅ Successfully added JSON data to graph. UUID: {uuid}")
                    print(f"Full response: {json.dumps(result, indent=2)}")
                else:
                    error = result.get("error", "Unknown error") if result else "Empty result"
                    print(f"❌ Failed to add JSON data to graph: {error}")
                    print(f"Full response: {json.dumps(result, indent=2) if result else 'None'}")
                    continue
            except Exception as e:
                print(f"❌ Exception during client.add_graph_data call: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
                
            # Wait a moment for the data to be processed
            print("Waiting for data to be processed (2 seconds)...")
            time.sleep(2)
            
            # Now search for the data to verify it was added
            search_terms = [
                test_data.get("name", ""),
                test_data.get("description", ""),
                "json test"
            ]
            
            search_term = next((term for term in search_terms if term), "test")
            print(f"Searching for '{search_term}' in graph...")
            
            search_result = client.search_graph(USER_ID, search_term, limit=5)
            
            if search_result:
                # Check if we got any results
                edges_count = len(search_result.get("edges", [])) if "edges" in search_result else 0
                nodes_count = len(search_result.get("nodes", [])) if "nodes" in search_result else 0
                results_count = len(search_result.get("results", [])) if "results" in search_result else 0
                
                print(f"Search results: edges={edges_count}, nodes={nodes_count}, combined={results_count}")
                
                if edges_count > 0 or nodes_count > 0 or results_count > 0:
                    print(f"✅ Data verification successful - found search results for JSON data")
                else:
                    print(f"⚠️ No search results found for JSON data. This might be normal if the data is still being processed.")
            else:
                print(f"❌ Search failed")
        except Exception as e:
            print(f"Error during test: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Try direct JSON string approach
    print("\n== Testing direct JSON string approach ==")
    direct_json_string = '{"name":"Direct JSON String","value":42,"direct":true}'
    print(f"Adding direct JSON string to graph: {direct_json_string}")
    
    try:
        result = client.add_graph_data(USER_ID, direct_json_string, "json")
        if result and result.get("success"):
            print("✅ Successfully added direct JSON string")
        else:
            error = result.get("error", "Unknown error") if result else "Empty result"
            print(f"❌ Failed to add direct JSON string: {error}")
    except Exception as e:
        print(f"❌ Exception adding direct JSON string: {str(e)}")
    
    # Final status
    print("\n=== Test Summary ===")
    print("Completed testing of JSON data addition")
    print("If issues persist, check the ZepCloudClient implementation and the Zep API documentation.")

if __name__ == "__main__":
    test_json_data_addition() 