import os
import typing as t
import logging
import json
from typing import cast
from crewai.tools import BaseTool
from crewai_tools.adapters.enterprise import registry
from crewai_tools.adapters.tool_collection import ToolCollection

logger = logging.getLogger(__name__)


def CrewaiEnterpriseTools(
    enterprise_token: t.Optional[str] = None,
    actions_list: t.Optional[t.List[str]] = None,
    **kwargs
) -> ToolCollection[BaseTool]:
    """Unified factory function that returns crewai enterprise tools.

    Automatically detects the appropriate toolkit based on provided parameters.

    Args:
        enterprise_token: The token for accessing enterprise actions.
                         If not provided, will try to use CREWAI_ENTERPRISE_TOOLS_TOKEN env var.
        actions_list: Optional list of specific tool names to include.
                     If provided, only tools with these names will be returned.
        **kwargs: Additional parameters for specific toolkits:
                 - base_url: For OAuth self-hosted toolkits
                 - enterprise_action_kit_project_id: For default ActionKit
                 - enterprise_action_kit_project_url: For default ActionKit

    Returns:
        A ToolCollection of BaseTool instances for enterprise actions
    """

    if enterprise_token is None or enterprise_token == "":
        enterprise_token = os.environ.get("CREWAI_ENTERPRISE_TOOLS_TOKEN")
        if not enterprise_token:
            logger.warning("No enterprise token provided")
            return ToolCollection([])

    kwargs["enterprise_token"] = enterprise_token

    detector = registry.get_detector(**kwargs)
    requester = detector.create_requester(**kwargs)

    all_tools = detector.create_tools(requester)

    parsed_actions_list = _parse_actions_list(actions_list)

    # Filter tools based on the provided list
    return ToolCollection(cast(t.List[BaseTool], all_tools)).filter_by_names(parsed_actions_list)


# ENTERPRISE INJECTION ONLY
def _parse_actions_list(actions_list: t.Optional[t.List[str]]) -> t.List[str] | None:
    """Parse a string representation of a list of tool names to a list of tool names.

    Args:
        actions_list: A string representation of a list of tool names.

    Returns:
        A list of tool names.
    """
    if actions_list is not None:
        return actions_list

    actions_list_from_env = os.environ.get("CREWAI_ENTERPRISE_TOOLS_ACTIONS_LIST")
    if actions_list_from_env is None:
        return None

    try:
        return json.loads(actions_list_from_env)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse actions_list as JSON: {actions_list_from_env}")
        return None
