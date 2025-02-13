"""
Databricks Tool for CrewAI that enables agents to interact with Databricks Delta Lake.
"""
from typing import Dict, List, Any, Union
from crewai.tools import tool
from databricks import sql
import os
from .cache import get_cached_result, cache_result

@tool("query_databricks")
def query_databricks(sql_query: str, use_cache: bool = True, cache_ttl: int = 300) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes a SQL query on Databricks Delta Lake and returns the results.
    
    Args:
        sql_query (str): The SQL query to execute on Databricks.
        
    Returns:
        Union[List[Dict[str, Any]], Dict[str, str]]: Either a list of dictionaries containing 
        the query results (where each dictionary represents a row with column names as keys) 
        or an error dictionary if the query fails.
        
    Example:
        ```python
        from crewai_tools.tools.databricks_tool import query_databricks
        
        # Execute a simple query
        results = query_databricks("SELECT * FROM my_database.my_table LIMIT 5")
        
        # Handle the results
        if "error" not in results:
            for row in results:
                print(row)
        else:
            print(f"Query failed: {results['error']}")
        ```
    """
    try:
        # Check cache first if enabled
        if use_cache:
            cached_result = get_cached_result(sql_query, cache_ttl)
            if cached_result is not None:
                return cached_result
                
        # Validate required environment variables
        required_vars = ["DATABRICKS_HOST", "DATABRICKS_HTTP_PATH", "DATABRICKS_TOKEN"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            return {
                "error": f"Missing required environment variables: {', '.join(missing_vars)}"
            }

        # Establish connection
        conn = sql.connect(
            server_hostname=os.getenv("DATABRICKS_HOST"),
            http_path=os.getenv("DATABRICKS_HTTP_PATH"),
            access_token=os.getenv("DATABRICKS_TOKEN")
        )
        
        # Execute query
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            # Convert results to list of dictionaries
            formatted_results = [dict(zip(columns, row)) for row in results]
            
            # Cache results if enabled
            if use_cache:
                cache_result(sql_query, formatted_results, cache_ttl)
                
            return formatted_results
            
    except sql.Error as e:
        return {"error": f"Databricks SQL error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
    finally:
        if 'conn' in locals():
            conn.close()
