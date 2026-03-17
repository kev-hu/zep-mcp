from tests.conftest import get_tool_names


def test_manage_context_templates_is_registered(mcp, zep):
    from tools.context import register
    register(mcp, zep)
    assert "manage_context_templates" in get_tool_names(mcp)


def test_project_info_is_registered(mcp, zep):
    from tools.context import register
    register(mcp, zep)
    assert "project_info" in get_tool_names(mcp)
