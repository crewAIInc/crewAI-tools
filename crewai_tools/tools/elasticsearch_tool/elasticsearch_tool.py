import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Type

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, ConfigDict, Field, SecretStr

try:
    from elasticsearch import AsyncElasticsearch
    from elasticsearch.exceptions import ConnectionError, RequestError

    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for search results
_search_cache = {}


class ElasticsearchConfig(BaseModel):
    """Configuration for Elasticsearch connection."""

    model_config = ConfigDict(protected_namespaces=())

    hosts: List[str] = Field(..., description="List of Elasticsearch hosts")
    username: Optional[str] = Field(None, description="Elasticsearch username")
    password: Optional[SecretStr] = Field(None, description="Elasticsearch password")
    api_key: Optional[SecretStr] = Field(None, description="Elasticsearch API key")
    cloud_id: Optional[str] = Field(None, description="Elasticsearch Cloud ID")
    verify_certs: bool = Field(True, description="Verify SSL certificates")
    default_index: Optional[str] = Field(None, description="Default index to search")

    @property
    def has_auth(self) -> bool:
        return bool((self.username and self.password) or self.api_key or self.cloud_id)

    def model_post_init(self, *args, **kwargs):
        if not self.hosts and not self.cloud_id:
            raise ValueError("Either hosts or cloud_id must be provided")


class ElasticsearchSearchToolInput(BaseModel):
    """Input schema for ElasticsearchSearchTool."""

    model_config = ConfigDict(protected_namespaces=())

    query: str = Field(
        ..., description="Elasticsearch query (JSON string or query string)"
    )
    index: Optional[str] = Field(None, description="Override default index")
    size: Optional[int] = Field(10, description="Maximum number of results")
    timeout: Optional[str] = Field("30s", description="Search timeout")
    routing: Optional[str] = Field(None, description="Routing value")


class ElasticsearchSearchTool(BaseTool):
    """Tool for executing searches on Elasticsearch."""

    name: str = "Elasticsearch Search"
    description: str = (
        "Execute searches on Elasticsearch using Query DSL or simple query string syntax. "
        "Supports both structured queries and natural language search."
    )
    args_schema: Type[BaseModel] = ElasticsearchSearchToolInput

    config: ElasticsearchConfig = Field(
        ..., description="Elasticsearch connection configuration"
    )
    pool_size: int = Field(default=5, description="Size of connection pool")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(
        default=1.0, description="Delay between retries in seconds"
    )
    enable_caching: bool = Field(
        default=True, description="Enable search result caching"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )

    _client: Optional[AsyncElasticsearch] = None
    _thread_pool: Optional[ThreadPoolExecutor] = None
    _model_rebuilt: bool = False

    def __init__(self, **data):
        """Initialize ElasticsearchSearchTool."""
        super().__init__(**data)
        self._initialize_elasticsearch()

    def _initialize_elasticsearch(self) -> None:
        """Initialize Elasticsearch client and resources."""
        try:
            if ELASTICSEARCH_AVAILABLE:
                self._thread_pool = ThreadPoolExecutor(max_workers=self.pool_size)
                self._create_client()
            else:
                raise ImportError
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'elasticsearch' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(
                        ["uv", "add", "elasticsearch"],
                        check=True,
                    )
                    self._thread_pool = ThreadPoolExecutor(max_workers=self.pool_size)
                    self._create_client()
                except subprocess.CalledProcessError:
                    raise ImportError("Failed to install Elasticsearch dependencies")
            else:
                raise ImportError(
                    "Elasticsearch dependencies not found. Please install them by running "
                    "`uv add elasticsearch`"
                )

    def _create_client(self) -> None:
        """Create Elasticsearch client with configured settings."""
        client_params = {
            "verify_certs": self.config.verify_certs,
        }

        if self.config.cloud_id:
            client_params["cloud_id"] = self.config.cloud_id
        else:
            client_params["hosts"] = self.config.hosts

        if self.config.username and self.config.password:
            client_params["basic_auth"] = (
                self.config.username,
                self.config.password.get_secret_value(),
            )
        elif self.config.api_key:
            client_params["api_key"] = self.config.api_key.get_secret_value()

        self._client = AsyncElasticsearch(**client_params)

    def _get_cache_key(self, query: str, index: str, size: int, timeout: str) -> str:
        """Generate a cache key for the search."""
        return f"{index}:{query}:{size}:{timeout}"

    async def _execute_search(
        self,
        query: str,
        index: Optional[str] = None,
        size: int = 10,
        timeout: str = "30s",
        routing: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a search with retries and return results."""

        search_index = index or self.config.default_index
        if not search_index:
            raise ValueError("No index specified and no default index configured")

        if self.enable_caching:
            cache_key = self._get_cache_key(query, search_index, size, timeout)
            if cache_key in _search_cache:
                logger.info("Returning cached result")
                return _search_cache[cache_key]

        for attempt in range(self.max_retries):
            try:
                # Try to parse as JSON query first
                try:
                    search_body = json.loads(query)
                except json.JSONDecodeError:
                    # Fall back to query string
                    search_body = {"query": {"query_string": {"query": query}}}

                search_params = {
                    "index": search_index,
                    "body": search_body,
                    "size": size,
                    "timeout": timeout,
                }

                if routing:
                    search_params["routing"] = routing

                results = await self._client.search(**search_params)

                if self.enable_caching:
                    _search_cache[
                        self._get_cache_key(query, search_index, size, timeout)
                    ] = results

                return results.raw

            except (ConnectionError, RequestError) as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (2**attempt))
                logger.warning(f"Search failed, attempt {attempt + 1}: {str(e)}")
                continue

    async def _run(
        self,
        query: str,
        index: Optional[str] = None,
        size: int = 10,
        timeout: str = "30s",
        routing: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Execute the search query."""

        try:
            results = await self._execute_search(
                query=query, index=index, size=size, timeout=timeout, routing=routing
            )
            return results
        except Exception as e:
            logger.error(f"Error executing search: {str(e)}")
            raise

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.close()
        if self._thread_pool:
            self._thread_pool.shutdown()

    def __del__(self):
        """Cleanup resources on deletion."""
        try:
            if self._client:
                asyncio.run(self._client.close())
            if self._thread_pool:
                self._thread_pool.shutdown()
        except Exception:
            pass


try:
    # Only rebuild if the class hasn't been initialized yet
    if not hasattr(ElasticsearchSearchTool, "_model_rebuilt"):
        ElasticsearchSearchTool.model_rebuild()
        ElasticsearchSearchTool._model_rebuilt = True
except Exception:
    pass
