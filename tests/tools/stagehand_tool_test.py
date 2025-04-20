import sys
from unittest.mock import MagicMock, patch

import pytest

# Create mock modules
mock_stagehand = MagicMock()
mock_stagehand_schemas = MagicMock()
mock_stagehand_utils = MagicMock()

# Create mock classes
mock_stagehand.Stagehand = MagicMock()
mock_stagehand.StagehandConfig = MagicMock()
mock_stagehand.StagehandPage = MagicMock()
mock_stagehand_schemas.ActOptions = MagicMock()
mock_stagehand_schemas.ExtractOptions = MagicMock()
mock_stagehand_schemas.ObserveOptions = MagicMock()
mock_stagehand_schemas.AvailableModel = MagicMock()
mock_stagehand_utils.configure_logging = MagicMock()

# Mock the imports
sys.modules["stagehand"] = mock_stagehand
sys.modules["stagehand.schemas"] = mock_stagehand_schemas
sys.modules["stagehand.utils"] = mock_stagehand_utils

# Now import the actual module
from crewai_tools.tools.stagehand_tool.stagehand_tool import (
    StagehandResult,
    StagehandTool,
)


class MockStagehandPage(MagicMock):
    async def act(self, options):
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "message": "Action completed successfully"
        }
        return mock_result

    async def goto(self, url):
        return MagicMock()

    async def extract(self, options):
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "data": "Extracted content",
            "metadata": {"source": "test"},
        }
        return mock_result

    async def observe(self, options):
        result1 = MagicMock()
        result1.description = "Button element"
        result1.method = "click"

        result2 = MagicMock()
        result2.description = "Input field"
        result2.method = "type"

        return [result1, result2]


class MockStagehand(MagicMock):
    async def init(self):
        self.session_id = "test-session-id"
        self.page = MockStagehandPage()

    async def close(self):
        pass


@pytest.fixture
def mock_stagehand_instance():
    with patch(
        "crewai_tools.tools.stagehand_tool.stagehand_tool.Stagehand",
        return_value=MockStagehand(),
    ) as mock:
        yield mock


@pytest.fixture
def stagehand_tool():
    return StagehandTool(
        api_key="test_api_key",
        project_id="test_project_id",
        model_api_key="test_model_api_key",
    )


def test_stagehand_tool_initialization():
    """Test that the StagehandTool initializes with the correct default values."""
    tool = StagehandTool(
        api_key="test_api_key",
        project_id="test_project_id",
        model_api_key="test_model_api_key",
    )

    assert tool.api_key == "test_api_key"
    assert tool.project_id == "test_project_id"
    assert tool.model_api_key == "test_model_api_key"
    assert tool.headless is False
    assert tool.dom_settle_timeout_ms == 3000
    assert tool.self_heal is True
    assert tool.wait_for_captcha_solves is True


@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.asyncio.get_event_loop")
@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.Stagehand")
def test_act_command(mock_stagehand, mock_get_loop, stagehand_tool):
    """Test the 'act' command functionality."""
    # Setup mock
    mock_page = MockStagehandPage()
    mock_stagehand_instance = mock_stagehand.return_value
    mock_stagehand_instance.page = mock_page
    mock_stagehand_instance.session_id = "test-session-id"

    # Setup mock for async execution
    mock_loop = MagicMock()
    mock_get_loop.return_value = mock_loop
    mock_loop.is_running.return_value = False
    mock_loop.run_until_complete.return_value = StagehandResult(
        success=True, data={"message": "Action completed successfully"}
    )

    # Run the tool
    result = stagehand_tool._run(
        instruction="Click the submit button", command_type="act"
    )

    # Assertions
    assert "Action result" in result
    assert "Action completed successfully" in result


@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.asyncio.get_event_loop")
@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.Stagehand")
def test_navigate_command(mock_stagehand, mock_get_loop, stagehand_tool):
    """Test the 'navigate' command functionality."""
    # Setup mock
    mock_page = MockStagehandPage()
    mock_stagehand_instance = mock_stagehand.return_value
    mock_stagehand_instance.page = mock_page
    mock_stagehand_instance.session_id = "test-session-id"

    # Setup mock for async execution
    mock_loop = MagicMock()
    mock_get_loop.return_value = mock_loop
    mock_loop.is_running.return_value = False
    mock_loop.run_until_complete.return_value = StagehandResult(
        success=True,
        data={
            "url": "https://example.com",
            "message": "Successfully navigated to https://example.com",
        },
    )

    # Run the tool
    result = stagehand_tool._run(
        instruction="Go to example.com",
        url="https://example.com",
        command_type="navigate",
    )

    # Assertions
    assert "https://example.com" in result


@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.asyncio.get_event_loop")
@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.Stagehand")
def test_extract_command(mock_stagehand, mock_get_loop, stagehand_tool):
    """Test the 'extract' command functionality."""
    # Setup mock
    mock_page = MockStagehandPage()
    mock_stagehand_instance = mock_stagehand.return_value
    mock_stagehand_instance.page = mock_page
    mock_stagehand_instance.session_id = "test-session-id"

    # Setup mock for async execution
    mock_loop = MagicMock()
    mock_get_loop.return_value = mock_loop
    mock_loop.is_running.return_value = False
    mock_loop.run_until_complete.return_value = StagehandResult(
        success=True, data={"data": "Extracted content", "metadata": {"source": "test"}}
    )

    # Run the tool
    result = stagehand_tool._run(
        instruction="Extract all product names and prices", command_type="extract"
    )

    # Assertions
    assert "Extracted data" in result
    assert "Extracted content" in result


@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.asyncio.get_event_loop")
@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.Stagehand")
def test_observe_command(mock_stagehand, mock_get_loop, stagehand_tool):
    """Test the 'observe' command functionality."""
    # Setup mock
    mock_page = MockStagehandPage()
    mock_stagehand_instance = mock_stagehand.return_value
    mock_stagehand_instance.page = mock_page
    mock_stagehand_instance.session_id = "test-session-id"

    # Setup mock for async execution
    mock_loop = MagicMock()
    mock_get_loop.return_value = mock_loop
    mock_loop.is_running.return_value = False
    mock_loop.run_until_complete.return_value = StagehandResult(
        success=True,
        data=[
            {"index": 1, "description": "Button element", "method": "click"},
            {"index": 2, "description": "Input field", "method": "type"},
        ],
    )

    # Run the tool
    result = stagehand_tool._run(
        instruction="Find all interactive elements", command_type="observe"
    )

    # Assertions
    assert "Element 1: Button element" in result
    assert "Element 2: Input field" in result
    assert "Suggested action: click" in result
    assert "Suggested action: type" in result


@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.asyncio.get_event_loop")
@patch("crewai_tools.tools.stagehand_tool.stagehand_tool.Stagehand")
def test_error_handling(mock_stagehand, mock_get_loop, stagehand_tool):
    """Test error handling in the tool."""
    # Setup mock
    mock_stagehand_instance = mock_stagehand.return_value
    mock_stagehand_instance.page = MagicMock()
    mock_stagehand_instance.page.act.side_effect = Exception("Browser automation error")
    mock_stagehand_instance.session_id = "test-session-id"

    # Setup mock for async execution
    mock_loop = MagicMock()
    mock_get_loop.return_value = mock_loop
    mock_loop.is_running.return_value = False
    mock_loop.run_until_complete.return_value = StagehandResult(
        success=False, data={}, error="Error using Stagehand: Browser automation error"
    )

    # Run the tool
    result = stagehand_tool._run(
        instruction="Click a non-existent button", command_type="act"
    )

    # Assertions
    assert "Error:" in result
    assert "Browser automation error" in result


def test_initialization_parameters():
    """Test that the StagehandTool initializes with the correct parameters."""
    # Create tool with custom parameters
    tool = StagehandTool(
        api_key="custom_api_key",
        project_id="custom_project_id",
        model_api_key="custom_model_api_key",
        headless=True,
        dom_settle_timeout_ms=5000,
        self_heal=False,
        wait_for_captcha_solves=False,
        verbose=3,
    )

    # Verify the tool was initialized with the correct parameters
    assert tool.api_key == "custom_api_key"
    assert tool.project_id == "custom_project_id"
    assert tool.model_api_key == "custom_model_api_key"
    assert tool.headless is True
    assert tool.dom_settle_timeout_ms == 5000
    assert tool.self_heal is False
    assert tool.wait_for_captcha_solves is False
    assert tool.verbose == 3


def test_close_method():
    """Test that the close method cleans up resources correctly."""
    # Create the tool
    tool = StagehandTool(
        api_key="test_api_key",
        project_id="test_project_id",
        model_api_key="test_model_api_key",
    )

    # Set up a mock for the stagehand instance
    mock_stagehand = MagicMock()

    # Create a mock async close method that does nothing
    async def mock_close():
        pass

    mock_stagehand.close = mock_close

    # Set the mock on the tool
    tool._stagehand = mock_stagehand
    tool._page = MagicMock()

    # Replace asyncio methods with mocks to avoid actual async execution
    with patch("asyncio.get_event_loop") as mock_get_loop:
        mock_loop = MagicMock()
        mock_get_loop.return_value = mock_loop
        mock_loop.is_running.return_value = False

        # Call the close method
        tool.close()

    # Verify resources were cleaned up
    assert tool._stagehand is None
    assert tool._page is None


if __name__ == "__main__":
    pytest.main(["-xvs", "stagehand_tool_test.py"])
