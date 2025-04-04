# Setup Guide for Claude Desktop Integration

This guide will help you fix the "spawn python ENOENT" error and properly configure your Claude Desktop to work with the Zep Cloud MCP server.

## Fix for "spawn python ENOENT" Error

The "spawn python ENOENT" error occurs when Claude Desktop cannot find the Python executable. Follow these steps to fix it:

### Step 1: Find the full path to your Python executable

**On macOS/Linux:**
```bash
which python3
```
This will return something like `/usr/local/bin/python3` or `/usr/bin/python3`

**On Windows:**
```cmd
where python
```
This will return something like `C:\Python39\python.exe`

### Step 2: Find the full path to your server script

**On macOS/Linux:**
```bash
pwd
```
When run from the server directory, this will give you the current directory path.

**On Windows:**
```cmd
cd
```
This will show your current directory.

### Step 3: Set up the Claude Desktop configuration

1. Locate or create your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%AppData%\Claude\claude_desktop_config.json`

2. Edit the file to use the full paths you found:

```json
{
    "mcpServers": {
        "zep-cloud": {
            "command": "/YOUR/PYTHON/PATH/FROM/STEP1",
            "args": [
                "/YOUR/SERVER/PATH/FROM/STEP2/zep_cloud_server.py"
            ]
        }
    }
}
```

3. Replace:
   - `/YOUR/PYTHON/PATH/FROM/STEP1` with the Python path you found in Step 1
   - `/YOUR/SERVER/PATH/FROM/STEP2` with the server directory path you found in Step 2

### Step 4: Restart Claude Desktop

After saving the configuration file, completely restart Claude Desktop.

## Example Configurations

### macOS Example
```json
{
    "mcpServers": {
        "zep-cloud": {
            "command": "/usr/local/bin/python3",
            "args": [
                "/Users/username/projects/mcp-zep-cloud-server/zep_cloud_server.py"
            ]
        }
    }
}
```

### Windows Example
```json
{
    "mcpServers": {
        "zep-cloud": {
            "command": "C:\\Python39\\python.exe",
            "args": [
                "C:\\Users\\username\\projects\\mcp-zep-cloud-server\\zep_cloud_server.py"
            ]
        }
    }
}
```

## Verify Setup

1. Make sure your `.env` file is properly set up with your Zep API Key
2. Run the test script to verify Zep Cloud connectivity:
   ```
   ./run_server.sh
   ```
   or on Windows:
   ```
   run_server.bat
   ```
3. Look for the tools in Claude Desktop (hammer icon should appear)
4. Try using the tools with a simple command like "List all users in Zep Cloud"

## Still Having Issues?

Check the Claude Desktop logs for more detailed error messages. Common issues include:

1. Python path incorrect
2. Server script path incorrect 
3. Missing or invalid Zep API Key
4. Python dependencies not installed

If you continue to have problems, please refer to the troubleshooting section in the README or contact support. 

## Security Considerations

### Protecting Your API Keys

The MCP Server requires access to your Zep Cloud API key. Follow these security best practices:

1. **Store API keys in the .env file only**
   - Never hardcode API keys in your Python code
   - Never include API keys in the `claude_desktop_config.json` file
   - The `.env` file should be kept out of version control (it's in .gitignore)

2. **Before first commit**
   - Make sure the `.gitignore` file is committed FIRST
   - Run our security check script to verify your setup:
     ```bash
     # On macOS/Linux
     ./scripts/check_security.sh
     
     # On Windows
     scripts\check_security.bat
     ```

3. **API key rotation**
   - Periodically rotate your Zep Cloud API keys
   - Update your `.env` file after generating a new key

### Repository Safety

If you're planning to fork or extend this project, carefully review the [SECURITY.md](SECURITY.md) file for comprehensive security guidelines. This contains important information about:
- Protecting sensitive information
- Safe development practices
- What to do if credentials are accidentally exposed

Remember: Never share API keys or sensitive credentials with others. Each developer should use their own API keys in their local environment. 