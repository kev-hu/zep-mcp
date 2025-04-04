#!/usr/bin/env python3
"""
Script to test that the MCP server starts correctly
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

# Path to the server script
SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "zep_cloud_server.py")

def test_server_startup():
    """Test that the server starts up correctly"""
    print(f"\n=== Testing MCP server startup ===")
    print(f"Using server script at: {SERVER_SCRIPT}")
    
    # Start the server in a separate process
    print("\nStarting MCP server...")
    server_process = subprocess.Popen(
        ["python3", SERVER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server time to start
    print("Waiting for server to start up (5 seconds)...")
    time.sleep(5)
    
    # Check if server is running
    if server_process.poll() is None:
        print("✅ Server started successfully and is running")
    else:
        print("❌ Server failed to start or exited early")
        stdout, stderr = server_process.communicate()
        print("Server stdout:", stdout)
        print("Server stderr:", stderr)
        return
    
    try:
        # Keep server running for a bit to see logs
        print("\nServer is running. Press Ctrl+C to stop...")
        while server_process.poll() is None:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nReceived Ctrl+C, stopping server...")
    finally:
        # Clean up the server process
        if server_process.poll() is None:
            print("Stopping MCP server...")
            server_process.send_signal(signal.SIGINT)
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Server didn't stop gracefully, force killing...")
                server_process.kill()
                
        stdout, stderr = server_process.communicate()
        if stdout:
            print("\nServer stdout:")
            print(stdout)
        if stderr:
            print("\nServer stderr:")
            print(stderr)
            
    print("\n=== Test Complete ===")
    print("The MCP server started successfully. You can now connect to it using Claude Desktop.")
    print("Instructions for Claude Desktop:")
    print("1. Open Claude Desktop")
    print("2. Add this MCP server in Claude settings")
    print("3. In conversation with Claude, you can now use the add_graph_data tool")
    print(f"4. Server path: {os.path.abspath(SERVER_SCRIPT)}")

if __name__ == "__main__":
    test_server_startup() 