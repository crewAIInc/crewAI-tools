"""Constants for CambAI TTS Tool."""

# Default values
DEFAULT_LANGUAGE = 1
DEFAULT_OUTPUT_TYPE = "FILE_URL"

# Environment variables
CAMB_API_KEY_ENV = "CAMB_API_KEY"

# Error messages
MISSING_API_KEY_ERROR = (
    "`api_key` is required, please set the `CAMB_API_KEY` environment variable or pass it directly"
)
MISSING_PACKAGE_ERROR = "`cambai` package not found, please run `pip install cambai-sdk`"
MISSING_TEXT_ERROR = "Text parameter is required for text-to-speech conversion"
NO_VOICES_AVAILABLE_ERROR = "No voices available from CambAI API"
API_ERROR = "CambAI API error occurred"
NETWORK_ERROR = "Network error while connecting to CambAI API"

# Package dependencies
REQUIRED_PACKAGES = ["cambai-sdk"]

# Tool metadata
TOOL_NAME = "CambAI TTS Tool"
TOOL_DESCRIPTION = "Converts text to speech using CambAI API"