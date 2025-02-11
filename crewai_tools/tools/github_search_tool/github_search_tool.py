from typing import Any, List, Optional, Type

from embedchain.loaders.github import GithubLoader
from pydantic import BaseModel, Field

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
    )
    content_types: List[str] = Field(
        ...,
        description="Content types to be included in search, options: [code, repo, pr, issue]",
    )

class GithubSearchToolSchema(FixedGithubSearchToolSchema):
    """Input for GithubSearchTool."""
    github_repo: str = Field(
        ...,
        description="GitHub repository to search",
    )


class GithubSearchTool(RagTool):
    name: str = "Search a github repo's content"
    description: str = "A tool that can be used to semantic search a query from a github repo's content. This is not the GitHub API, but instead a tool that can provide semantic search capabilities."
    summarize: bool = False
    args_schema: Type[BaseModel] = GithubSearchToolSchema
    gh_token: str = Field(default="")
    content_types: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._github_repo = None

    def __init__(self, github_repo: Optional[str] = None, gh_token: Optional[str] = None, content_types: Optional[List[str]] = None, **kwargs):
        if gh_token:
            kwargs["gh_token"] = gh_token
        if content_types:
            kwargs["content_types"] = content_types
        super().__init__(**kwargs)
        
        if github_repo is not None:
            self._github_repo = github_repo
            kwargs["data_type"] = "github"
            kwargs["loader"] = GithubLoader(config={"token": self.gh_token})
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

    def _before_run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        if "github_repo" in kwargs:
            kwargs["data_type"] = "github"
            kwargs["loader"] = GithubLoader(config={"token": self.gh_token})
            self.add(
                repo=kwargs["github_repo"], content_types=kwargs.get("content_types")
            )

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query, **kwargs)
