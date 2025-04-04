# MCP Server for Zep Cloud

MCP Server for Zep Cloud provides a bridge between Claude Desktop and the Zep Cloud API, enabling memory management for AI assistants.

## Repository Structure

The repository has been organized into the following directories:

- **core/**: Core functionality files
  - `zep_cloud_client.py`: Client implementation for the Zep Cloud API
  - `zep_cloud_server.py`: MCP server providing tools for Claude Desktop
  - `run_server.py`: Standalone script to run the server directly

- **scripts/**: Utility scripts for operations
  - `check_user_exists.py`: Utility to check if a user exists in Zep Cloud
  - `create_specific_user.py`: Script to create a specific user in Zep Cloud
  - `run_server.sh` / `run_server.bat`: Shell scripts to run the server with proper environment setup
  - Various other utility scripts for testing and debugging

- **tests/**: Test scripts organized by functionality
  - `test_specific_user.py`: Comprehensive test for all user operations
  - `test_zep_cloud_client.py`: Unit tests for the Zep Cloud client
  - `test_comprehensive.py`: Complete API tests for all features

- **config/**: Configuration files
  - `.env.example`: Template for environment configuration
  - `.env.new`: Updated environment configuration
  - `claude_desktop_config.json.example`: Template for Claude Desktop configuration
  - `requirements.txt`: Package dependencies

## Features

- **User Management**: Create, retrieve, update, and delete users in Zep Cloud
- **Collections Management**: Create and manage memory collections
- **Memory Operations**: Add, retrieve, and search memories
- **Modern Implementation**: Uses the FastMCP approach for a more efficient and maintainable server
- **Fallback Mode**: Automatically runs in fallback mode if Zep Cloud API is not accessible

## Requirements

- Python 3.8+
- Zep Cloud API key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/mcp-server-zep-cloud.git
cd mcp-server-zep-cloud
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r config/requirements.txt
```

4. Copy the `config/.env.example` file to `.env` and add your Zep Cloud API key:
```bash
cp config/.env.example .env
```

Edit the `.env` file and add your Zep Cloud API key:
```
ZEP_API_KEY=your_api_key_here
```

## Usage

### Starting the Server

To start the server on macOS/Linux:
```bash
cd scripts
./run_server.sh
```

Or on Windows:
```bash
cd scripts
run_server.bat
```

The server will start on `http://127.0.0.1:8000` by default.

### Testing API Connectivity

To test if a user exists in Zep Cloud:
```bash
cd scripts
python check_user_exists.py [user_id]
```

To create a specific user in Zep Cloud:
```bash
cd scripts
python create_specific_user.py
```

### Fallback Mode

If the server cannot connect to the Zep Cloud API (due to authentication issues, network problems, or other reasons), it will automatically start in fallback mode. In this mode:

- All API operations will be simulated and will return success
- No actual data will be sent to or received from the Zep Cloud API
- Warning messages will be logged to indicate that the server is running in fallback mode
- The server will remain operational, allowing the Claude Desktop integration to function

To learn more about potential authentication issues and how to fix them, see the [AUTHENTICATION_NOTE.md](AUTHENTICATION_NOTE.md) file.

## Configuring Claude Desktop

1. Open your Claude Desktop configuration file at:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Update the configuration with the absolute paths to your Python executable and server script:
```json
{
  "mcpServers": {
    "zep-cloud": {
      "command": "/ABSOLUTE/PATH/TO/venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/core/zep_cloud_server.py"
      ]
    }
  }
}
```

**Important Notes**:
- Replace `/ABSOLUTE/PATH/TO/` with the actual path to your Python executable in the virtual environment and the server script.
- Use absolute paths, not relative paths.
- On Windows, use double backslashes in paths (e.g., `C:\\Users\\YourUsername\\...`).

## Available Tools in Claude Desktop

Once configured, Claude Desktop will have access to the following tools:

1. **User Management**:
   - `create_user`: Create a new user
   - `get_user`: Get details of a user
   - `update_user`: Update a user's metadata
   - `delete_user`: Delete a user
   - `list_users`: List all users

2. **Collections Management**:
   - `create_collection`: Create a new collection
   - `get_collection`: Get details of a collection
   - `update_collection`: Update a collection's metadata
   - `delete_collection`: Delete a collection
   - `list_collections`: List all collections

3. **Memory Operations**:
   - `add_memory`: Add a memory to a collection for a user
   - `get_memory`: Get a memory from a collection for a user
   - `list_memories`: List memories from a collection for a user
   - `search_memories`: Search memories from a collection for a user

4. **Connectivity**:
   - `check_connection`: Check connection status with the Zep Cloud API

## Troubleshooting

For troubleshooting information, please see the [AUTHENTICATION_NOTE.md](AUTHENTICATION_NOTE.md) document, which contains detailed information about API connectivity and authentication issues.

## Security Considerations

### API Key Protection
- **NEVER commit your API key to version control**. The `.gitignore` file is configured to prevent `.env` files from being committed.
- Use the provided `.env.example` as a template and create your own `.env` file with your actual API key.
- Regularly rotate your API keys, especially if you suspect they might have been compromised.

### Configuration Files
- Personal configuration files like `claude_desktop_config.json` contain system-specific paths and should not be committed to version control.
- Use the provided `claude_desktop_config.json.example` as a reference to create your own configuration.

### First-Time Setup for Contributing
1. Always ensure `.gitignore` is committed before adding any code or configuration files
2. Copy `.env.example` to `.env` and add your API key
3. Copy `claude_desktop_config.json.example` to `claude_desktop_config.json` and update with your paths
4. Verify that sensitive files are being ignored before committing:
   ```bash
   git status --ignored
   ```

### Security Checks
Before committing code, always check that you haven't accidentally included:
- API keys or credentials
- Personal file paths or usernames
- Log files that might contain sensitive information
- Temporary files with debug information