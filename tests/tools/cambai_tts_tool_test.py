"""Unit tests for CambAI TTS Tool."""

import json
import os
from unittest.mock import MagicMock, patch
import pytest

from crewai_tools.tools.cambai_tool.cambai_tts_tool import (
    CambAITTSTool,
    VoiceManager,
    CambAIConfig,
)
from crewai_tools.tools.cambai_tool.constants import (
    MISSING_API_KEY_ERROR,
    MISSING_PACKAGE_ERROR,
    MISSING_TEXT_ERROR,
    NO_VOICES_AVAILABLE_ERROR,
    API_ERROR,
    NETWORK_ERROR,
)


class TestCambAITTSTool:
    """Test cases for CambAITTSTool class."""

    @pytest.fixture
    def mock_cambai_client(self):
        """Create a mock CambAI client."""
        mock_client = MagicMock()
        mock_client.text_to_speech.return_value = "https://example.com/audio.wav"
        
        # Mock voice objects
        mock_voice1 = MagicMock()
        mock_voice1.id = 1
        mock_voice2 = MagicMock()
        mock_voice2.id = 2
        mock_client.list_voices.return_value = [mock_voice1, mock_voice2]
        
        return mock_client

    @pytest.fixture
    def tool_with_api_key(self, mock_cambai_client):
        """Create CambAI tool instance with API key."""
        with patch('builtins.__import__') as mock_import:
            def import_side_effect(name, *args, **kwargs):
                if name == 'cambai':
                    mock_cambai_module = MagicMock()
                    mock_cambai_module.CambAI.return_value = mock_cambai_client
                    return mock_cambai_module
                else:
                    return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            tool = CambAITTSTool(api_key="test-api-key")
            return tool

    @pytest.fixture
    def tool_with_env_key(self, mock_cambai_client):
        """Create CambAI tool instance using environment variable."""
        with patch.dict(os.environ, {'CAMB_API_KEY': 'env-api-key'}):
            with patch('builtins.__import__') as mock_import:
                def import_side_effect(name, *args, **kwargs):
                    if name == 'cambai':
                        mock_cambai_module = MagicMock()
                        mock_cambai_module.CambAI.return_value = mock_cambai_client
                        return mock_cambai_module
                    else:
                        return __import__(name, *args, **kwargs)
                
                mock_import.side_effect = import_side_effect
                tool = CambAITTSTool()
                return tool

    def test_tool_initialization_with_api_key(self, tool_with_api_key):
        """Test tool initialization with API key parameter."""
        assert tool_with_api_key.api_key == "test-api-key"
        assert tool_with_api_key.client is not None
        assert tool_with_api_key.name == "CambAI TTS Tool"
        assert "Converts text to speech using CambAI API" in tool_with_api_key.description

    def test_tool_initialization_with_env_key(self, tool_with_env_key):
        """Test tool initialization with environment variable."""
        assert tool_with_env_key.api_key == "env-api-key"
        assert tool_with_env_key.client is not None

    def test_tool_initialization_no_api_key(self):
        """Test tool initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match=MISSING_API_KEY_ERROR):
                CambAITTSTool()

    def test_tool_initialization_missing_package(self):
        """Test tool initialization fails when cambai package is missing."""
        def import_side_effect(name, *args, **kwargs):
            if name == 'cambai':
                raise ImportError("No module named 'cambai'")
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=import_side_effect):
            with pytest.raises(ImportError, match=MISSING_PACKAGE_ERROR):
                CambAITTSTool(api_key="test-key")

    def test_tool_initialization_client_failure(self):
        """Test tool initialization fails when client creation fails."""
        with patch('builtins.__import__') as mock_import:
            def import_side_effect(name, *args, **kwargs):
                if name == 'cambai':
                    mock_cambai_module = MagicMock()
                    mock_cambai_module.CambAI.side_effect = Exception("Client error")
                    return mock_cambai_module
                else:
                    return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            with pytest.raises(RuntimeError, match="Failed to initialize CambAI client"):
                CambAITTSTool(api_key="test-key")

    def test_successful_text_to_speech(self, tool_with_api_key):
        """Test successful text-to-speech conversion."""
        result = tool_with_api_key._run(text="Hello, world!")
        
        # Verify the result is valid JSON
        audio_data = json.loads(result)
        assert "audio_url" in audio_data
        assert audio_data["audio_url"] == "https://example.com/audio.wav"
        
        # Verify client was called correctly
        tool_with_api_key.client.text_to_speech.assert_called_once()
        call_args = tool_with_api_key.client.text_to_speech.call_args
        assert call_args[1]["text"] == "Hello, world!"

    def test_text_to_speech_with_voice_id(self, tool_with_api_key):
        """Test text-to-speech with specific voice ID."""
        result = tool_with_api_key._run(text="Hello", voice_id=123)
        
        # Verify client was called with specific voice ID
        call_args = tool_with_api_key.client.text_to_speech.call_args
        assert call_args[1]["voice_id"] == 123

    def test_text_to_speech_with_language(self, tool_with_api_key):
        """Test text-to-speech with specific language."""
        result = tool_with_api_key._run(text="Hello", language=2)
        
        # Verify client was called with specific language
        call_args = tool_with_api_key.client.text_to_speech.call_args
        assert call_args[1]["language"] == 2

    def test_missing_text_parameter(self, tool_with_api_key):
        """Test error when text parameter is missing."""
        with pytest.raises(ValueError, match=MISSING_TEXT_ERROR):
            tool_with_api_key._run()

    def test_empty_text_parameter(self, tool_with_api_key):
        """Test error when text parameter is empty."""
        with pytest.raises(ValueError, match=MISSING_TEXT_ERROR):
            tool_with_api_key._run(text="")
        
        with pytest.raises(ValueError, match=MISSING_TEXT_ERROR):
            tool_with_api_key._run(text="   ")

    def test_non_string_text_parameter(self, tool_with_api_key):
        """Test error when text parameter is not a string."""
        with pytest.raises(ValueError, match=MISSING_TEXT_ERROR):
            tool_with_api_key._run(text=123)

    def test_api_error_handling(self, tool_with_api_key):
        """Test handling of API errors."""
        tool_with_api_key.client.text_to_speech.side_effect = Exception("API error")
        
        with pytest.raises(RuntimeError, match=API_ERROR):
            tool_with_api_key._run(text="Hello")

    def test_network_error_handling(self, tool_with_api_key):
        """Test handling of network errors."""
        tool_with_api_key.client.text_to_speech.side_effect = Exception("Network connection failed")
        
        with pytest.raises(RuntimeError, match=NETWORK_ERROR):
            tool_with_api_key._run(text="Hello")

    def test_empty_api_response(self, tool_with_api_key):
        """Test handling of empty API response."""
        tool_with_api_key.client.text_to_speech.return_value = None
        
        with pytest.raises(RuntimeError, match="Empty response from CambAI API"):
            tool_with_api_key._run(text="Hello")

    def test_missing_output_type_import(self, tool_with_api_key):
        """Test error when OutputType import fails."""
        with patch('builtins.__import__') as mock_import:
            def import_side_effect(name, *args, **kwargs):
                if name == 'cambai.models.output_type':
                    raise ImportError("No module named 'cambai.models.output_type'")
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            with pytest.raises(ImportError, match=MISSING_PACKAGE_ERROR):
                tool_with_api_key._run(text="Hello")


class TestVoiceManager:
    """Test cases for VoiceManager class."""

    @pytest.fixture
    def mock_client_with_voices(self):
        """Create mock client with available voices."""
        mock_client = MagicMock()
        mock_voice1 = MagicMock()
        mock_voice1.id = 1
        mock_voice2 = MagicMock()
        mock_voice2.id = 2
        mock_client.list_voices.return_value = [mock_voice1, mock_voice2]
        return mock_client

    @pytest.fixture
    def mock_client_no_voices(self):
        """Create mock client with no available voices."""
        mock_client = MagicMock()
        mock_client.list_voices.return_value = []
        return mock_client

    def test_voice_manager_initialization(self, mock_client_with_voices):
        """Test VoiceManager initialization."""
        voice_manager = VoiceManager(mock_client_with_voices)
        assert voice_manager.client == mock_client_with_voices

    def test_get_random_voice_success(self, mock_client_with_voices):
        """Test successful random voice selection."""
        voice_manager = VoiceManager(mock_client_with_voices)
        voice_id = voice_manager.get_random_voice()
        
        assert voice_id in [1, 2]
        mock_client_with_voices.list_voices.assert_called_once()

    def test_get_random_voice_no_voices_available(self, mock_client_no_voices):
        """Test error when no voices are available."""
        voice_manager = VoiceManager(mock_client_no_voices)
        
        with pytest.raises(RuntimeError, match=NO_VOICES_AVAILABLE_ERROR):
            voice_manager.get_random_voice()

    def test_get_random_voice_api_error(self):
        """Test error handling when voice API call fails."""
        mock_client = MagicMock()
        mock_client.list_voices.side_effect = Exception("API error")
        
        voice_manager = VoiceManager(mock_client)
        
        with pytest.raises(RuntimeError, match=API_ERROR):
            voice_manager.get_random_voice()

    def test_get_random_voice_no_voices_error(self):
        """Test specific error message when no voices available."""
        mock_client = MagicMock()
        mock_client.list_voices.side_effect = Exception("no voices available")
        
        voice_manager = VoiceManager(mock_client)
        
        with pytest.raises(RuntimeError, match=NO_VOICES_AVAILABLE_ERROR):
            voice_manager.get_random_voice()



class TestCambAIConfig:
    """Test cases for CambAIConfig dataclass."""

    def test_config_default_values(self):
        """Test default values in config dataclass."""
        config = CambAIConfig()
        assert config.api_key is None
        assert config.voice_id is None
        assert config.language == 1

    def test_config_with_values(self):
        """Test config dataclass with provided values.""" 
        config = CambAIConfig(
            api_key="test-key",
            voice_id=123,
            language=2
        )
        assert config.api_key == "test-key"
        assert config.voice_id == 123
        assert config.language == 2


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.text_to_speech.return_value = "https://example.com/test-audio.wav"
        
        mock_voice = MagicMock()
        mock_voice.id = 42
        mock_client.list_voices.return_value = [mock_voice]
        
        with patch('builtins.__import__') as mock_import:
            def import_side_effect(name, *args, **kwargs):
                if name == 'cambai':
                    mock_cambai_module = MagicMock()
                    mock_cambai_module.CambAI.return_value = mock_client
                    return mock_cambai_module
                elif name == 'cambai.models.output_type':
                    mock_output_module = MagicMock()
                    mock_output_module.OutputType.FILE_URL = "FILE_URL"
                    return mock_output_module
                else:
                    return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            # Create tool and run
            tool = CambAITTSTool(api_key="integration-test-key")
            result = tool._run(text="Integration test message")
            
            # Verify results
            audio_data = json.loads(result)
            assert audio_data["audio_url"] == "https://example.com/test-audio.wav"
            
            # Verify API calls
            mock_client.list_voices.assert_called_once()
            mock_client.text_to_speech.assert_called_once()
            
            call_args = mock_client.text_to_speech.call_args
            assert call_args[1]["text"] == "Integration test message"
            assert call_args[1]["voice_id"] == 42
            assert call_args[1]["language"] == 1


if __name__ == "__main__":
    pytest.main([__file__])