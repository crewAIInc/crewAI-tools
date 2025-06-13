import json
import os
from typing import Any, Optional, Type

from crewai.tools import BaseTool
from openai import OpenAI
from pydantic import BaseModel

class VoicePromptSchema(BaseModel):
    """Input for CambAI Tool."""
    text: str


class CambAITool(BaseTool):
    name: str = "CambAI Tool"
    description: str = "Generates Speech from Text"
    args_schema: Type[BaseModel] = VoicePromptSchema
    api_key: Optional[str] = None
    voice_id: int = 20303
    language: int = 1
    client: Optional[Any] = None

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv('CAMB_API_KEY')
        if not api_key:
            raise ValueError(
                "`api_key` is required, please set the `CAMB_API_KEY` environment variable or pass it directly"
            )
        try:
            from cambai import CambAI
        except ImportError:
            raise ImportError("`cambai` package not found, please run `pip install cambai`")
        client = CambAI(api_key=self.api_key)
        self.client = client

    def _run(self, **kwargs) -> str:

        text = kwargs.get("text")
        voice_id = kwargs.get("voice_id")
        language = kwargs.get("language")

        if not text:
            return "Text is required."

        response = self.client.text_to_speech(
            text=text, 
            voice_id=voice_id if voice_id is not None else 20303, 
            language=language if language is not None else 1
        )

        audio_data = json.dumps(
            {
                "audio_url": response,
            }
        )

        return audio_data
