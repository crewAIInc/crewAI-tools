import re
import urllib.parse
from typing import Any, Dict, Optional, Type

from embedchain.loaders.mysql import MySQLLoader
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    ValidationInfo,
    field_validator,
)
from pydantic_core import PydanticCustomError

from ..rag.rag_tool import RagTool


class MySQLSearchToolSchema(BaseModel):
    """Input schema for the MySQLSearchTool."""

    search_query: str = Field(..., description="Mandatory semantic search query.")


class MySQLSearchTool(RagTool):
    """
    A tool for performing semantic searches on the content of a specific
    table within a MySQL database.

    Requires a database URI and table name during initialization. Data is
    loaded lazily upon the first search execution.
    """
    
    model_config = {"extra": "allow"}


    name: str = "Search MySQL Database Table Content"
    description: str = "Performs semantic search on a specific MySQL table's content."
    args_schema: Type[BaseModel] = MySQLSearchToolSchema
    db_uri: str = Field(
        ...,
        description=(
            "Mandatory database connection URI. Format: "
            "mysql://[user[:password]@]host[:port]/database."
        ),
    )
    table_name: str = Field(
        ...,
        description="The specific table name to search within the database.",
    )


    _mysql_loader: Optional[MySQLLoader] = PrivateAttr(default=None)
    _parsed_db_config: Optional[Dict[str, Any]] = PrivateAttr(default=None)
    _initial_data_added: bool = PrivateAttr(default=False)


    @field_validator("db_uri")
    @classmethod
    def _validate_db_uri_format(cls, v: str, info: ValidationInfo) -> str:
        """
        Validates the MySQL URI format using a regular expression.

        Args:
            v: The database URI string to validate.
            info: Pydantic validation information (unused here).

        Returns:
            The validated database URI string.

        Raises:
            PydanticCustomError: If the URI format is invalid.
        """
        try:
            cls._parse_uri_to_config(v)
            return v
        except ValueError as e:
            raise PydanticCustomError(
                "value_error",
                "Invalid MySQL URI: {error}. Expected format: "
                "mysql://[user[:password]@]host[:port]/database. "
                "Ensure all parts are present and correctly formatted. "
                "URL-encode special characters if needed.",
                {"error": str(e)},
            ) from e
        except Exception as e:
            raise PydanticCustomError(
                "value_error",
                "An unexpected error occurred validating the MySQL URI: '{uri}'.",
                {"uri": v},
            ) from e


    def model_post_init(self, __context: Any) -> None:
        """
        Initializes the MySQL loader after Pydantic validation.

        Parses the validated URI, creates the MySQLLoader instance, and
        updates the tool's description. Defers adding data until the first run.

        Args:
            __context: Pydantic model validation context (unused here).

        Raises:
            RuntimeError: If URI parsing or loader initialization fails.
        """
        try:
            self._parsed_db_config = self._parse_uri_to_config(self.db_uri)
        except ValueError as e:
            raise RuntimeError(
                f"Could not parse database URI '{self.db_uri}' "
                f"during tool initialization: {e}"
            ) from e

        if not self._parsed_db_config:
            raise RuntimeError("Database configuration parsing failed unexpectedly.")

        # Initialize the Embedchain MySQLLoader
        try:
            self._mysql_loader = MySQLLoader(config=self._parsed_db_config)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize the underlying MySQLLoader: {e}"
            ) from e

        self.description = (
            f"Performs semantic search on the '{self.table_name}' table "
            f"in the specified MySQL database. Input is the search query."
        )


    @staticmethod
    def _validate_mysql_scheme(uri: str) -> None:
        """
        Validates that the URI uses the mysql scheme.
        
        Args:
            uri: The URI to validate.
            
        Raises:
            ValueError: If the URI does not use the mysql scheme.
        """
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != "mysql":
            raise ValueError(
                f"Invalid scheme: '{parsed.scheme}'. Expected 'mysql'."
            )
    
    @staticmethod
    def _parse_uri_to_config(db_uri: str) -> Dict[str, Any]:
        """
        Parses a MySQL URI into a config dictionary for MySQLLoader.

        Handles special characters in passwords and optional components
        like username, password, and port.

        Args:
            db_uri: The MySQL connection string (e.g.,
                    mysql://user:pass@host:port/db).

        Returns:
            A dictionary with 'host', 'port', 'database', and optionally
            'user' and 'password'.

        Raises:
            ValueError: If the URI format is invalid or missing required parts
                        (host, database).
        """
        MySQLSearchTool._validate_mysql_scheme(db_uri)
        
        parts = db_uri.split("://", 1)
        if len(parts) != 2:
            raise ValueError("Invalid URI format: missing scheme separator '://'")
        
        scheme, rest = parts
        
        last_at_pos = rest.rfind("@")
        
        if last_at_pos == -1:
            auth = None
            host_part = rest
        else:
            auth = rest[:last_at_pos]
            host_part = rest[last_at_pos + 1:]
        
        if "/" not in host_part:
            raise ValueError("Database name missing in the URI path.")
        
        host_port, path = host_part.split("/", 1)
        database = path.split("?")[0].split("#")[0]  # Remove query/fragment
        
        if not database:
            raise ValueError("Database name missing in the URI path.")
        
        if ":" in host_port:
            hostname, port_str = host_port.split(":", 1)
        else:
            hostname, port_str = host_port, ""
        
        if not hostname:
            raise ValueError("Hostname missing in the URI.")
        
        username = None
        password = None
        if auth:
            if ":" in auth:
                username, password = auth.split(":", 1)
            else:
                username = auth
        
        try:
            port = int(port_str) if port_str else 3306  # Default MySQL port
        except ValueError:
            raise ValueError(f"Invalid port number: '{port_str}'. Port must be numeric.") from None
        
        config: Dict[str, Any] = {
            "host": hostname,
            "port": port,
            "database": database,
        }
        if username is not None:
            config["user"] = username
            if password is not None:
                config["password"] = password
        
        return config


    def add(self, table_name: Optional[str] = None) -> None:
        """
        Adds data from a MySQL table to the RAG adapter.

        Defaults to the table specified during tool initialization if
        `table_name` is not provided.

        Args:
            table_name: The name of the table to load data from.

        Raises:
            ValueError: If no table name can be determined.
            RuntimeError: If the loader/adapter isn't ready or adding fails.
        """
        target_table = table_name or self.table_name
        if not target_table:
            raise ValueError("Table name must be provided during init or to add().")

        if not self._mysql_loader:
            raise RuntimeError("MySQLLoader is not initialized.")
        if not hasattr(self.adapter, "add"):
            adapter_type = type(self.adapter).__name__
            raise RuntimeError(
                f"Configured adapter ('{adapter_type}') lacks 'add' method."
            )
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            raise RuntimeError(
                "RAG adapter placeholder detected. Tool not fully initialized."
            )

        query = f"SELECT * FROM `{target_table}`;"

        try:
            self.adapter.add(query, data_type="mysql", loader=self._mysql_loader)

            if target_table == self.table_name:
                self._initial_data_added = True
        except NotImplementedError:
            adapter_type = type(self.adapter).__name__
            raise RuntimeError(
                f"Adapter '{adapter_type}' claims 'add' but did not implement it."
            ) from None
        except Exception as e:
            raise RuntimeError(
                f"Failed to add data from table '{target_table}': {e}"
            ) from e

    def _run(self, search_query: str) -> str:
        """
        Executes the semantic search query against the configured table.

        Loads data lazily on the first call if it hasn't been loaded yet.

        Args:
            search_query: The semantic query string.

        Returns:
            A string containing the relevant search results, or an
            error message if the search fails.

        Raises:
            RuntimeError: If lazy loading of initial data fails.
            NotImplementedError: If the adapter's query method isn't implemented.
        """
        if not self._initial_data_added:
            try:
                self.add()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to automatically load initial data for table "
                    f"'{self.table_name}' before query execution: {e}"
                ) from e

        try:
            result = super()._run(query=search_query)
            return result
        except NotImplementedError:
            adapter_type = type(self.adapter).__name__
            raise NotImplementedError(
                f"The configured RAG adapter ('{adapter_type}') does not "
                f"implement the required 'query' method."
            )
        except Exception as e:
            return (
                f"Error executing search query '{search_query}' on table "
                f"'{self.table_name}'. Failed to retrieve results. "
                f"Details: {type(e).__name__}"  # Avoid leaking full error details
            )
