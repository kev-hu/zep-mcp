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
