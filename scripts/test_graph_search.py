#!/usr/bin/env python3
"""
Script to test the Zep Cloud graph search API directly
This will help verify if the user has any data in the graph
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Try loading environment variables
env_path = Path('.env.new')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment from .env.new")
else:
    load_dotenv()  # Fallback to default .env
    print(f"Loaded environment from .env")

# User ID to search for
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

def test_graph_search():
    """Test searching the graph for a specific user"""
    print(f"\n=== Testing graph search for user: {USER_ID} ===")
    
    # Create client
    try:
        client = ZepCloudClient()
        print(f"Successfully initialized ZepCloudClient")
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        sys.exit(1)
    
    # List of test queries to try
    test_queries = [
        "feelings emotions mood",
        "recent activities",
        "conversation history",
        "messages",
        "user information",
        "data",  # Very generic query to try to match anything
    ]
    
    # Try different search scopes
    scopes = ["edges", "nodes", "both"]
    
    # Try all combinations
    success = False
    for scope in scopes:
        print(f"\n== Testing scope: {scope} ==")
        for query in test_queries:
            print(f"\nTrying query: '{query}'")
            try:
                # Call the graph search method
                result = client.search_graph(USER_ID, query, limit=20, scope=scope)
                
                # Check if we got any results
                if result:
                    # Print node/edge counts
                    edges_count = len(result.get("edges", [])) if "edges" in result else 0
                    nodes_count = len(result.get("nodes", [])) if "nodes" in result else 0
                    results_count = len(result.get("results", [])) if "results" in result else 0
                    
                    print(f"Results: edges={edges_count}, nodes={nodes_count}, combined={results_count}")
                    
                    if edges_count > 0 or nodes_count > 0 or results_count > 0:
                        print("✅ FOUND DATA!")
                        print(json.dumps(result, indent=2))
                        success = True
                else:
                    print("No results returned (null response)")
            except Exception as e:
                print(f"Error searching graph: {str(e)}")
    
    # Final status
    if success:
        print("\n✅ SUCCESS: Found data for the user in at least one query.")
    else:
        print("\n❌ No data found for this user with any of the test queries.")
        print("This could mean one of these issues:")
        print("1. The user doesn't have any data in the Zep graph")
        print("2. The search scope or queries aren't matching the data")
        print("3. There are permission issues with the API key")
        print("4. The graph search endpoint isn't working as expected")

if __name__ == "__main__":
    test_graph_search() 