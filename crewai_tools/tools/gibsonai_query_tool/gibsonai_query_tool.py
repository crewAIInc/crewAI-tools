import json
import os
from typing import Type, Optional, Any, Dict, List

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from crewai.tools import BaseTool, EnvVar

# Load environment variables from .env file
load_dotenv()


class GibsonAIQueryInput(BaseModel):
    """Input schema for GibsonAIQueryTool."""

    query: str = Field(
        description="SQL query to execute against the GibsonAI database. "
        "This should be a properly formatted SQL query (SELECT, INSERT, UPDATE, DELETE) "
        "that will be executed against your GibsonAI project database schema."
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional parameters for parameterized queries. "
        "Use this for prepared statements to avoid SQL injection.",
    )


class GibsonAIQueryTool(BaseTool):
    """
    Tool for executing SQL queries against GibsonAI database via hosted Data API.

    This tool allows you to execute SQL queries against your GibsonAI project database,
    supporting data operations including SELECT, INSERT, UPDATE, and DELETE.
    It works with any database schema deployed in your GibsonAI project.
    """

    name: str = "GibsonAIQueryTool"
    description: str = """
    Executes SQL queries against a GibsonAI database using the hosted Data API.
    
    This tool supports:
    - SELECT queries for data retrieval
    - INSERT queries for adding new data
    - UPDATE queries for modifying existing data  
    - DELETE queries for removing data
    - Parameterized queries for security
    
    The query should be properly formatted SQL that matches your GibsonAI project's schema.
    For parameterized queries, use the 'parameters' field to pass values safely.
    
    Example queries:
    - "SELECT * FROM users WHERE status = 'active'"
    - "INSERT INTO contacts (name, email) VALUES ('John Doe', 'john@example.com')"
    - "UPDATE products SET price = 99.99 WHERE id = 1"
    - "DELETE FROM orders WHERE created_at < '2023-01-01'"
    """
    args_schema: Type[BaseModel] = GibsonAIQueryInput
    env_vars: List[EnvVar] = [
        EnvVar(
            name="GIBSONAI_API_KEY",
            description="API key for GibsonAI Data API",
            required=True,
        ),
    ]

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        # Initialize API configuration
        self._api_base_url = "https://api.gibsonai.com/v1/-"
        self._api_key = api_key or os.getenv("GIBSONAI_API_KEY")

        if not self._api_key:
            raise ValueError(
                "Missing GIBSONAI_API_KEY. Please provide it as a parameter "
                "or set the GIBSONAI_API_KEY environment variable."
            )

    def _run(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute the SQL query against the GibsonAI database.

        Args:
            query: SQL query string to execute
            parameters: Optional parameters for parameterized queries

        Returns:
            String containing the query results or success/error message
        """
        try:
            # Prepare the request payload
            payload = {"query": query.strip()}

            if parameters:
                payload["parameters"] = parameters

            # Execute the query via GibsonAI Data API
            response = requests.post(
                f"{self._api_base_url}/query",
                json=payload,
                headers={
                    "X-Gibson-API-Key": self._api_key,
                    "Content-Type": "application/json",
                },
                timeout=30,
            )

            # Handle different response status codes
            if response.status_code == 200:
                result = response.json()
                return self._format_response(query, result)
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Bad request")
                return f"Error: Invalid query - {error_detail}"
            elif response.status_code == 401:
                return "Error: Unauthorized - Please check your GIBSONAI_API_KEY"
            elif response.status_code == 403:
                return "Error: Forbidden - Insufficient permissions for this operation"
            elif response.status_code == 404:
                return "Error: Not found - Check your API endpoint or project configuration"
            elif response.status_code == 500:
                return "Error: Internal server error - Please try again later"
            else:
                return f"Error: Unexpected response (Status {response.status_code}): {response.text}"

        except Exception as e:
            # Handle specific request exceptions
            if "Timeout" in str(type(e).__name__):
                return "Error: Request timeout - The query took too long to execute"
            elif "ConnectionError" in str(type(e).__name__):
                return "Error: Connection failed - Unable to reach GibsonAI API"
            elif "RequestException" in str(type(e).__name__):
                return f"Error: Request failed - {str(e)}"
            elif "JSONDecodeError" in str(type(e).__name__):
                return "Error: Invalid JSON response from API"
            else:
                return f"Error: Unexpected error occurred - {str(e)}"

    def _format_response(self, query: str, result: Dict[str, Any]) -> str:
        """
        Format the API response into a readable string.

        Args:
            query: The original SQL query
            result: The response data from the API

        Returns:
            Formatted string representation of the results
        """
        try:
            query_type = query.strip().upper().split()[0]

            # Handle different types of query responses
            if query_type == "SELECT":
                return self._format_select_response(result)
            elif query_type in ["INSERT", "UPDATE", "DELETE"]:
                return self._format_modification_response(query_type, result)
            else:
                return self._format_generic_response(result)

        except Exception:
            # Fallback to generic formatting if parsing fails
            return f"Query executed successfully. Raw response: {json.dumps(result, indent=2)}"

    def _format_select_response(self, result: Dict[str, Any]) -> str:
        """Format SELECT query response."""
        if "data" in result:
            data = result["data"]
            if isinstance(data, list):
                if len(data) == 0:
                    return "Query executed successfully. No rows returned."

                # Format as a table-like structure
                rows_text = []
                for i, row in enumerate(data):
                    if isinstance(row, dict):
                        row_items = [f"{k}: {v}" for k, v in row.items()]
                        rows_text.append(f"Row {i + 1}: {{{', '.join(row_items)}}}")
                    else:
                        rows_text.append(f"Row {i + 1}: {row}")

                return (
                    f"Query executed successfully. Retrieved {len(data)} row(s):\n"
                    + "\n".join(rows_text)
                )
            else:
                return f"Query executed successfully. Result: {data}"

        return f"Query executed successfully. Response: {json.dumps(result, indent=2)}"

    def _format_modification_response(
        self, query_type: str, result: Dict[str, Any]
    ) -> str:
        """Format INSERT, UPDATE, DELETE query response."""
        affected_rows = result.get(
            "affected_rows", result.get("rowsAffected", "unknown")
        )

        if affected_rows != "unknown":
            return f"{query_type} query executed successfully. {affected_rows} row(s) affected."

        return f"{query_type} query executed successfully."

    def _format_generic_response(self, result: Dict[str, Any]) -> str:
        """Format generic query response."""
        if "success" in result and result["success"]:
            return "Query executed successfully."

        return f"Query executed. Response: {json.dumps(result, indent=2)}"
