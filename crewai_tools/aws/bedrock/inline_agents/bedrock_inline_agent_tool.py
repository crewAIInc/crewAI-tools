from typing import Dict, List, Optional, Any, Union
from crewai.tools import BaseTool
from pydantic import Field, model_validator

import json, os
import uuid
import logging
from datetime import datetime
from crewai.utilities.config import process_config

from utils.response_handler import ResponseHandler
from ..exceptions import BedrockAgentError, BedrockValidationError

logger = logging.getLogger(__file__)


class BedrockInlineAgentTool(BaseTool):
    """Tool for interacting with Amazon Bedrock Inline Agents.

    This tool allows CrewAI agents to leverage Amazon Bedrock Inline Agents
    for dynamic, context-aware responses and actions.
    """
    
    # Define all fields as class attributes with Field
    name: str = Field(default="BedrockInlineAgent")
    description: str = Field(default="Use this tool to interact with an Amazon Bedrock Inline Agent.")
    model_id: str = Field(description="The ID of the Amazon Bedrock model to use")
    region_name: str = Field(description="The AWS region where Bedrock is available")
    instruction: str = Field(description="Instructions for the inline agent")
    enable_trace: bool = Field(default=False, description="Whether to enable trace logging")
    enable_code_interpreter: bool = Field(default=True, description="Whether to enable code interpreter")
    knowledge_base_id: Optional[str] = Field(default=None, description="Optional Knowledge Base ID to use with the agent")
    kb_description: Optional[str] = Field(default=None, description="Description of the knowledge base")
    kb_num_results: int = Field(default=3, description="Number of results to return from the knowledge base")
    kb_search_type: str = Field(default="HYBRID", description="Type of search to perform (HYBRID, SEMANTIC)")
    lambda_function_arn: Optional[str] = Field(default=None, description="Optional Lambda function ARN for custom actions")
    action_group_name: Optional[str] = Field(default=None, description="Name for the custom action group")
    output_folder: str = Field(default="output", description="Folder to save generated files")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuration for the tool")
    
    # Private attributes
    _bedrock_client = None
    _session_id = None
    _response_handler = None
    
    @model_validator(mode="before")
    @classmethod
    def process_tool_config(cls, values):
        """Process the configuration before model validation."""
        return process_config(values, cls)
    
    def _substitute_env_vars(self, value):
        """Substitute environment variables in a value."""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var_name = value[2:-1]
            env_value = os.environ.get(env_var_name)
            if env_value is None:
                if self.enable_trace:
                    logger.warning(f"Warning: Environment variable {env_var_name} not found")
                return None
            return env_value
        return value
    
    @model_validator(mode="after")
    def setup_client(self):
        """Set up the Bedrock Agent Runtime client after validation."""
        # Conditional import and setup for the Bedrock Agent Runtime client.
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise ImportError("`boto3` package not found, please run `uv add boto3`")
        
        # Process environment variables in fields
        self.model_id = self._substitute_env_vars(self.model_id) or self.model_id
        self.knowledge_base_id = self._substitute_env_vars(self.knowledge_base_id)
        
        # Validate required fields
        if not self.model_id:
            raise BedrockValidationError("model_id must be provided either directly or through config")
        if not self.region_name:
            raise BedrockValidationError("region_name must be provided either directly or through config")
        if not self.instruction:
            raise BedrockValidationError("instruction must be provided either directly or through config")
        
        # Check if VERBOSE_MODE environment variable is set to override enable_trace
        if os.environ.get("VERBOSE_MODE", "false").lower() == "true":
            self.enable_trace = True
        
        # Initialize the Bedrock client
        self._bedrock_client = boto3.client(
            "bedrock-agent-runtime",
            region_name=self.region_name
        )
        
        # Generate a unique session ID for this tool instance
        self._session_id = f"session-{uuid.uuid4()}"
        
        # Create output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # Initialize response handler
        self._response_handler = ResponseHandler(
            output_folder=self.output_folder,
            enable_trace=self.enable_trace
        )
        
        return self

    def _run(self, query: str) -> str:
        """Run the tool to interact with the Bedrock Inline Agent.

        Args:
            query: The query to send to the Inline Agent.

        Returns:
            A string containing the agent's response.
        """
        
        try:
            # Prepare the request parameters
            request_params = self._prepare_request_params(query)
            
            # Invoke the inline agent
            response = self._invoke_inline_agent(request_params)
            
            return response
            
        except BedrockAgentError as e:
            return f"Bedrock Agent Error: {str(e)}"
        except Exception as e:
            return f"Error interacting with Bedrock Inline Agent: {str(e)}"
    
    def _prepare_request_params(self, query: str) -> Dict:
        """Prepare the request parameters for the inline agent.

        Args:
            query: The query to send to the agent.

        Returns:
            A dictionary with the request parameters.
        """
        request_params = {
            "instruction": self.instruction,
            "foundationModel": self.model_id,
            "sessionId": self._session_id,
            "endSession": False,
            "enableTrace": self.enable_trace,
            "inputText": query
        }
        
        # Add action groups if needed
        action_groups = []
        
        # Add code interpreter if enabled
        if self.enable_code_interpreter:
            code_interpreter_tool = {
                "actionGroupName": "UserInputAction",
                "parentActionGroupSignature": "AMAZON.CodeInterpreter"
            }
            action_groups.append(code_interpreter_tool)
        
        # Add custom action group if provided
        if self.lambda_function_arn and self.action_group_name:
            custom_action_group = {
                "actionGroupName": self.action_group_name,
                "actionGroupExecutor": {
                    "lambda": self.lambda_function_arn
                }
            }
            action_groups.append(custom_action_group)
        
        if action_groups:
            request_params["actionGroups"] = action_groups
        
        # Add knowledge base if provided
        if self.knowledge_base_id:
            # Default description if none provided
            kb_desc = self.kb_description or f"Knowledge base containing information related to {self.name}"
            
            kb_config = {
                "knowledgeBaseId": self.knowledge_base_id,
                "description": kb_desc,
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": self.kb_num_results,
                        "overrideSearchType": self.kb_search_type
                    }
                }
            }
            request_params["knowledgeBases"] = [kb_config]
        
        return request_params
    
    def _invoke_inline_agent(self, request_params: Dict) -> str:
        """Invoke the inline agent and process the response.

        Args:
            request_params: The parameters for the inline agent request.

        Returns:
            The processed response from the agent.
            
        Raises:
            BedrockAgentError: If there is an error invoking the Bedrock Inline Agent.
        """
        try:
            agent_resp = self._bedrock_client.invoke_inline_agent(**request_params)
            
            # Process the response using the response handler
            agent_answer = self._response_handler.process_response(agent_resp)
            
            return agent_answer
        except Exception as e:
            # Wrap the exception in a BedrockAgentError
            error_message = f"Error invoking Bedrock Inline Agent: {str(e)}"
            if self.enable_trace:
                logger.error(error_message)
            raise BedrockAgentError(error_message) from e
    
    def get_generated_files(self) -> List[Dict]:
        """Get information about files generated during the last invocation.
        
        Returns:
            A list of dictionaries with information about generated files.
        """
        return self._response_handler.generated_files


# Example usage
if __name__ == "__main__":
    import os
    import yaml
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment variables
    model_id = os.environ.get("CLAUDE_HAIKU_MODEL_ID")
    region = os.environ.get("AWS_REGION", "us-east-1")
    
    if not model_id:
        logger.error("CLAUDE_HAIKU_MODEL_ID environment variable not set")
        exit(1)
    
    logger.info(f"Testing BedrockInlineAgentTool with model ID: {model_id} in region: {region}")
    
    # Example 1: Using direct parameters
    logger.info("Example 1: Using direct parameters")
    direct_agent = BedrockInlineAgentTool(
        model_id=model_id,
        region_name=region,
        instruction="""
        You are a helpful financial analyst assistant. Answer questions about financial reports concisely and accurately.
        You are able to write code to generate visualizations and perform calculations if needed.

        Here is Amazon's revenue data from 2020-2024:
        2020: $386.1 billion
        2021: $469.8 billion
        2022: $513.9 billion
        2023: $574.8 billion
        2024: $641.1 billion
        
        Amazon's business segments include:
        - North America
        - International
        - AWS (Amazon Web Services)
        
        AWS has shown the highest growth rate and profit margins among all segments.
        """,
        enable_trace=True,
        enable_code_interpreter=True,
        output_folder="output/financial_analysis",
        name="Financial_Analyst_Agent",
        description="Use this tool to get financial analysis and insights"
    )
    
    # Test query
    test_query = "Create a chart showing the revenue growth trend for Amazon from 2020 to 2024. Use Python code to generate this chart and save it as a PNG file."
    logger.info(f"Running query: '{test_query}'")
    
    try:
        result = direct_agent.run(test_query)
        logger.info("Result:")
        logger.info(result)
        
        # Print information about generated files
        files = direct_agent.get_generated_files()
        if files:
            logger.info("Generated files:")
            for file in files:
                logger.info(f"- {file['name']} ({file['type']}): {file['path']}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    
    # Example 2: Using YAML configuration
    logger.info("Example 2: Using YAML configuration")
    try:
        # Load the agents configuration
        # with open("src/sec_10k_analyser_flow/crews/research/config/bedrock_agents.yaml", "r") as f:
        bedrock_agent_config = "config/bedrock_agent.yaml"
        
        config_agent = BedrockInlineAgentTool(
            config=bedrock_agent_config["data_analyst"],
            region_name=region,
            output_folder="output/config_example"
        )
        
        # Test the agent
        query = """Create a bar chart showing Amazon's revenue growth from 2020 to 2024. 
        Use different colors for each year and include a title and proper axis labels.
        Make sure to save the visualization as 'amazon_revenue_growth.png'."""
        
        logger.info(f"Running query: '{query}'")
        response = config_agent.run(query)
        logger.info("Response from Bedrock Inline Agent:")
        logger.info(response)
        
        # Print information about generated files
        files = config_agent.get_generated_files()
        if files:
            logger.info("Generated files:")
            for file in files:
                logger.info(f"- {file['name']} ({file['type']}): {file['path']}")
    except FileNotFoundError:
        logger.warning("Configuration file not found. Skipping Example 2.")
