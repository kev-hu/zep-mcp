from tests.conftest import get_tool_names


def test_manage_thread_is_registered(mcp, zep):
    from tools.threads import register
    register(mcp, zep)
    assert "manage_thread" in get_tool_names(mcp)
