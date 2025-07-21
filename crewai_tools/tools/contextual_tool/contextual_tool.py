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
