import os
import asyncio
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
    return [t.name for t in asyncio.run(mcp.list_tools())]
