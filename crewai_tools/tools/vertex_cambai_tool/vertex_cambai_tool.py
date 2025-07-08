"""Vertex CambAI Tool for text-to-speech synthesis using Google Cloud Vertex AI."""

import base64
import json
import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel
from google.cloud import aiplatform

class VertexCambAISchema(BaseModel):
    """Input schema for Vertex CambAI Tool."""
    
    text: str
    audio_ref_path: str
    ref_text: str
    language: str = "en-us"
    output_file: str = "output.flac"


class VertexCambAITool(BaseTool):
    """Tool for text-to-speech synthesis using Google Cloud Vertex AI with CambAI's MARS7 model.
    
    This tool provides voice cloning capabilities using the MARS7 model.
    Requires Google Cloud credentials and Vertex AI endpoint access.
    
    Environment Variables Required:
        GOOGLE_APPLICATION_CREDENTIALS: Path to service account key file
        PROJECT_ID: Google Cloud project ID
        LOCATION: Google Cloud location (e.g., us-central1)
        ENDPOINT_ID: Vertex AI endpoint ID for MARS7 model
    """
    
    name: str = "Vertex CambAI Tool"
    description: str = (
        "Converts text to speech using CambAI's MARS7 model on Google Cloud Vertex AI. "
        "Requires reference audio and transcription for voice cloning."
    )
    args_schema: Type[BaseModel] = VertexCambAISchema
    package_dependencies: list = ["google-cloud-aiplatform", "soundfile"]
    
    def __init__(self, **kwargs):
        """Initialize the Vertex CambAI Tool."""
        super().__init__(**kwargs)
        
        # Check required environment variables
        required_vars = ["GOOGLE_APPLICATION_CREDENTIALS", "PROJECT_ID", "LOCATION", "ENDPOINT_ID"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Initialize Vertex AI
        try:
            aiplatform.init(
                project=os.getenv("PROJECT_ID"),
                location=os.getenv("LOCATION")
            )
        except ImportError:
            raise ImportError("Please install google-cloud-aiplatform: pip install google-cloud-aiplatform")
    
    def _run(self, **kwargs) -> str:
        """Execute the text-to-speech synthesis."""
        try:
            # Validate inputs
            schema = VertexCambAISchema(**kwargs)
            
            # Encode reference audio
            with open(schema.audio_ref_path, "rb") as f:
                audio_ref_base64 = base64.b64encode(f.read()).decode("utf-8")
            
            # Build prediction instances
            instances = {
                "text": schema.text,
                "audio_ref": audio_ref_base64,
                "ref_text": schema.ref_text,
                "language": schema.language
            }
            
            # Make prediction
            endpoint = aiplatform.Endpoint(endpoint_name=os.getenv("ENDPOINT_ID"))
            response = endpoint.raw_predict(
                body=json.dumps({"instances": [instances]}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            
            # Save audio response
            predictions = json.loads(response.content)["predictions"]
            audio_bytes = base64.b64decode(predictions[0])
            
            with open(schema.output_file, "wb") as f:
                f.write(audio_bytes)
            
            result = {
                "status": "success",
                "message": f"Audio saved to {schema.output_file}",
                "audio_file_path": os.path.abspath(schema.output_file),
                "text": schema.text,
                "language": schema.language
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "audio_file_path": None
            }
            return json.dumps(error_result, indent=2)