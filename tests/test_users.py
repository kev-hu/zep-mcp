from tests.conftest import get_tool_names


def test_manage_user_is_registered(mcp, zep):
    from tools.users import register
    register(mcp, zep)
    assert "manage_user" in get_tool_names(mcp)


def test_manage_user_instructions_is_registered(mcp, zep):
    from tools.users import register
    register(mcp, zep)
    assert "manage_user_instructions" in get_tool_names(mcp)
