import json
import os
import random
from typing import Any, Optional, Type
from dataclasses import dataclass

from crewai.tools import BaseTool
from pydantic import BaseModel

from .constants import (
    DEFAULT_LANGUAGE,
    CAMB_API_KEY_ENV,
    MISSING_API_KEY_ERROR,
    MISSING_PACKAGE_ERROR,
    MISSING_TEXT_ERROR,
    NO_VOICES_AVAILABLE_ERROR,
    API_ERROR,
    NETWORK_ERROR,
    REQUIRED_PACKAGES,
    TOOL_NAME,
    TOOL_DESCRIPTION,
)

@dataclass
class CambAIConfig:
    """Configuration dataclass for CambAI TTS Tool.
    
    Attributes:
        api_key (Optional[str]): API key for CambAI authentication.
        voice_id (Optional[int]): Specific voice ID to use for speech generation.
        language (Optional[int]): Language code for speech generation.
    """
    api_key: Optional[str] = None
    voice_id: Optional[int] = None
    language: Optional[int] = DEFAULT_LANGUAGE


class VoicePromptSchema(BaseModel):
    """Input schema for CambAI TTS Tool.
    
    Attributes:
        text (str): The text to convert to speech.
    """
    text: str


class VoiceManager:
    """Manages voice selection for CambAI TTS.
    
    This class handles retrieving available voices from the CambAI API
    and selecting voices for text-to-speech conversion.
    """
    
    def __init__(self, client: Any) -> None:
        """Initialize VoiceManager with CambAI client.
        
        Args:
            client: CambAI client instance for API communication.
        """
        self.client = client

    def get_random_voice(self) -> int:
        """Get a random voice ID from available voices.
        
        Returns:
            int: Random voice ID from available voices.
            
        Raises:
            RuntimeError: If no voices are available or API call fails.
        """
        try:
            voices = self.client.list_voices()
            if not voices:
                raise RuntimeError(NO_VOICES_AVAILABLE_ERROR)
            
            voice_list = [voice.id for voice in voices]
            return random.choice(voice_list)
            
        except Exception as e:
            if "no voices" in str(e).lower():
                raise RuntimeError(NO_VOICES_AVAILABLE_ERROR) from e
            raise RuntimeError(f"{API_ERROR}: {str(e)}") from e
class CambAITTSTool(BaseTool):
    """CambAI Text-to-Speech Tool for CrewAI.
    
    This tool converts text to speech using the CambAI API, allowing agents
    to generate high-quality audio from text input. It supports multiple voices
    and languages, with automatic voice selection when not specified.
    
    Attributes:
        name (str): The name of the tool.
        description (str): Description of what the tool does.
        args_schema (Type[BaseModel]): Pydantic schema for input validation.
        api_key (Optional[str]): CambAI API key for authentication.
        voice_id (Optional[int]): Specific voice ID to use.
        language (Optional[int]): Language code for speech generation.
        client (Optional[Any]): CambAI client instance.
        package_dependencies (List[str]): Required packages for this tool.
    
    Usage:
        >>> tool = CambAITTSTool(api_key="your-api-key")
        >>> result = tool.run(text="Hello, world!")
        >>> audio_data = json.loads(result)
        >>> audio_url = audio_data["audio_url"]
    """
    
    name: str = TOOL_NAME
    description: str = TOOL_DESCRIPTION
    args_schema: Type[BaseModel] = VoicePromptSchema
    api_key: Optional[str] = None
    voice_id: Optional[int] = None
    language: Optional[int] = None
    client: Any = None
    config: Optional[CambAIConfig] = None
    package_dependencies: list[str] = REQUIRED_PACKAGES

    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[int] = None, language: Optional[int] = None, **kwargs) -> None:
        """Initialize CambAI TTS Tool.
        
        Args:
            api_key (Optional[str]): CambAI API key. If not provided,
                                   will look for CAMB_API_KEY environment variable.
            voice_id (Optional[int]): Default voice ID to use.
            language (Optional[int]): Default language code.
            **kwargs: Additional arguments passed to BaseTool.
        
        Raises:
            ValueError: If no API key is provided or found in environment.
            ImportError: If cambai-sdk package is not installed.
            RuntimeError: If client initialization fails.
        """
        super().__init__(**kwargs)
        
        # Create configuration
        self.config = CambAIConfig(
            api_key=api_key or os.getenv(CAMB_API_KEY_ENV),
            voice_id=voice_id,
            language=language or DEFAULT_LANGUAGE
        )
        
        if not self.config.api_key:
            raise ValueError(MISSING_API_KEY_ERROR)
        
        # Set instance attributes for compatibility
        self.api_key = self.config.api_key
        self.voice_id = self.config.voice_id
        self.language = self.config.language
        
        # Import and initialize CambAI client
        try:
            from cambai import CambAI
        except ImportError as e:
            raise ImportError(MISSING_PACKAGE_ERROR) from e
        
        try:
            self.client = CambAI(api_key=self.config.api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize CambAI client: {str(e)}") from e

    def _run(self, **kwargs) -> str:
        """Execute text-to-speech conversion.
        
        Args:
            **kwargs: Keyword arguments containing:
                - text (str): Text to convert to speech (required)
                - voice_id (Optional[int]): Specific voice ID to use
                - language (Optional[int]): Language code for speech
        
        Returns:
            str: JSON string containing audio_url of the generated speech
        
        Raises:
            ValueError: If required text parameter is missing or invalid
            RuntimeError: If API call fails or other errors occur
        """
        try:
            from cambai.models.output_type import OutputType
        except ImportError as e:
            raise ImportError(MISSING_PACKAGE_ERROR) from e
        
        # Extract and validate parameters
        text = kwargs.get("text")
        voice_id = kwargs.get("voice_id", self.voice_id)
        language = kwargs.get("language", self.language)
        
        if not isinstance(text, str) or not text or not text.strip():
            raise ValueError(MISSING_TEXT_ERROR)

        # Get voice ID if not provided
        if not voice_id:
            try:
                voice_manager = VoiceManager(self.client)
                voice_id = voice_manager.get_random_voice()
            except Exception as e:
                raise RuntimeError(f"Failed to get voice: {str(e)}") from e

        # Perform text-to-speech conversion
        try:
            response = self.client.text_to_speech(
                text=text.strip(),
                voice_id=voice_id,
                language=language if language is not None else DEFAULT_LANGUAGE,
                output_type=OutputType.FILE_URL
            )
        except Exception as e:
            if "network" in str(e).lower() or "connection" in str(e).lower():
                raise RuntimeError(f"{NETWORK_ERROR}: {str(e)}") from e
            raise RuntimeError(f"{API_ERROR}: {str(e)}") from e

        # Validate and format response
        if not response:
            raise RuntimeError("Empty response from CambAI API")

        try:
            audio_data = json.dumps({
                "audio_url": response,
            })
            return audio_data
        except Exception as e:
            raise RuntimeError(f"Failed to format response: {str(e)}") from e
