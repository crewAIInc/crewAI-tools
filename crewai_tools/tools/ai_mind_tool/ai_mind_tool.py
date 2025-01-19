import os
import secrets
from typing import Any, Dict, List, Optional, Text, Type

from crewai.tools import BaseTool
from openai import OpenAI
from pydantic import BaseModel


class AIMindToolConstants:
    MINDS_API_BASE_URL = "https://mdb.ai/"


class AIMindToolInputSchema(BaseModel):
    """Input for AIMind Tool."""

    query: str = "Question in natural language to ask the AI-Mind"


class AIMindTool(BaseTool):
    name: str = "AIMind Tool"
    description: str = (
        "A wrapper around [AI-Minds](https://mindsdb.com/minds). "
        "Useful for when you need answers to questions from your data, stored in "
        "data sources including PostgreSQL, MySQL, MariaDB, ClickHouse, Snowflake "
        "and Google BigQuery. "
        "Input should be a question in natural language."
    )
    args_schema: Type[BaseModel] = AIMindToolInputSchema
    api_key: Optional[str] = None
    datasources: Optional[List[Dict[str, Any]]] = None
    mind_name: Optional[Text] = None

    def __init__(self, name: Text, api_key: Optional[Text] = None, **kwargs):
        super().__init__(**kwargs)
        if name is None:
            raise ValueError("Name of the Mind must be provided.")
        else:
            self.mind_name = name

        self.api_key = api_key or os.getenv("MINDS_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided either through constructor or MINDS_API_KEY environment variable.")

        try:
            from minds.client import Client  # type: ignore
            from minds.datasources import DatabaseConfig  # type: ignore
            from minds.exceptions import ObjectNotFound  # type: ignore
        except ImportError:
            raise ImportError(
                "`minds_sdk` package not found, please run `pip install minds-sdk`"
            )

        minds_client = Client(api_key=self.api_key)

        # Check if the Mind already exists.
        try:
            # If the Mind already exists, only the name is required.
            if minds_client.minds.get(self.mind_name) and self.datasources:
                raise ValueError(
                    f"The Mind with the name '{self.name}' already exists."
                    "Only the name is required to initialize an existing Mind."
                )
            return
        except ObjectNotFound:
            # If the data sources are not provided, raise an error.
            if not self.datasources:
                raise ValueError(
                    "At least one data source should be configured to create a Mind."
                )

        # Convert the datasources to DatabaseConfig objects.
        datasources = []
        for datasource in self.datasources:
            config = DatabaseConfig(
                name=datasource["name"],
                engine=datasource["engine"],
                description=datasource["description"],
                connection_data=datasource["connection_data"],
                tables=datasource["tables"],
            )
            datasources.append(config)

        mind = minds_client.minds.create(
            name=name, datasources=datasources, replace=True
        )

        self.mind_name = mind.name

    def _run(
        self,
        query: Text
    ):
        # Run the query on the AI-Mind.
        # The Minds API is OpenAI compatible and therefore, the OpenAI client can be used.
        openai_client = OpenAI(base_url=AIMindToolConstants.MINDS_API_BASE_URL, api_key=self.api_key)

        completion = openai_client.chat.completions.create(
            model=self.mind_name,
            messages=[{"role": "user", "content": query}],
            stream=False,
        )

        return completion.choices[0].message.content