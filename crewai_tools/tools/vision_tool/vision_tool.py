import base64
from pathlib import Path
from typing import Type

from crewai import LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, field_validator


class ImagePromptSchema(BaseModel):
    """Input for Vision Tool."""

    image_path_url: str = "The image path or URL."

    @field_validator("image_path_url")
    def validate_image_path_url(cls, v: str) -> str:
        if v.startswith("http"):
            return v

        path = Path(v)
        if not path.exists():
            raise ValueError(f"Image file does not exist: {v}")

        # Validate supported formats
        valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Unsupported image format. Supported formats: {valid_extensions}"
            )

        return v


class VisionTool(BaseTool):
    name: str = "Vision Tool"
    description: str = (
        "This tool uses OpenAI's Vision API to describe the contents of an image."
    )
    args_schema: Type[BaseModel] = ImagePromptSchema

    def __init__(self, llm: LLM | None = None, **kwargs):
        super().__init__(**kwargs)

        self._llm = llm

    @property
    def llm(self) -> LLM:
        """Default LLM instance."""
        if self._llm is None:
            self._llm = LLM(
                model="gpt-4o-mini",
            )
        return self._llm

    def _run(self, **kwargs):
        try:
            image_path_url = kwargs.get("image_path_url")
            if not image_path_url:
                return "Image Path or URL is required."

            # Validate input using Pydantic
            ImagePromptSchema(image_path_url=image_path_url)

            if image_path_url.startswith("http"):
                image_data = image_path_url
            else:
                try:
                    base64_image = self._encode_image(image_path_url)
                    image_data = f"data:image/jpeg;base64,{base64_image}"
                except Exception as e:
                    return f"Error processing image: {str(e)}"

                response = self.llm.call(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "What's in this image?"},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_data},
                                },
                            ],
                        },
                    ],
                )
                return response
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
