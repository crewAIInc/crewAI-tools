from typing import Any, Optional
from pydantic import Field
from crewai_tools.tools.rag.rag_tool import RagTool
from crewai_tools.adapters.elasticsearch_adapter import ElasticsearchAdapter

class ElasticsearchTool(RagTool):
    name: str = "Elasticsearch Knowledge Base"
    description: str = """Search and retrieve information from Elasticsearch using both semantic and keyword search.
    Supports vector search for semantic understanding and traditional text search for precise matching."""
    adapter: ElasticsearchAdapter
    
    def _run(
        self,
        query: str,
        metadata_filter: Optional[dict] = None,
        **kwargs: Any
    ) -> str:
        if metadata_filter:
            kwargs["filter"] = metadata_filter
        return super()._run(query, **kwargs)
