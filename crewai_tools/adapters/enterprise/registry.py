import os
from abc import ABC, abstractmethod
from typing import List

from crewai_tools.adapters.enterprise.base import BaseToolRequester, EnterpriseActionParser
from crewai_tools.adapters.enterprise.tools import EnterpriseActionTool
from crewai_tools.adapters.enterprise.requesters import DefaultKitToolRequester, CustomOauthToolRequester


class ToolkitDetector(ABC):
    priority: int = 50

    @abstractmethod
    def can_handle(self, **kwargs) -> bool:
        pass

    @abstractmethod
    def create_requester(self, **kwargs) -> BaseToolRequester:
        pass

    def create_tools(self, requester: BaseToolRequester) -> List[EnterpriseActionTool]:
        actions_schema = requester.fetch_actions()

        parser = EnterpriseActionParser()

        tools = []
        for action_name, action_data in actions_schema.items():
            if isinstance(action_data, dict):
                if 'schema' in action_data:
                    action_schema = action_data['schema']
                    tool_name = action_name.lower().replace(" ", "_").replace("-", "_")
                else:
                    action_schema = action_data
                    tool_name = action_name.lower().replace(" ", "_")
            else:
                action_schema = {}
                tool_name = action_name.lower().replace(" ", "_")

            description = parser.generate_description(action_schema)

            tool = EnterpriseActionTool(
                name=tool_name,
                description=description,
                requester=requester,
                action_name=action_name,
                action_schema=action_schema,
                parser=parser
            )
            tools.append(tool)

        return tools


class OAuthDetector(ToolkitDetector):
    priority = 100  # Check OAuth first

    def can_handle(self, **kwargs) -> bool:
        return (
            "base_url" in kwargs or
            os.environ.get("CREWAI_OAUTH_BASE_URL") is not None
        )

    def create_requester(self, **kwargs) -> BaseToolRequester:
        base_url = kwargs.pop("base_url", None) or os.environ.get("CREWAI_OAUTH_BASE_URL")
        if not base_url:
            raise ValueError("base_url is required for OAuth toolkit")

        return CustomOauthToolRequester(
            base_url=base_url,
            **kwargs
        )


class DefaultDetector(ToolkitDetector):
    priority = 50  # Fallback

    def can_handle(self, **kwargs) -> bool:
        return True  # Always can handle (fallback)

    def create_requester(self, **kwargs) -> BaseToolRequester:
        return DefaultKitToolRequester(**kwargs)


class ToolkitRegistry:
    def __init__(self):
        self._detectors: List[ToolkitDetector] = []

    def register(self, detector: ToolkitDetector):
        self._detectors.append(detector)
        self._detectors.sort(key=lambda d: d.priority, reverse=True)

    def get_detector(self, **kwargs) -> ToolkitDetector:
        for detector in self._detectors:
            if detector.can_handle(**kwargs):
                return detector

        raise ValueError("No suitable toolkit found for the given parameters")


registry = ToolkitRegistry()
registry.register(OAuthDetector())
registry.register(DefaultDetector())
