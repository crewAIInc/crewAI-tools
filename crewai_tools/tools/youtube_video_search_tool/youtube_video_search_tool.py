from typing import Any, Optional, Type

from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool

class FallbackDataType:
    YOUTUBE_VIDEO = "youtube_video"

try:
    from embedchain.models.data_type import DataType
except ImportError:
    DataType = FallbackDataType


class FixedYoutubeVideoSearchToolSchema(BaseModel):
    """Input for YoutubeVideoSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the Youtube Video content",
    )


class YoutubeVideoSearchToolSchema(FixedYoutubeVideoSearchToolSchema):
    """Input for YoutubeVideoSearchTool."""

    youtube_video_url: str = Field(
        ..., description="Mandatory youtube_video_url path you want to search"
    )


class YoutubeVideoSearchTool(RagTool):
    name: str = "Search a Youtube Video content"
    description: str = "A tool that can be used to semantic search a query from a Youtube Video content."
    args_schema: Type[BaseModel] = YoutubeVideoSearchToolSchema

    def __init__(self, youtube_video_url: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if youtube_video_url is not None:
            try:
                kwargs["data_type"] = DataType.YOUTUBE_VIDEO
                self.add(youtube_video_url)
                self.description = f"A tool that can be used to semantic search a query the {youtube_video_url} Youtube Video content."
                self.args_schema = FixedYoutubeVideoSearchToolSchema
                self._generate_description()
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for YoutubeVideoSearchTool to function. Please install it with 'pip install embedchain'") from e

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().add(*args, **kwargs)

    def _before_run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        if "youtube_video_url" in kwargs:
            self.add(kwargs["youtube_video_url"])

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query, **kwargs)
