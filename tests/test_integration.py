"""Integration tests — call tools through FastMCP against the real Zep Cloud API."""

import asyncio
import pytest
from fastmcp import FastMCP
from tools import register_all


@pytest.fixture
def server(zep):
    """Create an MCP server with all tools registered."""
    mcp = FastMCP()
    register_all(mcp, zep, ["memory", "admin"])
    return mcp


def call(server, tool_name, args=None):
    """Call an MCP tool and return the result."""
    return asyncio.run(server.call_tool(tool_name, args or {}))


def test_project_info(server):
    result = call(server, "project_info")
    assert result is not None


def test_manage_user_list(server):
    result = call(server, "manage_user", {"action": "list"})
    assert result is not None


def test_manage_thread_list(server):
    result = call(server, "manage_thread", {"action": "list"})
    assert result is not None


def test_manage_graph_list(server):
    result = call(server, "manage_graph", {"action": "list"})
    assert result is not None


def test_search_graph(server):
    users = call(server, "manage_user", {"action": "list"})
    if not users.structured_content.get("users"):
        pytest.skip("No users in project")
    user_id = users.structured_content["users"][0]["user_id"]
    result = call(server, "search_graph", {
        "query": "test",
        "user_id": user_id,
        "scope": "edges",
        "limit": 1,
    })
    assert result is not None


def test_list_entity_types(server):
    result = call(server, "manage_graph_structure", {"action": "list_entity_types"})
    assert result is not None


def test_list_context_templates(server):
    result = call(server, "manage_context_templates", {"action": "list"})
    assert result is not None
