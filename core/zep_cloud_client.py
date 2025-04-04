#!/usr/bin/env python3
"""
Zep Cloud Client
This module provides a client for interacting with the Zep Cloud API
using the official Zep Cloud SDK.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
import json
import requests

from dotenv import load_dotenv

# Import the Zep Cloud SDK
try:
    from zep_cloud.client import Zep
    from zep_cloud import User
except ImportError:
    raise ImportError(
        "zep-cloud SDK not found. Install with: pip install zep-cloud"
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ZepCloudClient:
    """Client for interacting with the Zep Cloud API"""
    
    def __init__(self):
        """Initialize the Zep Cloud client"""
        self.api_key = os.getenv("ZEP_API_KEY")
        
        if not self.api_key:
            raise ValueError("ZEP_API_KEY environment variable not set")
        
        # Initialize the client
        try:
            self.client = Zep(api_key=self.api_key)
            logger.info("Zep Cloud client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Zep Cloud client: {str(e)}")
            raise
        
    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users
        
        Returns:
            List[Dict[str, Any]]: List of user objects
        """
        try:
            user_response = self.client.user.list_ordered()
            users = user_response.users or []
            
            # Convert User objects to dictionaries
            user_dicts = []
            for user in users:
                user_dict = {
                    "user_id": user.user_id,
                    "metadata": user.metadata if user.metadata else {}
                }
                user_dicts.append(user_dict)
                
            return user_dicts
            
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return []
            
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID
        
        Args:
            user_id (str): The user ID
            
        Returns:
            Optional[Dict[str, Any]]: User object if found, None otherwise
        """
        try:
            user = self.client.user.get(user_id=user_id)
            
            if user:
                return {
                    "user_id": user.user_id,
                    "metadata": user.metadata if user.metadata else {},
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
            
    def create_user(self, user_id: str, metadata: Optional[Dict[str, Any]] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new user
        
        Args:
            user_id (str): The user ID
            metadata (Optional[Dict[str, Any]]): User metadata
            first_name (Optional[str]): User's first name
            last_name (Optional[str]): User's last name
            email (Optional[str]): User's email address
            
        Returns:
            Optional[Dict[str, Any]]: Created user object if successful, None otherwise
        """
        try:
            # Ensure metadata is not None
            metadata_dict = metadata if metadata is not None else {}
            
            # Create the user
            user = self.client.user.add(
                user_id=user_id,
                metadata=metadata_dict,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            
            return {
                "user_id": user.user_id,
                "metadata": user.metadata if user.metadata else {},
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
            
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {str(e)}")
            return None
            
    def update_user(self, user_id: str, metadata: Optional[Dict[str, Any]] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a user's metadata and profile information
        
        Args:
            user_id (str): The user ID
            metadata (Optional[Dict[str, Any]]): User metadata
            first_name (Optional[str]): User's first name
            last_name (Optional[str]): User's last name 
            email (Optional[str]): User's email address
            
        Returns:
            Optional[Dict[str, Any]]: Updated user object if successful, None otherwise
        """
        try:
            # Ensure metadata is not None
            metadata_dict = metadata if metadata is not None else {}
            
            # Update the user
            user = self.client.user.update(
                user_id=user_id,
                metadata=metadata_dict,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            
            return {
                "user_id": user.user_id,
                "metadata": user.metadata if user.metadata else {},
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return None
            
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user
        
        Args:
            user_id (str): The user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.user.delete(user_id=user_id)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            return False
            
    def search_graph(self, user_id: str, query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Search the user's graph with a query
        
        Args:
            user_id (str): The user ID
            query (str): The search query
            limit (int): The maximum number of results to return
            
        Returns:
            Optional[Dict[str, Any]]: Search results if successful, None otherwise
        """
        try:
            # Keep queries concise as recommended by docs
            if len(query) > 8000:
                logger.warning(f"Search query exceeds recommended length. Truncating to 8000 characters.")
                query = query[:8000]
                
            # Call the graph search API
            search_results = self.client.graph.search(
                user_id=user_id,
                query=query,
                limit=limit
            )
            
            # Create a digestible result that can be serialized to JSON
            results = {
                "query": query,
                "user_id": user_id,
                "limit": limit,
                "success": True,
                "results": []  # Keep generic results array for backward compatibility
            }
            
            # Add edges (facts) if they exist
            if hasattr(search_results, 'edges') and search_results.edges:
                results["edges"] = []
                for edge in search_results.edges:
                    edge_data = {
                        "id": edge.id if hasattr(edge, 'id') else None,
                        "fact": edge.fact if hasattr(edge, 'fact') else None,
                        "created_at": str(edge.created_at) if hasattr(edge, 'created_at') else None,
                        "updated_at": str(edge.updated_at) if hasattr(edge, 'updated_at') else None,
                        "score": edge.score if hasattr(edge, 'score') else None
                    }
                    results["edges"].append(edge_data)
                    # Also add to generic results for backward compatibility
                    results["results"].append(edge_data)
            
            # Add nodes if they exist
            if hasattr(search_results, 'nodes') and search_results.nodes:
                results["nodes"] = []
                for node in search_results.nodes:
                    node_data = {
                        "id": node.id if hasattr(node, 'id') else None,
                        "label": node.label if hasattr(node, 'label') else None,
                        "attributes": node.attributes if hasattr(node, 'attributes') else {},
                        "score": node.score if hasattr(node, 'score') else None
                    }
                    results["nodes"].append(node_data)
                    # Also add to generic results for backward compatibility
                    results["results"].append(node_data)
            
            # Add a summary field to help Claude understand the results
            if len(results["results"]) > 0:
                results["summary"] = f"Found {len(results['results'])} results for query '{query}'"
                if "nodes" in results and len(results["nodes"]) > 0:
                    results["summary"] += f", including {len(results['nodes'])} nodes"
                if "edges" in results and len(results["edges"]) > 0:
                    results["summary"] += f", including {len(results['edges'])} edges/facts"
            else:
                results["summary"] = f"No results found for query '{query}'"
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching graph for user {user_id}: {str(e)}")
            return None
            
    def add_graph_data(self, user_id, data, data_type="text"):
        """
        Add data to a user's graph in Zep Cloud.
        
        Args:
            user_id: The unique identifier for the user
            data: The data to add to the graph (string or dict)
            data_type: The type of data, can be "text", "json", or "message"
            
        Returns:
            A dictionary with information about the added data
        """
        if not user_id:
            return {"error": "User ID is required", "success": False}
        
        if data is None:
            return {"error": "Data is required", "success": False}
        
        valid_types = ["text", "json", "message"]
        if data_type not in valid_types:
            return {
                "error": f"Invalid data type: {data_type}. Must be one of {valid_types}",
                "success": False
            }
        
        # Convert dict to JSON string if needed
        if data_type == "json" and isinstance(data, dict):
            try:
                data = json.dumps(data)
                logging.info(f"Converted Python dict to JSON string: {type(data)}")
            except Exception as e:
                return {
                    "error": f"Error converting dict to JSON: {str(e)}",
                    "success": False
                }
        
        # Check data size limits (after possible conversion)
        data_len = len(data) if isinstance(data, str) else len(str(data))
        if data_len > 100000:  # 100KB limit
            return {
                "error": f"Data size of {data_len} bytes exceeds 100KB limit",
                "success": False
            }
        
        # Additional validation for JSON data
        if data_type == "json":
            try:
                # Verify it's valid JSON
                if isinstance(data, str):
                    try:
                        json_data = json.loads(data)
                    except json.JSONDecodeError as e:
                        # Check for JSON with extra quotes
                        if data.startswith('"') and data.endswith('"') and len(data) > 2:
                            try:
                                # Try to parse the inner content without outer quotes
                                inner_data = data[1:-1]
                                if inner_data.lstrip().startswith(('{', '[')):
                                    json_data = json.loads(inner_data)
                                    data = inner_data
                                    logging.info(f"Fixed JSON by removing outer quotes: {type(json_data)}")
                                else:
                                    raise e
                            except Exception:
                                # If that didn't work, re-raise the original error
                                raise e
                        else:
                            raise e
                else:
                    # If already a dict or other Python object, convert to JSON string
                    json_data = data
                    data = json.dumps(data)
                
                # If we get here, data is valid JSON
                logging.info(f"Validated JSON data: {type(json_data)}")
            except json.JSONDecodeError as e:
                return {
                    "error": f"Invalid JSON data: {str(e)}",
                    "success": False
                }
            except Exception as e:
                return {
                    "error": f"Error processing JSON data: {str(e)}",
                    "success": False
                }
        
        # Use the Zep SDK to add the data to the graph
        try:
            # Call the graph add API
            response = self.client.graph.add(
                user_id=user_id,
                type=data_type,
                data=data
            )
            
            # Create a return value that can be serialized to JSON
            result = {
                "success": True,
                "user_id": user_id,
                "data_type": data_type,
                "data_length": len(data),
                "response": {
                    "uuid": response.uuid if hasattr(response, 'uuid') else None,
                    "content": response.content if hasattr(response, 'content') else None,
                    "created_at": str(response.created_at) if hasattr(response, 'created_at') else None,
                    "processed": response.processed if hasattr(response, 'processed') else None
                }
            }
            
            return result
            
        except Exception as e:
            error_message = f"Exception adding graph data: {str(e)}"
            logging.error(error_message)
            return {
                "error": error_message,
                "success": False
            } 