from typing import Any
from crewai_tools.tools.rag.rag_tool import RagTool
from crewai_tools.adapters.elasticsearch_adapter import ElasticsearchAdapter

class ElasticsearchTool(RagTool):
    name: str = "Elasticsearch Knowledge Base"
    description: str = "Search and retrieve information from Elasticsearch."
    adapter: ElasticsearchAdapter
