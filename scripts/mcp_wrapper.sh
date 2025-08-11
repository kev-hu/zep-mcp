#!/bin/bash
# Zep Cloud MCP Server Wrapper Script
# This script provides a portable way to run the Zep Cloud MCP Server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if virtual environment exists and activate it
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_DIR/venv/bin/activate"
elif [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    echo "Activating virtual environment (.venv)..."
    source "$PROJECT_DIR/.venv/bin/activate"
else
    echo "Warning: No virtual environment found. Using system Python."
fi

# Change to project directory to ensure relative imports work
cd "$PROJECT_DIR"

# Run the MCP server
exec python "$PROJECT_DIR/core/zep_cloud_server.py" "$@"
