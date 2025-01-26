import os
from typing import Any, Literal, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DappierAIRecommendationsToolSchema(BaseModel):
    query: str = Field(
        description="The user-provided input string for AI recommendations across Sports, Lifestyle News, and niche favorites like I Heart Dogs, I Heart Cats, WishTV, and many more."
    )
    data_model_id: str = Field(
        default="dm_01j0pb465keqmatq9k83dthx34",
        description="The data model ID to use for recommendations. Data model IDs always start with the prefix 'dm_'. Defaults to 'dm_01j0pb465keqmatq9k83dthx34'. Multiple AI models are available, which can be found at: https://marketplace.dappier.com/marketplace",
    )
    similarity_top_k: int = Field(
        default=9,
        description="The number of top documents to retrieve based on similarity. Defaults to 9.",
    )
    ref: Optional[str] = Field(
        default=None,
        description="The site domain where AI recommendations should be displayed. Defaults to None.",
    )
    num_articles_ref: int = Field(
        default=0,
        description="The minimum number of articles to return from the specified reference domain (`ref`). The remaining articles will come from other sites in the RAG model. Defaults to 0.",
    )
    search_algorithm: Literal[
        "most_recent", "semantic", "most_recent_semantic", "trending"
    ] = Field(
        default="most_recent",
        description="The search algorithm to use for retrieving articles. Defaults to 'most_recent'.",
    )


class DappierAIRecommendationsTool(BaseTool):
    """DappierAIRecommendationsTool

    Search ai recommendations accross Sports and Lifestyle News to niche favorites like I Heart Dogs, I Heart Cats, WishTV and many more.
    Requires the `dappier` package.
    Get your API Key from https://platform.dappier.com/profile/api-keys

    Args:
        api_key: The Dappier API key, can be set as an environment variable `DAPPIER_API_KEY` or passed directly
    """

    name: str = "Dappier ai recommendations tool"
    description: str = "Search ai recommendations accross Sports and Lifestyle News to niche favorites like I Heart Dogs, I Heart Cats, WishTV and many more."
    args_schema: Type[BaseModel] = DappierAIRecommendationsToolSchema
    api_key: Optional[str] = None
    dappier_client: Optional[Any] = None

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ["DAPPIER_API_KEY"]

        try:
            from dappier import Dappier
        except ImportError:
            raise ImportError(
                "`dappier` package not found, please run `pip install dappier`"
            )

        if not self.api_key:
            raise ValueError(
                "DAPPIER_API_KEY is not set. Please provide it either via the constructor with the `api_key` argument or by setting the DAPPIER_API_KEY environment variable."
            )

        self.dappier_client = Dappier(api_key=self.api_key)

    def _run(
        self,
        query: str,
        data_model_id: str = "dm_01j0pb465keqmatq9k83dthx34",
        similarity_top_k: int = 9,
        ref: Optional[str] = None,
        num_articles_ref: int = 0,
        search_algorithm: Literal[
            "most_recent", "semantic", "most_recent_semantic", "trending"
        ] = "most_recent",
    ):
        try:
            response = self.dappier_client.get_ai_recommendations(  # type: ignore
                query=query,
                data_model_id=data_model_id,
                similarity_top_k=similarity_top_k,
                ref=ref,
                num_articles_ref=num_articles_ref,
                search_algorithm=search_algorithm,
            )

            if response is None or response.status != "success":
                return {"error": "An unknown error occurred."}

            # Collect only relevant information from the response.
            results = [
                {
                    "author": result.author,
                    "image_url": result.image_url,
                    "pubdate": result.pubdate,
                    "source_url": result.source_url,
                    "summary": result.summary,
                    "title": result.title,
                }
                for result in (getattr(response.response, "results", None) or [])
            ]

            return results

        except Exception as e:
            return {"error": f"An unexpected error occurred: {e!s}"}
