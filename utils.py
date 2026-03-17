def _require_one_of(**kwargs):
    """Validate that exactly one of the provided kwargs is set."""
    provided = {k: v for k, v in kwargs.items() if v is not None}
    if len(provided) == 0:
        names = " or ".join(kwargs.keys())
        raise ValueError(f"Either {names} is required")
    if len(provided) > 1:
        names = " and ".join(provided.keys())
        raise ValueError(f"Provide only one of: {names}")
