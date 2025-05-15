# /home/reaich/CAB_ReAIch_Cloud/cabreaich-common/cabreaich_common/config.py
# Shared configuration loaded via Pydantic BaseSettings.
# Defines environment variables needed by MULTIPLE services.

import os
import logging # Keep for initial setup logging
from enum import Enum # Added for LogLevel Enum
from pydantic import AnyHttpUrl, Field, SecretStr, validator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Configure a basic logger specifically for config loading issues
# This runs before the common logger might be fully configured via settings
config_log = logging.getLogger(__name__ + ".config_loader")
# BasicConfig should ideally only be called once. If another module calls it,
# subsequent calls might be ignored. For a library, it's often better to
# let the application configure basicConfig. However, for this specific config_log,
# it's done here for early feedback.
if not config_log.handlers: # Avoid adding multiple handlers if module is reloaded
    logging.basicConfig(level=os.getenv("PRE_CONFIG_LOG_LEVEL", "INFO").upper(), 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define LogLevel Enum
class LogLevel(str, Enum):
    """Standard logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    # DEBUG_VERBOSE could be added if it's a distinct level you handle,
    # otherwise, DEBUG usually covers verbosity.
    # For Pydantic conversion, it will match these names case-insensitively by default.

# Define the path to the .env file relative to where the app runs
# Assuming containers run with /app as the working directory
DOTENV_PATH = os.getenv("DOTENV_PATH", "/app/.env") # This can be specific to the container
if not os.path.exists(DOTENV_PATH) and DOTENV_PATH != "/app/.env": # Log only if a custom path was specified and not found
    config_log.warning(f".env file not found at specified DOTENV_PATH: {DOTENV_PATH}. Relying on environment variables or default .env path.")
    # If default /app/.env also not found, pydantic will just ignore it.
    # effective_dotenv_path = None # BaseSettings handles missing file gracefully
elif os.path.exists(DOTENV_PATH):
    config_log.info(f"Attempting to load environment variables from: {DOTENV_PATH}")
    # effective_dotenv_path = DOTENV_PATH # Not needed, BaseSettings takes path directly


class Settings(BaseSettings):
    """
    Shared configuration settings loaded from environment variables.
    These variables are expected to be used by multiple services.
    """

    # --- Shared Service URLs ---
    QLOGIC_ROUTE_URL: HttpUrl = Field(..., validation_alias="QLOGIC_ROUTE_URL")
    GAME_LAUNCH_URL: HttpUrl = Field(..., validation_alias="GAME_LAUNCH_URL")
    INTEGRATION_API_URL: HttpUrl = Field(..., validation_alias="INTEGRATION_API_URL")
    SPEECH_API_URL: HttpUrl = Field(..., validation_alias="SPEECH_API_URL")

    # --- Shared OpenAI Config ---
    OPENAI_KEY: SecretStr = Field(..., validation_alias="OPENAI_API_KEY")
    OPENAI_PROJECT: Optional[str] = Field(None, validation_alias="OPENAI_PROJECT_ID")
    OPENAI_ORG: Optional[str] = Field(None, validation_alias="OPENAI_ORG_ID")
    OPENAI_MODEL: str = Field("gpt-4-turbo", validation_alias="OPENAI_MODEL")

    # --- Shared Azure Cosmos DB Config ---
    AZURE_COSMOS_ENDPOINT: AnyHttpUrl = Field(..., validation_alias="AZURE_COSMOS_ENDPOINT")
    AZURE_COSMOS_KEY: SecretStr = Field(..., validation_alias="AZURE_COSMOS_KEY")
    AZURE_COSMOS_DB: str = Field(..., validation_alias="AZURE_COSMOS_DB")
    AZURE_COSMOS_CONTAINER: str = Field(..., validation_alias="AZURE_COSMOS_CONTAINER")
    AZURE_COSMOS_PARTITION_KEY_PATH: str = Field("/session_id", validation_alias="AZURE_COSMOS_PARTITION_KEY_PATH")

    # --- Azure Speech Settings ---
    AZURE_SPEECH_KEY: SecretStr = Field(..., validation_alias="AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION: str = Field(..., validation_alias="AZURE_SPEECH_REGION")

    # --- Shared Logging Config ---
    # Use the LogLevel Enum for type safety and validation
    # Pydantic will attempt to convert the string from ENV (e.g., "DEBUG")
    # to a LogLevel Enum member. It's case-insensitive for string enums.
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, validation_alias="LOG_LEVEL")

    # --- Configuration for loading .env files ---
    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH if os.path.exists(DOTENV_PATH) else None, # Pass path if it exists
        env_file_encoding='utf-8',
        extra='ignore', 
        case_sensitive=False # Env var names are typically case-insensitive
    )

    # Removed custom validate_log_level as Pydantic handles Enum conversion and validation.
    # If custom error messages or specific transformations (like .upper()) were strictly
    # needed before Enum conversion, a pre-validator could be used, but generally not required.

    @validator('AZURE_COSMOS_PARTITION_KEY_PATH')
    def validate_pk_path(cls, value: str) -> str: # Added type hint for value
        """Ensure partition key path starts with '/'."""
        if not value.startswith('/'):
            raise ValueError(f"Invalid AZURE_COSMOS_PARTITION_KEY_PATH: '{value}'. Must start with '/'.")
        return value


# --- Instantiate settings once for easy import across services ---
try:
    settings = Settings()
    config_log.info("Shared settings loaded successfully.")
    # LOG_LEVEL will now be an Enum member. Access its string value via .value
    config_log.info(f"Log Level set to: {settings.LOG_LEVEL.value} (Enum member: {settings.LOG_LEVEL})")
except Exception as e:
    config_log.critical(f"CRITICAL: Failed to load/validate shared settings: {e}", exc_info=True)
    raise SystemExit(f"CRITICAL: Failed to load/validate shared settings: {e}") from e


# --- Example Usage (in other service code) ---
# from cabreaich_common.config import settings, LogLevel
#
# # To use the log level string value for configuring a logger:
# # logger.setLevel(settings.LOG_LEVEL.value)
#
# def call_qlogic(data: dict):
#     url = str(settings.QLOGIC_ROUTE_URL) 
#     # ... make request ...
#
# def get_cosmos_client():
#     endpoint = str(settings.AZURE_COSMOS_ENDPOINT)
#     key = settings.AZURE_COSMOS_KEY.get_secret_value() 
#     # ... create client ...
#
# print(f"Using OpenAI model: {settings.OPENAI_MODEL}")
# print(f"Log Level (Enum): {settings.LOG_LEVEL}, Log Level (value): {settings.LOG_LEVEL.value}")