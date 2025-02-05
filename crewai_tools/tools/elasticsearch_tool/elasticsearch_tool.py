from typing import Any, Optional
from pydantic import Field
from crewai_tools.tools.rag.rag_tool import RagTool
from crewai_tools.adapters.elasticsearch_adapter import ElasticsearchAdapter

class ElasticsearchTool(RagTool):
    name: str = "Elasticsearch Knowledge Base"
    description: str = """Search and retrieve information from Elasticsearch using both semantic and keyword search.
    Features:
    - Vector search for semantic understanding
    - Traditional text search for precise matching
    - Configurable result count
    - Support for metadata filtering
    - Bulk document operations
    - Multiple authentication methods (API key, username/password, cloud ID)
    - Hybrid search combining vector and text similarity
    - Automatic index validation and creation"""
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
