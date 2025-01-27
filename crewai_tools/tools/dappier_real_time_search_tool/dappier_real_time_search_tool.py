import os
from typing import Any, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DappierRealTimeSearchToolSchema(BaseModel):
    query: str = Field(
        description="The user-provided input string for retrieving real-time data, including web search results, financial information, news, weather, and more, with AI-powered insights and updates."
    )
    ai_model_id: str = Field(
        default="am_01j06ytn18ejftedz6dyhz2b15",
        description="The AI model ID to use for the query. The AI model ID always starts with the prefix 'am_'. Defaults to 'am_01j06ytn18ejftedz6dyhz2b15'. Multiple AI models are available, which can be found at: https://marketplace.dappier.com/marketplace",
    )


class DappierRealTimeSearchTool(BaseTool):
    """DappierRealTimeSearchTool

    Search real time data, including web search results, financial information, news, weather, and more, with AI-powered insights and updates.
    Requires the `dappier` package.
    Get your API Key from https://platform.dappier.com/profile/api-keys

    Args:
        api_key: The Dappier API key, can be set as an environment variable `DAPPIER_API_KEY` or passed directly
    """

    name: str = "Dappier real time search tool"
    description: str = "Search real time data, including web search results, financial information, news, weather, and more, with AI-powered insights and updates."
    args_schema: Type[BaseModel] = DappierRealTimeSearchToolSchema
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

    def _run(self, query: str, ai_model_id: str = "am_01j06ytn18ejftedz6dyhz2b15"):
        try:
            response = self.dappier_client.search_real_time_data(query=query, ai_model_id=ai_model_id)  # type: ignore
            return response.message
        except ConnectionError as e:
            return f"Failed to connect to Dappier API: {e}"
        except ValueError as e:
            return f"Invalid input parameters: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
