from typing import Dict, Any
from pydantic import Field
from crewai.tools import BaseTool

from crewai_tools.adapters.enterprise.base import BaseToolRequester, EnterpriseActionParser


class EnterpriseActionTool(BaseTool):
    requester: BaseToolRequester = Field(description="The toolkit requester")
    action_name: str = Field(description="The name of the action")
    action_schema: Dict[str, Any] = Field(description="The schema of the action")
    parser: EnterpriseActionParser = Field(description="The action schema parser")

    def __init__(
        self,
        name: str,
        description: str,
        requester: BaseToolRequester,
        action_name: str,
        action_schema: Dict[str, Any],
        parser: EnterpriseActionParser,
    ):
        args_schema = parser.create_pydantic_model(action_schema, name)

        super().__init__(
            name=name,
            description=description,
            args_schema=args_schema,
            requester=requester,
            action_name=action_name,
            action_schema=action_schema,
            parser=parser
        )

    def _run(self, **kwargs) -> str:
        try:
            cleaned_kwargs = self.parser.clean_parameters(kwargs, self.action_schema)

            return self.requester.execute(self.action_name, cleaned_kwargs)

        except Exception as e:
            return f"Error executing action {self.action_name}: {str(e)}"
