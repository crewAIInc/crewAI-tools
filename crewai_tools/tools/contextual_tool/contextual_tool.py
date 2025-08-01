from typing import Any, Optional, Type, List, Union
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ContextualQuerySchema(BaseModel):
    """Schema for contextual query tool."""
    query: str = Field(..., description="Query to send to the Contextual AI agent.")


class ContextualTool(BaseTool):
    """Tool to interact with Contextual AI RAG agents."""
    
    name: str = "Contextual AI Query Tool"
    description: str = "Use this tool to query a Contextual AI RAG agent with access to your documents"
    args_schema: Type[BaseModel] = ContextualQuerySchema
    
    api_key: str
    agent_id: Optional[str] = None
    datastore_id: Optional[str] = None
    contextual_client: Any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            from contextual import ContextualAI
            self.contextual_client = ContextualAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "contextual-client package is required. Install it with: pip install contextual-client"
            )

    def _run(self, query: str) -> str:
        """Run the tool by querying the Contextual AI agent."""
        if not self.agent_id:
            raise ValueError("Agent ID is required to query the Contextual AI agent")
        
        try:
            response = self.contextual_client.agents.query.create(
                agent_id=self.agent_id,
                messages=[
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            )
            
            # Extract the response content based on the response structure
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'message'):
                return response.message.content if hasattr(response.message, 'content') else str(response.message)
            elif hasattr(response, 'messages') and len(response.messages) > 0:
                last_message = response.messages[-1]
                return last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                return str(response)
                
        except Exception as e:
            return f"Error querying Contextual AI agent: {str(e)}"

    @classmethod
    def from_existing_agent(
        cls,
        api_key: str,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> "ContextualTool":
        """
        Create a ContextualTool from an existing agent.
        
        Args:
            api_key: Your Contextual AI API key
            agent_id: ID of the existing agent
            name: Custom name for the tool
            description: Custom description for the tool
            **kwargs: Additional arguments passed to the tool
            
        Returns:
            ContextualTool instance
        """
        return cls(
            api_key=api_key,
            agent_id=agent_id,
            name=name or "Contextual AI Query Tool",
            description=description or "Use this tool to query a Contextual AI RAG agent with access to your documents",
            **kwargs
        )

    @classmethod
    def from_existing_datastore(
        cls,
        api_key: str,
        datastore_id: str,
        agent_name: str,
        agent_description: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> "ContextualTool":
        """
        Create a ContextualTool by creating a new agent with an existing datastore.
        
        Args:
            api_key: Your Contextual AI API key
            datastore_id: ID of the existing datastore
            agent_name: Name for the new agent
            agent_description: Description for the new agent
            name: Custom name for the tool
            description: Custom description for the tool
            **kwargs: Additional arguments passed to the tool
            
        Returns:
            ContextualTool instance
        """
        try:
            from contextual import ContextualAI
            
            contextual = ContextualAI(api_key=api_key)
            
            # Create agent with the existing datastore
            agent = contextual.agents.create(
                name=agent_name,
                description=agent_description,
                datastore_ids=[datastore_id]
            )
            
            return cls(
                api_key=api_key,
                agent_id=agent.id,
                datastore_id=datastore_id,
                name=name or f"Contextual AI Query Tool - {agent_name}",
                description=description or f"Query the {agent_name} agent with access to your documents",
                **kwargs
            )
            
        except ImportError:
            raise ImportError(
                "contextual-client package is required. Install it with: pip install contextual-client"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create agent with existing datastore: {str(e)}")

    @classmethod
    def create_with_documents(
        cls,
        api_key: str,
        agent_name: str,
        agent_description: str,
        datastore_name: str,
        document_paths: List[str],
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> "ContextualTool":
        """
        Create a ContextualTool by setting up a complete RAG pipeline with documents.
        
        Args:
            api_key: Your Contextual AI API key
            agent_name: Name for the new agent
            agent_description: Description for the new agent
            datastore_name: Name for the new datastore
            document_paths: List of file paths to upload
            name: Custom name for the tool
            description: Custom description for the tool
            **kwargs: Additional arguments passed to the tool
            
        Returns:
            ContextualTool instance
        """
        try:
            from contextual import ContextualAI
            import os
            
            contextual = ContextualAI(api_key=api_key)
            
            # Create datastore
            datastore = contextual.datastores.create(name=datastore_name)
            datastore_id = datastore.id
            
            # Upload documents
            document_ids = []
            for doc_path in document_paths:
                if not os.path.exists(doc_path):
                    raise FileNotFoundError(f"Document not found: {doc_path}")
                
                with open(doc_path, 'rb') as f:
                    ingestion_result = contextual.datastores.documents.ingest(datastore_id, file=f)
                    document_ids.append(ingestion_result.id)
            
            # Create agent
            agent = contextual.agents.create(
                name=agent_name,
                description=agent_description,
                datastore_ids=[datastore_id]
            )
            
            return cls(
                api_key=api_key,
                agent_id=agent.id,
                datastore_id=datastore_id,
                name=name or f"Contextual AI Query Tool - {agent_name}",
                description=description or f"Query the {agent_name} agent with access to your uploaded documents",
                **kwargs
            )
            
        except ImportError:
            raise ImportError(
                "contextual-client package is required. Install it with: pip install contextual-client"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create agent with documents: {str(e)}")

    def upload_additional_documents(self, document_paths: List[str]) -> List[str]:
        """
        Upload additional documents to the existing datastore.
        
        Args:
            document_paths: List of file paths to upload
            
        Returns:
            List of document IDs
        """
        if not self.datastore_id:
            raise ValueError("No datastore associated with this tool. Use create_with_documents() method.")
        
        try:
            import os
            document_ids = []
            
            for doc_path in document_paths:
                if not os.path.exists(doc_path):
                    raise FileNotFoundError(f"Document not found: {doc_path}")
                
                with open(doc_path, 'rb') as f:
                    ingestion_result = self.contextual_client.datastores.documents.ingest(
                        self.datastore_id, file=f
                    )
                    document_ids.append(ingestion_result.id)
            
            return document_ids
            
        except Exception as e:
            raise RuntimeError(f"Failed to upload documents: {str(e)}")

    def get_document_status(self, document_id: str) -> dict:
        """
        Get the status of a specific document in the datastore.
        
        Args:
            document_id: Document ID to check (required)
            
        Returns:
            Dictionary containing document metadata and status
        """
        if not self.datastore_id:
            raise ValueError("No datastore associated with this tool.")
        
        try:
            metadata = self.contextual_client.datastores.documents.metadata(
                datastore_id=self.datastore_id, 
                document_id=document_id
            )
            return metadata
            
        except Exception as e:
            raise RuntimeError(f"Failed to get document status: {str(e)}")


    def parse_document(
        self, 
        file_path: str, 
        parse_mode: str = "standard",
        figure_caption_mode: str = "concise",
        enable_document_hierarchy: bool = True,
        page_range: Optional[str] = None,
        output_types: List[str] = ["markdown-per-page"]
    ) -> dict:
        """
        Parse a document using Contextual AI's parsing service.
        
        Args:
            file_path: Path to the document to parse
            parse_mode: Parsing mode (default: "standard")
            figure_caption_mode: Figure caption mode (default: "concise") 
            enable_document_hierarchy: Enable document hierarchy (default: True)
            page_range: Page range to parse (e.g., "0-5"), None for all pages
            output_types: List of output types (default: ["markdown-per-page"])
            
        Returns:
            Dictionary containing parsed document results
        """
        try:
            import requests
            import json
            import os
            from time import sleep
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            base_url = "https://api.contextual.ai/v1"
            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {self.api_key}"
            }
            
            # Submit parse job
            url = f"{base_url}/parse"
            config = {
                "parse_mode": parse_mode,
                "figure_caption_mode": figure_caption_mode,
                "enable_document_hierarchy": enable_document_hierarchy,
            }
            
            if page_range:
                config["page_range"] = page_range
            
            with open(file_path, "rb") as fp:
                file = {"raw_file": fp}
                result = requests.post(url, headers=headers, data=config, files=file)
                response = json.loads(result.text)
                job_id = response['job_id']
            
            # Monitor job status
            status_url = f"{base_url}/parse/jobs/{job_id}/status"
            while True:
                result = requests.get(status_url, headers=headers)
                parse_response = json.loads(result.text)['status']
                
                if parse_response == "completed":
                    break
                elif parse_response == "failed":
                    raise RuntimeError("Document parsing failed")
                
                sleep(5)  # Check every 5 seconds
            
            # Get parse results
            results_url = f"{base_url}/parse/jobs/{job_id}/results"
            result = requests.get(
                results_url,
                headers=headers,
                params={"output_types": ",".join(output_types)},
            )
            
            return json.loads(result.text)
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse document: {str(e)}")

    @classmethod
    def create_parser_only(
        cls,
        api_key: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> "ContextualTool":
        """
        Create a ContextualTool for document parsing only (no RAG capabilities).
        
        Args:
            api_key: Your Contextual AI API key
            name: Custom name for the tool
            description: Custom description for the tool
            **kwargs: Additional arguments passed to the tool
            
        Returns:
            ContextualTool instance configured for parsing only
        """
        return cls(
            api_key=api_key,
            name=name or "Contextual AI Document Parser",
            description=description or "Use this tool to parse documents using Contextual AI's parsing service",
            **kwargs
        )

    def rerank_documents(
        self,
        query: str,
        documents: List[str],
        instruction: Optional[str] = None,
        metadata: Optional[List[str]] = None,
        model: str = "ctxl-rerank-en-v1-instruct"
    ) -> dict:
        """
        Rerank documents using Contextual AI's instruction-following reranker.
        
        Args:
            query: The search query to rerank documents against
            documents: List of document texts to rerank
            instruction: Optional instruction for reranking behavior
            metadata: Optional list of metadata for each document
            model: Reranker model to use (default: "ctxl-rerank-en-v1-instruct")
            
        Returns:
            Dictionary containing reranked documents with scores
        """
        try:
            import requests
            import json
            
            base_url = "https://api.contextual.ai/v1"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "query": query,
                "documents": documents,
                "model": model
            }
            
            if instruction:
                payload["instruction"] = instruction
            
            if metadata:
                if len(metadata) != len(documents):
                    raise ValueError("Metadata list must have the same length as documents list")
                payload["metadata"] = metadata
            
            rerank_url = f"{base_url}/rerank"
            result = requests.post(rerank_url, json=payload, headers=headers)
            
            if result.status_code != 200:
                raise RuntimeError(f"Reranker API returned status {result.status_code}: {result.text}")
            
            return result.json()
            
        except Exception as e:
            raise RuntimeError(f"Failed to rerank documents: {str(e)}")

    @classmethod
    def create_reranker_only(
        cls,
        api_key: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> "ContextualTool":
        """
        Create a ContextualTool for document reranking only.
        
        Args:
            api_key: Your Contextual AI API key
            name: Custom name for the tool
            description: Custom description for the tool
            **kwargs: Additional arguments passed to the tool
            
        Returns:
            ContextualTool instance configured for reranking only
        """
        return cls(
            api_key=api_key,
            name=name or "Contextual AI Document Reranker",
            description=description or "Use this tool to rerank documents using Contextual AI's instruction-following reranker",
            **kwargs
        )