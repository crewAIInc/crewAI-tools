from enum import Enum
from typing import Any, Optional, Type, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool, EnvVar
import os

try:
    from desearch_py import Desearch

    DESEARCH_INSTALLED = True
except ImportError:
    Desearch = Any
    DESEARCH_INSTALLED = False


class DesearchToolEnum(str, Enum):
    web = "web"
    hacker_news = "hackernews"
    reddit = "reddit"
    wikipedia = "wikipedia"
    youtube = "youtube"
    twitter = "twitter"
    arxiv = "arxiv"


class DesearchModelEnum(Enum):
    NOVA = "NOVA"
    ORBIT = "ORBIT"
    HORIZON = "HORIZON"


class DesearchDateFilterEnum(Enum):
    PAST_24_HOURS = "PAST_24_HOURS"
    PAST_2_DAYS = "PAST_2_DAYS"
    PAST_WEEK = "PAST_WEEK"
    PAST_2_WEEKS = "PAST_2_WEEKS"
    PAST_MONTH = "PAST_MONTH"
    PAST_2_MONTHS = "PAST_2_MONTHS"
    PAST_YEAR = "PAST_YEAR"
    PAST_2_YEARS = "PAST_2_YEARS"


class DesearchBaseToolSchema(BaseModel):
    prompt: str = Field(
        ...,
        description="Search query prompt",
        example="Bittensor",
    )
    tools: Optional[List[DesearchToolEnum]] = Field(
        [DesearchToolEnum.web.value, DesearchToolEnum.twitter.value],
        description="A list of tools to be used for the search",
        example=[
            DesearchToolEnum.web.value,
            DesearchToolEnum.hacker_news.value,
            DesearchToolEnum.reddit.value,
            DesearchToolEnum.wikipedia.value,
            DesearchToolEnum.youtube.value,
            DesearchToolEnum.twitter.value,
            DesearchToolEnum.arxiv.value,
        ],
    )
    model: Optional[DesearchModelEnum] = Field(
        DesearchModelEnum.NOVA,
        description="The model to be used for the search",
        example=DesearchModelEnum.NOVA,
    )

    date_filter: Optional[DesearchDateFilterEnum] = Field(
        DesearchDateFilterEnum.PAST_24_HOURS,
        description="The date filter to be used for the search",
        example=DesearchDateFilterEnum.PAST_24_HOURS,
    )


class DesearchTool(BaseTool):
    model_config = {"arbitrary_types_allowed": True}
    name: str = "DesearchTool"
    description: str = "Search the internet using Desearch"
    args_schema: Type[BaseModel] = DesearchBaseToolSchema
    client: Optional["Desearch"] = None

    package_dependencies: List[str] = ["desearch_py"]
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("DESEARCH_API_KEY"),
        description="API key for Desearch services",
        required=False,
    )
    env_vars: List[EnvVar] = [
        EnvVar(
            name="DESEARCH_API_KEY",
            description="API key for Desearch services",
            required=False,
        ),
    ]

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if not DESEARCH_INSTALLED:
            import click

            if click.confirm(
                "You are missing the 'desearch_py' package. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "add", "desearch_py"], check=True)

            else:
                raise ImportError(
                    "You are missing the 'desearch_py' package. Would you like to install it?"
                )
        self.client = Desearch(api_key=self.api_key)

    def _run(
        self,
        search_query: str,
        tools: Optional[List[DesearchToolEnum]] = [
            DesearchToolEnum.web.value,
            DesearchToolEnum.twitter.value,
        ],
        model: Optional[DesearchModelEnum] = DesearchModelEnum.NOVA,
        date_filter: Optional[
            DesearchDateFilterEnum
        ] = DesearchDateFilterEnum.PAST_24_HOURS,
    ) -> Any:
        if self.client is None:
            raise ValueError("Client not initialized")

        results = self.client.ai_search(
            prompt=search_query,
            tools=tools,
            model=model,
            date_filter=date_filter,
            streaming=False,
        )

        return results
