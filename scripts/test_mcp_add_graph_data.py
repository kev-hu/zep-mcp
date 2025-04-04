#!/usr/bin/env python3
"""
Script to test the MCP add_graph_data tool directly
This simulates Claude calling the tool through the MCP server
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# User ID to test with
USER_ID = "16263830569"

# Path to the server script
SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "zep_cloud_server.py")

def test_mcp_tool():
    """Test calling the add_graph_data MCP tool"""
    print(f"\n=== Testing MCP add_graph_data tool ===")
    print(f"Using server script at: {SERVER_SCRIPT}")
    
    # Test data
    test_data = "This is a test message added through the MCP server directly. It contains information about climate change and renewable energy."
    data_type = "text"
    
    # Start the server in a separate process
    print("\nStarting MCP server...")
    server_process = subprocess.Popen(
        ["python3", SERVER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server time to start
    print("Waiting for server to start up (3 seconds)...")
    time.sleep(3)
    
    try:
        # Execute the mcp-eval command to call the tool
        print("\nCalling add_graph_data tool...")
        mcp_command = [
            "mcp-eval", 
            "--server", SERVER_SCRIPT,
            "--tool", "add_graph_data",
            "--args", json.dumps({
                "user_id": USER_ID,
                "data": test_data,
                "data_type": data_type
            })
        ]
        
        print(f"Running command: {' '.join(mcp_command)}")
        result = subprocess.run(
            mcp_command,
            capture_output=True,
            text=True
        )
        
        # Display the results
        print("\n=== Tool Call Results ===")
        if result.returncode == 0:
            print("✅ MCP tool call successful")
            print("Output:")
            try:
                result_json = json.loads(result.stdout)
                print(json.dumps(result_json, indent=2))
                
                if result_json.get("success"):
                    print("\n✅ Data successfully added to graph!")
                else:
                    print("\n❌ Failed to add data to graph:", result_json.get("error", "Unknown error"))
            except json.JSONDecodeError:
                print("Could not parse JSON response:")
                print(result.stdout)
        else:
            print("❌ MCP tool call failed")
            print(f"Return code: {result.returncode}")
            print("Error output:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error testing MCP tool: {str(e)}")
    finally:
        # Clean up the server process
        print("\nStopping MCP server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            
        stdout, stderr = server_process.communicate()
        if stdout:
            print("\nServer stdout:")
            print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
        if stderr:
            print("\nServer stderr:")
            print(stderr[:500] + "..." if len(stderr) > 500 else stderr)
            
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_mcp_tool() 