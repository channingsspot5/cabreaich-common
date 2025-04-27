# /cabreaich-common/cabreaich_common/utils.py
# Generic utility functions shared across services.

import uuid
import logging
import re
from datetime import datetime, timezone # Use timezone-aware UTC
from .logging import LogEntry # Import your structured log model if using log_structured

# Get a logger instance for utility functions
# Using NullHandler to prevent "No handler found" warnings if not configured upstream.
util_logger = logging.getLogger(__name__)
if not util_logger.handlers:
    util_logger.addHandler(logging.NullHandler())

def generate_uuid() -> uuid.UUID:
    """Generates a new version 4 UUID."""
    return uuid.uuid4()

def clean_text(text: str) -> str:
    """
    Performs basic text cleaning: strips leading/trailing whitespace
    and replaces multiple consecutive whitespace characters with a single space.
    Does NOT remove punctuation or special characters.
    """
    if not isinstance(text, str):
        util_logger.warning("clean_text received non-string input, returning empty string.")
        return ""
    text = text.strip()
    # Replace multiple whitespace characters (space, tab, newline etc.) with a single space
    text = re.sub(r'\s+', ' ', text)
    return text

def format_datetime_iso(dt: datetime | None = None) -> str:
    """
    Formats a datetime object into ISO 8601 string format (UTC) with milliseconds.
    If no datetime is provided, uses the current UTC time.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    # Ensure the datetime is timezone-aware (assume UTC if naive)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # Format to ISO 8601 with milliseconds and 'Z' for UTC
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def log_structured(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Logs a message using the structured LogEntry model (if defined in logging.py).
    Requires LogEntry Pydantic model to be defined in cabreaich_common.logging.

    Args:
        logger: The logging.Logger instance to use.
        level: The log level (e.g., "INFO", "WARNING").
        message: The main log message.
        **kwargs: Additional fields to include in the structured log
                  (e.g., session_id, duration_ms).
    """
    # Ensure level is valid
    level_upper = level.upper()
    log_level_int = getattr(logging, level_upper, logging.INFO) # Default to INFO if invalid

    if logger.isEnabledFor(log_level_int):
        try:
            log_entry = LogEntry(
                level=level_upper,
                message=message,
                logger_name=logger.name,
                **kwargs # Pass any extra fields directly
            )
            # Log as JSON string (adapt if your logging setup expects dicts)
            logger.log(log_level_int, log_entry.model_dump_json(exclude_none=True))
        except NameError:
            # Fallback if LogEntry is not available or structured logging isn't set up
            logger.log(log_level_int, f"{message} | Extra: {kwargs}")
        except Exception as e:
            logger.error(f"Failed to create or log structured entry: {e}", exc_info=True)


# --- Example Usage ---
# from cabreaich_common.utils import generate_uuid, clean_text, format_datetime_iso, log_structured
# import logging
# logger = logging.getLogger("my_service") # Assume logger is configured elsewhere
#
# session_id = generate_uuid()
# raw_text = "  some input\t text  with extra   spaces. "
# cleaned = clean_text(raw_text) # Result: "some input text with extra spaces."
# timestamp = format_datetime_iso()
#
# log_structured(logger, "info", "Processing started", session_id=session_id, input_text=cleaned)


