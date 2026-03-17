# MCP Server Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the existing MCP server with a modern 13-tool FastMCP server covering the full Zep Cloud API.

**Architecture:** Single `server.py` entry point initializes the Zep SDK client and FastMCP instance, then delegates to `tools/` modules that each export a `register(mcp, zep)` function. Tools are grouped by domain (memory, users, threads, graphs, context) and gated by `ZEP_TOOLSETS` env var.

**Tech Stack:** Python 3.13, FastMCP >=2.11.2, zep-cloud >=3.2.0, python-dotenv, pytest

**Spec:** `docs/superpowers/specs/2026-03-17-mcp-server-rewrite-design.md`

---

## File Map

| File | Responsibility | Status |
|---|---|---|
| `server.py` | Entry point: env loading, Zep client init, FastMCP init, toolset gating | Create |
| `utils.py` | Shared validation helpers (`_require_one_of`) | Create |
| `tools/__init__.py` | `register_all(mcp, zep, toolsets)` dispatcher | Create |
| `tools/memory.py` | 5 tools: add_messages, get_context, add_graph_data, search_graph, get_task | Create |
| `tools/users.py` | 2 tools: manage_user, manage_user_instructions | Create |
| `tools/threads.py` | 1 tool: manage_thread | Create |
| `tools/graphs.py` | 3 tools: manage_graph, manage_graph_structure, manage_graph_data | Create |
| `tools/context.py` | 2 tools: manage_context_templates, project_info | Create |
| `requirements.txt` | Minimal deps: fastmcp, zep-cloud, python-dotenv | Create (root) |
| `.env.example` | Template with ZEP_API_KEY and ZEP_TOOLSETS | Create (root) |
| `CLAUDE.md` | Updated project instructions | Rewrite |
| `.gitignore` | Keep as-is, already covers .env and venv | Keep |
| `tests/test_utils.py` | Unit tests for `_require_one_of` and `register_all` | Create |
| `tests/test_memory.py` | Integration tests for memory tools | Create |
| `tests/test_users.py` | Integration tests for user tools | Create |
| `tests/test_threads.py` | Integration tests for thread tools | Create |
| `tests/test_graphs.py` | Integration tests for graph tools | Create |
| `tests/test_context.py` | Integration tests for context tools | Create |
| `core/` | Entire directory | Delete |
| `scripts/` | Entire directory | Delete |
| `config/` | Entire directory | Delete |
| `docs/interview-coach-*.md` | 6 files | Delete |
| `HANDOFF.md` | Incorporated into spec | Delete |
| `SECURITY.md` | Old doc | Delete |
| `SETUP_GUIDE.md` | Old doc, replaced by CLAUDE.md | Delete |
| `README.md` | Old readme | Delete |
| `claude_desktop_config.json.example` | Root copy | Delete |
| `claude_desktop_config.json` | Old config pointing to deleted paths | Delete |
| `.env.example` (root) | Old copy, will be recreated | Delete & recreate |
| `tests/*.py` (old) | Old test files | Delete |
| `tests/conftest.py` | Shared test fixtures (zep client, skip markers) | Create |

---

### Task 1: Clean slate — delete old code

**Files:**
- Delete: `core/` (entire directory)
- Delete: `scripts/` (entire directory)
- Delete: `config/` (entire directory)
- Delete: `tests/` (all old test files)
- Delete: `docs/interview-coach-*.md` (6 files)
- Delete: `HANDOFF.md`, `SECURITY.md`, `SETUP_GUIDE.md`, `README.md`
- Delete: `claude_desktop_config.json.example`, `.env.example` (root)

- [ ] **Step 1: Delete old directories and files**

```bash
rm -rf core/ scripts/ config/ tests/
rm -f HANDOFF.md SECURITY.md SETUP_GUIDE.md README.md
rm -f claude_desktop_config.json claude_desktop_config.json.example .env.example
rm -f docs/interview-coach-*.md
```

- [ ] **Step 2: Verify only docs/superpowers/ and dotfiles remain**

```bash
find . -maxdepth 2 -not -path './venv/*' -not -path './.git/*' -not -path './.claude/*' -not -path './.cursor/*' | sort
```

Expected: `.env`, `.gitignore`, `CLAUDE.md`, `docs/superpowers/` tree only.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: remove old server code, scripts, and docs

Full rewrite in progress. Deleting: core/, scripts/, config/,
old tests, interview coach docs, and obsolete root files."
```

---

### Task 2: New requirements and env template

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`

- [ ] **Step 1: Create requirements.txt**

```
fastmcp>=2.11.2
zep-cloud>=3.2.0
python-dotenv>=1.1.1
pytest>=8.0.0
```

- [ ] **Step 2: Create .env.example**

```
# Required — server won't start without it
ZEP_API_KEY=zep_your_api_key_here

# Optional — comma-separated list of tool groups to enable
# Values: memory, admin. Defaults to "memory,admin" (all tools).
# ZEP_TOOLSETS=memory,admin
```

- [ ] **Step 3: Rebuild venv with new dependencies**

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 4: Verify SDK versions**

```bash
source venv/bin/activate
python -c "import zep_cloud; print(zep_cloud.__version__)"
python -c "import fastmcp; print(fastmcp.__version__)"
```

Expected: zep-cloud >=3.2.0, fastmcp >=2.11.2. If either is wrong, check pip output for errors.

- [ ] **Step 5: Verify FastMCP tags and annotations API exists**

```bash
source venv/bin/activate
python -c "
from fastmcp import FastMCP
mcp = FastMCP()
try:
    @mcp.tool(tags={'test'}, annotations={'readOnlyHint': True})
    def test_tool(): pass
    print('tags and annotations: SUPPORTED')
except TypeError as e:
    print(f'tags/annotations NOT supported: {e}')
    print('Strip tags= and annotations= from all @mcp.tool() calls')
"
```

If tags/annotations aren't supported, remove them from all `@mcp.tool()` decorators in subsequent tasks. The toolset gating via `register_all()` still works regardless.

- [ ] **Step 5b: Verify UserInstruction import**

```bash
source venv/bin/activate
python -c "from zep_cloud import UserInstruction; print('UserInstruction: OK')"
python -c "from zep_cloud import CustomInstruction; print('CustomInstruction: OK')"
python -c "from zep_cloud import Message; print('Message: OK')"
```

If `UserInstruction` doesn't exist, check the SDK for the correct class name (may be `Instruction` or similar).

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example
git commit -m "chore: add new requirements and env template

Upgraded to zep-cloud>=3.2.0 (SDK v3) and fastmcp>=2.11.2.
Minimal deps: no requests, httpx, or other extras."
```

---

### Task 3: Server entry point, utils, and tool registration framework

**Files:**
- Create: `server.py`
- Create: `utils.py`
- Create: `tools/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_utils.py`

**Annotation decision:** MCP tool annotations are per-tool, not per-action. For action-based tools that include `delete`, set `annotations={"destructiveHint": True}` — better to over-warn than under-warn. Read-only tools get `annotations={"readOnlyHint": True}`. Write-only tools (like `add_messages`) get no annotations.

- [ ] **Step 1: Create `utils.py`** (avoids circular imports — tools import from here, not from server)

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

- [ ] **Step 2: Write failing test for `_require_one_of`**

Create `tests/test_utils.py`:

```python
import pytest
from utils import _require_one_of


def test_require_one_of_raises_when_none_provided():
    with pytest.raises(ValueError, match="user_id or graph_id"):
        _require_one_of(user_id=None, graph_id=None)


def test_require_one_of_raises_when_both_provided():
    with pytest.raises(ValueError, match="Provide only one"):
        _require_one_of(user_id="u1", graph_id="g1")


def test_require_one_of_passes_when_one_provided():
    _require_one_of(user_id="u1", graph_id=None)
    _require_one_of(user_id=None, graph_id="g1")
```

- [ ] **Step 3: Create `tests/conftest.py`** (shared fixtures for all test files)

```python
import os
import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def zep():
    """Create a Zep client. Skips test if ZEP_API_KEY not set."""
    api_key = os.environ.get("ZEP_API_KEY")
    if not api_key:
        pytest.skip("ZEP_API_KEY not set")
    from zep_cloud.client import Zep
    return Zep(api_key=api_key)


@pytest.fixture
def mcp():
    """Create a fresh FastMCP instance."""
    from fastmcp import FastMCP
    return FastMCP()


def get_tool_names(mcp):
    """Extract registered tool names from an MCP instance."""
    return [t.name for t in mcp._tool_manager.tools.values()]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
mkdir -p tests
source venv/bin/activate
python -m pytest tests/test_utils.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 5: Create `server.py`**

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

- [ ] **Step 6: Create `tools/__init__.py`** (empty registrars for now)

```python
def register_all(mcp, zep, toolsets):
    """Register tool modules based on enabled toolsets."""
    registrars = {
        "memory": [],
        "admin": [],
    }
    for toolset in toolsets:
        handlers = registrars.get(toolset, [])
        for register_fn in handlers:
            register_fn(mcp, zep)
```

- [ ] **Step 7: Commit**

```bash
git add server.py utils.py tools/__init__.py tests/conftest.py tests/test_utils.py
git commit -m "feat: add server entry point, utils, and test framework

_require_one_of in utils.py (avoids circular imports).
Shared test fixtures in conftest.py. Toolset gating framework
in place. No tools registered yet."
```

---

### Task 4: Memory tools — search_graph and get_task

Start with the simplest memory tools to validate the registration pattern works end-to-end.

**Files:**
- Create: `tools/memory.py`
- Modify: `tools/__init__.py`
- Create: `tests/test_memory.py`

- [ ] **Step 1: Write failing test for search_graph**

Create `tests/test_memory.py`:

```python
import pytest
from tests.conftest import get_tool_names


def test_search_graph_is_registered(mcp, zep):
    from tools.memory import register
    register(mcp, zep)
    assert "search_graph" in get_tool_names(mcp)


def test_get_task_is_registered(mcp, zep):
    from tools.memory import register
    register(mcp, zep)
    assert "get_task" in get_tool_names(mcp)


def test_search_graph_requires_user_or_graph_id():
    """Verify mutual exclusivity validation works."""
    from utils import _require_one_of
    with pytest.raises(ValueError, match="user_id or graph_id"):
        _require_one_of(user_id=None, graph_id=None)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
source venv/bin/activate
python -m pytest tests/test_memory.py -v
```

Expected: FAIL — `tools.memory` module doesn't exist.

- [ ] **Step 3: Create `tools/memory.py` with search_graph and get_task**

```python
from typing import Literal


def register(mcp, zep):
    """Register memory tools."""

    @mcp.tool(tags={"memory"}, annotations={"readOnlyHint": True})
    def search_graph(
        query: str,
        user_id: str | None = None,
        graph_id: str | None = None,
        scope: Literal["edges", "nodes", "episodes"] = "edges",
        limit: int = 10,
        reranker: Literal["rrf", "mmr", "node_distance", "episode_mentions", "cross_encoder"] | None = None,
        mmr_lambda: float | None = None,
        search_filters: dict | None = None,
    ):
        """Search a knowledge graph for relevant facts, entities, or episodes.
        Keep queries concise and specific for best results."""
        from utils import _require_one_of
        _require_one_of(user_id=user_id, graph_id=graph_id)
        kwargs = dict(
            user_id=user_id,
            graph_id=graph_id,
            query=query,
            scope=scope,
            limit=limit,
        )
        if reranker is not None:
            kwargs["reranker"] = reranker
        if mmr_lambda is not None:
            kwargs["mmr_lambda"] = mmr_lambda
        if search_filters is not None:
            kwargs["search_filters"] = search_filters
        return zep.graph.search(**kwargs)

    @mcp.tool(tags={"memory"}, annotations={"readOnlyHint": True})
    def get_task(task_id: str):
        """Poll the status of an async Zep operation (batch import, cloning, etc.)."""
        return zep.task.get(task_id=task_id)
```

Note: If FastMCP 2.x doesn't support `tags` or `annotations` kwargs in `@mcp.tool()`, remove them and just use `@mcp.tool()`. Check step 5 of Task 2 — if that verification failed, strip tags/annotations from all tool registrations.

- [ ] **Step 4: Update `tools/__init__.py` to wire in memory**

```python
from tools.memory import register as register_memory


def register_all(mcp, zep, toolsets):
    """Register tool modules based on enabled toolsets."""
    registrars = {
        "memory": [register_memory],
        "admin": [],
    }
    for toolset in toolsets:
        handlers = registrars.get(toolset, [])
        for register_fn in handlers:
            register_fn(mcp, zep)
```

- [ ] **Step 5: Run tests**

```bash
source venv/bin/activate
python -m pytest tests/test_memory.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/memory.py tools/__init__.py tests/test_memory.py
git commit -m "feat: add search_graph and get_task memory tools

First tools registered via the register(mcp, zep) pattern.
search_graph supports scope, reranker, and filters."
```

---

### Task 5: Memory tools — add_messages, get_context, add_graph_data

**Files:**
- Modify: `tools/memory.py`
- Modify: `tests/test_memory.py`

- [ ] **Step 1: Add tests for the remaining memory tools**

Append to `tests/test_memory.py`:

```python
def test_add_messages_is_registered(mcp, zep):
    from tools.memory import register
    register(mcp, zep)
    assert "add_messages" in get_tool_names(mcp)


def test_get_context_is_registered(mcp, zep):
    from tools.memory import register
    register(mcp, zep)
    assert "get_context" in get_tool_names(mcp)


def test_add_graph_data_is_registered(mcp, zep):
    from tools.memory import register
    register(mcp, zep)
    assert "add_graph_data" in get_tool_names(mcp)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
source venv/bin/activate
python -m pytest tests/test_memory.py -v
```

Expected: 3 new tests FAIL.

- [ ] **Step 3: Add add_messages, get_context, add_graph_data to `tools/memory.py`**

Add inside the `register` function, after the existing tools:

```python
    @mcp.tool(tags={"memory"})
    def add_messages(
        thread_id: str,
        messages: list[dict],
    ):
        """Add messages to a thread. Each message needs 'role' (user/assistant/system),
        'content', and optionally 'name'."""
        from zep_cloud import Message
        msg_objects = [Message(**m) for m in messages]
        return zep.thread.add_messages(thread_id=thread_id, messages=msg_objects)

    @mcp.tool(tags={"memory"}, annotations={"readOnlyHint": True})
    def get_context(
        thread_id: str,
        template_id: str | None = None,
    ):
        """Get the assembled context block for a user based on thread history.
        Optionally pass a template_id for custom formatting."""
        kwargs = dict(thread_id=thread_id)
        if template_id is not None:
            kwargs["template_id"] = template_id
        return zep.thread.get_user_context(**kwargs)

    @mcp.tool(tags={"memory"})
    def add_graph_data(
        type: Literal["text", "json", "message", "triple"],
        data: str | None = None,
        user_id: str | None = None,
        graph_id: str | None = None,
        fact: str | None = None,
        fact_name: str | None = None,
        source_node_name: str | None = None,
        target_node_name: str | None = None,
        valid_at: str | None = None,
        invalid_at: str | None = None,
        source_node_attributes: dict | None = None,
        edge_attributes: dict | None = None,
        target_node_attributes: dict | None = None,
    ):
        """Add data to a knowledge graph. Types: text, json, message, or triple.
        For triple: provide fact, fact_name, source_node_name, and target_node_name."""
        from utils import _require_one_of
        _require_one_of(user_id=user_id, graph_id=graph_id)
        if type == "triple":
            kwargs = dict(
                fact=fact, fact_name=fact_name,
                user_id=user_id, graph_id=graph_id,
            )
            if source_node_name is not None:
                kwargs["source_node_name"] = source_node_name
            if target_node_name is not None:
                kwargs["target_node_name"] = target_node_name
            if valid_at is not None:
                kwargs["valid_at"] = valid_at
            if invalid_at is not None:
                kwargs["invalid_at"] = invalid_at
            if source_node_attributes is not None:
                kwargs["source_node_attributes"] = source_node_attributes
            if edge_attributes is not None:
                kwargs["edge_attributes"] = edge_attributes
            if target_node_attributes is not None:
                kwargs["target_node_attributes"] = target_node_attributes
            return zep.graph.add_fact_triple(**kwargs)
        return zep.graph.add(
            user_id=user_id, graph_id=graph_id, type=type, data=data,
        )
```

- [ ] **Step 4: Run tests**

```bash
source venv/bin/activate
python -m pytest tests/test_memory.py -v
```

Expected: All 5 memory tool tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/memory.py tests/test_memory.py
git commit -m "feat: add add_messages, get_context, add_graph_data tools

All 5 memory tools complete. add_graph_data routes triple
type to graph.add_fact_triple with separate params."
```

---

### Task 6: Admin tools — manage_user and manage_user_instructions

**Files:**
- Create: `tools/users.py`
- Modify: `tools/__init__.py`
- Create: `tests/test_users.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_users.py`:

```python
from tests.conftest import get_tool_names


def test_manage_user_is_registered(mcp, zep):
    from tools.users import register
    register(mcp, zep)
    assert "manage_user" in get_tool_names(mcp)


def test_manage_user_instructions_is_registered(mcp, zep):
    from tools.users import register
    register(mcp, zep)
    assert "manage_user_instructions" in get_tool_names(mcp)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
source venv/bin/activate
python -m pytest tests/test_users.py -v
```

- [ ] **Step 3: Create `tools/users.py`**

```python
from typing import Literal


def register(mcp, zep):
    """Register user admin tools."""

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_user(
        action: Literal["create", "get", "update", "delete", "list", "warm"],
        user_id: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        metadata: dict | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
    ):
        """Manage users in Zep Cloud. Actions: create, get, update, delete, list, warm."""
        match action:
            case "create":
                kwargs = dict(user_id=user_id)
                if email is not None:
                    kwargs["email"] = email
                if first_name is not None:
                    kwargs["first_name"] = first_name
                if last_name is not None:
                    kwargs["last_name"] = last_name
                if metadata is not None:
                    kwargs["metadata"] = metadata
                return zep.user.add(**kwargs)
            case "get":
                return zep.user.get(user_id=user_id)
            case "update":
                kwargs = dict(user_id=user_id)
                if email is not None:
                    kwargs["email"] = email
                if first_name is not None:
                    kwargs["first_name"] = first_name
                if last_name is not None:
                    kwargs["last_name"] = last_name
                if metadata is not None:
                    kwargs["metadata"] = metadata
                return zep.user.update(**kwargs)
            case "delete":
                return zep.user.delete(user_id=user_id)
            case "list":
                kwargs = {}
                if page_number is not None:
                    kwargs["page_number"] = page_number
                if page_size is not None:
                    kwargs["page_size"] = page_size
                return zep.user.list_ordered(**kwargs)
            case "warm":
                return zep.user.warm(user_id=user_id)

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_user_instructions(
        action: Literal["list", "add", "delete"],
        instructions: list[dict] | None = None,
        user_ids: list[str] | None = None,
    ):
        """Manage user summary instructions. Actions: list, add, delete.
        For add: provide instructions as [{name: str, text: str}]."""
        match action:
            case "list":
                kwargs = {}
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                return zep.user.list_user_summary_instructions(**kwargs)
            case "add":
                from zep_cloud import UserInstruction
                instr_objects = [UserInstruction(**i) for i in (instructions or [])]
                kwargs = dict(instructions=instr_objects)
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                return zep.user.add_user_summary_instructions(**kwargs)
            case "delete":
                kwargs = {}
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                return zep.user.delete_user_summary_instructions(**kwargs)
```

- [ ] **Step 4: Wire into `tools/__init__.py`**

Add `from tools.users import register as register_users` and add `register_users` to the `"admin"` list.

```python
from tools.memory import register as register_memory
from tools.users import register as register_users


def register_all(mcp, zep, toolsets):
    """Register tool modules based on enabled toolsets."""
    registrars = {
        "memory": [register_memory],
        "admin": [register_users],
    }
    for toolset in toolsets:
        handlers = registrars.get(toolset, [])
        for register_fn in handlers:
            register_fn(mcp, zep)
```

- [ ] **Step 5: Run tests**

```bash
source venv/bin/activate
python -m pytest tests/test_users.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/users.py tools/__init__.py tests/test_users.py
git commit -m "feat: add manage_user and manage_user_instructions tools

User CRUD (create/get/update/delete/list/warm) and summary
instruction management via action-based routing."
```

---

### Task 7: Admin tools — manage_thread

**Files:**
- Create: `tools/threads.py`
- Modify: `tools/__init__.py`
- Create: `tests/test_threads.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_threads.py`:

```python
from tests.conftest import get_tool_names


def test_manage_thread_is_registered(mcp, zep):
    from tools.threads import register
    register(mcp, zep)
    assert "manage_thread" in get_tool_names(mcp)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
source venv/bin/activate
python -m pytest tests/test_threads.py -v
```

- [ ] **Step 3: Create `tools/threads.py`**

```python
from typing import Literal


def register(mcp, zep):
    """Register thread admin tools."""

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_thread(
        action: Literal["create", "get", "delete", "list"],
        thread_id: str | None = None,
        user_id: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        order_by: str | None = None,
        asc: bool | None = None,
    ):
        """Manage conversation threads. Actions: create, get, delete, list.
        Create requires thread_id and user_id."""
        match action:
            case "create":
                return zep.thread.create(thread_id=thread_id, user_id=user_id)
            case "get":
                return zep.thread.get(thread_id=thread_id)
            case "delete":
                return zep.thread.delete(thread_id=thread_id)
            case "list":
                kwargs = {}
                if page_number is not None:
                    kwargs["page_number"] = page_number
                if page_size is not None:
                    kwargs["page_size"] = page_size
                if order_by is not None:
                    kwargs["order_by"] = order_by
                if asc is not None:
                    kwargs["asc"] = asc
                return zep.thread.list_all(**kwargs)
```

- [ ] **Step 4: Wire into `tools/__init__.py`**

Add `from tools.threads import register as register_threads` and add `register_threads` to the `"admin"` list.

- [ ] **Step 5: Run tests**

```bash
source venv/bin/activate
python -m pytest tests/test_threads.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/threads.py tools/__init__.py tests/test_threads.py
git commit -m "feat: add manage_thread tool

Thread CRUD (create/get/delete/list) with pagination support."
```

---

### Task 8: Admin tools — manage_graph, manage_graph_structure, manage_graph_data

This is the largest tool module. Three tools covering graph lifecycle, schema/ontology, and node/edge/episode CRUD.

**Files:**
- Create: `tools/graphs.py`
- Modify: `tools/__init__.py`
- Create: `tests/test_graphs.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_graphs.py`:

```python
from tests.conftest import get_tool_names


def test_manage_graph_is_registered(mcp, zep):
    from tools.graphs import register
    register(mcp, zep)
    assert "manage_graph" in get_tool_names(mcp)


def test_manage_graph_structure_is_registered(mcp, zep):
    from tools.graphs import register
    register(mcp, zep)
    assert "manage_graph_structure" in get_tool_names(mcp)


def test_manage_graph_data_is_registered(mcp, zep):
    from tools.graphs import register
    register(mcp, zep)
    assert "manage_graph_data" in get_tool_names(mcp)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
source venv/bin/activate
python -m pytest tests/test_graphs.py -v
```

- [ ] **Step 3: Create `tools/graphs.py`**

```python
from typing import Literal


def register(mcp, zep):
    """Register graph admin tools."""

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_graph(
        action: Literal["create", "get", "update", "delete", "list", "clone"],
        graph_id: str | None = None,
        description: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        source_graph_id: str | None = None,
        source_user_id: str | None = None,
        target_graph_id: str | None = None,
        target_user_id: str | None = None,
    ):
        """Manage standalone knowledge graphs. Actions: create, get, update, delete, list, clone.
        Clone copies a graph — provide source and target IDs."""
        match action:
            case "create":
                return zep.graph.create(graph_id=graph_id)
            case "get":
                return zep.graph.get(graph_id=graph_id)
            case "update":
                kwargs = dict(graph_id=graph_id)
                if description is not None:
                    kwargs["description"] = description
                return zep.graph.update(**kwargs)
            case "delete":
                return zep.graph.delete(graph_id=graph_id)
            case "list":
                kwargs = {}
                if page_number is not None:
                    kwargs["page_number"] = page_number
                if page_size is not None:
                    kwargs["page_size"] = page_size
                return zep.graph.list_all(**kwargs)
            case "clone":
                kwargs = {}
                if source_graph_id is not None:
                    kwargs["source_graph_id"] = source_graph_id
                if source_user_id is not None:
                    kwargs["source_user_id"] = source_user_id
                if target_graph_id is not None:
                    kwargs["target_graph_id"] = target_graph_id
                if target_user_id is not None:
                    kwargs["target_user_id"] = target_user_id
                return zep.graph.clone(**kwargs)

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_graph_structure(
        action: Literal[
            "set_ontology", "list_ontology",
            "add_instructions", "list_instructions", "delete_instructions",
            "detect_patterns",
        ],
        entities: dict | None = None,
        edges: dict | None = None,
        instructions: list[dict] | None = None,
        user_id: str | None = None,
        graph_id: str | None = None,
        user_ids: list[str] | None = None,
        graph_ids: list[str] | None = None,
        query: str | None = None,
        limit: int | None = None,
        min_occurrences: int | None = None,
    ):
        """Manage graph schema and structure. Actions: set_ontology, list_ontology,
        add_instructions, list_instructions, delete_instructions, detect_patterns."""
        match action:
            case "set_ontology":
                return zep.graph.set_ontology(
                    entities=entities or {},
                    edges=edges or {},
                )
            case "list_ontology":
                return zep.graph.list_ontology()
            case "add_instructions":
                from zep_cloud import CustomInstruction
                instr = [CustomInstruction(**i) for i in (instructions or [])]
                kwargs = dict(instructions=instr)
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                if graph_ids is not None:
                    kwargs["graph_ids"] = graph_ids
                return zep.graph.add_custom_instructions(**kwargs)
            case "list_instructions":
                return zep.graph.list_custom_instructions()
            case "delete_instructions":
                kwargs = {}
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                if graph_ids is not None:
                    kwargs["graph_ids"] = graph_ids
                return zep.graph.delete_custom_instructions(**kwargs)
            case "detect_patterns":
                kwargs = {}
                if user_id is not None:
                    kwargs["user_id"] = user_id
                if graph_id is not None:
                    kwargs["graph_id"] = graph_id
                if query is not None:
                    kwargs["query"] = query
                if limit is not None:
                    kwargs["limit"] = limit
                if min_occurrences is not None:
                    kwargs["min_occurrences"] = min_occurrences
                return zep.graph.detect_patterns(**kwargs)

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_graph_data(
        scope: Literal["node", "edge", "episode"],
        action: Literal["get", "update", "delete", "list", "get_edges", "get_episodes", "get_mentions"],
        uuid: str | None = None,
        user_id: str | None = None,
        graph_id: str | None = None,
        name: str | None = None,
        summary: str | None = None,
        fact: str | None = None,
        labels: list[str] | None = None,
        attributes: dict | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ):
        """Inspect and manage graph nodes, edges, and episodes.
        Scope selects the entity type; action selects the operation."""
        match (scope, action):
            # Node operations
            case ("node", "get"):
                return zep.graph.node.get(uuid=uuid)
            case ("node", "update"):
                kwargs = dict(uuid=uuid)
                if name is not None:
                    kwargs["name"] = name
                if summary is not None:
                    kwargs["summary"] = summary
                if labels is not None:
                    kwargs["labels"] = labels
                if attributes is not None:
                    kwargs["attributes"] = attributes
                return zep.graph.node.update(**kwargs)
            case ("node", "delete"):
                return zep.graph.node.delete(uuid=uuid)
            case ("node", "list"):
                if user_id:
                    return zep.graph.node.get_by_user_id(user_id=user_id, limit=limit, cursor=cursor)
                return zep.graph.node.get_by_graph_id(graph_id=graph_id, limit=limit, cursor=cursor)
            case ("node", "get_edges"):
                return zep.graph.node.get_edges(uuid=uuid)
            case ("node", "get_episodes"):
                return zep.graph.node.get_episodes(uuid=uuid)
            # Edge operations
            case ("edge", "get"):
                return zep.graph.edge.get(uuid=uuid)
            case ("edge", "update"):
                kwargs = dict(uuid_=uuid)
                if fact is not None:
                    kwargs["fact"] = fact
                if name is not None:
                    kwargs["name"] = name
                if attributes is not None:
                    kwargs["attributes"] = attributes
                return zep.graph.edge.update(**kwargs)
            case ("edge", "delete"):
                return zep.graph.edge.delete(uuid_=uuid)
            case ("edge", "list"):
                if user_id:
                    return zep.graph.edge.get_by_user_id(user_id=user_id, limit=limit, cursor=cursor)
                return zep.graph.edge.get_by_graph_id(graph_id=graph_id, limit=limit, cursor=cursor)
            # Episode operations
            case ("episode", "get"):
                return zep.graph.episode.get(uuid_=uuid)
            case ("episode", "delete"):
                return zep.graph.episode.delete(uuid_=uuid)
            case ("episode", "list"):
                if user_id:
                    return zep.graph.episode.get_by_user_id(user_id=user_id, lastn=limit)
                return zep.graph.episode.get_by_graph_id(graph_id=graph_id, lastn=limit)
            case ("episode", "get_mentions"):
                return zep.graph.episode.get_mentions(uuid_=uuid)
            case _:
                raise ValueError(f"Invalid scope/action combination: {scope}/{action}")
```

Note: The exact SDK method names for node/edge/episode sub-clients (e.g. `get_by_user_id` vs `get_user_nodes`) need to be verified against the installed SDK. If method names differ, adjust accordingly.

- [ ] **Step 4: Wire into `tools/__init__.py`**

Add `from tools.graphs import register as register_graphs` and add to the `"admin"` list.

- [ ] **Step 5: Run tests**

```bash
source venv/bin/activate
python -m pytest tests/test_graphs.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/graphs.py tools/__init__.py tests/test_graphs.py
git commit -m "feat: add graph admin tools (manage_graph, structure, data)

Graph lifecycle, ontology/instructions, and node/edge/episode
CRUD with scope+action routing pattern."
```

---

### Task 9: Admin tools — manage_context_templates and project_info

**Files:**
- Create: `tools/context.py`
- Modify: `tools/__init__.py`
- Create: `tests/test_context.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_context.py`:

```python
from tests.conftest import get_tool_names


def test_manage_context_templates_is_registered(mcp, zep):
    from tools.context import register
    register(mcp, zep)
    assert "manage_context_templates" in get_tool_names(mcp)


def test_project_info_is_registered(mcp, zep):
    from tools.context import register
    register(mcp, zep)
    assert "project_info" in get_tool_names(mcp)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
source venv/bin/activate
python -m pytest tests/test_context.py -v
```

- [ ] **Step 3: Create `tools/context.py`**

```python
from typing import Literal


def register(mcp, zep):
    """Register context template and project tools."""

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_context_templates(
        action: Literal["create", "get", "update", "list", "delete"],
        template_id: str | None = None,
        template: str | None = None,
    ):
        """Manage context templates for customizing context block format.
        Actions: create, get, update, list, delete.
        Templates use Zep's template syntax: %{user_summary}, %{edges limit=10}, etc."""
        match action:
            case "create":
                return zep.context.create_context_template(
                    template_id=template_id, template=template,
                )
            case "get":
                return zep.context.get_context_template(template_id=template_id)
            case "update":
                kwargs = dict(template_id=template_id)
                if template is not None:
                    kwargs["template"] = template
                return zep.context.update_context_template(**kwargs)
            case "list":
                return zep.context.list_context_templates()
            case "delete":
                return zep.context.delete_context_template(template_id=template_id)

    @mcp.tool(tags={"admin"}, annotations={"readOnlyHint": True})
    def project_info():
        """Get information about the current Zep Cloud project."""
        return zep.project.get()
```

- [ ] **Step 4: Wire into `tools/__init__.py`**

Add `from tools.context import register as register_context` and add to the `"admin"` list. Final `__init__.py`:

```python
from tools.memory import register as register_memory
from tools.users import register as register_users
from tools.threads import register as register_threads
from tools.graphs import register as register_graphs
from tools.context import register as register_context


def register_all(mcp, zep, toolsets):
    """Register tool modules based on enabled toolsets."""
    registrars = {
        "memory": [register_memory],
        "admin": [register_users, register_threads, register_graphs, register_context],
    }
    for toolset in toolsets:
        handlers = registrars.get(toolset, [])
        for register_fn in handlers:
            register_fn(mcp, zep)
```

- [ ] **Step 5: Run all tests**

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

Expected: All tests PASS across all files.

- [ ] **Step 6: Commit**

```bash
git add tools/context.py tools/__init__.py tests/test_context.py
git commit -m "feat: add context template and project_info tools

All 13 tools now registered. Context template CRUD and
project info complete the admin toolset."
```

---

### Task 10: Update CLAUDE.md

**Files:**
- Rewrite: `CLAUDE.md`

- [ ] **Step 1: Replace CLAUDE.md with spec-defined content**

Replace the entire contents of `CLAUDE.md` with the content specified in the spec (lines 280-336 of the design spec). Copy it verbatim.

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: rewrite CLAUDE.md for new architecture

Updated to reflect 13-tool jobs-to-be-done design,
toolset gating, and new file structure."
```

---

### Task 11: End-to-end smoke test

Verify the server actually starts and all 13 tools are registered.

**Files:**
- None (manual verification)

- [ ] **Step 1: Verify all 13 tools are registered**

```bash
source venv/bin/activate
python -c "
from server import mcp
tools = list(mcp._tool_manager.tools.keys())
print(f'{len(tools)} tools registered:')
for t in sorted(tools):
    print(f'  - {t}')
assert len(tools) == 13, f'Expected 13 tools, got {len(tools)}'
"
```

Expected: 13 tools listed: add_graph_data, add_messages, get_context, get_task, manage_context_templates, manage_graph, manage_graph_data, manage_graph_structure, manage_thread, manage_user, manage_user_instructions, project_info, search_graph.

- [ ] **Step 2: Verify toolset gating (memory only)**

```bash
source venv/bin/activate
ZEP_TOOLSETS=memory python -c "
from server import mcp
tools = list(mcp._tool_manager.tools.keys())
print(f'{len(tools)} tools registered:')
for t in sorted(tools):
    print(f'  - {t}')
assert len(tools) == 5, f'Expected 5 tools, got {len(tools)}'
"
```

Expected: Only 5 memory tools.

- [ ] **Step 3: Run full test suite one final time**

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 4: Commit any fixes if needed**

Only if the smoke test revealed issues that required code changes.

---

### Task 12: Final cleanup and commit

- [ ] **Step 1: Verify no old files remain**

```bash
find . -maxdepth 2 -not -path './venv/*' -not -path './.git/*' -not -path './.claude/*' -not -path './.cursor/*' -not -path './docs/*' -not -path './tests/*' -not -path './tools/*' -not -name '__pycache__' | sort
```

Expected: Only `.`, `.env`, `.env.example`, `.gitignore`, `CLAUDE.md`, `requirements.txt`, `server.py`, `utils.py`.

- [ ] **Step 2: Run the full test suite once more**

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

- [ ] **Step 3: Create final summary commit if any cleanup was done**

```bash
git add -A
git status
```

If there are uncommitted changes, commit them. If clean, skip.
