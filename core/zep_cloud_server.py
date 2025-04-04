#!/usr/bin/env python3
"""
MCP Server for Zep Cloud
This server provides tools for Claude Desktop to interact with Zep Cloud API.
"""

import os
import json
import sys
import logging
import requests
import socket
from dotenv import load_dotenv
from fastmcp import FastMCP
from typing import Optional, Dict, Any, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ZepCloudServer")

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP()

# Track the number of tools registered
tool_count = 0

# Import our ZepCloudClient or use the local implementation as fallback
try:
    # First try to import from the core directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from zep_cloud_client import ZepCloudClient
    logger.info("✅ Imported ZepCloudClient from zep_cloud_client.py")
    use_new_client = True
except ImportError:
    logger.warning("⚠️ Failed to import ZepCloudClient from zep_cloud_client.py. Using local implementation.")
    use_new_client = False
    
    # ZEP API Configuration if using local implementation
    ZEP_API_KEY = os.getenv("ZEP_API_KEY")
    ZEP_CLOUD_API_URL = "https://api.getzep.com/api/v2"

# If using the old client implementation, define it here
if not use_new_client:
    class ZepCloudClient:
        """Client for interacting with the Zep Cloud API."""

        def __init__(self, api_key=None, api_url=None):
            """Initialize the client with API key and URL."""
            self.api_key = api_key or ZEP_API_KEY
            self.api_url = api_url or ZEP_CLOUD_API_URL
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            self.fallback_mode = False
            self.test_connection()

        def test_connection(self):
            """Test the connection to the Zep Cloud API."""
            try:
                response = self._make_request("GET", f"{self.api_url}/health")
                if response.status_code == 200:
                    logger.info("✅ Connected to Zep Cloud API")
                    self.fallback_mode = False
                    return True
                else:
                    logger.warning(f"❌ Zep Cloud API authentication failed: {response.status_code} - {response.text}")
                    self.fallback_mode = True
                    return False
            except Exception as e:
                logger.error(f"❌ Failed to connect to Zep Cloud API: {str(e)}")
                self.fallback_mode = True
                return False

        def _handle_request_error(self, e, context_msg):
            """Handle request errors with detailed logging and diagnostics."""
            if isinstance(e, requests.exceptions.ConnectionError):
                # Check if it's a DNS resolution error
                if isinstance(e.args[0], socket.gaierror):
                    logger.error(f"❌ DNS resolution error during {context_msg}. Check your internet connection and API URL.")
                else:
                    logger.error(f"❌ Connection error during {context_msg}: {str(e)}")
            elif isinstance(e, requests.exceptions.HTTPError):
                status_code = e.response.status_code
                error_text = e.response.text

                if status_code == 401:
                    logger.error(f"❌ Authentication error during {context_msg}. Check your ZEP_API_KEY.")
                elif status_code == 404:
                    logger.error(f"❌ Resource not found during {context_msg}. Check the API endpoint.")
                else:
                    logger.error(f"❌ HTTP error {status_code} during {context_msg}: {error_text}")
            else:
                logger.error(f"❌ Error during {context_msg}: {str(e)}")

        def _make_request(self, method, url, data=None):
            """Make a request to the Zep Cloud API."""
            try:
                response = requests.request(method, url, headers=self.headers, json=data)
                response.raise_for_status()
                return response
            except Exception as e:
                self._handle_request_error(e, f"{method} request to {url}")
                raise

        def create_user(self, user_id: str, metadata: Optional[dict] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None):
            """Create a new user in Zep Cloud."""
            # Handle case where metadata is the string "null"
            if metadata == "null":
                metadata = None
                
            if self.fallback_mode:
                logger.warning("⚠️ Running in fallback mode. User creation simulated.")
                return {"user_id": user_id, "metadata": metadata or {}, "first_name": first_name, "last_name": last_name, "email": email, "success": True, "fallback": True}
                
            url = f"{self.api_url}/users"
            data = {"user_id": user_id}
            
            if metadata:
                data["metadata"] = metadata
            
            if first_name:
                data["first_name"] = first_name
                
            if last_name:
                data["last_name"] = last_name
            
            if email:
                data["email"] = email
            
            try:
                response = self._make_request("POST", url, data)
                return response.json()
            except Exception as e:
                logger.error(f"❌ Failed to create user: {str(e)}")
                return {"error": str(e), "success": False}

        def get_user(self, user_id):
            """Get a user from Zep Cloud."""
            if self.fallback_mode:
                logger.warning("⚠️ Running in fallback mode. User retrieval simulated.")
                return {"user_id": user_id, "success": True, "fallback": True}
                
            url = f"{self.api_url}/users/{user_id}"
            
            try:
                response = self._make_request("GET", url)
                return response.json()
            except Exception as e:
                logger.error(f"❌ Failed to get user: {str(e)}")
                return {"error": str(e), "success": False}

        def update_user(self, user_id, metadata):
            """Update a user in Zep Cloud."""
            # Handle case where metadata is the string "null"
            if metadata == "null":
                metadata = None
                
            if self.fallback_mode:
                logger.warning("⚠️ Running in fallback mode. User update simulated.")
                return {"user_id": user_id, "metadata": metadata or {}, "success": True, "fallback": True}
                
            url = f"{self.api_url}/users/{user_id}"
            data = {"metadata": metadata or {}}
            
            try:
                response = self._make_request("PATCH", url, data)
                return response.json()
            except Exception as e:
                logger.error(f"❌ Failed to update user: {str(e)}")
                return {"error": str(e), "success": False}

        def delete_user(self, user_id):
            """Delete a user from Zep Cloud."""
            if self.fallback_mode:
                logger.warning("⚠️ Running in fallback mode. User deletion simulated.")
                return {"success": True, "fallback": True}
                
            url = f"{self.api_url}/users/{user_id}"
            
            try:
                response = self._make_request("DELETE", url)
                return {"success": True}
            except Exception as e:
                logger.error(f"❌ Failed to delete user: {str(e)}")
                return {"error": str(e), "success": False}

        def list_users(self, limit: int = 100, cursor: Optional[str] = None):
            """List users in Zep Cloud."""
            if self.fallback_mode:
                logger.warning("⚠️ Running in fallback mode. User listing simulated.")
                return {"users": [], "success": True, "fallback": True}
                
            url = f"{self.api_url}/users?limit={limit}"
            if cursor:
                url += f"&cursor={cursor}"
            
            try:
                response = self._make_request("GET", url)
                return response.json()
            except Exception as e:
                logger.error(f"❌ Failed to list users: {str(e)}")
                return {"error": str(e), "success": False}

        def search_graph(self, user_id: str, query: str, limit: int = 10):
            """
            Search a user's graph in Zep Cloud.
            
            Args:
                user_id: The unique identifier for the user
                query: The search query to find relevant information about the user
                limit: The maximum number of results to return (default: 10)
                
            Returns:
                A JSON object with the search results including facts and/or nodes about the user
            """
            if self.fallback_mode:
                logger.warning("⚠️ Running in fallback mode. Graph search simulated.")
                return {
                    "query": query, 
                    "user_id": user_id, 
                    "limit": limit,
                    "edges": [],
                    "nodes": [],
                    "results": [],  # Include generic results array for backward compatibility
                    "success": True,
                    "summary": "No results found for query (fallback mode)",
                    "fallback": True
                }
                
            url = f"{self.api_url}/graph/search"
            data = {
                "user_id": user_id,
                "query": query,
                "limit": limit
            }
            
            try:
                response = self._make_request("POST", url, data)
                response_json = response.json()
                
                # Enhance response for better compatibility
                if "results" not in response_json:
                    response_json["results"] = []
                    
                    # Copy any edges or nodes to results array for backward compatibility
                    if "edges" in response_json and response_json["edges"]:
                        for edge in response_json["edges"]:
                            response_json["results"].append(edge)
                            
                    if "nodes" in response_json and response_json["nodes"]:
                        for node in response_json["nodes"]:
                            response_json["results"].append(node)
                
                # Add success flag
                response_json["success"] = True
                
                # Add a summary field to help Claude understand the results
                if len(response_json.get("results", [])) > 0:
                    response_json["summary"] = f"Found {len(response_json['results'])} results for query '{query}'"
                    if "nodes" in response_json and response_json["nodes"]:
                        response_json["summary"] += f", including {len(response_json['nodes'])} nodes"
                    if "edges" in response_json and response_json["edges"]:
                        response_json["summary"] += f", including {len(response_json['edges'])} edges/facts"
                else:
                    response_json["summary"] = f"No results found for query '{query}'"
                
                return response_json
            except Exception as e:
                logger.error(f"❌ Failed to search graph: {str(e)}")
                return {
                    "error": str(e), 
                    "success": False,
                    "summary": f"Error searching graph: {str(e)}"
                }
                
        def add_graph_data(self, user_id: str, data: str, data_type: str):
            """
            Add data to a user's graph in Zep Cloud.
            
            Args:
                user_id: The unique identifier for the user
                data: The data to add to the graph (text, JSON, or message)
                data_type: The type of data, can be "text", "json", or "message"
                
            Returns:
                A JSON object with information about the added data
            """
            if self.fallback_mode:
                logger.warning("⚠️ Running in fallback mode. Graph data addition simulated.")
                return {
                    "success": True,
                    "user_id": user_id,
                    "data_type": data_type,
                    "data_length": len(data),
                    "fallback": True,
                    "response": {
                        "uuid": "simulated-uuid",
                        "content": "Simulated content (fallback mode)",
                        "created_at": "simulated-timestamp",
                        "processed": True
                    }
                }
                
            # Check if data exceeds size limit
            if len(data) > 10000:
                logger.warning(f"Data exceeds maximum size of 10,000 characters. Truncating to 10,000 characters.")
                data = data[:10000]
                
            # Validate data type
            valid_types = ["text", "json", "message"]
            if data_type not in valid_types:
                logger.error(f"Invalid data type: {data_type}. Must be one of {valid_types}")
                return {
                    "error": f"Invalid data type: {data_type}. Must be one of {valid_types}",
                    "success": False
                }
                
            url = f"{self.api_url}/graph"
            post_data = {
                "user_id": user_id,
                "type": data_type,
                "data": data
            }
            
            try:
                response = self._make_request("POST", url, post_data)
                response_json = response.json()
                
                # Add success flag and additional info
                result = {
                    "success": True,
                    "user_id": user_id,
                    "data_type": data_type,
                    "data_length": len(data),
                    "response": response_json
                }
                
                return result
            except Exception as e:
                logger.error(f"❌ Failed to add data to graph: {str(e)}")
                return {
                    "error": str(e),
                    "success": False
                }

# Create a global client instance
try:
    client = ZepCloudClient()
    if hasattr(client, 'fallback_mode'):
        fallback_mode = client.fallback_mode
    else:
        # Check if connection works
        test_users = client.list_users()
        fallback_mode = test_users is None or len(test_users) == 0
        
    if fallback_mode:
        logger.warning("⚠️ Zep Cloud client is running in fallback mode. Operations will be simulated.")
    else:
        logger.info("✅ Zep Cloud client is connected and ready.")
        
except Exception as e:
    logger.error(f"❌ Failed to initialize Zep Cloud client: {str(e)}")
    logger.warning("⚠️ Falling back to simulation mode.")
    fallback_mode = True

# === Tool Definitions ===

@mcp.tool()
def create_user(user_id: str, metadata: Optional[dict] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None):
    """
    Create a new user in Zep Cloud.
    
    Args:
        user_id: The unique identifier for the user
        metadata: Optional metadata for the user
        first_name: Optional first name for the user
        last_name: Optional last name for the user
        email: Optional email address for the user
        
    Returns:
        A JSON object with the user information
    """
    global tool_count
    tool_count += 1
    logger.info(f"📝 Tool call {tool_count}: create_user({user_id}, {metadata}, {first_name}, {last_name}, {email})")
    
    # Handle case where metadata is the string "null"
    if metadata == "null":
        metadata = None
        
    result = client.create_user(user_id, metadata, first_name, last_name, email)
    return json.dumps(result)

@mcp.tool()
def get_user(user_id: str):
    """
    Get a user from Zep Cloud.
    
    Args:
        user_id: The unique identifier for the user
        
    Returns:
        A JSON object with the user information
    """
    global tool_count
    tool_count += 1
    logger.info(f"📝 Tool call {tool_count}: get_user({user_id})")
    
    result = client.get_user(user_id)
    return json.dumps(result)

@mcp.tool()
def update_user(user_id: str, metadata: dict):
    """
    Update a user in Zep Cloud.
    
    Args:
        user_id: The unique identifier for the user
        metadata: The new metadata for the user
        
    Returns:
        A JSON object with the updated user information
    """
    global tool_count
    tool_count += 1
    logger.info(f"📝 Tool call {tool_count}: update_user({user_id}, {metadata})")
    
    # Handle case where metadata is the string "null"
    if metadata == "null":
        metadata = None
        
    result = client.update_user(user_id, metadata)
    return json.dumps(result)

@mcp.tool()
def delete_user(user_id: str):
    """
    Delete a user from Zep Cloud.
    
    Args:
        user_id: The unique identifier for the user
        
    Returns:
        A JSON object indicating success or failure
    """
    global tool_count
    tool_count += 1
    logger.info(f"📝 Tool call {tool_count}: delete_user({user_id})")
    
    result = client.delete_user(user_id)
    return json.dumps(result)

@mcp.tool()
def list_users(limit: int = 100, cursor: Optional[str] = None):
    """
    List users in Zep Cloud.
    
    Args:
        limit: The maximum number of users to return
        cursor: A cursor for pagination
        
    Returns:
        A JSON object with the list of users
    """
    global tool_count
    tool_count += 1
    logger.info(f"📝 Tool call {tool_count}: list_users({limit}, {cursor})")
    
    result = client.list_users(limit, cursor)
    return json.dumps(result)

@mcp.tool()
def check_connection():
    """
    Check the connection to the Zep Cloud API.
    
    Returns:
        A JSON object indicating connection status
    """
    global tool_count
    tool_count += 1
    logger.info(f"📝 Tool call {tool_count}: check_connection()")
    
    global fallback_mode
    result = {
        "connected": not fallback_mode,
        "fallback_mode": fallback_mode,
        "message": "Connected to Zep Cloud API" if not fallback_mode else "Running in fallback mode"
    }
    return json.dumps(result)

@mcp.tool()
def search_graph(user_id: str, query: str, limit: int = 10):
    """
    Search a user's graph in Zep Cloud.
    
    Args:
        user_id: The unique identifier for the user
        query: The search query to find relevant information about the user
        limit: The maximum number of results to return (default: 10)
        
    Returns:
        A JSON object with the search results including facts and/or nodes about the user
    """
    global tool_count
    tool_count += 1
    logger.info(f"📝 Tool call {tool_count}: search_graph({user_id}, {query}, {limit})")
    
    # Truncate very long queries
    if len(query) > 8000:
        logger.warning(f"Search query exceeds recommended length. Truncating to 8000 characters.")
        query = query[:8000]
    
    # If query seems to be about user information, emotions, or general data,
    # we know these provide better results
    lower_query = query.lower()
    if not query or len(query.strip()) == 0:
        query = "user information"
        logger.info(f"Empty query detected, using 'user information' instead")
    elif "user" not in lower_query and "information" not in lower_query and "data" not in lower_query:
        # Add "user information" to the query if it doesn't already contain similar terms
        enriched_query = f"{query} user information"
        logger.info(f"Enriching query to: {enriched_query}")
        query = enriched_query
    
    result = client.search_graph(user_id, query, limit)
    
    # Log the result structure for debugging
    result_info = {}
    if isinstance(result, dict):
        if "edges" in result and result["edges"]:
            result_info["edges_count"] = len(result["edges"])
        else:
            result_info["edges_count"] = 0
            
        if "nodes" in result and result["nodes"]:
            result_info["nodes_count"] = len(result["nodes"])
        else:
            result_info["nodes_count"] = 0
            
        if "results" in result and result["results"]:
            result_info["results_count"] = len(result["results"])
        else:
            result_info["results_count"] = 0
            
        logger.info(f"🔍 Search results: {result_info}")
    
    # Final result string that Claude can understand
    json_result = json.dumps(result)
    return json_result

@mcp.tool()
def add_graph_data(user_id: str, data: Union[str, dict], data_type: str):
    """
    Add data to a user's graph in Zep Cloud.
    
    Args:
        user_id: The unique identifier for the user
        data: The data to add to the graph (string or JSON object)
        data_type: The type of data, can be "text", "json", or "message"
        
    Returns:
        A JSON object with information about the added data
    """
    global tool_count
    tool_count += 1
    logger.info(f"📝 Tool call {tool_count}: add_graph_data({user_id}, [data length: {len(str(data))}], {data_type})")
    
    # Handle case where data is a Python dict instead of a string (Claude sometimes does this)
    if not isinstance(data, str) and data_type == "json":
        try:
            # Convert to string if it's a dict
            logger.info(f"Converting Python dict to JSON string")
            data = json.dumps(data)
        except Exception as e:
            error_msg = f"Failed to convert Python dict to JSON string: {str(e)}"
            logger.error(f"❌ {error_msg}")
            result = {
                "error": error_msg,
                "success": False
            }
            return json.dumps(result)
    
    # Validate data type
    valid_types = ["text", "json", "message"]
    if data_type not in valid_types:
        error_msg = f"Invalid data type: {data_type}. Must be one of {valid_types}"
        logger.error(f"❌ {error_msg}")
        result = {
            "error": error_msg,
            "success": False
        }
        return json.dumps(result)
    
    # Special handling for JSON data to make it more robust
    if data_type == "json":
        try:
            # If it's already JSON, this will validate it
            json.loads(data)
            logger.info(f"✅ Valid JSON data format detected")
        except json.JSONDecodeError:
            logger.warning(f"⚠️ Invalid JSON format detected. Attempting to fix...")
            
            # Try to fix common issues with JSON that Claude might introduce
            try:
                # Remove extra quotes that Claude might add
                if data.startswith("'") and data.endswith("'"):
                    data = data[1:-1]
                    logger.info("Removed outer single quotes")
                elif data.startswith('"') and data.endswith('"') and len(data) > 2:
                    # Check if this might be a JSON string with extra quotes
                    try:
                        # Try to parse without the outer quotes
                        inner_data = data[1:-1]
                        # If inner_data starts with { or [, it's likely a JSON object with extra quotes
                        if inner_data.lstrip().startswith(('{', '[')):
                            json.loads(inner_data)
                            # If we get here, the inner content is valid JSON
                            data = inner_data
                            logger.info("Removed outer double quotes from JSON string")
                    except Exception:
                        # If that didn't work, continue with other fixes
                        pass
                
                # Handle multi-line formatted JSON that Claude might provide
                data = data.strip()
                
                # Try to parse as Python literal if it looks like a dict
                if data.startswith('{') and data.endswith('}'):
                    try:
                        import ast
                        parsed_data = ast.literal_eval(data)
                        data = json.dumps(parsed_data)
                        logger.info("Fixed JSON using ast.literal_eval")
                    except Exception as e:
                        logger.warning(f"Could not parse as Python literal: {str(e)}")
                
                # Final validation of the fixed JSON
                try:
                    json.loads(data)
                    logger.info("✅ Successfully fixed JSON format")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to fix JSON format: {str(e)}")
                    result = {
                        "error": f"Invalid JSON format: {str(e)}",
                        "success": False
                    }
                    return json.dumps(result)
            except Exception as e:
                logger.error(f"❌ Error trying to fix JSON format: {str(e)}")
                result = {
                    "error": f"Failed to process JSON data: {str(e)}",
                    "success": False
                }
                return json.dumps(result)
    
    # Call the client method
    try:
        result = client.add_graph_data(user_id, data, data_type)
        
        # Log summary based on result
        if isinstance(result, dict) and result.get("success"):
            uuid = result.get("response", {}).get("uuid", "unknown")
            logger.info(f"✅ Successfully added data to graph for user {user_id}, data type: {data_type}, UUID: {uuid}")
        else:
            error = result.get("error", "Unknown error") if isinstance(result, dict) else "Unknown error"
            logger.error(f"❌ Failed to add data to graph for user {user_id}: {error}")
        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"❌ Exception adding data to graph: {str(e)}")
        import traceback
        traceback.print_exc()
        result = {
            "error": str(e),
            "success": False
        }
        return json.dumps(result)

# === Main Entry Point ===

if __name__ == "__main__":
    # Log successful startup
    logger.info("🚀 Starting Zep Cloud MCP Server")
    logger.info(f"📡 Connection Status: {'✅ Connected' if not fallback_mode else '⚠️ Fallback Mode'}")
    
    # Start the server
    mcp.run()
