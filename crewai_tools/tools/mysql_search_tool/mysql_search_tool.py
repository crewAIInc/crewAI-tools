from typing import Any, Type, Union

from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool

class FallbackMySQLLoader:
    def __init__(self, **kwargs):
        pass

try:
    from embedchain.loaders.mysql import MySQLLoader
except ImportError:
    MySQLLoader = FallbackMySQLLoader


class MySQLSearchToolSchema(BaseModel):
    """Input for MySQLSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory semantic search query you want to use to search the database's content",
    )


class MySQLSearchTool(RagTool):
    name: str = "Search a database's table content"
    description: str = "A tool that can be used to semantic search a query from a database table's content."
    args_schema: Type[BaseModel] = MySQLSearchToolSchema
    db_uri: str = Field(..., description="Mandatory database URI")

    def __init__(self, table_name: str, **kwargs):
        super().__init__(**kwargs)
        try:
            kwargs["data_type"] = "mysql"
            kwargs["loader"] = MySQLLoader(config=dict(url=self.db_uri))
            self.add(table_name)
            self.description = f"A tool that can be used to semantic search a query the {table_name} database table's content."
            self._generate_description()
        except NotImplementedError as e:
            raise ImportError("Embedchain is required for MySQLSearchTool to function. Please install it with 'pip install embedchain'") from e

    def add(
        self,
        table_name: str,
        **kwargs: Any,
    ) -> None:
        super().add(f"SELECT * FROM {table_name};", **kwargs)

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query)
