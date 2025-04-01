from typing import Any, Dict, Optional, Type, Union

from embedchain.models.data_type import DataType
from pydantic import BaseModel, Field, model_validator

from ..rag.rag_tool import RagTool


class FixedJSONSearchToolSchema(BaseModel):
    """Input for JSONSearchTool."""

    search_query: Union[str, Dict[str, Any]] = Field(
        ...,
        description="Mandatory search query as either a string or a dictionary with 'description' key",
    )

    @model_validator(mode="after")
    def validate_search_query(self):
        """Validate and convert search_query to string format."""
        if isinstance(self.search_query, dict):
            if "description" not in self.search_query:
                raise ValueError("Dictionary input must contain a 'description' key")
            if not isinstance(self.search_query["description"], str):
                raise ValueError("Description value must be a string")
            self.search_query = self.search_query["description"]
        elif not isinstance(self.search_query, str):
            raise ValueError("search_query must be a string or a dictionary with a 'description' key")
        return self


class JSONSearchToolSchema(FixedJSONSearchToolSchema):
    """Input for JSONSearchTool."""

    json_path: str = Field(..., description="Mandatory json path you want to search")


class JSONSearchTool(RagTool):
    name: str = "Search a JSON's content"
    description: str = (
        "A tool that can be used to semantic search a query from a JSON's content."
    )
    args_schema: Type[BaseModel] = JSONSearchToolSchema

    def __init__(self, json_path: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if json_path is not None:
            kwargs["data_type"] = DataType.JSON
            self.add(json_path)
            self.description = f"A tool that can be used to semantic search a query the {json_path} JSON's content."
            self.args_schema = FixedJSONSearchToolSchema
            self._generate_description()

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
        if "json_path" in kwargs:
            self.add(kwargs["json_path"])

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query, **kwargs)
