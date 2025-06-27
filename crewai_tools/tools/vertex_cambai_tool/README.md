# Vertex CambAI Tool

The Vertex CambAI Tool provides voice cloning capabilities using CambAI's MARS7 model deployed on Google Cloud Vertex AI. This tool requires reference audio and transcription for all voice synthesis.

## Features

- **Voice Cloning with MARS7**: High-quality voice cloning using CambAI's advanced model
- **Multilingual Support**: English (en-us) and Spanish (es-es)
- **FLAC Audio Output**: Professional-grade audio format
- **Google Cloud Integration**: Deployed on Vertex AI infrastructure

## Installation

Install the required dependencies:

```bash
pip install google-cloud-aiplatform soundfile
```

Or install with optional dependencies:

```bash
pip install crewai-tools[vertex-cambai]
```

## Setup

### Required Environment Variables

Set these environment variables before using the tool:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export PROJECT_ID="your-google-cloud-project-id"
export LOCATION="us-central1"
export ENDPOINT_ID="your-vertex-ai-endpoint-id"
```

### Google Cloud Setup

1. Create a Google Cloud service account with Vertex AI access
2. Download the service account key file
3. Deploy the MARS7 model on Vertex AI (contact CambAI for access)
4. Get your endpoint ID from the Vertex AI console

## Usage

### Basic Voice Cloning

```python
from crewai_tools import VertexCambAITool

# Initialize tool (requires environment variables)
tts_tool = VertexCambAITool()

# Synthesize speech with voice cloning
result = tts_tool.run(
    text="Hello, this will sound like my voice!",
    audio_ref_path="./my_voice_reference.wav",
    ref_text="This is the transcription of my reference audio",
    language="en-us",
    output_file="cloned_speech.flac"
)

print(result)
```

### Multilingual Voice Cloning

```python
from crewai_tools import VertexCambAITool

tts_tool = VertexCambAITool()

# English voice cloning
english_result = tts_tool.run(
    text="Hello, how are you today?",
    audio_ref_path="./english_ref.wav",
    ref_text="Hello, this is my English voice",
    language="en-us",
    output_file="english_output.flac"
)

# Spanish voice cloning
spanish_result = tts_tool.run(
    text="Hola, ¿cómo estás hoy?",
    audio_ref_path="./spanish_ref.wav", 
    ref_text="Hola, esta es mi voz en español",
    language="es-es",
    output_file="spanish_output.flac"
)
```

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | str | Text to synthesize |
| `audio_ref_path` | str | Path to reference audio file |
| `ref_text` | str | Transcription of reference audio |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | str | `"en-us"` | Language code (en-us, es-es) |
| `output_file` | str | `"output.flac"` | Output audio file path |

## Response Format

```json
{
  "status": "success",
  "message": "Audio saved to output.flac",
  "audio_file_path": "/absolute/path/to/output.flac",
  "text": "Synthesized text",
  "language": "en-us"
}
```

## Error Handling

```json
{
  "status": "error",
  "message": "Error description",
  "audio_file_path": null
}
```

## Supported Audio Formats

- **Input**: WAV, FLAC, MP3, M4A, OGG, WEBM
- **Output**: FLAC (default)

## Testing

Run the test script to verify your setup:

```bash
python test_vertex_cambai_example.py
```

Make sure all environment variables are set before testing.

## Integration with CrewAI

```python
from crewai import Agent, Task, Crew
from crewai_tools import VertexCambAITool

# Initialize tool
voice_tool = VertexCambAITool()

# Create agent
voice_agent = Agent(
    role="Voice Cloning Specialist",
    goal="Convert text to cloned speech",
    backstory="Expert in voice cloning with MARS7",
    tools=[voice_tool]
)

# Create task
task = Task(
    description="Clone voice saying: 'Welcome to CrewAI voice cloning!'",
    agent=voice_agent
)

# Run
crew = Crew(agents=[voice_agent], tasks=[task])
result = crew.kickoff()
```

## Troubleshooting

### Common Issues

**Missing Environment Variables**
```bash
ValueError: Missing required environment variables: PROJECT_ID, ENDPOINT_ID
```
Solution: Set all required environment variables

**Import Error**
```bash
ImportError: Please install google-cloud-aiplatform
```
Solution: `pip install google-cloud-aiplatform soundfile`

**File Not Found**
```bash
FileNotFoundError: [Errno 2] No such file or directory: './reference.wav'
```
Solution: Provide correct path to reference audio file

**Authentication Error**
```bash
DefaultCredentialsError: Could not automatically determine credentials
```
Solution: Check GOOGLE_APPLICATION_CREDENTIALS path

## Example Script

```python
#!/usr/bin/env python3
import os
import json
from crewai_tools import VertexCambAITool

# Set environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/key.json"
os.environ["PROJECT_ID"] = "your-project"
os.environ["LOCATION"] = "us-central1"
os.environ["ENDPOINT_ID"] = "your-endpoint"

# Initialize and use tool
tool = VertexCambAITool()
result = tool.run(
    text="This is a test of voice cloning",
    audio_ref_path="./reference.wav",
    ref_text="Hello, this is my reference voice",
    language="en-us"
)

# Parse result
data = json.loads(result)
if data["status"] == "success":
    print(f"✅ Audio saved: {data['audio_file_path']}")
else:
    print(f"❌ Error: {data['message']}")
```

## License

This tool is part of the CrewAI Tools package.

## Support

- **Tool Issues**: CrewAI Tools GitHub repository
- **MARS7 Model**: Contact CambAI support
- **Google Cloud**: Google Cloud documentation