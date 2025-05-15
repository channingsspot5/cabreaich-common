import logging
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path # Added for robust path handling

# Attempt to import specific logging constants from cabreaich_common, with fallbacks
try:
    from cabreaich_common.constants import (
        FALLBACK_LOG_PATH_DEFAULT,    # Standardized name for default log file path
        ALLOWED_LOG_ROTATION_BYTES, # Standardized name for log rotation size in bytes
        ALLOWED_LOG_BACKUPS         # Standardized name for log backup count
    )
except ImportError:
    # Define fallback values if specific constants cannot be imported.
    # This might happen if this logging module is part of cabreaich_common itself
    # and is initialized before constants, or in an isolated environment.
    # A warning ideally would be logged here, but the logger isn't set up yet.
    # Using original hardcoded values as fallbacks:
    FALLBACK_LOG_PATH_DEFAULT = "/app/logs/speech_sdk.log"
    ALLOWED_LOG_ROTATION_BYTES = 2_000_000
    ALLOWED_LOG_BACKUPS = 3
    # To aid debugging if this happens:
    # print(f"Warning: Could not import logging constants from cabreaich_common.constants. Using hardcoded fallbacks for logging setup in logging.py.")


# --- Constants ---
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
TIMESTAMP_FIELD = "timestamp"
LEVEL_FIELD = "level"
MESSAGE_FIELD = "message"
SESSION_ID_FIELD = "session_id"
# Add other standard fields you want

# --- Pydantic Model for Log Records (Contract Testing) ---
class LogEntry(BaseModel):
    """Defines the structure for structured log entries."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    message: str
    logger_name: str
    session_id: uuid.UUID | None = None
    # Add other common fields with appropriate types
    # e.g., request_id: str | None = None
    # e.g., duration_ms: float | None = None
    # Use extra='allow' or specific fields for additional context
    class Config:
        extra = 'allow' # Allow arbitrary extra fields

# ---  Logger Setup (can be customized further) ---

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Sets up a logger with stdout + rotating file handler."""
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    if not logger.handlers: # Ensure handlers are not added multiple times
        formatter = logging.Formatter(LOG_FORMAT)

        # File handler using constants
        log_file_path = Path(FALLBACK_LOG_PATH_DEFAULT)
        # Ensure parent directory exists for the log file
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=str(log_file_path), # Convert Path object to string for the handler
            maxBytes=ALLOWED_LOG_ROTATION_BYTES,
            backupCount=ALLOWED_LOG_BACKUPS
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Stdout/console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


# Example usage elsewhere:
# from cabreaich_common.logging import setup_logger, LogEntry
# from cabreaich_common.config import settings
# logger = setup_logger(__name__, settings.LOG_LEVEL)
# log_data = LogEntry(level="INFO", message="Service started", logger_name=__name__)
# logger.info(log_data.model_dump_json()) # Example for structured JSON logging