import os
import yaml
import inspect
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """Utility class for loading and processing YAML configuration files."""
    
    def __init__(self, base_directory: Optional[Path] = None, verbose: bool = False):
        """Initialize the ConfigLoader.
        
        Args:
            base_directory: The base directory for resolving relative paths
            verbose: Whether to print verbose output
        """
        self.verbose = verbose
        
        # Use provided base_directory or determine from calling class
        if base_directory:
            self.base_directory = base_directory
        else:
            # Get the directory of the calling class (similar to CrewBase)
            frame = inspect.currentframe().f_back
            try:
                calling_module = inspect.getmodule(frame)
                if calling_module:
                    module_file = calling_module.__file__
                    self.base_directory = Path(module_file).parent
                else:
                    self.base_directory = Path.cwd()
            except (AttributeError, ValueError):
                self.base_directory = Path.cwd()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load a YAML configuration file and process environment variables.
        
        Args:
            config_path: Path to the YAML configuration file (relative to base_directory)
            
        Returns:
            The loaded and processed configuration dictionary
        """
        # Resolve the path relative to the base directory
        full_path = self.base_directory / config_path
        
        if self.verbose:
            print(f"Looking for config file at: {full_path}")
        
        try:
            # Load the YAML file (following CrewBase pattern)
            config = self.load_yaml(full_path)
            
            # Process environment variables in the config
            self._process_env_vars_in_config(config)
                
            if self.verbose:
                print(f"Loaded configuration from {full_path}")
                
            return config
        except FileNotFoundError:
            if self.verbose:
                print(f"Configuration file not found at {full_path}. Using empty config.")
            return {}
        except Exception as e:
            if self.verbose:
                print(f"Error loading configuration: {str(e)}. Using empty config.")
            return {}
    
    def load_yaml(self, config_path: Path) -> Dict[str, Any]:
        """Load a YAML file.
        
        Args:
            config_path: Path to the YAML file
            
        Returns:
            The loaded YAML content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            if self.verbose:
                print(f"File not found: {config_path}")
            raise
    
    def _process_env_vars_in_config(self, config: Any) -> None:
        """Process environment variables in the configuration.
        
        This method recursively processes the configuration dictionary or list,
        replacing environment variable references (${VAR_NAME}) with their values.
        
        Args:
            config: The configuration object to process (dict or list)
        """
        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    env_value = os.environ.get(env_var)
                    if env_value:
                        config[key] = env_value
                    elif self.verbose:
                        print(f"Warning: Environment variable {env_var} not found")
                elif isinstance(value, (dict, list)):
                    self._process_env_vars_in_config(value)
        elif isinstance(config, list):
            for i, item in enumerate(config):
                if isinstance(item, (dict, list)):
                    self._process_env_vars_in_config(item)
                elif isinstance(item, str) and item.startswith("${") and item.endswith("}"):
                    env_var = item[2:-1]
                    env_value = os.environ.get(env_var)
                    if env_value:
                        config[i] = env_value
                    elif self.verbose:
                        print(f"Warning: Environment variable {env_var} not found")
