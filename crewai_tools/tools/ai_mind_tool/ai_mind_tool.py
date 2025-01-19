import os
from typing import Any, Dict, List, Optional, Type, Union

from crewai.tools import BaseTool
from openai import OpenAI
from pydantic import BaseModel, SecretStr


def convert_to_secret_str(value: Union[SecretStr, str]) -> SecretStr:
    """Convert a string to a SecretStr if needed.

    Args:
        value (Union[SecretStr, str]): The value to convert.

    Returns:
        SecretStr: The SecretStr value.
    """
    if isinstance(value, SecretStr):
        return value
    return SecretStr(value)


class AIMindToolConstants:
    MINDS_API_BASE_URL = "https://mdb.ai/"


class AIMindToolInputSchema(BaseModel):
    """Input for AIMind Tool."""

    query: str = "Question in natural language to ask the AI-Mind"


class AIMindEnvVar:
    """
    The loader for environment variables used by the AIMindTool.
    """

    value: Union[str, SecretStr]

    def __init__(self, name: str, is_secret: bool = False) -> None:
        if is_secret:
            self.value = convert_to_secret_str(os.environ[name])
        else:
            self.value = os.environ[name]


class AIMindDataSource(BaseModel):
    """
    The configuration for data sources used by the AIMindTool.
    """

    name: str
    minds_api_key = None
    engine: Optional[str] = None
    description: Optional[str] = ""
    connection_data: Optional[Dict[str, Any]] = {}
    tables: Optional[List[str]] = []

    def __init__(self, **data: Any) -> None:
        """
        Initializes the data source configuration.
        Validates the API key is available and the name is set.
        Creates the data source if it does not exist.

        There are two ways to initialize the data source:
        1. If the data source already exists, only the name is required.
        2. If the data source does not exist, the following are required:
            - name
            - engine
            - description
            - connection_data

        The tables are optional and can be provided if the data source does not exist.
        """
        super().__init__(**data)

        # Validate that the API key is provided.
        self.minds_api_key = convert_to_secret_str(
            os.getenv("MINDS_API_KEY") or self.minds_api_key
        )

        try:
            from minds.client import Client  # type: ignore
            from minds.datasources import DatabaseConfig  # type: ignore
            from minds.exceptions import ObjectNotFound  # type: ignore
        except ImportError:
            raise ImportError(
                "`minds_sdk` package not found, please run `pip install minds-sdk`"
            )

        # Create a Minds client.
        minds_client = Client(
            self.minds_api_key.get_secret_value(),
            # self.minds_api_base
        )

        # Check if the data source already exists.
        try:
            # If the data source already exists, only the name is required.
            if minds_client.datasources.get(self.name) and (
                self.engine or self.description or self.connection_data
            ):
                raise ValueError(
                    f"The data source with the name '{self.name}' already exists."
                    "Only the name is required to initialize an existing data source."
                )
            return
        except ObjectNotFound:
            # If the parameters for creating the data source are not provided,
            # raise an error.
            if not self.engine or not self.connection_data:
                raise ValueError(
                    "The required parameters for creating the data source are not"
                    " provided."
                )

        # Convert the parameters set as environment variables to the actual values.
        connection_data = {}
        for key, value in (self.connection_data or {}).items():
            if isinstance(value, AIMindEnvVar):
                connection_data[key] = (
                    value.value.get_secret_value()
                    if isinstance(value.value, SecretStr)
                    else value.value
                )
            else:
                connection_data[key] = value

        # Create the data source.
        minds_client.datasources.create(
            DatabaseConfig(
                name=self.name,
                engine=self.engine,
                description=self.description,
                connection_data=connection_data,
                tables=self.tables,
            )
        )


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
    datasources: Optional[AIMindDataSource] = None
    mind_name: Optional[str] = None

    def __init__(self, name: str, api_key: Optional[str] = None, **kwargs):
        """
        Initializes the AIMindTool.
        Validates the API key is available and the name is set.
        Creates the Mind and adds the data sources to it.
        Initializes the OpenAI client used to interact with the created Mind.

        There are two ways to initialize the AIMindTool:
        1. If the Mind already exists, only the name is required.
        2. If the Mind does not exist, data sources are required.
        """
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

        # Create the Mind.
        mind = minds_client.minds.create(name=self.mind_name)

        # Add the data sources to the Mind.
        for data_source in self.datasources or []:
            mind.add_datasource(data_source.name)

    def _run(
        self,
        query: str
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