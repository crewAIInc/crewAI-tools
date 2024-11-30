from typing import Any, Optional
from pydantic.v1 import BaseModel, Field
from ..base_tool import BaseTool
import requests

class SearxNGSearchToolSchema(BaseModel):
    query: str = Field(..., description="The search query to be executed")
    num_results: Optional[int] = Field(10, description="Number of results to return (default: 10)")

class SearxNGSearchTool(BaseTool):
    name: str = "SearxNG Search"
    description: str = "Search the web using a SearxNG instance"
    args_schema: Any = SearxNGSearchToolSchema

    def __init__(self, base_url: str):
        self.base_url = base_url

    def _run(self, query: str, num_results: int = 10) -> str:
        try:
            params = {
                "q": query,
                "format": "json",
                "engines": "general",
                "limit": num_results
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "results" not in data:
                return "No results found or invalid response from SearxNG instance."
            
            results = data["results"]
            formatted_results = []
            for result in results:
                formatted_results.append(f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['content']}\n")
            
            return "\n".join(formatted_results)
        
        except requests.RequestException as e:
            return f"Error occurred while making the request: {str(e)}"
        except ValueError as e:
            return f"Error occurred while parsing the response: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
