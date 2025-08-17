import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from browser_use import Agent as BrowserUseAgent
from browser_use.agent.views import AgentHistoryList as BrowserUseAgentHistoryList
from browser_use.llm import BaseChatModel as BrowserUseBaseChatModel
from pydantic import ValidationError

from crewai_tools.tools.browser_use_tool import (
    BrowserUseTool,
    BrowserUseToolSchema,
)


class MockLLM(BrowserUseBaseChatModel):
    """Mock LLM for testing."""
    def __init__(self):
        pass


class TestBrowserUseToolSchema:
    """Test suite for BrowserUseToolSchema."""

    def test_schema_with_valid_instruction(self):
        """Test schema creation with valid instruction."""
        schema = BrowserUseToolSchema(
            instruction="Navigate to Google and search for CrewAI",
            max_steps=100
        )
        assert schema.instruction == "Navigate to Google and search for CrewAI"
        assert schema.max_steps == 100  # default value

    def test_schema_with_custom_max_steps(self):
        """Test schema creation with custom max_steps."""
        schema = BrowserUseToolSchema(
            instruction="Search for something",
            max_steps=50
        )
        assert schema.instruction == "Search for something"
        assert schema.max_steps == 50

    def test_schema_requires_instruction(self):
        """Test that instruction is required."""
        with pytest.raises(ValidationError):
            BrowserUseToolSchema(instruction="", max_steps=100)

    def test_schema_json_schema(self):
        """Test that schema generates correct JSON schema."""
        json_schema = BrowserUseToolSchema.model_json_schema()

        assert "properties" in json_schema
        assert "instruction" in json_schema["properties"]
        assert "max_steps" in json_schema["properties"]
        assert json_schema["properties"]["instruction"]["type"] == "string"
        # max_steps can be null (None) so it uses anyOf structure
        assert "anyOf" in json_schema["properties"]["max_steps"] or "type" in json_schema["properties"]["max_steps"]
        assert json_schema["required"] == ["instruction"]


class TestBrowserUseTool:
    """Test suite for BrowserUseTool."""

    def test_tool_creation_with_valid_llm(self):
        """Test tool creation with valid LLM."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        assert tool.llm == mock_llm
        assert tool.args_schema == BrowserUseToolSchema
        assert tool.agent_kwargs == {}
        assert tool.browser_loop is None

    def test_tool_creation_with_agent_kwargs(self):
        """Test tool creation with custom agent_kwargs."""
        mock_llm = MockLLM()
        agent_kwargs = {"validate_output": False, "timeout": 30}
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None, agent_kwargs=agent_kwargs)

        assert tool.agent_kwargs == agent_kwargs

    def test_tool_creation_requires_llm(self):
        """Test that LLM is required for tool creation."""
        with pytest.raises(ValidationError):
            BrowserUseTool()

    def test_tool_creation_with_invalid_llm(self):
        """Test that invalid LLM raises error."""
        with pytest.raises(ValidationError):
            BrowserUseTool(llm=None)

    def test_get_emoji_success(self):
        """Test emoji generation for success evaluation."""
        emoji = BrowserUseTool._get_emoji("Success: Task completed")
        assert emoji == "👍"

    def test_get_emoji_failed(self):
        """Test emoji generation for failed evaluation."""
        emoji = BrowserUseTool._get_emoji("Failed: Could not find element")
        assert emoji == "⚠️"

    def test_get_emoji_unknown(self):
        """Test emoji generation for unknown evaluation."""
        emoji = BrowserUseTool._get_emoji("In progress")
        assert emoji == "🤷"

    def test_parse_history_empty(self):
        """Test parsing empty history."""
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = []  # Empty history - this triggers "Browser did not do anything."
        result = BrowserUseTool._parse_history(
            instruction="Test instruction",
            agent_history_list=mock_history,
            max_steps=100
        )
        assert result == "Browser did not do anything."

    def test_parse_history_with_data(self):
        """Test parsing history with actual data."""
        # Create mock history
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock()]  # Non-empty history

        # Mock state
        mock_state = MagicMock()
        mock_state.evaluation_previous_goal = "Success: Found element"
        mock_state.memory = "Previous action successful"
        mock_state.next_goal = "Click on search button"

        # Mock model output
        mock_action = MagicMock()
        mock_action.model_dump_json.return_value = '{"type": "click", "element": "button"}'
        mock_model_output = MagicMock()
        mock_model_output.action = [mock_action]

        # Configure mock methods
        mock_history.model_thoughts.return_value = [mock_state]
        mock_history.extracted_content.return_value = ["Search results found"]
        mock_history.model_outputs.return_value = [mock_model_output]
        mock_history.is_done.return_value = True
        mock_history.has_errors.return_value = False

        result = BrowserUseTool._parse_history(
            instruction="Search for CrewAI",
            agent_history_list=mock_history,
            max_steps=100
        )

        assert "🚀 Starting task: Search for CrewAI" in result
        assert "✅ Successfully completed browser interaction." in result
        assert "📍 Step 1:" in result
        assert "👍 Evaluation: Success: Found element" in result
        assert "🧠 Memory: Previous action successful" in result
        assert "🎯 Next Goal: Click on search button" in result
        assert "📄 Result: Search results found" in result

    def test_parse_history_not_done(self):
        """Test parsing history when task is not completed."""
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock()]
        mock_history.model_thoughts.return_value = []
        mock_history.extracted_content.return_value = []
        mock_history.model_outputs.return_value = []
        mock_history.is_done.return_value = False
        mock_history.has_errors.return_value = False

        result = BrowserUseTool._parse_history(
            instruction="Test",
            agent_history_list=mock_history,
            max_steps=50
        )

        assert "❌ Failed to complete browser interaction in 50 maximum steps." in result

    def test_parse_history_with_errors(self):
        """Test parsing history when there are errors."""
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock()]
        mock_history.model_thoughts.return_value = []
        mock_history.extracted_content.return_value = []
        mock_history.model_outputs.return_value = []
        mock_history.is_done.return_value = True
        mock_history.has_errors.return_value = True
        mock_history.errors.return_value = ["Timeout error", "Element not found"]

        result = BrowserUseTool._parse_history(
            instruction="Test",
            agent_history_list=mock_history,
            max_steps=100
        )

        assert "❌ Failed to complete browser interaction due to errors:" in result
        assert "Timeout error" in result
        assert "Element not found" in result

    @pytest.mark.asyncio
    async def test_run_with_no_instruction(self):
        """Test running tool without instruction."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        result = tool._run(instruction="")
        assert result == "No instruction provided."

    @pytest.mark.asyncio
    async def test_run_successful(self):
        """Test successful browser task execution."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        # Mock the browser agent
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock()]
        mock_history.model_thoughts.return_value = []
        mock_history.extracted_content.return_value = []
        mock_history.model_outputs.return_value = []
        mock_history.is_done.return_value = True
        mock_history.has_errors.return_value = False

        with patch.object(tool, '_create_browser_task', return_value=mock_history):
            with patch.object(BrowserUseAgent, '__init__', return_value=None):
                result = tool._run(instruction="Navigate to Google")

                assert "🚀 Starting task: Navigate to Google" in result
                assert "✅ Successfully completed browser interaction." in result

    @pytest.mark.asyncio
    async def test_run_with_cancellation(self):
        """Test handling of cancelled browser task."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        with patch.object(tool, '_create_browser_task', side_effect=asyncio.CancelledError()):
            with patch.object(BrowserUseAgent, '__init__', return_value=None):
                with patch.object(BrowserUseAgent, 'stop'):
                    result = tool._run(instruction="Test task")

                    assert "Browser agent was interrupted" in result
                    assert "You MUST stop now and return a result!" in result

    @pytest.mark.asyncio
    async def test_run_with_exception(self):
        """Test handling of exceptions during execution."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        with patch.object(tool, '_create_browser_task', side_effect=RuntimeError("Test error")):
            with patch.object(BrowserUseAgent, '__init__', return_value=None):
                with patch.object(BrowserUseAgent, 'stop'):
                    result = tool._run(instruction="Test task")

                    assert "Error during execution: Test error" in result
                    assert "Browser agent was interrupted" in result

    @pytest.mark.asyncio
    async def test_create_browser_task_without_loop(self):
        """Test creating browser task without custom event loop."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        mock_agent = MagicMock(spec=BrowserUseAgent)
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_agent.run = AsyncMock(return_value=mock_history)

        result = await tool._create_browser_task(mock_agent, 100)
        assert result == mock_history

    def test_tool_attributes(self):
        """Test that BrowserUseTool has correct attributes."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        assert tool.name == "Browser Use Tool"
        assert "Interact with the browser using natural language commands" in tool.description
        assert "Basic navigation actions" in tool.description
        assert "Element interaction actions" in tool.description
        assert "Tab management actions" in tool.description
        assert "Content actions" in tool.description
        assert "Google Sheets actions" in tool.description

    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test executing the BrowserUseTool."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        # Mock successful execution
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock()]
        mock_history.model_thoughts.return_value = []
        mock_history.extracted_content.return_value = []
        mock_history.model_outputs.return_value = []
        mock_history.is_done.return_value = True
        mock_history.has_errors.return_value = False

        with patch.object(tool, '_create_browser_task', return_value=mock_history):
            with patch.object(BrowserUseAgent, '__init__', return_value=None):
                result = tool._run(
                    instruction="Search for CrewAI on Google",
                    max_steps=50
                )

                assert "🚀 Starting task: Search for CrewAI on Google" in result
                assert "✅ Successfully completed browser interaction." in result

    def test_tool_schema_properties(self):
        """Test that tool schema has expected properties."""
        schema = BrowserUseToolSchema.model_json_schema()

        # Check instruction field
        assert schema["properties"]["instruction"]["description"]
        assert "natural language" in schema["properties"]["instruction"]["description"].lower()

        # Check max_steps field
        assert schema["properties"]["max_steps"]["description"]
        assert "maximum number of steps" in schema["properties"]["max_steps"]["description"].lower()
        assert schema["properties"]["max_steps"]["default"] == 100


class TestIntegration:
    """Integration tests for BrowserUseTool."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow from instruction to result."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        # Create comprehensive mock history
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock(), MagicMock()]  # Two steps

        # Mock states for two steps
        state1 = MagicMock()
        state1.evaluation_previous_goal = "Success: Navigated to Google"
        state1.memory = "Google homepage loaded"
        state1.next_goal = "Enter search query"

        state2 = MagicMock()
        state2.evaluation_previous_goal = "Success: Search completed"
        state2.memory = "Search results displayed"
        state2.next_goal = "Task complete"

        # Mock actions
        action1 = MagicMock()
        action1.model_dump_json.return_value = '{"type": "navigate", "url": "google.com"}'
        action2 = MagicMock()
        action2.model_dump_json.return_value = '{"type": "input", "text": "CrewAI"}'

        output1 = MagicMock()
        output1.action = [action1]
        output2 = MagicMock()
        output2.action = [action2]

        # Configure mock methods
        mock_history.model_thoughts.return_value = [state1, state2]
        mock_history.extracted_content.return_value = ["Google homepage", "Search results for CrewAI"]
        mock_history.model_outputs.return_value = [output1, output2]
        mock_history.is_done.return_value = True
        mock_history.has_errors.return_value = False

        with patch.object(tool, '_create_browser_task', return_value=mock_history):
            with patch.object(BrowserUseAgent, '__init__', return_value=None):
                result = tool._run(
                    instruction="Search for CrewAI on Google",
                    max_steps=100
                )

                # Verify the result contains expected elements
                assert "🚀 Starting task: Search for CrewAI on Google" in result
                assert "📍 Step 1:" in result
                assert "📍 Step 2:" in result
                assert "Google homepage loaded" in result
                assert "Search results displayed" in result
                assert "✅ Successfully completed browser interaction." in result

    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test error recovery and reporting."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        # Test various error scenarios
        error_scenarios = [
            (asyncio.CancelledError(), "Browser agent was interrupted"),
            (RuntimeError("Connection failed"), "Error during execution: Connection failed"),
            (ValueError("Invalid input"), "Error during execution: Invalid input"),
        ]

        for error, expected_message in error_scenarios:
            with patch.object(tool, '_create_browser_task', side_effect=error):
                with patch.object(BrowserUseAgent, '__init__', return_value=None):
                    with patch.object(BrowserUseAgent, 'stop'):
                        result = tool._run(instruction="Test error handling")
                        assert expected_message in result

    def test_validate_llm_field_validator(self):
        """Test the LLM field validator."""
        # Test with valid LLM
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)
        assert tool.llm == mock_llm

        # Test with None LLM
        with pytest.raises(ValidationError) as exc_info:
            BrowserUseTool(llm=None)
        assert "llm must be specified" in str(exc_info.value)

    def test_parse_history_empty_history_list(self):
        """Test parsing when history list exists but history is empty."""
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = []  # Empty history list

        result = BrowserUseTool._parse_history(
            instruction="Test instruction",
            agent_history_list=mock_history,
            max_steps=100
        )
        assert result == "Browser did not do anything."

    def test_parse_history_without_memory(self):
        """Test parsing history when state has no memory."""
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock()]

        # Mock state without memory
        mock_state = MagicMock()
        mock_state.evaluation_previous_goal = "Success: Task done"
        mock_state.memory = None  # No memory
        mock_state.next_goal = "Complete"

        # Mock model output
        mock_action = MagicMock()
        mock_action.model_dump_json.return_value = '{"type": "done"}'
        mock_model_output = MagicMock()
        mock_model_output.action = [mock_action]

        # Configure mock methods
        mock_history.model_thoughts.return_value = [mock_state]
        mock_history.extracted_content.return_value = [None]  # No extracted content
        mock_history.model_outputs.return_value = [mock_model_output]
        mock_history.is_done.return_value = True
        mock_history.has_errors.return_value = False

        result = BrowserUseTool._parse_history(
            instruction="Test without memory",
            agent_history_list=mock_history,
            max_steps=100
        )

        # Should not contain memory line when memory is None
        assert "🧠 Memory:" not in result
        assert "📄 Result:" not in result  # No extracted content either
        assert "✅ Successfully completed browser interaction." in result

    @pytest.mark.asyncio
    async def test_create_browser_task_return_type(self):
        """Test that _create_browser_task returns correct type."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        mock_agent = MagicMock(spec=BrowserUseAgent)
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_agent.run = AsyncMock(return_value=mock_history)

        # Test without loop - should return history directly
        result = await tool._create_browser_task(mock_agent, 100)
        assert result == mock_history

    @pytest.mark.asyncio
    async def test_run_with_custom_max_steps(self):
        """Test running with custom max_steps parameter."""
        mock_llm = MockLLM()
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None)

        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock()]
        mock_history.model_thoughts.return_value = []
        mock_history.extracted_content.return_value = []
        mock_history.model_outputs.return_value = []
        mock_history.is_done.return_value = False  # Not done
        mock_history.has_errors.return_value = False

        with patch.object(tool, '_create_browser_task', return_value=mock_history):
            with patch.object(BrowserUseAgent, '__init__', return_value=None):
                with patch.object(BrowserUseAgent, 'run', new_callable=AsyncMock):
                    result = tool._run(instruction="Test task", max_steps=25)

                    # Check that max_steps was used correctly
                    assert "❌ Failed to complete browser interaction in 25 maximum steps." in result

    def test_browser_use_tool_exports(self):
        """Test that all expected classes are exported."""
        from crewai_tools.tools.browser_use_tool import __all__

        assert "BrowserUseTool" in __all__
        assert "BrowserUseToolSchema" in __all__
        assert len(__all__) == 2

    def test_schema_field_descriptions(self):
        """Test that schema fields have proper descriptions."""
        schema = BrowserUseToolSchema.model_json_schema()

        # Check instruction field description
        instruction_desc = schema["properties"]["instruction"]["description"]
        assert "natural language" in instruction_desc
        assert "broken down into multiple steps" in instruction_desc

        # Check max_steps field description
        max_steps_desc = schema["properties"]["max_steps"]["description"]
        assert "maximum number of steps" in max_steps_desc
        assert "step-by-step" in max_steps_desc
        assert "increase the max_steps" in max_steps_desc

    def test_browser_agent_initialization(self):
        """Test that BrowserUseAgent is initialized with correct parameters."""
        mock_llm = MockLLM()
        agent_kwargs = {"validate_output": False, "timeout": 60}
        tool = BrowserUseTool(llm=mock_llm, browser_loop=None, agent_kwargs=agent_kwargs)

        with patch.object(BrowserUseAgent, '__init__', return_value=None) as mock_init:
            with patch.object(tool, '_create_browser_task', side_effect=Exception("Stop early")):
                with patch.object(BrowserUseAgent, 'stop'):
                    tool._run(instruction="Test initialization")

                    # Verify BrowserUseAgent was initialized with correct params
                    mock_init.assert_called_once()
                    call_kwargs = mock_init.call_args.kwargs
                    assert call_kwargs["task"] == "Test initialization"
                    assert call_kwargs["llm"] == mock_llm
                    assert not call_kwargs["validate_output"]
                    assert call_kwargs["timeout"] == 60

    def test_multiple_actions_in_step(self):
        """Test parsing history with multiple actions in a single step."""
        mock_history = MagicMock(spec=BrowserUseAgentHistoryList)
        mock_history.history = [MagicMock()]

        # Mock state
        mock_state = MagicMock()
        mock_state.evaluation_previous_goal = "Success: Multiple actions"
        mock_state.memory = "Performing multiple actions"
        mock_state.next_goal = "Continue"

        # Mock multiple actions
        action1 = MagicMock()
        action1.model_dump_json.return_value = '{"type": "click", "element": "button1"}'
        action2 = MagicMock()
        action2.model_dump_json.return_value = '{"type": "input", "text": "test"}'
        action3 = MagicMock()
        action3.model_dump_json.return_value = '{"type": "submit"}'

        mock_model_output = MagicMock()
        mock_model_output.action = [action1, action2, action3]

        # Configure mock methods
        mock_history.model_thoughts.return_value = [mock_state]
        mock_history.extracted_content.return_value = ["Form submitted"]
        mock_history.model_outputs.return_value = [mock_model_output]
        mock_history.is_done.return_value = True
        mock_history.has_errors.return_value = False

        result = BrowserUseTool._parse_history(
            instruction="Submit form",
            agent_history_list=mock_history,
            max_steps=100
        )

        # Verify all three actions are in the output
        assert "⚒️ Action 1:" in result
        assert "⚒️ Action 2:" in result
        assert "⚒️ Action 3:" in result
        assert '"type": "click"' in result
        assert '"type": "input"' in result
        assert '"type": "submit"' in result