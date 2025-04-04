#!/usr/bin/env python3
"""
Script to test the Zep Cloud graph data addition functionality
This will add sample data to a user's graph and then search for it to verify it works
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

# User ID to test with - change this to a real user ID in your system
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

def test_add_graph_data():
    """Test adding different types of data to a user's graph and searching for it"""
    print(f"\n=== Testing graph data addition for user: {USER_ID} ===")
    
    # Create client
    try:
        client = ZepCloudClient()
        print(f"Successfully initialized ZepCloudClient")
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        sys.exit(1)
    
    # Test data for each type
    test_data = {
        "text": "This is a test document about artificial intelligence and its applications in healthcare. AI has the potential to transform patient diagnosis, treatment planning, and medical research.",
        
        "json": json.dumps({
            "name": "John Smith",
            "age": 35,
            "occupation": "Software Engineer",
            "skills": ["Python", "JavaScript", "Machine Learning"],
            "projects": [
                {"name": "Healthcare AI", "status": "In Progress"},
                {"name": "Data Analytics Platform", "status": "Completed"}
            ]
        }),
        
        "message": "User: I'm interested in learning more about how AI can help improve healthcare outcomes. Assistant: AI has several applications in healthcare, including improving diagnosis accuracy, personalizing treatment plans, and accelerating medical research."
    }
    
    # Add each type of data to the graph
    for data_type, data in test_data.items():
        print(f"\n== Testing data type: {data_type} ==")
        print(f"Adding {data_type} data to graph... ({len(data)} characters)")
        
        try:
            # Call the add_graph_data method
            result = client.add_graph_data(USER_ID, data, data_type)
            
            if result and result.get("success"):
                uuid = result.get("response", {}).get("uuid", "unknown")
                print(f"✅ Successfully added {data_type} data to graph. UUID: {uuid}")
            else:
                error = result.get("error", "Unknown error") if result else "Empty result"
                print(f"❌ Failed to add {data_type} data to graph: {error}")
                continue
                
            # Wait a moment for the data to be processed
            print("Waiting for data to be processed (2 seconds)...")
            time.sleep(2)
            
            # Now search for the data to verify it was added
            search_query = "healthcare AI" if data_type != "json" else "software engineer skills"
            print(f"Searching for '{search_query}' in graph...")
            
            search_result = client.search_graph(USER_ID, search_query, limit=5)
            
            if search_result:
                # Check if we got any results
                edges_count = len(search_result.get("edges", [])) if "edges" in search_result else 0
                nodes_count = len(search_result.get("nodes", [])) if "nodes" in search_result else 0
                results_count = len(search_result.get("results", [])) if "results" in search_result else 0
                
                print(f"Search results: edges={edges_count}, nodes={nodes_count}, combined={results_count}")
                
                if edges_count > 0 or nodes_count > 0 or results_count > 0:
                    print(f"✅ Data verification successful - found search results for {data_type} data")
                else:
                    print(f"⚠️ No search results found for {data_type} data. This might be normal if the data is still being processed.")
            else:
                print(f"❌ Search failed for {data_type} data")
        except Exception as e:
            print(f"Error during {data_type} data test: {str(e)}")
    
    # Final status
    print("\n=== Test Summary ===")
    print("Completed testing of graph data addition functionality")
    print("Note: If search verification didn't find results, it might be because Zep needs more time to process the data.")
    print("You can run this test again in a few minutes to check if the data becomes searchable.")

if __name__ == "__main__":
    test_add_graph_data() 