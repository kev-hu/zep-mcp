# MCP Server Rewrite — Design Spec

## Problem

The current MCP server was built as a learning project. It has duplicated client implementations, a misleading fallback mode, silent query mutation, manual JSON serialization, and covers only a fraction of the Zep Cloud API. It needs a full rewrite to modern FastMCP standards with complete API coverage.

## Prerequisites

- **Upgrade `zep-cloud` to v3.x** (`>=3.2.0`). The installed venv has v2.9.0 which uses a completely different API surface (`memory`/`session`/`group` → `thread`/`graph`). Rebuild the venv from the new `requirements.txt`.
- **Upgrade `fastmcp` to v2.x** (`>=2.11.2`). The installed venv has v0.4.1 which does not support tags, annotations, or structured output. Verify tag/annotation APIs against actual FastMCP 2.x docs before implementation.

## Decisions Made

- **Full rewrite** — no backward compatibility constraints
- **Remove fallback mode** — if the API is unreachable, tools fail with real errors
- **Remove the fallback HTTP client** — `zep-cloud` SDK is a hard dependency
- **Remove query enrichment** — no silent mutation of search queries
- **Remove interview coach code** — delete `core/interview_coach_*.py` and `docs/` design docs
- **Remove `zep_api_request` passthrough** — all operations have dedicated typed tools instead
- **Jobs-to-be-done tool design** — 13 typed tools covering the entire Zep API, not 1:1 endpoint mapping
- **Two-server split via tag gating** — `memory` (5 tools) and `admin` (8 tools), controlled by `ZEP_TOOLSETS` env var

---

## Tool Inventory (13 tools)

### Memory tools (tag: `memory`)

| Tool | Scope / Actions | Zep Endpoints | Annotations |
|---|---|---|---|
| `add_messages` | single (list of messages) | `thread.add_messages` | |
| `get_context` | optional `template_id` | `thread.get_user_context` | `readOnlyHint` |
| `add_graph_data` | type: text / json / message / triple | `graph.add` (text/json/message) or `graph.add_fact_triple` (triple) — see routing note below | |
| `search_graph` | scope: edges / nodes; filters, reranker | `graph.search` | `readOnlyHint` |
| `get_task` | poll by task_id | Verify exact SDK method name during implementation | `readOnlyHint` |

### Admin tools (tag: `admin`)

| Tool | Actions | Zep Endpoints | Annotations |
|---|---|---|---|
| `manage_user` | create / get / update / delete / list / warm | `user.add`, `.get`, `.update`, `.delete`, `.list_ordered`, `.warm` | `destructiveHint` on delete |
| `manage_user_instructions` | list / add / delete | `user.*_user_summary_instructions` | `destructiveHint` on delete |
| `manage_thread` | create / get / delete / list | `thread.create`, `.get`, `.delete`; listing via `user.get_threads` (requires `user_id`) | `destructiveHint` on delete |
| `manage_graph` | create / get / update / delete / list / clone | `graph.create`, `.get`, `.update`, `.delete`, `.list_all`, `.clone` — verify `clone` SDK method exists | `destructiveHint` on delete |
| `manage_graph_structure` | set_ontology / list_ontology / add_instructions / list_instructions / delete_instructions / detect_patterns | Verify exact SDK v3 method names during implementation (docs show REST endpoints, Python SDK names may differ) | |
| `manage_graph_data` | scope: node / edge / episode; action: get / update / delete / list / get_edges / get_episodes / get_mentions | Node/edge/episode CRUD + traversal endpoints | `destructiveHint` on delete |
| `manage_context_templates` | create / get / update / list / delete | `context.*_context_template` | `destructiveHint` on delete |
| `project_info` | — | `project.get` | `readOnlyHint` |

---

## Implementation Patterns

### Tool shape

Every tool follows this pattern:

```python
@mcp.tool(tags={"memory"}, annotations={"readOnlyHint": True})
def search_graph(
    query: str,
    user_id: str | None = None,
    graph_id: str | None = None,
    scope: Literal["edges", "nodes"] = "edges",
    limit: int = 10,
) -> dict:
    """Search a knowledge graph for relevant facts or entities.
    Keep queries concise and specific for best results."""
    _require_one_of(user_id=user_id, graph_id=graph_id)
    return zep.graph.search(
        user_id=user_id,
        graph_id=graph_id,
        query=query,
        scope=scope,
        limit=limit,
    )
```

Rules:
- Return plain Python objects (dicts, lists, SDK model instances). No `json.dumps()`. FastMCP handles serialization into both TextContent and StructuredContent. Return type annotations should use the actual SDK types where possible (e.g. `-> GraphSearchResults`), not `-> dict`. Verify during implementation that FastMCP 2.x can serialize Pydantic model instances from the SDK.
- Use `Literal` types for action/scope/type params. Claude sees the allowed values in the schema.
- No try/except in tool functions. Let SDK exceptions bubble up. FastMCP converts them to MCP tool errors automatically.
- Tool annotations (`readOnlyHint`, `destructiveHint`) on every tool.
- Tool docstrings are concise and action-oriented — they're what Claude reads to decide which tool to use.

### `add_graph_data` routing note

The `type` param routes to different SDK methods:
- `text`, `json`, `message` → `graph.add(user_id=..., type=type, data=data)`
- `triple` → `graph.add_fact_triple(...)` — this is a separate SDK method with different required params (`fact`, `fact_name`, `target_node_name`). The tool must accept these as optional params and validate they're present when `type="triple"`.

```python
@mcp.tool(tags={"memory"})
def add_graph_data(
    type: Literal["text", "json", "message", "triple"],
    data: str | None = None,
    user_id: str | None = None,
    graph_id: str | None = None,
    # Triple-specific params:
    fact: str | None = None,
    fact_name: str | None = None,
    target_node_name: str | None = None,
) -> dict:
    """Add data to a knowledge graph. Use type to specify the data format."""
    _require_one_of(user_id=user_id, graph_id=graph_id)
    if type == "triple":
        return zep.graph.add_fact_triple(
            user_id=user_id, graph_id=graph_id,
            fact=fact, fact_name=fact_name, target_node_name=target_node_name,
        )
    return zep.graph.add(
        user_id=user_id, graph_id=graph_id, type=type, data=data,
    )
```

### Mutual exclusivity validation

For tools accepting `user_id` or `graph_id`:

```python
def _require_one_of(**kwargs):
    """Validate that exactly one of the provided kwargs is set."""
    provided = {k: v for k, v in kwargs.items() if v is not None}
    if len(provided) == 0:
        names = " or ".join(kwargs.keys())
        raise ValueError(f"Either {names} is required")
    if len(provided) > 1:
        names = " and ".join(provided.keys())
        raise ValueError(f"Provide only one of: {names}")
```

This lives in `server.py` (or a small `utils.py`) and is imported by tool modules.

### Action-based tools

For tools with an `action` param (e.g. `manage_user`):

```python
@mcp.tool(tags={"admin"})
def manage_user(
    action: Literal["create", "get", "update", "delete", "list", "warm"],
    user_id: str | None = None,
    email: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    metadata: dict | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
) -> dict:
    """Manage users in Zep Cloud. Use action to specify the operation."""
    match action:
        case "create":
            return zep.user.add(user_id=user_id, email=email, ...)
        case "get":
            return zep.user.get(user_id=user_id)
        case "list":
            return zep.user.list_ordered(page_number=page_number, ...)
        # ... etc
```

Not every param is relevant to every action. The docstring and `Literal` type guide Claude. Invalid combinations (e.g. `action="create"` without `user_id`) are caught by the SDK.

---

## Error Handling

- **No fallback mode.** If `ZEP_API_KEY` is unset, `server.py` raises on startup with a clear message.
- **No silent error swallowing.** SDK exceptions propagate as MCP tool errors.
- **Validation at tool boundary only.** Mutual exclusivity checks (`user_id` vs `graph_id`), required param checks for actions. Everything else is the SDK's job.

---

## Configuration

```
.env:
  ZEP_API_KEY=zep_...               # required — server won't start without it
  ZEP_TOOLSETS=memory,admin          # optional — defaults to all tools
```

`ZEP_TOOLSETS` controls which tool modules are registered at startup via `register_all()`. This is conditional registration (tools not in the selected toolsets are never registered), not post-registration filtering. This approach works regardless of whether FastMCP supports native tag filtering. Tags are still applied to tools as metadata for client introspection.

---

## File Structure

```
mcp-server-zep-cloud/
├── server.py                  # ~30 lines: Zep client init, tag gating, register_all()
├── tools/
│   ├── __init__.py            # exports register_all(mcp, zep, toolsets)
│   ├── memory.py              # add_messages, get_context, add_graph_data, search_graph, get_task
│   ├── users.py               # manage_user, manage_user_instructions
│   ├── threads.py             # manage_thread
│   ├── graphs.py              # manage_graph, manage_graph_structure, manage_graph_data
│   └── context.py             # manage_context_templates, project_info
├── requirements.txt           # zep-cloud, fastmcp, python-dotenv (minimal)
├── .env.example               # template with ZEP_API_KEY and ZEP_TOOLSETS
├── tests/
│   ├── test_memory.py
│   ├── test_users.py
│   ├── test_threads.py
│   ├── test_graphs.py
│   └── test_context.py
├── .env                       # gitignored
├── .gitignore
└── CLAUDE.md
```

### `tools/__init__.py`

```python
from tools.memory import register as register_memory
from tools.users import register as register_users
from tools.threads import register as register_threads
from tools.graphs import register as register_graphs
from tools.context import register as register_context

def register_all(mcp, zep, toolsets):
    """Register tool modules based on enabled toolsets."""
    registrars = {
        "memory": register_memory,
        "admin": [register_users, register_threads, register_graphs, register_context],
    }
    for toolset in toolsets:
        handlers = registrars.get(toolset, [])
        if callable(handlers):
            handlers = [handlers]
        for register_fn in handlers:
            register_fn(mcp, zep)
```

Each tool module exports a `register(mcp, zep)` function that decorates and registers its tools against the FastMCP instance with the Zep client available via closure.

### `server.py`

```python
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from zep_cloud.client import Zep
from tools import register_all

load_dotenv()

api_key = os.environ.get("ZEP_API_KEY")
if not api_key:
    raise RuntimeError("ZEP_API_KEY environment variable is required")

zep = Zep(api_key=api_key)
mcp = FastMCP(name="zep-cloud")

toolsets = os.environ.get("ZEP_TOOLSETS", "memory,admin").split(",")
toolsets = [t.strip() for t in toolsets]
register_all(mcp, zep, toolsets)

if __name__ == "__main__":
    mcp.run()
```

---

## CLAUDE.md Content

```markdown
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
```

---

## What Gets Deleted

- `core/zep_cloud_client.py` — replaced by direct SDK calls in tools
- `core/zep_cloud_server.py` — replaced by `server.py` + `tools/`
- `core/run_server.py` — replaced by `server.py`
- `core/interview_coach_client.py` — removed (decision: not pursuing)
- `core/interview_coach_server.py` — removed (decision: not pursuing)
- `docs/interview-coach-*.md` — removed (6 files)
- `scripts/` — removed entirely (wrapper scripts, test scripts)
- `tests/` — removed and replaced with new test files
- `config/` — removed; `requirements.txt` and `.env.example` move to repo root
- `HANDOFF.md` — incorporated into this spec, can be removed

---

## Requirements (minimal)

```
fastmcp>=2.11.2
zep-cloud>=3.2.0
python-dotenv>=1.1.1
```

No `requests`, `httpx`, `pydantic`, `rich`, `click`, `jsonschema`, or other dependencies from the original `requirements.txt`. The SDK handles HTTP internally. FastMCP handles validation and serialization.

---

## Testing Strategy

- Tests use pytest
- Tests require a live `ZEP_API_KEY` in `.env` (integration tests against real API)
- Each test file mirrors a tool module: `test_memory.py`, `test_users.py`, etc.
- Tests validate: correct return types, error propagation, mutual exclusivity checks, action routing
- Future: add mock/unit tests for `_require_one_of` and `register_all` logic (no API needed)

---

## SDK Method Verification Checklist

The Zep docs show multi-language examples and REST endpoints. The Python SDK method names may differ. The following must be verified against the actual installed `zep-cloud>=3.2.0` Python package before implementation:

- [ ] `graph.clone()` — exists as SDK method or requires raw API call?
- [ ] `graph.set_ontology()` / `graph.list_ontology()` — actual method names in Python SDK?
- [ ] `graph.custom_instructions.*` — actual method names?
- [ ] `graph.detect_patterns()` — actual method name and params?
- [ ] `graph.add_fact_triple()` — actual method name and required params?
- [ ] `thread.list_all()` — exists, or is thread listing only via `user.get_threads()`?
- [ ] `task.get()` — actual SDK client path for task polling?
- [ ] `graph_id` vs `group_id` — which parameter name does SDK v3 use? If `graph_id`, great. If `group_id`, tool params should use `graph_id` and map internally.
- [ ] `thread.add_messages_batch()` — separate method or same as `add_messages` with a list?
- [ ] FastMCP 2.x `tags` and `annotations` API — verify syntax and behavior

Resolve each item by reading the installed SDK source after upgrading. Update tool implementations accordingly.
