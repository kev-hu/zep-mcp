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
