"""
Utility module for handling Amazon Bedrock Inline Agent responses.
"""

import os
import json
import traceback
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__file__)

class ResponseHandler:
    """Handler for processing Amazon Bedrock Inline Agent responses."""
    
    def __init__(self, output_folder: str = "output", enable_trace: bool = False):
        """Initialize the ResponseHandler."""
        self.output_folder = output_folder
        self.enable_trace = enable_trace
        self.generated_files = []
        self.token_usage = {"input_tokens": 0, "output_tokens": 0}
        self.llm_calls = 0
        
        # Create output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            
        if self.enable_trace:
            logger.debug(f"[TRACE] ResponseHandler initialized with output folder: {self.output_folder}")
    
    def process_response(self, response: Dict) -> str:
        """Process a Bedrock Inline Agent response."""
        try:
            # Clear previous state
            self.generated_files = []
            self.token_usage = {"input_tokens": 0, "output_tokens": 0}
            self.llm_calls = 0
            
            # Check response status
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                if self.enable_trace:
                    logger.error(f"[TRACE] Error: API Response was not 200: {response}")
                return f"Error: API Response was not 200: {response}"
            elif response['completion'] is None:
                if self.enable_trace:
                    logger.warning(f"[TRACE] No completion found in the response.")
                return "Error: No completion found in the response."
            
            if self.enable_trace:
                logger.debug(f"[TRACE] Processing response with request ID: {response['ResponseMetadata']['RequestId']}")
            
            # Process event stream
            agent_answer = ""
            event_stream = response['completion']
            
          
            # Process each event in the stream
            for event_idx, event in enumerate(event_stream):
              
                # Process text chunks
                if "chunk" in event:
                    data = event["chunk"]["bytes"]
                    text_chunk = data.decode("utf8")
                    agent_answer += text_chunk
                    if self.enable_trace:
                        print(f"[TRACE] Received text chunk ({len(text_chunk)} chars)")
                
                # Process files
                if "files" in event:
                    if self.enable_trace:
                        print(f"[TRACE] Found files in event")
                    self._process_files_event(event["files"])
                
                # Process trace information for token usage
                if "trace" in event and "trace" in event["trace"]:
                    if self.enable_trace:
                        print(f"[TRACE] Processing trace information")
                    self._update_token_usage(event["trace"]["trace"])
            
            # Add token usage summary to the response
            token_summary = self._get_token_summary()
            if token_summary:
                agent_answer += token_summary
            
            # Add generated files information to the response
            files_markdown = self._get_files_markdown()
            if files_markdown:
                agent_answer += files_markdown
            
            # Add a machine-readable file list for downstream agents
            file_list_json = self._get_files_json()
            if file_list_json:
                agent_answer += file_list_json
            
            if self.enable_trace:
                print(f"[TRACE] Response processing complete")
                print(f"[TRACE] Token usage: {self.token_usage['input_tokens']} input, {self.token_usage['output_tokens']} output")
                print(f"[TRACE] Generated Answer: \n{agent_answer}")
                print(f"[TRACE] Generated files: \n{len(self.generated_files)}")
                
            
            return agent_answer
        
        except Exception as e:
            error_msg = f"Error processing response: {str(e)}"
            if self.enable_trace:
                print(f"[TRACE] {error_msg}")
                print(f"[TRACE] {traceback.format_exc()}")
            return error_msg
    
    def _save_file(self, file_name: str, file_type: str, file_content, source: str = "direct") -> bool:
        """Save a file to disk and register it in the generated files list."""
        if self.enable_trace:
            print(f"[TRACE] Saving file: {file_name} ({file_type}) from {source}")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder, exist_ok=True)
            
        # Construct file path
        file_path = os.path.join(self.output_folder, file_name)
        
        try:
            # Check if file_content is already bytes or if it's a string
            if isinstance(file_content, bytes):
                # Binary data
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                if self.enable_trace:
                    print(f"[TRACE] Saved binary file: {file_path} ({len(file_content)} bytes)")
            else:
                # Text data
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                if self.enable_trace:
                    print(f"[TRACE] Saved text file: {file_path} ({len(file_content)} chars)")
            
            # Add to generated files list (avoid duplicates)
            self._add_to_files_list(file_name, file_type, file_path, source)
            return True
        except Exception as e:
            if self.enable_trace:
                print(f"[TRACE] Error saving file {file_path}: {str(e)}")
                print(f"[TRACE] {traceback.format_exc()}")
            return False
    
    def _add_to_files_list(self, file_name: str, file_type: str, file_path: str, source: str) -> None:
        """Add a file to the generated files list, avoiding duplicates."""
        # Check if file already exists in the list
        for existing_file in self.generated_files:
            if existing_file["name"] == file_name:
                # Update source if needed
                if source == "code_interpreter":
                    existing_file["source"] = source
                    if self.enable_trace:
                        print(f"[TRACE] Updated existing file source: {file_name} -> {source}")
                return
        
        # Add new file to the list
        self.generated_files.append({
            "name": file_name,
            "type": file_type,
            "path": file_path,
            "source": source
        })
        
        if self.enable_trace:
            print(f"[TRACE] Added file to generated list: {file_name} ({file_type})")
        
    
    def _process_files_event(self, files_event: Dict) -> None:
        """Process files from a files event."""
        files_list = files_event["files"]
        
        if self.enable_trace:
            print(f"[TRACE] Processing {len(files_list)} files from event")
        
        for file_idx, file in enumerate(files_list):
            file_name = file["name"]
            file_type = file["type"]
            file_content = file["bytes"]
            
            if self.enable_trace:
                print(f"[TRACE] Processing file {file_idx+1}/{len(files_list)}: {file_name} ({file_type})")
            
            # Save the file
            self._save_file(file_name, file_type, file_content, "direct")
    
    def _update_token_usage(self, trace_data: Dict) -> None:
        """Extract token usage from trace data."""
        print(f"[TRACE] {trace_data}")
        # Check different trace sections for token usage
        for section_name in ["orchestrationTrace", "preProcessingTrace", "postProcessingTrace"]:
            if section_name in trace_data:
                section = trace_data[section_name]
                if "modelInvocationOutput" in section and "metadata" in section["modelInvocationOutput"]:
                    metadata = section["modelInvocationOutput"]["metadata"]
                    if "usage" in metadata:
                        usage = metadata["usage"]
                        input_tokens = usage.get("inputTokens", 0)
                        output_tokens = usage.get("outputTokens", 0)
                        self.token_usage["input_tokens"] += input_tokens
                        self.token_usage["output_tokens"] += output_tokens
                        self.llm_calls += 1
                        
                        if self.enable_trace:
                            print(f"[TRACE] LLM call in {section_name}: {input_tokens} input tokens, {output_tokens} output tokens")
        
        # Process code interpreter if present
        if "orchestrationTrace" in trace_data and "observation" in trace_data["orchestrationTrace"]:
            obs = trace_data["orchestrationTrace"]["observation"]
            if "codeInterpreterInvocationOutput" in obs:
                code_output = obs["codeInterpreterInvocationOutput"]
                
                # Log code execution
                if self.enable_trace:
                    if "executionOutput" in code_output and code_output["executionOutput"]:
                        print(f"[TRACE] Code execution output: {code_output['executionOutput'][:200]}...")
                    if "executionError" in code_output and code_output["executionError"]:
                        print(f"[TRACE] Code execution error: {code_output['executionError']}")
                
                # Process files from code interpreter
                if "files" in code_output:
                    files = code_output["files"]
                    if self.enable_trace:
                        print(f"[TRACE] Code interpreter generated {len(files)} files")
                    
                    for file_name in files:
                        if isinstance(file_name, str):
                            file_path = os.path.join(self.output_folder, file_name)
                            if os.path.exists(file_path):
                                # Determine file type from extension
                                _, ext = os.path.splitext(file_name)
                                file_type = self._get_file_type(ext)
                                
                                if self.enable_trace:
                                    print(f"[TRACE] Found code-generated file: {file_name} ({file_type})")
                                
                                # Add to generated files list
                                self._add_to_files_list(file_name, file_type, file_path, "code_interpreter")
    
    def _get_file_type(self, extension: str) -> str:
        """Get the file type based on the file extension."""
        extension = extension.lower()
        
        if extension in ['.png', '.jpg', '.jpeg', '.gif']:
            return f"image/{extension[1:]}"
        elif extension == '.csv':
            return "text/csv"
        elif extension in ['.xls', '.xlsx']:
            return "application/vnd.ms-excel"
        else:
            return "application/octet-stream"
    
    def _get_files_markdown(self) -> str:
        """Get markdown references to generated files."""
        if not self.generated_files:
            return ""
        
        markdown = "\n\n## Generated Files\n\n"
        
        for file_info in self.generated_files:
            file_name = file_info["name"]
            file_path = file_info["path"]
            file_type = file_info["type"].lower()
            source = file_info["source"]
            
            if "image" in file_type:
                markdown += f"![{file_name}]({file_path}) (Source: {source})\n\n"
            elif "csv" in file_type:
                markdown += f"CSV file: [{file_name}]({file_path}) (Source: {source})\n\n"
            else:
                markdown += f"File: [{file_name}]({file_path}) (Source: {source})\n\n"
            
            # Add file path explicitly for downstream agents
            markdown += f"File path: `{file_path}`\n\n"
        
        if self.enable_trace:
            print(f"[TRACE] Generated markdown for {len(self.generated_files)} files")
            print(f"[TRACE] Markdown content:\n{markdown}")
        
        return markdown
    
    def _get_token_summary(self) -> str:
        """Get a summary of token usage."""
        total_tokens = self.token_usage["input_tokens"] + self.token_usage["output_tokens"]
        
        if total_tokens == 0:
            return ""
            
        summary = f"\n\n---\n### Token Usage\n"
        summary += f"- Input tokens: {self.token_usage['input_tokens']}\n"
        summary += f"- Output tokens: {self.token_usage['output_tokens']}\n"
        summary += f"- Total tokens: {total_tokens}\n"
        summary += f"- LLM calls: {self.llm_calls}\n"
        
        return summary
        
    def _get_files_json(self) -> str:
        """Get a machine-readable JSON representation of generated files."""
        if not self.generated_files:
            return ""
            
        # Create a simplified file list for downstream agents
        file_list = []
        for file_info in self.generated_files:
            file_list.append({
                "name": file_info["name"],
                "path": file_info["path"],
                "type": file_info["type"],
                "source": file_info["source"]
            })
            
        # Format as a code block for easy parsing
        json_str = json.dumps(file_list, indent=2)
        return f"\n\n```json\n// GENERATED_FILES\n{json_str}\n```\n"
