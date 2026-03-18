from typing import Literal


def register(mcp, zep):
    """Register graph admin tools."""

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_graph(
        action: Literal["create", "get", "update", "delete", "list", "clone"],
        graph_id: str | None = None,
        description: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        source_graph_id: str | None = None,
        source_user_id: str | None = None,
        target_graph_id: str | None = None,
        target_user_id: str | None = None,
    ):
        """Manage standalone knowledge graphs. Actions: create, get, update, delete, list, clone.
        Clone copies a graph — provide source and target IDs."""
        match action:
            case "create":
                return zep.graph.create(graph_id=graph_id)
            case "get":
                return zep.graph.get(graph_id=graph_id)
            case "update":
                kwargs = dict(graph_id=graph_id)
                if description is not None:
                    kwargs["description"] = description
                return zep.graph.update(**kwargs)
            case "delete":
                return zep.graph.delete(graph_id=graph_id)
            case "list":
                kwargs = {}
                if page_number is not None:
                    kwargs["page_number"] = page_number
                if page_size is not None:
                    kwargs["page_size"] = page_size
                return zep.graph.list_all(**kwargs)
            case "clone":
                kwargs = {}
                if source_graph_id is not None:
                    kwargs["source_graph_id"] = source_graph_id
                if source_user_id is not None:
                    kwargs["source_user_id"] = source_user_id
                if target_graph_id is not None:
                    kwargs["target_graph_id"] = target_graph_id
                if target_user_id is not None:
                    kwargs["target_user_id"] = target_user_id
                return zep.graph.clone(**kwargs)

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_graph_structure(
        action: Literal[
            "set_entity_types", "list_entity_types",
            "add_instructions", "list_instructions", "delete_instructions",
            "detect_patterns",
        ],
        entity_types: list[dict] | None = None,
        edge_types: list[dict] | None = None,
        instructions: list[dict] | None = None,
        user_id: str | None = None,
        graph_id: str | None = None,
        user_ids: list[str] | None = None,
        graph_ids: list[str] | None = None,
        query: str | None = None,
        limit: int | None = None,
        min_occurrences: int | None = None,
    ):
        """Manage graph schema and structure. Actions: set_entity_types, list_entity_types,
        add_instructions, list_instructions, delete_instructions, detect_patterns."""
        match action:
            case "set_entity_types":
                kwargs = {}
                if entity_types is not None:
                    from zep_cloud import EntityType
                    kwargs["entity_types"] = [EntityType(**e) for e in entity_types]
                if edge_types is not None:
                    from zep_cloud import EdgeType
                    kwargs["edge_types"] = [EdgeType(**e) for e in edge_types]
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                if graph_ids is not None:
                    kwargs["graph_ids"] = graph_ids
                return zep.graph.set_entity_types_internal(**kwargs)
            case "list_entity_types":
                kwargs = {}
                if user_id is not None:
                    kwargs["user_id"] = user_id
                if graph_id is not None:
                    kwargs["graph_id"] = graph_id
                return zep.graph.list_entity_types(**kwargs)
            case "add_instructions":
                from zep_cloud import CustomInstruction
                instr = [CustomInstruction(**i) for i in (instructions or [])]
                kwargs = dict(instructions=instr)
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                if graph_ids is not None:
                    kwargs["graph_ids"] = graph_ids
                return zep.graph.add_custom_instructions(**kwargs)
            case "list_instructions":
                return zep.graph.list_custom_instructions()
            case "delete_instructions":
                kwargs = {}
                if user_ids is not None:
                    kwargs["user_ids"] = user_ids
                if graph_ids is not None:
                    kwargs["graph_ids"] = graph_ids
                return zep.graph.delete_custom_instructions(**kwargs)
            case "detect_patterns":
                kwargs = {}
                if user_id is not None:
                    kwargs["user_id"] = user_id
                if graph_id is not None:
                    kwargs["graph_id"] = graph_id
                if query is not None:
                    kwargs["query"] = query
                if limit is not None:
                    kwargs["limit"] = limit
                if min_occurrences is not None:
                    kwargs["min_occurrences"] = min_occurrences
                return zep.graph.detect_patterns(**kwargs)

    @mcp.tool(tags={"admin"}, annotations={"destructiveHint": True})
    def manage_graph_data(
        scope: Literal["node", "edge", "episode"],
        action: Literal["get", "update", "delete", "list", "get_edges", "get_episodes", "get_mentions"],
        uuid: str | None = None,
        user_id: str | None = None,
        graph_id: str | None = None,
        name: str | None = None,
        summary: str | None = None,
        fact: str | None = None,
        labels: list[str] | None = None,
        attributes: dict | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ):
        """Inspect and manage graph nodes, edges, and episodes.
        Scope selects the entity type; action selects the operation."""
        match (scope, action):
            case ("node", "get"):
                return zep.graph.node.get(uuid=uuid)
            case ("node", "update"):
                kwargs = dict(uuid=uuid)
                if name is not None:
                    kwargs["name"] = name
                if summary is not None:
                    kwargs["summary"] = summary
                if labels is not None:
                    kwargs["labels"] = labels
                if attributes is not None:
                    kwargs["attributes"] = attributes
                return zep.graph.node.update(**kwargs)
            case ("node", "delete"):
                return zep.graph.node.delete(uuid=uuid)
            case ("node", "list"):
                if user_id:
                    return zep.graph.node.get_by_user_id(user_id=user_id, limit=limit, cursor=cursor)
                return zep.graph.node.get_by_graph_id(graph_id=graph_id, limit=limit, cursor=cursor)
            case ("node", "get_edges"):
                return zep.graph.node.get_edges(uuid=uuid)
            case ("node", "get_episodes"):
                return zep.graph.node.get_episodes(uuid=uuid)
            case ("edge", "get"):
                return zep.graph.edge.get(uuid=uuid)
            case ("edge", "update"):
                kwargs = dict(uuid_=uuid)
                if fact is not None:
                    kwargs["fact"] = fact
                if name is not None:
                    kwargs["name"] = name
                if attributes is not None:
                    kwargs["attributes"] = attributes
                return zep.graph.edge.update(**kwargs)
            case ("edge", "delete"):
                return zep.graph.edge.delete(uuid_=uuid)
            case ("edge", "list"):
                if user_id:
                    return zep.graph.edge.get_by_user_id(user_id=user_id, limit=limit, cursor=cursor)
                return zep.graph.edge.get_by_graph_id(graph_id=graph_id, limit=limit, cursor=cursor)
            case ("episode", "get"):
                return zep.graph.episode.get(uuid_=uuid)
            case ("episode", "delete"):
                return zep.graph.episode.delete(uuid_=uuid)
            case ("episode", "list"):
                if user_id:
                    return zep.graph.episode.get_by_user_id(user_id=user_id, lastn=limit)
                return zep.graph.episode.get_by_graph_id(graph_id=graph_id, lastn=limit)
            case ("episode", "get_mentions"):
                return zep.graph.episode.get_mentions(uuid_=uuid)
            case _:
                raise ValueError(f"Invalid scope/action combination: {scope}/{action}")
