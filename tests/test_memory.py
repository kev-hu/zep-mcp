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
