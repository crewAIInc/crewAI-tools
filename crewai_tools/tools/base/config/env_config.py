"""Central configuration for environment variables with validation."""
import os
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class EnvVarType(str, Enum):
    """Types of environment variables for validation."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    URL = "url"
    API_KEY = "api_key"


class EnvVarConfig(BaseModel):
    """Configuration for an environment variable."""

    name: str = Field(description="Name of the environment variable")
    description: str = Field(
        description="Description of what the environment variable is used for"
    )
    required: bool = Field(
        default=True, description="Whether the environment variable is required"
    )
    var_type: EnvVarType = Field(
        default=EnvVarType.STRING,
        description="Type of the environment variable for validation",
    )
    min_length: Optional[int] = Field(
        default=None, description="Minimum length of the environment variable value"
    )
    is_secret: bool = Field(
        default=False,
        description="Whether the environment variable contains sensitive data",
    )

    def mask_value(self, value: str) -> str:
        """Mask sensitive values in error messages.

        Args:
            value: The value to mask

        Returns:
            Masked value if is_secret is True, otherwise original value
        """
        if not self.is_secret or not value:
            return value
        if len(value) <= 8:
            return "*" * len(value)
        return value[:4] + "*" * (len(value) - 8) + value[-4:]


class EnvironmentConfig(BaseModel):
    """Central configuration for environment variables."""

    env_vars: Dict[str, EnvVarConfig] = Field(
        default_factory=dict,
        description="Dictionary of environment variable configurations",
    )

    def register_var(
        self,
        name: str,
        description: str,
        required: bool = True,
        min_length: Optional[int] = None,
        is_secret: bool = False,
    ) -> None:
        """Register a new environment variable configuration.

        Args:
            name: Name of the environment variable
            description: Description of what the environment variable is used for
            required: Whether the environment variable is required
            min_length: Minimum length of the environment variable value
            is_secret: Whether the environment variable contains sensitive data
        """
        self.env_vars[name] = EnvVarConfig(
            name=name,
            description=description,
            required=required,
            min_length=min_length,
            is_secret=is_secret,
        )

    def get_var_config(self, name: str) -> Optional[EnvVarConfig]:
        """Get the configuration for an environment variable.

        Args:
            name: Name of the environment variable

        Returns:
            Configuration for the environment variable if registered, None otherwise
        """
        return self.env_vars.get(name)

    def validate_var(self, name: str) -> Optional[str]:
        """Validate an environment variable against its configuration.

        Args:
            name: Name of the environment variable to validate

        Returns:
            Error message if validation fails, None if validation succeeds
        """
        config = self.get_var_config(name)
        if not config:
            return f"Environment variable {name} is not registered"

        value = os.getenv(name)
        if config.required and not value:
            return f"Required environment variable {name} is not set"

        if not value:
            return None

        if config.min_length and len(value) < config.min_length:
            masked_value = config.mask_value(value)
            return f"Environment variable {name} must be at least {config.min_length} characters long (got {len(masked_value)} characters)"

        try:
            if config.var_type == EnvVarType.INTEGER:
                int(value)
            elif config.var_type == EnvVarType.FLOAT:
                float(value)
            elif config.var_type == EnvVarType.BOOLEAN:
                value = value.lower()
                if value not in ("true", "false", "1", "0"):
                    raise ValueError
            elif config.var_type == EnvVarType.URL:
                from urllib.parse import urlparse

                result = urlparse(value)
                if not all([result.scheme, result.netloc]):
                    raise ValueError
        except ValueError:
            masked_value = config.mask_value(value)
            return f"Environment variable {name} must be a valid {config.var_type.value} (got {masked_value})"

        return None


# Global environment configuration instance
env_config = EnvironmentConfig()

# Register common environment variables
env_config.register_var(
    "OPENAI_API_KEY",
    "OpenAI API key for language model access",
    required=True,
    min_length=20,
    is_secret=True,
)

env_config.register_var(
    "SERPLY_API_KEY",
    "Serply API key for web search and content extraction",
    required=True,
    min_length=32,
    is_secret=True,
)

env_config.register_var(
    "MULTION_API_KEY",
    "MultiOn API key for browser automation",
    required=True,
    min_length=32,
    is_secret=True,
)

env_config.register_var(
    "BRAVE_API_KEY",
    "Brave Search API key for web search",
    required=True,
    min_length=32,
    is_secret=True,
)

env_config.register_var(
    "EXA_API_KEY",
    "EXA API key for search functionality",
    required=True,
    min_length=32,
    is_secret=True,
)
