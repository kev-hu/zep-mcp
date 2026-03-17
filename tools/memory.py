from typing import Literal


def register(mcp, zep):
    """Register memory tools."""

    @mcp.tool(tags={"memory"}, annotations={"readOnlyHint": True})
    def search_graph(
        query: str,
        user_id: str | None = None,
        graph_id: str | None = None,
        scope: Literal["edges", "nodes", "episodes"] = "edges",
        limit: int = 10,
        reranker: Literal["rrf", "mmr", "node_distance", "episode_mentions", "cross_encoder"] | None = None,
        mmr_lambda: float | None = None,
        search_filters: dict | None = None,
    ):
        """Search a knowledge graph for relevant facts, entities, or episodes.
        Keep queries concise and specific for best results."""
        from utils import _require_one_of
        _require_one_of(user_id=user_id, graph_id=graph_id)
        kwargs = dict(
            user_id=user_id,
            graph_id=graph_id,
            query=query,
            scope=scope,
            limit=limit,
        )
        if reranker is not None:
            kwargs["reranker"] = reranker
        if mmr_lambda is not None:
            kwargs["mmr_lambda"] = mmr_lambda
        if search_filters is not None:
            kwargs["search_filters"] = search_filters
        return zep.graph.search(**kwargs)

    @mcp.tool(tags={"memory"}, annotations={"readOnlyHint": True})
    def get_task(task_id: str):
        """Poll the status of an async Zep operation (batch import, cloning, etc.)."""
        return zep.task.get(task_id=task_id)
