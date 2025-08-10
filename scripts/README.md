# MCP Server Wrapper Scripts

This directory contains cross-platform wrapper scripts to run the Zep Cloud MCP Server.

## Available Scripts

### Unix/Linux/macOS: `mcp_wrapper.sh`
```bash
# Make executable
chmod +x scripts/mcp_wrapper.sh

# Run the MCP server
./scripts/mcp_wrapper.sh
```

### Windows: `mcp_wrapper.bat`
```cmd
# Run the MCP server
scripts\mcp_wrapper.bat
```

## Features

- **Cross-platform compatibility**: Works on Windows, macOS, and Linux
- **Automatic virtual environment detection**: Looks for `venv/` or `.venv/` directories
- **Relative path resolution**: No hardcoded paths, works from any location
- **Proper working directory**: Changes to project root for correct imports
- **Error handling**: Graceful fallback to system Python if venv not found

## How It Works

1. **Path Resolution**: Scripts automatically detect their location and find the project root
2. **Virtual Environment**: Automatically activates Python virtual environment if found
3. **Working Directory**: Changes to project root to ensure imports work correctly
4. **Execution**: Runs the MCP server with all passed arguments

## Usage in Claude Desktop Config

### macOS/Linux
```json
{
  "mcpServers": {
    "zep-cloud": {
      "command": "/full/path/to/mcp-server-zep-cloud/scripts/mcp_wrapper.sh",
      "env": {
        "ZEP_API_KEY": "your-zep-api-key"
      }
    }
  }
}
```

### Windows
```json
{
  "mcpServers": {
    "zep-cloud": {
      "command": "C:\\full\\path\\to\\mcp-server-zep-cloud\\scripts\\mcp_wrapper.bat",
      "env": {
        "ZEP_API_KEY": "your-zep-api-key"
      }
    }
  }
}
```

## Troubleshooting

- Ensure the scripts have execute permissions on Unix systems
- Make sure Python and required dependencies are installed:
  ```bash
  pip install -r config/requirements.txt
  ```
- Check that the ZEP_API_KEY environment variable is set in `.env` file
- Verify the virtual environment exists (run `python -m venv venv` if needed)
- Copy `.env.example` to `.env` and configure your ZEP_API_KEY
