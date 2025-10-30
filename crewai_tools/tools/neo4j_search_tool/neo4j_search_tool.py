from typing import Any, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


from ..rag.rag_tool import RagTool
from crewai_tools.rag.data_types import DataType


class Neo4jSearchToolSchema(BaseModel):
    """Input for Neo4jSearchTool."""
    search_query: str = Field(..., description="Cypher query to search the Neo4j database.")



class Neo4jSearchTool(RagTool):
    name: str = "Neo4j Search Tool"
    description: str = "A tool that can be used to search the Neo4j database using a Cypher query."
    args_schema: Type[BaseModel] = Neo4jSearchToolSchema
    neo4j_uri: str = Field(..., description="The URI of the Neo4j database.")
    neo4j_user: str = Field(..., description="The username for the Neo4j database.")
    neo4j_password: str = Field(..., description="The password for the Neo4j database.")

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, **kwargs):
        super().__init__(neo4j_uri=neo4j_uri, neo4j_user=neo4j_user, neo4j_password=neo4j_password, **kwargs)
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.description = f"A tool that can be used to search the Neo4j database."
        self._generate_description()

    def _run(self, search_query: str, **kwargs: Any) -> Any:
        self.add(search_query, data_type=DataType.NEO4J, metadata={
            "neo4j_uri": self.neo4j_uri,
            "neo4j_user": self.neo4j_user,
            "neo4j_password": self.neo4j_password
        })
        return super()._run(query=search_query, **kwargs)
    
    def add(self, search_query: str, **kwargs: Any) -> None:
        # Get data_type from kwargs if present, otherwise use NEO4J
        data_type = kwargs.get('data_type', DataType.NEO4J)
        # Get metadata if present and add neo4j credentials
        metadata = kwargs.get('metadata', {})
        metadata.update({
            "neo4j_uri": self.neo4j_uri,
            "neo4j_user": self.neo4j_user,
            "neo4j_password": self.neo4j_password
        })
        kwargs['metadata'] = metadata
        kwargs['data_type'] = data_type
        super().add(search_query, **kwargs)
        self.description = f"A tool that can be used to search the Neo4j database."
        self._generate_description()
    