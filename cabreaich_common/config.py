# /home/reaich/CAB_ReAIch_Cloud/cabreaich-common/cabreaich_common/config.py
# Shared configuration loaded via Pydantic BaseSettings.
# Defines environment variables needed by MULTIPLE services.

import os
import logging # Keep for initial setup logging
from pydantic import AnyHttpUrl, Field, SecretStr, validator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Configure a basic logger specifically for config loading issues
# This runs before the common logger might be fully configured via settings
config_log = logging.getLogger(__name__ + ".config_loader")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the path to the .env file relative to where the app runs
# Assuming containers run with /app as the working directory
DOTENV_PATH = os.getenv("DOTENV_PATH", "/app/.env")
if not os.path.exists(DOTENV_PATH):
    config_log.warning(f".env file not found at specified DOTENV_PATH: {DOTENV_PATH}. Relying on environment variables.")
    effective_dotenv_path = None
else:
    config_log.info(f"Attempting to load environment variables from: {DOTENV_PATH}")
    effective_dotenv_path = DOTENV_PATH


class Settings(BaseSettings):
    """
    Shared configuration settings loaded from environment variables.
    These variables are expected to be used by multiple services.
    """

    # --- Shared Service URLs ---
    # URL for the QLogic routing service (Required)
    QLOGIC_ROUTE_URL: HttpUrl = Field(..., validation_alias="QLOGIC_ROUTE_URL")
    # URL for the Game Launch service (Required)
    GAME_LAUNCH_URL: HttpUrl = Field(..., validation_alias="GAME_LAUNCH_URL")
    # ADDED: URL for the Integration API (Required by Speech Container)
    INTEGRATION_API_URL: HttpUrl = Field(..., validation_alias="INTEGRATION_API_URL")
    # ADDED: URL for the Speech API (Required by Integration Container for callbacks)
    SPEECH_API_URL: HttpUrl = Field(..., validation_alias="SPEECH_API_URL")

    # --- Shared OpenAI Config (Example assuming standard API) ---
    # API Key for OpenAI (Required, treated as secret)
    OPENAI_KEY: SecretStr = Field(..., validation_alias="OPENAI_API_KEY")
    # Optional OpenAI Project ID
    OPENAI_PROJECT: Optional[str] = Field(None, validation_alias="OPENAI_PROJECT_ID")
    # Optional OpenAI Organization ID
    OPENAI_ORG: Optional[str] = Field(None, validation_alias="OPENAI_ORG_ID")
    # Default OpenAI Model to use if not specified elsewhere
    OPENAI_MODEL: str = Field("gpt-4-turbo", validation_alias="OPENAI_MODEL")

    # --- Shared Azure Cosmos DB Config (Required for shared logging/data) ---
    # Endpoint URL for Cosmos DB (Required)
    # Using AnyHttpUrl as Cosmos endpoint might not always be standard http/https
    AZURE_COSMOS_ENDPOINT: AnyHttpUrl = Field(..., validation_alias="AZURE_COSMOS_ENDPOINT")
    # Primary or Secondary Key for Cosmos DB (Required, treated as secret)
    AZURE_COSMOS_KEY: SecretStr = Field(..., validation_alias="AZURE_COSMOS_KEY")
    # Name of the Cosmos Database (Required)
    AZURE_COSMOS_DB: str = Field(..., validation_alias="AZURE_COSMOS_DB")
    # Name of the Cosmos Container (Required)
    AZURE_COSMOS_CONTAINER: str = Field(..., validation_alias="AZURE_COSMOS_CONTAINER")
    # Partition key path for the Cosmos Container (Required)
    AZURE_COSMOS_PARTITION_KEY_PATH: str = Field("/session_id", validation_alias="AZURE_COSMOS_PARTITION_KEY_PATH")

    # --- Shared Logging Config ---
    # Default log level for services (e.g., INFO, DEBUG, WARNING)
    LOG_LEVEL: str = Field("INFO", validation_alias="LOG_LEVEL")

    # --- Configuration for loading .env files ---
    model_config = SettingsConfigDict(
        env_file=effective_dotenv_path, # Load .env if it exists and path found
        env_file_encoding='utf-8',
        extra='ignore', # Ignore extra env vars not defined in the model
        # Use validation_alias to map env var names (e.g., OPENAI_API_KEY)
        # to field names (e.g., OPENAI_KEY) if they differ.
        case_sensitive=False # Environment variable names are typically case-insensitive
    )

    @validator('LOG_LEVEL')
    def validate_log_level(cls, value):
        """Ensure log level is a valid logging level name."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        upper_value = value.upper()
        if upper_value not in valid_levels:
            raise ValueError(f"Invalid LOG_LEVEL: {value}. Must be one of {valid_levels}")
        return upper_value

    @validator('AZURE_COSMOS_PARTITION_KEY_PATH')
    def validate_pk_path(cls, value):
        """Ensure partition key path starts with '/'."""
        if not value.startswith('/'):
            raise ValueError(f"Invalid AZURE_COSMOS_PARTITION_KEY_PATH: '{value}'. Must start with '/'.")
        return value


# --- Instantiate settings once for easy import across services ---
try:
    settings = Settings()
    # Use the specific config logger here
    config_log.info("Shared settings loaded successfully.")
    config_log.info(f"Log Level set to: {settings.LOG_LEVEL}")
    # Avoid logging sensitive URLs/keys in production environments
    # config_log.debug(f"QLogic URL: {settings.QLOGIC_ROUTE_URL}")
except Exception as e:
    # Handle potential validation errors during loading
    config_log.critical(f"CRITICAL: Failed to load/validate shared settings: {e}", exc_info=True)
    # Depending on the application, you might want to exit or raise here
    raise SystemExit(f"CRITICAL: Failed to load/validate shared settings: {e}") from e


# --- Example Usage (in other service code) ---
# from cabreaich_common.config import settings
#
# def call_qlogic(data: dict):
#     url = str(settings.QLOGIC_ROUTE_URL) # Access URL
#     # ... make request ...
#
# def get_cosmos_client():
#     endpoint = str(settings.AZURE_COSMOS_ENDPOINT)
#     key = settings.AZURE_COSMOS_KEY.get_secret_value() # Safely access secret
#     # ... create client ...
#
# print(f"Using OpenAI model: {settings.OPENAI_MODEL}")
# print(f"Log Level set to: {settings.LOG_LEVEL}")

    
