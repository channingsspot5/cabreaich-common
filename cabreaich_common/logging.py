import logging
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import os
from logging.handlers import RotatingFileHandler


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
    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)

        # File handler
        os.makedirs("/app/logs", exist_ok=True)
        file_handler = RotatingFileHandler("/app/logs/speech_sdk.log", maxBytes=2_000_000, backupCount=3)
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
