from typing import Literal


def register(mcp, zep):
    """Register user admin tools."""

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_user(
        action: Literal["create", "get", "update", "delete", "list", "warm"],
        user_id: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        metadata: dict | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
    ):
        """Manage users in Zep Cloud. Actions: create, get, update, delete, list, warm."""
        match action:
            case "create":
                kwargs = dict(user_id=user_id)
                if email is not None:
                    kwargs["email"] = email
                if first_name is not None:
                    kwargs["first_name"] = first_name
                if last_name is not None:
                    kwargs["last_name"] = last_name
                if metadata is not None:
                    kwargs["metadata"] = metadata
                return zep.user.add(**kwargs)
            case "get":
                return zep.user.get(user_id=user_id)
            case "update":
                kwargs = dict(user_id=user_id)
                if email is not None:
                    kwargs["email"] = email
                if first_name is not None:
                    kwargs["first_name"] = first_name
                if last_name is not None:
                    kwargs["last_name"] = last_name
                if metadata is not None:
                    kwargs["metadata"] = metadata
                return zep.user.update(**kwargs)
            case "delete":
                return zep.user.delete(user_id=user_id)
            case "list":
                kwargs = {}
                if page_number is not None:
                    kwargs["page_number"] = page_number
                if page_size is not None:
                    kwargs["page_size"] = page_size
                return zep.user.list_ordered(**kwargs)
            case "warm":
                return zep.user.warm(user_id=user_id)

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_user_instructions(
        action: Literal["list", "add", "delete"],
        instructions: list[dict] | None = None,
        user_ids: list[str] | None = None,
    ):
        """Manage user summary instructions. Actions: list, add, delete.
        For add: provide instructions as [{name: str, text: str}]."""
        match action:
            case "list":
                kwargs = {}
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                return zep.user.list_user_summary_instructions(**kwargs)
            case "add":
                from zep_cloud import UserInstruction
                instr_objects = [UserInstruction(**i) for i in (instructions or [])]
                kwargs = dict(instructions=instr_objects)
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                return zep.user.add_user_summary_instructions(**kwargs)
            case "delete":
                kwargs = {}
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                return zep.user.delete_user_summary_instructions(**kwargs)
