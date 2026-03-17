from typing import Literal


def register(mcp, zep):
    """Register thread admin tools."""

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_thread(
        action: Literal["create", "get", "delete", "list"],
        thread_id: str | None = None,
        user_id: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        order_by: str | None = None,
        asc: bool | None = None,
    ):
        """Manage conversation threads. Actions: create, get, delete, list.
        Create requires thread_id and user_id."""
        match action:
            case "create":
                return zep.thread.create(thread_id=thread_id, user_id=user_id)
            case "get":
                return zep.thread.get(thread_id=thread_id)
            case "delete":
                return zep.thread.delete(thread_id=thread_id)
            case "list":
                kwargs = {}
                if page_number is not None:
                    kwargs["page_number"] = page_number
                if page_size is not None:
                    kwargs["page_size"] = page_size
                if order_by is not None:
                    kwargs["order_by"] = order_by
                if asc is not None:
                    kwargs["asc"] = asc
                return zep.thread.list_all(**kwargs)
