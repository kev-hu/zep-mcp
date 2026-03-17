# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server that bridges Claude Desktop and the Zep Cloud API for AI assistant memory management. Built with FastMCP and the Zep Cloud Python SDK.

## Commands

### Run the server (dev mode)
```bash
source venv/bin/activate
fastmcp dev core/zep_cloud_server.py
```

Or use the wrapper script:
```bash
scripts/run_server.sh
```

### Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

### Run tests
Tests require a live Zep Cloud API key in `.env`. They are integration tests that hit the real API.
```bash
source venv/bin/activate
cd core && python -m pytest ../tests/test_zep_cloud_client.py
cd core && python -m pytest ../tests/test_comprehensive.py
cd core && python -m pytest ../tests/test_specific_user.py
```

Tests in `scripts/` are standalone test scripts (not pytest), run directly:
```bash
cd core && python ../scripts/test_graph_search.py
```

Note: Tests import `zep_cloud_client` as a bare module name, so `core/` must be the working directory or on `sys.path`.

## Architecture

### Two-layer client design

- **`core/zep_cloud_client.py`** — The primary client. Uses the official `zep_cloud` SDK (`from zep_cloud.client import Zep`). Handles user CRUD, graph search, and graph data operations. Returns Python dicts/lists.

- **`core/zep_cloud_server.py`** — The MCP server. Uses `FastMCP` to expose tools to Claude Desktop. Tries to import `ZepCloudClient` from `zep_cloud_client.py`; if that fails, defines its own fallback `ZepCloudClient` using raw `requests` against `https://api.getzep.com/api/v2`. Tool functions are thin wrappers that call the client and return `json.dumps(result)`.

### Fallback mode

Both the SDK client and the raw-requests fallback client have a `fallback_mode` flag. When the API is unreachable or auth fails, operations return simulated success responses. This keeps Claude Desktop functional even without a live API connection.

### MCP tools exposed

User management: `create_user`, `get_user`, `update_user`, `delete_user`, `list_users`
Graph operations: `search_graph`, `add_graph_data`
Connectivity: `check_connection`

### Key conventions

- Zep Cloud API base URL: `https://api.getzep.com/api/v2`
- API key is loaded from `ZEP_API_KEY` in `.env` via `python-dotenv`
- The server entry point is `core/zep_cloud_server.py` — runs via `mcp.run()` (stdio transport for Claude Desktop)
- `core/run_server.py` is an alternative entry point that imports the server module dynamically
- Configuration templates live in `config/`; active `.env` lives at repo root
