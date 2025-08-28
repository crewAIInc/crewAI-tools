import os
import unittest
import requests
from unittest.mock import patch, MagicMock

from crewai.tools import BaseTool
from crewai_tools.tools import CrewaiEnterpriseTools
from crewai_tools.adapters.tool_collection import ToolCollection
from crewai_tools.adapters.enterprise import EnterpriseActionTool, DefaultKitToolRequester, EnterpriseActionParser


class TestCrewaiEnterpriseTools(unittest.TestCase):
    def setUp(self):
        self.mock_tools = [
            self._create_mock_tool("tool1", "Tool 1 Description"),
            self._create_mock_tool("tool2", "Tool 2 Description"),
            self._create_mock_tool("tool3", "Tool 3 Description"),
        ]
        self.registry_patcher = patch(
            "crewai_tools.tools.crewai_enterprise_tools.crewai_enterprise_tools.registry"
        )
        self.mock_registry = self.registry_patcher.start()


        self.mock_detector = MagicMock()
        self.mock_requester = MagicMock()

        self.mock_registry.get_detector.return_value = self.mock_detector
        self.mock_detector.create_requester.return_value = self.mock_requester
        self.mock_detector.create_tools.return_value = self.mock_tools

    def tearDown(self):
        self.registry_patcher.stop()

    def _create_mock_tool(self, name, description):
        mock_tool = MagicMock(spec=BaseTool)
        mock_tool.name = name
        mock_tool.description = description
        return mock_tool

    @patch.dict(os.environ, {"CREWAI_ENTERPRISE_TOOLS_TOKEN": "env-token"})
    def test_returns_tool_collection(self):
        tools = CrewaiEnterpriseTools()
        self.assertIsInstance(tools, ToolCollection)

    @patch.dict(os.environ, {"CREWAI_ENTERPRISE_TOOLS_TOKEN": "env-token"})
    def test_returns_all_tools_when_no_actions_list(self):
        tools = CrewaiEnterpriseTools()
        self.assertEqual(len(tools), 3)
        self.assertEqual(tools[0].name, "tool1")
        self.assertEqual(tools[1].name, "tool2")
        self.assertEqual(tools[2].name, "tool3")

    @patch.dict(os.environ, {"CREWAI_ENTERPRISE_TOOLS_TOKEN": "env-token"})
    def test_filters_tools_by_actions_list(self):
        tools = CrewaiEnterpriseTools(actions_list=["ToOl1", "tool3"])
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0].name, "tool1")
        self.assertEqual(tools[1].name, "tool3")

    def test_uses_provided_parameters(self):
        CrewaiEnterpriseTools(
            enterprise_token="test-token",
            enterprise_action_kit_project_id="project-id",
            enterprise_action_kit_project_url="project-url",
        )

        self.mock_registry.get_detector.assert_called_once()
        call_kwargs = self.mock_registry.get_detector.call_args[1]
        self.assertEqual(call_kwargs["enterprise_token"], "test-token")
        self.assertEqual(call_kwargs["enterprise_action_kit_project_id"], "project-id")
        self.assertEqual(call_kwargs["enterprise_action_kit_project_url"], "project-url")

    @patch.dict(os.environ, {"CREWAI_ENTERPRISE_TOOLS_TOKEN": "env-token"})
    def test_uses_environment_token(self):
        CrewaiEnterpriseTools()

        self.mock_registry.get_detector.assert_called_once()
        call_kwargs = self.mock_registry.get_detector.call_args[1]
        self.assertEqual(call_kwargs["enterprise_token"], "env-token")

    @patch.dict(os.environ, {"CREWAI_ENTERPRISE_TOOLS_TOKEN": "env-token"})
    def test_uses_environment_token_when_no_token_provided(self):
        CrewaiEnterpriseTools(enterprise_token="")

        self.mock_registry.get_detector.assert_called_once()
        call_kwargs = self.mock_registry.get_detector.call_args[1]
        self.assertEqual(call_kwargs["enterprise_token"], "env-token")

    @patch.dict(
        os.environ,
        {
            "CREWAI_ENTERPRISE_TOOLS_TOKEN": "env-token",
            "CREWAI_ENTERPRISE_TOOLS_ACTIONS_LIST": '["tool1", "tool3"]',
        },
    )
    def test_uses_environment_actions_list(self):
        tools = CrewaiEnterpriseTools()
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0].name, "tool1")
        self.assertEqual(tools[1].name, "tool3")


class TestEnterpriseActionToolSchemaConversion(unittest.TestCase):
    """Test the enterprise action tool schema conversion and validation."""

    def setUp(self):
        self.test_schema = {
            "type": "function",
            "function": {
                "name": "TEST_COMPLEX_ACTION",
                "description": "Test action with complex nested structure",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filterCriteria": {
                            "type": "object",
                            "description": "Filter criteria object",
                            "properties": {
                                "operation": {"type": "string", "enum": ["AND", "OR"]},
                                "rules": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "field": {
                                                "type": "string",
                                                "enum": ["name", "email", "status"],
                                            },
                                            "operator": {
                                                "type": "string",
                                                "enum": ["equals", "contains"],
                                            },
                                            "value": {"type": "string"},
                                        },
                                        "required": ["field", "operator", "value"],
                                    },
                                },
                            },
                            "required": ["operation", "rules"],
                        },
                        "options": {
                            "type": "object",
                            "properties": {
                                "limit": {"type": "integer"},
                                "offset": {"type": "integer"},
                            },
                            "required": [],
                        },
                    },
                    "required": [],
                },
            },
        }

    def test_complex_schema_conversion(self):
        """Test that complex nested schemas are properly converted to Pydantic models."""
        tool = EnterpriseActionTool(
            name="gmail_search_for_email",
            description="Test tool",
            action_name="GMAIL_SEARCH_FOR_EMAIL",
            action_schema=self.test_schema,
            requester=DefaultKitToolRequester(enterprise_token="test_token"),
            parser=EnterpriseActionParser(),
        )

        self.assertEqual(tool.name, "gmail_search_for_email")
        self.assertEqual(tool.action_name, "GMAIL_SEARCH_FOR_EMAIL")

        schema_class = tool.args_schema
        self.assertIsNotNone(schema_class)

        schema_fields = schema_class.model_fields
        self.assertIn("filterCriteria", schema_fields)
        self.assertIn("options", schema_fields)

        # Test valid input structure
        valid_input = {
            "filterCriteria": {
                "operation": "AND",
                "rules": [
                    {"field": "name", "operator": "contains", "value": "test"},
                    {"field": "status", "operator": "equals", "value": "active"},
                ],
            },
            "options": {"limit": 10},
        }

        # This should not raise an exception
        validated_input = schema_class(**valid_input)
        self.assertIsNotNone(validated_input.filterCriteria)
        self.assertIsNotNone(validated_input.options)

    def test_optional_fields_validation(self):
        """Test that optional fields work correctly."""
        tool = EnterpriseActionTool(
            name="gmail_search_for_email",
            description="Test tool",
            action_name="GMAIL_SEARCH_FOR_EMAIL",
            action_schema=self.test_schema,
            requester=DefaultKitToolRequester(enterprise_token="test_token"),
            parser=EnterpriseActionParser(),
        )

        schema_class = tool.args_schema

        minimal_input = {}
        validated_input = schema_class(**minimal_input)
        self.assertIsNone(validated_input.filterCriteria)
        self.assertIsNone(validated_input.options)

        partial_input = {"options": {"limit": 10}}
        validated_input = schema_class(**partial_input)
        self.assertIsNone(validated_input.filterCriteria)
        self.assertIsNotNone(validated_input.options)

    def test_enum_validation(self):
        """Test that enum values are properly validated."""
        tool = EnterpriseActionTool(
            name="gmail_search_for_email",
            description="Test tool",
            action_name="GMAIL_SEARCH_FOR_EMAIL",
            action_schema=self.test_schema,
            requester=DefaultKitToolRequester(enterprise_token="test_token"),
            parser=EnterpriseActionParser(),
        )

        schema_class = tool.args_schema

        invalid_input = {
            "filterCriteria": {
                "operation": "INVALID_OPERATOR",
                "rules": [],
            }
        }

        with self.assertRaises(Exception):
            schema_class(**invalid_input)

    def test_required_nested_fields(self):
        """Test that required fields in nested objects are validated."""
        tool = EnterpriseActionTool(
            name="gmail_search_for_email",
            description="Test tool",
            action_name="GMAIL_SEARCH_FOR_EMAIL",
            action_schema=self.test_schema,
            requester=DefaultKitToolRequester(enterprise_token="test_token"),
            parser=EnterpriseActionParser(),
        )

        schema_class = tool.args_schema

        incomplete_input = {
            "filterCriteria": {
                "operation": "OR",
                "rules": [
                    {
                        "field": "name",
                        "operator": "contains",
                    }
                ],
            }
        }

        with self.assertRaises(Exception):
            schema_class(**incomplete_input)

    @patch("requests.post")
    def test_tool_execution_with_complex_input(self, mock_post):
        """Test that the tool can execute with complex validated input."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True, "results": []}
        mock_post.return_value = mock_response

        tool = EnterpriseActionTool(
            name="gmail_search_for_email",
            description="Test tool",
            action_name="GMAIL_SEARCH_FOR_EMAIL",
            action_schema=self.test_schema,
            requester=DefaultKitToolRequester(enterprise_token="test_token"),
            parser=EnterpriseActionParser(),
        )

        tool._run(
            filterCriteria={
                "operation": "OR",
                "rules": [
                    {"field": "name", "operator": "contains", "value": "test"},
                    {"field": "status", "operator": "equals", "value": "active"},
                ],
            },
            options={"limit": 10},
        )

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        self.assertEqual(payload["action"], "GMAIL_SEARCH_FOR_EMAIL")
        self.assertIn("filterCriteria", payload["parameters"])
        self.assertIn("options", payload["parameters"])
        self.assertEqual(payload["parameters"]["filterCriteria"]["operation"], "OR")

    def test_model_naming_convention(self):
        """Test that generated model names follow proper conventions."""
        tool = EnterpriseActionTool(
            name="gmail_search_for_email",
            description="Test tool",
            action_name="GMAIL_SEARCH_FOR_EMAIL",
            action_schema=self.test_schema,
            requester=DefaultKitToolRequester(enterprise_token="test_token"),
            parser=EnterpriseActionParser(),
        )

        schema_class = tool.args_schema
        self.assertIsNotNone(schema_class)

        self.assertTrue(schema_class.__name__.endswith("Schema"))
        self.assertTrue(schema_class.__name__[0].isupper())

        complex_input = {
            "filterCriteria": {
                "operation": "OR",
                "rules": [
                    {"field": "name", "operator": "contains", "value": "test"},
                    {"field": "status", "operator": "equals", "value": "active"},
                ],
            },
            "options": {"limit": 10},
        }

        validated = schema_class(**complex_input)
        self.assertIsNotNone(validated.filterCriteria)

    def test_simple_schema_with_enums(self):
        """Test a simpler schema with basic enum validation."""
        simple_schema = {
            "type": "function",
            "function": {
                "name": "SIMPLE_TEST",
                "description": "Simple test function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["active", "inactive", "pending"],
                        },
                        "priority": {"type": "integer", "enum": [1, 2, 3]},
                    },
                    "required": ["status"],
                },
            },
        }

        tool = EnterpriseActionTool(
            name="simple_test",
            description="Simple test tool",
            action_name="SIMPLE_TEST",
            action_schema=simple_schema,
            requester=DefaultKitToolRequester(enterprise_token="test_token"),
            parser=EnterpriseActionParser(),
        )

        schema_class = tool.args_schema

        valid_input = {"status": "active", "priority": 2}
        validated = schema_class(**valid_input)
        self.assertEqual(validated.status, "active")
        self.assertEqual(validated.priority, 2)

        with self.assertRaises(Exception):
            schema_class(status="invalid_status")


class TestCrewaiEnterpriseToolsOAuthStrategy(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8787"
        self.token = "test-token"
        self.oauth_actions_response = {
            "actions": [
                {
                    "name": "send_email",
                    "app_key": "gmail_app",
                    "description": "Send an email via Gmail",
                    "endpoint": "/apps/gmail_app/actions/send_email/execute",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Recipient email"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body"}
                        },
                        "required": ["to", "subject"]
                    }
                },
                {
                    "name": "list_events",
                    "app_key": "google_calendar",
                    "description": "List calendar events",
                    "endpoint": "/apps/google_calendar/actions/list_events/execute",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "calendar_id": {"type": "string", "description": "Calendar ID"}
                        },
                        "required": ["calendar_id"]
                    }
                }
            ]
        }

    def mock_get_success(self, mock_get, response=None):
        mock_response = MagicMock()
        mock_response.json.return_value = response or self.oauth_actions_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

    def get_tools(self, **kwargs):
        return CrewaiEnterpriseTools(
            enterprise_token=self.token,
            **kwargs
        )

    def find_tool(self, tools, name):
        return next((t for t in tools if t.name == name), None)


    @patch("requests.get")
    def test_oauth_detection_with_base_url(self, mock_get):
        self.mock_get_success(mock_get)
        tools = self.get_tools(base_url=self.base_url, user_id="test-user")

        self.assertIsInstance(tools, ToolCollection)
        self.assertEqual(len(tools), 2)
        self.assertIn("gmail_app_send_email", [t.name for t in tools])
        mock_get.assert_called_once_with(
            f"{self.base_url}/actions",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=30
        )

    @patch.dict(os.environ, {"CREWAI_OAUTH_BASE_URL": "http://localhost:8787"})
    @patch("requests.get")
    def test_oauth_detection_with_env_var(self, mock_get):
        self.mock_get_success(mock_get)
        tools = self.get_tools()

        self.assertEqual(len(tools), 2)
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_oauth_tool_naming_convention(self, mock_get):
        self.mock_get_success(mock_get)
        tools = self.get_tools(base_url=self.base_url)

        self.assertEqual(
            {t.name for t in tools},
            {"gmail_app_send_email", "google_calendar_list_events"}
        )

    @patch("requests.get")
    def test_oauth_tool_schema_parsing(self, mock_get):
        self.mock_get_success(mock_get)
        tools = self.get_tools(base_url=self.base_url)
        gmail_tool = self.find_tool(tools, "gmail_app_send_email")

        schema = gmail_tool.args_schema
        valid = schema(to="x@test.com", subject="Hello")
        self.assertEqual(valid.to, "x@test.com")

        with self.assertRaises(Exception):
            schema(subject="Missing to")

    @patch("requests.get")
    @patch("requests.post")
    def test_oauth_tool_execution(self, mock_post, mock_get):
        self.mock_get_success(mock_get)
        mock_post.return_value = MagicMock(ok=True, json=lambda: {"success": True})

        tools = self.get_tools(base_url=self.base_url)
        gmail_tool = self.find_tool(tools, "gmail_app_send_email")
        gmail_tool._run(to="me@test.com", subject="Hi")

        expected_url = f"{self.base_url}/apps/gmail_app/actions/send_email/execute"
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args[1]["url"], expected_url)

    @patch("requests.get")
    def test_oauth_filtering(self, mock_get):
        self.mock_get_success(mock_get)
        tools = self.get_tools(base_url=self.base_url, actions_list=["gmail_app_send_email"])
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].name, "gmail_app_send_email")

    @patch("requests.get")
    def test_oauth_parameter_precedence(self, mock_get):
        self.mock_get_success(mock_get)
        with patch.dict(os.environ, {"CREWAI_OAUTH_BASE_URL": "http://env"}):
            self.get_tools(base_url="http://param")
        mock_get.assert_called_once_with(
            "http://param/actions",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=30
        )

    @patch("requests.get")
    def test_oauth_api_error_handling(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        tools = self.get_tools(base_url=self.base_url)
        self.assertEqual(len(tools), 0)
