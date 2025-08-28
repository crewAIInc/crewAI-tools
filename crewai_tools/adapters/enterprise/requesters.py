import os
import json
import requests
from typing import Dict, Any, Optional

from crewai_tools.adapters.enterprise.base import BaseToolRequester

# DEFAULTS
ENTERPRISE_ACTION_KIT_PROJECT_ID = "dd525517-df22-49d2-a69e-6a0eed211166"
ENTERPRISE_ACTION_KIT_PROJECT_URL = "https://worker-actionkit.tools.crewai.com/projects"


class DefaultKitToolRequester(BaseToolRequester):
    def __init__(
        self,
        enterprise_token: str,
        enterprise_action_kit_project_url: str = ENTERPRISE_ACTION_KIT_PROJECT_URL,
        enterprise_action_kit_project_id: str = ENTERPRISE_ACTION_KIT_PROJECT_ID,
        **kwargs
    ):
        super().__init__(enterprise_token, **kwargs)
        self.enterprise_action_kit_project_url = enterprise_action_kit_project_url
        self.enterprise_action_kit_project_id = enterprise_action_kit_project_id
        self._actions_schema = {}

    def fetch_actions(self) -> Dict[str, Any]:
        try:
            if not self.enterprise_token:
                self.enterprise_token = os.environ.get("CREWAI_ENTERPRISE_TOOLS_TOKEN")

            actions_url = f"{self.enterprise_action_kit_project_url}/{self.enterprise_action_kit_project_id}/actions"
            headers = {"Authorization": f"Bearer {self.enterprise_token}"}
            params = {"format": "json_schema"}

            response = requests.get(
                actions_url, headers=headers, params=params, timeout=30
            )
            response.raise_for_status()

            raw_data = response.json()
            if "actions" not in raw_data:
                print(f"Unexpected API response structure: {raw_data}")
                return {}

            parsed_schema = {}
            action_categories = raw_data["actions"]

            for category, action_list in action_categories.items():
                if isinstance(action_list, list):
                    for action in action_list:
                        func_details = action.get("function")
                        if func_details and "name" in func_details:
                            action_name = func_details["name"]
                            parsed_schema[action_name] = action

            self._actions_schema = parsed_schema
            return parsed_schema

        except Exception as e:
            print(f"Error fetching actions: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def execute(self, action_name: str, parameters: Dict[str, Any]) -> str:
        try:
            api_url = f"{self.enterprise_action_kit_project_url}/{self.enterprise_action_kit_project_id}/actions"
            headers = {
                "Authorization": f"Bearer {self.enterprise_token}",
                "Content-Type": "application/json",
            }
            payload = {"action": action_name, "parameters": parameters}

            response = requests.post(
                url=api_url, headers=headers, json=payload, timeout=60
            )

            data = response.json()
            if not response.ok:
                error_message = data.get("error", {}).get("message", json.dumps(data))
                return f"API request failed: {error_message}"

            return json.dumps(data, indent=2)

        except Exception as e:
            return f"Error executing action {action_name}: {str(e)}"


class CustomOauthToolRequester(BaseToolRequester):
    def __init__(
        self,
        enterprise_token: str,
        base_url: str,
        user_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(enterprise_token, **kwargs)
        self.base_url = base_url.rstrip('/')
        self.user_id = user_id
        self._actions_schema = {}

    def fetch_actions(self) -> Dict[str, Any]:
        try:
            if not self.enterprise_token:
                token = os.environ.get("CREWAI_ENTERPRISE_TOKEN")
                if token:
                    self.enterprise_token = token

            actions_url = f"{self.base_url}/actions"
            headers = {"Authorization": f"Bearer {self.enterprise_token}"}

            response = requests.get(actions_url, headers=headers, timeout=30)
            response.raise_for_status()

            actions_data = response.json()

            parsed_schema = {}
            if isinstance(actions_data, dict) and 'actions' in actions_data:
                for action in actions_data['actions']:
                    action_name = action.get('name')
                    app_key = action.get('app_key')

                    if action_name and app_key:
                        execute_endpoint = action.get('endpoint')

                        tool_key = f"{app_key}_{action_name}"

                        parsed_schema[tool_key] = {
                            'action_name': action_name,
                            'schema': action,
                            'execute_endpoint': execute_endpoint
                        }

            self._actions_schema = parsed_schema
            return parsed_schema

        except Exception as e:
            print(f"Error fetching actions: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def execute(self, action_name: str, parameters: Dict[str, Any]) -> str:
        try:
            action_info = None
            for tool_key, info in self._actions_schema.items():
                if tool_key == action_name or info['action_name'] == action_name:
                    action_info = info
                    break

            if not action_info:
                return f"Action {action_name} not found in available actions"

            execute_endpoint = action_info.get('execute_endpoint')

            if execute_endpoint:
                api_url = execute_endpoint
                if not api_url.startswith(('http://', 'https://')):
                    api_url = f"{self.base_url.rstrip('/')}/{api_url.lstrip('/')}"

            headers = {
                "Authorization": f"Bearer {self.enterprise_token}",
                "Content-Type": "application/json",
            }

            payload: Dict[str, Any] = {"input": parameters}

            response = requests.post(
                url=api_url, headers=headers, json=payload, timeout=60
            )

            data = response.json()
            if not response.ok:
                error_message = data.get("error", {}).get("message", json.dumps(data))
                return f"API request failed: {error_message}"

            return json.dumps(data, indent=2)

        except Exception as e:
            return f"Error executing action {action_name}: {str(e)}"
