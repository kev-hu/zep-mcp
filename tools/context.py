from typing import Literal


def register(mcp, zep):
    """Register context template and project tools."""

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_context_templates(
        action: Literal["create", "get", "update", "list", "delete"],
        template_id: str | None = None,
        template: str | None = None,
    ):
        """Manage context templates for customizing context block format.
        Actions: create, get, update, list, delete.
        Templates use Zep's template syntax: %{user_summary}, %{edges limit=10}, etc."""
        match action:
            case "create":
                return zep.context.create_context_template(
                    template_id=template_id, template=template,
                )
            case "get":
                return zep.context.get_context_template(template_id=template_id)
            case "update":
                kwargs = dict(template_id=template_id)
                if template is not None:
                    kwargs["template"] = template
                return zep.context.update_context_template(**kwargs)
            case "list":
                return zep.context.list_context_templates()
            case "delete":
                return zep.context.delete_context_template(template_id=template_id)

    @mcp.tool(tags={"admin"}, annotations={"readOnlyHint": True})
    def project_info():
        """Get information about the current Zep Cloud project."""
        return zep.project.get()
