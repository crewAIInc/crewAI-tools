from typing import Any, Callable
import logging
from elasticsearch import Elasticsearch, ConnectionError, AuthenticationError, NotFoundError
from openai import Client as OpenAIClient
from pydantic import Field, PrivateAttr, validator

from crewai_tools.tools.rag.rag_tool import Adapter

logger = logging.getLogger(__name__)


def _default_embedding_function():
    client = OpenAIClient()

    def _embedding_function(input):
        rs = client.embeddings.create(input=input, model="text-embedding-ada-002")
        return [record.embedding for record in rs.data]

    return _embedding_function


class ElasticsearchAdapter(Adapter):
    es_url: str
    index_name: str
    embedding_function: Callable = Field(default_factory=_default_embedding_function)
    api_key: str | None = None
    username: str | None = None
    password: str | None = None
    cloud_id: str | None = None
    top_k: int = Field(default=3, gt=0)
    
    _client: Elasticsearch = PrivateAttr()
    
    @validator("es_url")
    def validate_es_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("es_url must start with http:// or https://")
        return v
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize Elasticsearch client with authentication and validate connection."""
        try:
            auth_kwargs = {}
            if self.api_key:
                auth_kwargs["api_key"] = self.api_key
                logger.debug("Using API key authentication")
            elif self.username and self.password:
                auth_kwargs["basic_auth"] = (self.username, self.password)
                logger.debug("Using basic authentication")
            if self.cloud_id:
                auth_kwargs["cloud_id"] = self.cloud_id
                logger.debug("Using cloud ID configuration")
                
            logger.debug(f"Initializing Elasticsearch client for {self.es_url}")
            self._client = Elasticsearch(self.es_url, **auth_kwargs)
            
            # Validate connection and index existence
            if not self._client.ping():
                raise ConnectionError("Failed to connect to Elasticsearch")
            if not self._client.indices.exists(index=self.index_name):
                logger.warning(f"Index {self.index_name} does not exist")
                
            logger.info(f"Successfully connected to Elasticsearch at {self.es_url}")
            super().model_post_init(__context)
        except ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise RuntimeError(f"Failed to connect to Elasticsearch: {str(e)}")
        except AuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            raise RuntimeError(f"Failed to authenticate with Elasticsearch: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {str(e)}")
            raise RuntimeError(f"Elasticsearch initialization failed: {str(e)}")
    
    def query(self, question: str) -> str:
        """Query Elasticsearch using hybrid search (vector + text).
        
        Args:
            question: The search query text
            
        Returns:
            str: Concatenated text from the most relevant documents
            
        Raises:
            RuntimeError: If the query fails due to connection or other errors
        """
        try:
            query_vector = self.embedding_function([question])[0]
            logger.debug(f"Generated embedding for question: {question[:50]}...")
            
            response = self._client.search(
                index=self.index_name,
                body={
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "script_score": {
                                        "query": {"match_all": {}},
                                        "script": {
                                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                            "params": {"query_vector": query_vector}
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "text": {
                                            "query": question,
                                            "boost": 0.3
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "size": self.top_k
                }
            )
            
            hits = response["hits"]["hits"]
            total_hits = response["hits"]["total"]["value"]
            logger.info(f"Found {total_hits} total hits, returning top {len(hits)} results")
            
            if not hits:
                logger.warning("No results found for query")
                return ""
                
            return "\n".join(hit["_source"]["text"] for hit in hits)
            
        except ConnectionError as e:
            logger.error(f"Connection error during query: {str(e)}")
            raise RuntimeError(f"Failed to connect to Elasticsearch: {str(e)}")
        except NotFoundError as e:
            logger.error(f"Index not found: {str(e)}")
            raise RuntimeError(f"Index {self.index_name} not found: {str(e)}")
        except Exception as e:
            logger.error(f"Error during query: {str(e)}")
            raise RuntimeError(f"Elasticsearch query failed: {str(e)}")
    
    def add(self, texts: list[str], **kwargs: Any) -> None:
        """Add documents to Elasticsearch with embeddings.
        
        Args:
            texts: List of text documents to index
            **kwargs: Additional fields to store with each document
            
        Raises:
            RuntimeError: If document indexing fails
        """
        try:
            if not texts:
                logger.warning("No texts provided for indexing")
                return
                
            embeddings = self.embedding_function(texts)
            logger.debug(f"Generated embeddings for {len(texts)} documents")
            
            documents = []
            for text, embedding in zip(texts, embeddings):
                doc = {
                    "text": text,
                    "embedding": embedding,
                    **kwargs
                }
                documents.append(doc)
            
            actions = []
            for doc in documents:
                actions.extend([
                    {"index": {"_index": self.index_name}},
                    doc
                ])
            
            response = self._client.bulk(
                index=self.index_name,
                body=actions,
                refresh=True  # Ensure documents are searchable immediately
            )
            
            if response.get("errors"):
                error_items = [item for item in response["items"] if item.get("index", {}).get("error")]
                error_details = [f"{item['index']['error']['type']}: {item['index']['error']['reason']}" 
                               for item in error_items]
                error_msg = f"Bulk indexing had errors: {'; '.join(error_details)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
            logger.info(f"Successfully indexed {len(texts)} documents")
            
        except ConnectionError as e:
            logger.error(f"Connection error during indexing: {str(e)}")
            raise RuntimeError(f"Failed to connect to Elasticsearch: {str(e)}")
        except Exception as e:
            logger.error(f"Error during document indexing: {str(e)}")
            raise RuntimeError(f"Failed to index documents: {str(e)}")
