#!/bin/bash
# Script to run the Zep Cloud MCP Server

# Navigate to the repository root directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r config/requirements.txt
else
    # Activate virtual environment
    source venv/bin/activate
fi

# Get the Python path from the virtual environment
PYTHON_PATH="$(which python)"
echo "Using Python at: $PYTHON_PATH"

# Check dependencies
echo "Checking dependencies..."
pip install -r config/requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating example .env file..."
    if [ -f "config/.env.example" ]; then
        cp config/.env.example .env
        echo "Created .env from example file. Please edit it to add your Zep API Key."
    else
        echo "ZEP_API_KEY=" > .env
        echo "Created empty .env file. Please edit it to add your Zep API Key."
    fi
fi

# Run the server
echo "Starting Zep Cloud MCP Server..."

# Run the server in development mode using the file from the core directory
fastmcp dev core/zep_cloud_server.py 