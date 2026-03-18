# mcp-server-zep-cloud

MCP server for the [Zep Cloud](https://www.getzep.com/) API — a context engineering platform for AI agent memory. Built with [FastMCP](https://github.com/jlowin/fastmcp) and the [zep-cloud](https://pypi.org/project/zep-cloud/) Python SDK.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your Zep Cloud API key:

```bash
cp .env.example .env
```

## Run the server

```bash
source venv/bin/activate
python server.py
```

Or with FastMCP dev mode:

```bash
fastmcp dev server.py
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `ZEP_API_KEY` | Yes | Zep Cloud API key |
| `ZEP_TOOLSETS` | No | Comma-separated tool groups to enable. Values: `memory`, `admin`. Defaults to `memory,admin` (all tools). |

## Tools

13 tools organized by jobs-to-be-done:

**Memory tools** (`memory`):
- `add_messages` — Add messages to a conversation thread
- `get_context` — Get assembled context block for a user
- `add_graph_data` — Add data to a knowledge graph (text, JSON, message, or triple)
- `search_graph` — Search a knowledge graph for facts, entities, or episodes
- `get_task` — Poll status of an async Zep operation

**Admin tools** (`admin`):
- `manage_user` — User CRUD (create, get, update, delete, list, warm)
- `manage_user_instructions` — Manage user summary instructions
- `manage_thread` — Thread CRUD (create, get, delete, list)
- `manage_graph` — Graph lifecycle (create, get, update, delete, list, clone)
- `manage_graph_structure` — Graph schema, ontology, and custom instructions
- `manage_graph_data` — Node, edge, and episode inspection and management
- `manage_context_templates` — Context template CRUD
- `project_info` — Get current Zep Cloud project info

## Running tests

```bash
source venv/bin/activate
python -m pytest tests/
```

## License

MIT
