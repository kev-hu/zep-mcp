#!/usr/bin/env python3
"""
Simple script to run the Zep Cloud server directly
"""

import os
import sys
import logging
from importlib import import_module

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ServerRunner")

def main():
    """Run the server"""
    logger.info("🚀 Starting the Zep Cloud server")
    
    try:
        # Import the server module
        server_module = import_module("zep_cloud_server")
        
        # Get the MCP instance
        if hasattr(server_module, "mcp"):
            mcp = server_module.mcp
            
            # Run the server on a specific host and port
            host = os.getenv("MCP_HOST", "0.0.0.0")
            port = int(os.getenv("MCP_PORT", "8080"))
            logger.info(f"🌐 Server running at http://{host}:{port}")
            
            # Run the server
            mcp.run()
        else:
            logger.error("❌ MCP instance not found in server module")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 