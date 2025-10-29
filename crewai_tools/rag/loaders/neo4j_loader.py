"""Neo4j database loader."""

from typing import Any
from urllib.parse import urlparse

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

from crewai_tools.rag.base_loader import BaseLoader, LoaderResult
from crewai_tools.rag.source_content import SourceContent


class Neo4jLoader(BaseLoader):
    """Loader for Neo4j database content."""

    def load(self, source: SourceContent, **kwargs) -> LoaderResult:
        """Load content from a Neo4j database using a Cypher query.
        
        Args:
            source: Cypher query string
            **kwargs: Additional arguments including neo4j_uri, neo4j_user, neo4j_password
            
        Returns:
            LoaderResult with database content
        """
        if GraphDatabase is None:
            raise ImportError(
                "The neo4j package is required to use Neo4jLoader. "
                "Install it with: pip install neo4j"
            )
        
        metadata = kwargs.get("metadata", {})
        neo4j_uri = metadata.get("neo4j_uri")
        neo4j_user = metadata.get("neo4j_user")
        neo4j_password = metadata.get("neo4j_password")
        
        if not neo4j_uri or not neo4j_user or not neo4j_password:
            raise ValueError("Neo4j URI, user, and password are required for Neo4j loader")
        
        query = source.source
        
        parsed = urlparse(neo4j_uri)
        if parsed.scheme not in ["bolt", "neo4j", "bolt+s", "neo4j+s"]:
            raise ValueError(f"Invalid Neo4j URI scheme: {parsed.scheme}")
        
        connection_params = {
            "uri": neo4j_uri,
            "auth": (neo4j_user, neo4j_password)
        }
        
        try:
            driver = GraphDatabase.driver(**connection_params)
            try:
                with driver.session() as session:
                    result = session.run(query)
                    records = list(result)
                    
                    if not records:
                        content = "No data found from the query"
                        return LoaderResult(
                            content=content,
                            metadata={"source": query, "record_count": 0},
                            doc_id=self.generate_doc_id(source_ref=query, content=content)
                        )
                    
                    text_parts = []
                    text_parts.append(f"Total records: {len(records)}")
                    text_parts.append("")
                    
                    for i, record in enumerate(records, 1):
                        text_parts.append(f"Record {i}:")
                        for key in record.keys():
                            value = record[key]
                            if value is not None:
                                text_parts.append(f"  {key}: {value}")
                        text_parts.append("")
                    
                    content = "\n".join(text_parts)
                    
                    if len(content) > 100000:
                        content = content[:100000] + "\n\n[Content truncated...]"
                    
                    return LoaderResult(
                        content=content,
                        metadata={
                            "source": query,
                            "record_count": len(records),
                        },
                        doc_id=self.generate_doc_id(source_ref=query, content=content)
                    )
            finally:
                driver.close()
        except Exception as e:
            raise ValueError(f"Neo4j database error: {e}")

