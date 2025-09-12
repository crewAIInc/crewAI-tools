"""Adapter for CrewAI's native RAG system."""

from typing import Any, TypedDict, Unpack, TypeAlias
from pathlib import Path

from pydantic import Field
from crewai.rag.config.utils import get_rag_client
from crewai.rag.types import BaseRecord, SearchResult
from crewai.rag.core.base_client import BaseClient

from crewai_tools.tools.rag.rag_tool import Adapter
from crewai_tools.rag.data_types import DataType

ContentItem: TypeAlias = str | Path | dict[str, Any]

class AddDocumentParams(TypedDict, total=False):
    """Parameters for adding documents to the RAG system."""
    data_type: DataType
    metadata: dict[str, Any]
    website: str
    url: str
    file_path: str | Path
    github_url: str
    youtube_url: str
    directory_path: str | Path


class CrewAIRagAdapter(Adapter):
    """Adapter that uses CrewAI's native RAG system instead of embedchain."""
    
    collection_name: str = "default"
    summarize: bool = False
    client: BaseClient = Field(default_factory=get_rag_client)
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize the CrewAI RAG client after model initialization."""
        self.client.get_or_create_collection(collection_name=self.collection_name)
    
    def query(self, question: str) -> str:
        """Query the knowledge base with a question.
        
        Args:
            question: The question to ask
            
        Returns:
            Relevant content from the knowledge base
        """
        results: list[SearchResult] = self.client.search(
            collection_name=self.collection_name,
            query=question,
            limit=5
        )
        
        if not results:
            return "No relevant content found."
        
        contents: list[str] = []
        for result in results:
            content: str = result.get("content", "")
            if content:
                contents.append(content)
        
        return "\n\n".join(contents)
    
    def add(self, *args: ContentItem, **kwargs: Unpack[AddDocumentParams]) -> None:
        """Add content to the knowledge base.
        
        This method handles various input types and converts them to documents
        for the vector database. It supports the data_type parameter for 
        compatibility with existing tools.
        
        Args:
            *args: Content items to add (strings, paths, or document dicts)
            **kwargs: Additional parameters including data_type, metadata, etc.
        """
        from crewai_tools.rag.data_types import DataTypes, DataType
        from crewai_tools.rag.source_content import SourceContent
        from crewai_tools.rag.base_loader import LoaderResult
        import os
        
        documents: list[BaseRecord] = []
        data_type: DataType | None = kwargs.get("data_type")
        base_metadata: dict[str, Any] = kwargs.get("metadata", {})
        
        for arg in args:
            source_ref: str
            if isinstance(arg, dict):
                source_ref = str(arg.get("source", arg.get("content", "")))
            else:
                source_ref = str(arg)
            
            if not data_type:
                data_type = DataTypes.from_content(source_ref)
            
            if data_type == DataType.DIRECTORY:
                if not os.path.isdir(source_ref):
                    raise ValueError(f"Directory does not exist: {source_ref}")
                
                for root, dirs, files in os.walk(source_ref):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for filename in files:
                        if filename.startswith('.'):
                            continue
                        
                        file_path: str = os.path.join(root, filename)
                        try:
                            file_data_type: DataType = DataTypes.from_content(file_path)
                            file_loader = file_data_type.get_loader()
                            
                            file_source = SourceContent(file_path)
                            file_result: LoaderResult = file_loader.load(file_source)
                            
                            file_metadata: dict[str, Any] = base_metadata.copy()
                            file_metadata.update(file_result.metadata)
                            file_metadata["data_type"] = str(file_data_type)
                            file_metadata["directory_source"] = source_ref
                            file_metadata["file_path"] = file_path
                            
                            if isinstance(arg, dict):
                                file_metadata.update(arg.get("metadata", {}))
                            
                            documents.append({
                                "doc_id": file_result.doc_id,
                                "content": file_result.content,
                                "metadata": file_metadata
                            })
                        except Exception as e:
                            print(f"Error processing {file_path}: {e}")
                            continue
            else:
                metadata: dict[str, Any] = base_metadata.copy()
                
                loader = data_type.get_loader()
                
                source_content = SourceContent(source_ref)
                loader_result: LoaderResult = loader.load(source_content)
                
                metadata.update(loader_result.metadata)
                metadata["data_type"] = str(data_type)
                
                if isinstance(arg, dict):
                    metadata.update(arg.get("metadata", {}))
                
                documents.append({
                    "doc_id": loader_result.doc_id,
                    "content": loader_result.content,
                    "metadata": metadata
                })
        
        if documents:
            self.client.add_documents(
                collection_name=self.collection_name,
                documents=documents
            )