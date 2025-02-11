import re
from functools import lru_cache
from typing import Any, List, Optional, Type

from embedchain.loaders.github import GithubLoader
from pydantic import BaseModel, Field, field_validator, model_validator

from ..rag.rag_tool import RagTool


class FixedGithubSearchToolSchema(BaseModel):
    """Input for GithubSearchTool."""
    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the github repo's content",
    )
    gh_token: str = Field(
        ...,
        description="GitHub token for authentication",
        pattern=r'^gh[ps]_[a-zA-Z0-9]{36}$'
    )
    content_types: List[str] = Field(
        ...,
        description="Content types to be included in search, options: [code, repo, pr, issue]",
        json_schema_extra={"allowed_values": ["code", "repo", "pr", "issue"]}
    )
    gh_token: str = Field(
        ...,
        description="GitHub token for authentication",
        pattern=r'^gh[ps]_[a-zA-Z0-9]{36}$'
    )
    content_types: List[str] = Field(
        ...,
        description="Content types to be included in search, options: [code, repo, pr, issue]",
        json_schema_extra={"allowed_values": ["code", "repo", "pr", "issue"]}
    )

    @field_validator('content_types')
    @classmethod
    def validate_content_types(cls, v: List[str]) -> List[str]:
        """Validate content types are from allowed values."""
        allowed = {'code', 'repo', 'pr', 'issue'}
        if not all(t in allowed for t in v):
            raise ValueError(f"Invalid content types. Must be one of: {list(allowed)}")
        return v

    @field_validator('gh_token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate GitHub token format."""
        if not v:
            raise ValueError("GitHub token is required")
        if not re.match(r'^gh[ps]_[a-zA-Z0-9]{36}$', v):
            raise ValueError("Invalid GitHub token format. Must start with 'ghp_' or 'ghs_' followed by 36 alphanumeric characters")
        return v



class GithubSearchToolSchema(FixedGithubSearchToolSchema):
    """Input for GithubSearchTool."""
    github_repo: str = Field(
        ...,
        description="GitHub repository to search",
    )


# Cache for query results to improve performance
_query_cache = {}
MAX_CACHE_SIZE = 100

class GithubSearchTool(RagTool):
    name: str = "Search a github repo's content"
    description: str = "A tool that can be used to semantic search a query from a github repo's content. This is not the GitHub API, but instead a tool that can provide semantic search capabilities."
    summarize: bool = False
    args_schema: Type[BaseModel] = GithubSearchToolSchema
    gh_token: str = Field(..., pattern=r'^gh[ps]_[a-zA-Z0-9]{36}$')
    content_types: List[str] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": False,
        "extra": "allow",
        "protected_namespaces": ()
    }



    @field_validator('content_types')
    @classmethod
    def validate_content_types(cls, v: List[str]) -> List[str]:
        """Validate content types are from allowed values."""
        allowed = {'code', 'repo', 'pr', 'issue'}
        if not all(t in allowed for t in v):
            raise ValueError(f"Invalid content types. Must be one of: {list(allowed)}")
        return v

    @field_validator('gh_token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate GitHub token format."""
        if not v:
            raise ValueError("GitHub token is required")
        if not re.match(r'^gh[ps]_[a-zA-Z0-9]{36}$', v):
            raise ValueError("Invalid GitHub token format. Must start with 'ghp_' or 'ghs_' followed by 36 alphanumeric characters")
        return v

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._github_repo = None

    def __init__(self, github_repo: Optional[str] = None, gh_token: Optional[str] = None, content_types: Optional[List[str]] = None, **kwargs: Any) -> None:
        if gh_token:
            kwargs["gh_token"] = gh_token
        if content_types:
            kwargs["content_types"] = content_types
        super().__init__(**kwargs)
        
        self._github_loader = None
        if github_repo is not None:
            self._github_repo = github_repo
            kwargs["data_type"] = "github"
            self._github_loader = GithubLoader(config={"token": self.gh_token})
            kwargs["loader"] = self._github_loader
            self.add(repo=github_repo)
            self.description = f"A tool that can be used to semantic search a query from the {github_repo} github repo's content. This is not the GitHub API, but instead a tool that can provide semantic search capabilities."
            self.args_schema = FixedGithubSearchToolSchema
            self._generate_description()

    def add(
        self,
        repo: str,
        content_types: List[str] | None = None,
        **kwargs: Any,
    ) -> None:
        types = content_types or self.content_types
        if not types:
            types = ["code"]  # Default to code if no content types specified

        super().add(f"repo:{repo} type:{','.join(types)}", **kwargs)

    def _sanitize_query(self, query: str) -> str:
        """Sanitize the search query to handle edge cases."""
        # Remove potentially problematic characters
        sanitized = re.sub(r'[^\w\s-]', '', query)
        # Limit query length
        return sanitized[:1000]  # GitHub's max query length

    def _get_cache_key(self, query: str, repo: str) -> str:
        """Generate a cache key for the query."""
        return f"{repo}:{query}"

    def _before_run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        if "github_repo" in kwargs:
            kwargs["data_type"] = "github"
            if not hasattr(self, '_github_loader'):
                self._github_loader = GithubLoader(config={"token": self.gh_token})
            kwargs["loader"] = self._github_loader
            self.add(
                repo=kwargs["github_repo"], content_types=kwargs.get("content_types")
            )
        return super()._before_run(query=query, **kwargs)

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        sanitized_query = self._sanitize_query(search_query)
        repo = kwargs.get("github_repo", "")
        cache_key = self._get_cache_key(sanitized_query, repo)
        
        if cache_key in _query_cache:
            return _query_cache[cache_key]
            
        if "github_repo" in kwargs:
            kwargs["data_type"] = "github"
            if not hasattr(self, '_github_loader'):
                self._github_loader = GithubLoader(config={"token": self.gh_token})
            kwargs["loader"] = self._github_loader
            self.add(
                repo=kwargs["github_repo"], content_types=kwargs.get("content_types")
            )
            
        result = f"Relevant Content:\n{self.adapter.query(sanitized_query)}"
        
        if len(_query_cache) < MAX_CACHE_SIZE:
            _query_cache[cache_key] = result
            
        return result
