#!/usr/bin/env python3
"""
Comprehensive test script for Zep Cloud API authentication.
This script examines the API key format and tries multiple authentication methods.
"""

import os
import re
import sys
import json
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Zep API Key from environment variables
ZEP_API_KEY = os.getenv("ZEP_API_KEY")
if not ZEP_API_KEY:
    print("Error: ZEP_API_KEY not found in environment variables.")
    print("Please set it in the .env file before running this test.")
    sys.exit(1)

# Zep Cloud API base URL
ZEP_CLOUD_API_URL = "https://api.getzep.com/api/v2"

def examine_token_format():
    """Examine the token format and structure"""
    print(f"\n===== TOKEN EXAMINATION =====")
    print(f"API Key length: {len(ZEP_API_KEY)}")
    print(f"API Key prefix: {ZEP_API_KEY[:5]}...")
    print(f"API Key suffix: ...{ZEP_API_KEY[-5:]}")
    
    # Check if it starts with "z_"
    if ZEP_API_KEY.startswith("z_"):
        print("Token starts with 'z_' prefix.")
        base_token = ZEP_API_KEY[2:]
    else:
        print("Token does not start with 'z_' prefix.")
        base_token = ZEP_API_KEY
    
    # Check if it looks like a JWT (three dot-separated base64 sections)
    jwt_pattern = r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$'
    if re.match(jwt_pattern, base_token):
        print("Token appears to be in JWT format (header.payload.signature)")
        try:
            # Split the JWT into its components
            header, payload, signature = base_token.split('.')
            
            # Pad the base64 strings if necessary
            header_pad = header + '=' * (4 - len(header) % 4) if len(header) % 4 else header
            payload_pad = payload + '=' * (4 - len(payload) % 4) if len(payload) % 4 else payload
            
            # Decode header and payload
            header_json = base64.b64decode(header_pad.replace('-', '+').replace('_', '/')).decode('utf-8')
            payload_json = base64.b64decode(payload_pad.replace('-', '+').replace('_', '/')).decode('utf-8')
            
            print(f"JWT Header: {json.loads(header_json)}")
            print(f"JWT Payload: {json.loads(payload_json)}")
        except Exception as e:
            print(f"Error decoding JWT: {e}")
    else:
        print("Token does not appear to be in standard JWT format.")
    
    # Check if it could be basic auth (username:password in base64)
    try:
        decoded = base64.b64decode(base_token).decode('utf-8')
        if ':' in decoded:
            print("Token could be a base64-encoded Basic Auth credential (username:password).")
    except:
        pass

def test_auth_methods():
    """Test various authentication methods with the Zep Cloud API"""
    print(f"\n===== TESTING AUTHENTICATION METHODS =====")
    
    # Generate different authentication headers to try
    auth_methods = [
        {
            "name": "Standard Bearer token with full token",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ZEP_API_KEY}"
            }
        },
        {
            "name": "Bearer token without z_ prefix (if applicable)",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ZEP_API_KEY[2:]}" if ZEP_API_KEY.startswith("z_") else "N/A"
            }
        },
        {
            "name": "Bearer token with lowercase 'bearer'",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"bearer {ZEP_API_KEY}"
            }
        },
        {
            "name": "API Key as header without Bearer prefix",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": ZEP_API_KEY
            }
        },
        {
            "name": "Basic Auth with API key as username",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Basic {base64.b64encode(f'{ZEP_API_KEY}:'.encode()).decode()}"
            }
        },
        {
            "name": "Basic Auth with API key as password",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Basic {base64.b64encode(f':{ZEP_API_KEY}'.encode()).decode()}"
            }
        },
        {
            "name": "X-API-Key header",
            "headers": {
                "Content-Type": "application/json",
                "X-API-Key": ZEP_API_KEY
            }
        },
        {
            "name": "api_key query parameter",
            "headers": {
                "Content-Type": "application/json"
            },
            "params": {
                "api_key": ZEP_API_KEY
            }
        }
    ]
    
    # Remove N/A methods
    auth_methods = [method for method in auth_methods if method.get("headers", {}).get("Authorization", "") != "N/A"]
    
    # Endpoints to test against
    endpoints = [
        "/health",
        "/users",
        "",  # Root API endpoint
    ]
    
    success_found = False
    
    for endpoint in endpoints:
        url = f"{ZEP_CLOUD_API_URL}{endpoint}"
        print(f"\n----- Testing endpoint: {url} -----")
        
        for method in auth_methods:
            print(f"Trying {method['name']}...")
            try:
                params = method.get("params", {})
                response = requests.get(url, headers=method["headers"], params=params)
                
                print(f"Status code: {response.status_code}")
                print(f"Response: {response.text[:100]}..." if len(response.text) > 100 else f"Response: {response.text}")
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS! {method['name']} worked!")
                    success_found = True
                    print("\nRecommended authentication method:")
                    print(f"Method: {method['name']}")
                    print(f"Headers: {json.dumps(method['headers'], indent=2)}")
                    if params:
                        print(f"Parameters: {json.dumps(params, indent=2)}")
                    return True
                else:
                    print(f"❌ Failed with {method['name']}")
            except Exception as e:
                print(f"❌ Error with {method['name']}: {str(e)}")
    
    if not success_found:
        print("\n❌ All authentication methods failed.")
        print("Suggestions:")
        print("1. Verify your API key is correct")
        print("2. Check if your Zep Cloud subscription is active")
        print("3. Contact Zep Cloud support for assistance")
    
    return False

if __name__ == "__main__":
    print(f"🔑 Testing Zep Cloud API Connection")
    print(f"API URL: {ZEP_CLOUD_API_URL}")
    print(f"API Key: {ZEP_API_KEY[:5]}...{ZEP_API_KEY[-5:]} (length: {len(ZEP_API_KEY)})")
    
    examine_token_format()
    success = test_auth_methods()
    
    if success:
        print("\n✅ Successfully authenticated with Zep Cloud API!")
        print("You can now use the MCP server with Claude Desktop.")
    else:
        print("\n❌ Unable to authenticate with Zep Cloud API.")
        print("Please check the issues mentioned above and try again.") 