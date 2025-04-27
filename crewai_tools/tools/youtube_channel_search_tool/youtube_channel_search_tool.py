from typing import Any, Optional, Type

from embedchain.models.data_type import DataType
from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool


class FixedYoutubeChannelSearchToolSchema(BaseModel):
    """Input for YoutubeChannelSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the Youtube Channels content",
    )


class YoutubeChannelSearchToolSchema(FixedYoutubeChannelSearchToolSchema):
    """Input for YoutubeChannelSearchTool."""

    youtube_channel: str = Field(
        ..., description="Mandatory youtube_channel path you want to search"
    )


class YoutubeChannelSearchTool(RagTool):
    name: str = "Search a Youtube Channels content"
    description: str = (
        "A tool that can be used to semantic search a query from a Youtube Channels content."
    )
    args_schema: Type[BaseModel] = YoutubeChannelSearchToolSchema

    def __init__(self, youtube_channel: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if youtube_channel is not None:
            self.add(youtube_channel)
            self.description = f"A tool that can be used to semantic search a query the {youtube_channel} Youtube Channels content."
            self.args_schema = FixedYoutubeChannelSearchToolSchema
            self._generate_description()

    def add(
        self,
        youtube_channel: str,
    ) -> None:
        if not youtube_channel.startswith("@"):
            youtube_channel = f"@{youtube_channel}"
        super().add(youtube_channel, data_type=DataType.YOUTUBE_CHANNEL)

    def _run(
        self,
        search_query: str,
        youtube_channel: Optional[str] = None,
    ) -> str:
        if youtube_channel is not None:
            self.add(youtube_channel)
        return super()._run(query=search_query)
