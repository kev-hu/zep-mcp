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
