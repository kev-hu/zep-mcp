# CLAUDE.md

## Project Overview

MCP server for the Zep Cloud API — a context engineering platform for AI agent memory.
Built with FastMCP and the zep-cloud Python SDK.

## Run the server

    source venv/bin/activate
    python server.py

Or with FastMCP dev mode:

    fastmcp dev server.py

## Configuration

- `ZEP_API_KEY` (required) — Zep Cloud API key, set in `.env`
- `ZEP_TOOLSETS` (optional) — comma-separated list of tool groups to enable.
  Values: `memory`, `admin`. Defaults to `memory,admin` (all tools).

## Architecture

13 tools organized by jobs-to-be-done, not API structure:

**Memory tools** (tag: `memory`):
  add_messages, get_context, add_graph_data, search_graph, get_task

**Admin tools** (tag: `admin`):
  manage_user, manage_user_instructions, manage_thread, manage_graph,
  manage_graph_structure, manage_graph_data, manage_context_templates, project_info

## Adding a new tool

1. Pick the right file in `tools/` (or create a new one for a new domain)
2. Define the function following the existing pattern:
   - Use `Literal` types for action/scope params
   - Return plain dicts (no json.dumps)
   - No try/except — let exceptions propagate
   - Add `annotations` (readOnlyHint, destructiveHint)
   - Add the appropriate tag ("memory" or "admin")
3. Register it in the module's `register(mcp, zep)` function
4. Add tests in the matching `tests/test_*.py` file

## Running tests

    source venv/bin/activate
    python -m pytest tests/

## Key conventions

- Zep Cloud API base URL: https://api.getzep.com/api/v2
- API key loaded from ZEP_API_KEY in .env via python-dotenv
- Server runs via mcp.run() (stdio transport for Claude Desktop)
- Tools accepting user_id/graph_id enforce mutual exclusivity via _require_one_of()
