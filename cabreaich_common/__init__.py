# /home/reaich/CAB_ReAIch_Cloud/cabreaich-common/cabreaich_common/__init__.py
# Make key components easily importable from the package root

# Version
from .version import __version__

# Configuration
from .config import settings

# Logging
from .logging import setup_logger, LogEntry, LOG_FORMAT

# Exceptions
from .exceptions import CabreaichError, APIError, ValidationError

# Flags / Enums
from .flags import VADFlag, EngagementFlag, QualityFlag, EmotionFlag # Add others as needed

# Models (Import commonly used ones, others can be imported directly from .models)
from .models import (
    GuardianInputModel,
    QLogicResponse,
    QLogicTurnInput,
    VADEventData,
    VADEventType,
    PhonemeData,
    WordAssessmentData,
    PronunciationAnalysisResult,
    VADTimingFlagsData # Add any other frequently used models
)

# Clients (Expose the async clients defined)
from .clients import (
    AsyncBaseClient,
    AsyncIntegrationClient,
    AsyncSpeechApiClient,
    AsyncQLogicClient
)

# Utilities
from .utils import generate_uuid, clean_text, format_datetime_iso, log_structured

#Constants
from .constants import (
    PHONEME_SCORE_KEY,
    AZURE_PRON_SCORE_RANGE,
    DEFAULT_AUDIO_RING_BUFFER_CHUNKS,
    FALLBACK_LOG_PATH_DEFAULT,
    ALLOWED_LOG_ROTATION_BYTES,
    ALLOWED_LOG_BACKUPS,
    LOG_TYPE_TURN,
    LOG_TYPE_ERROR,
    MODE_SCORED,
    MODE_OPEN,
    MODE_CHAT,
    MODE_AUTO,
    PromptMode,
    FALLBACK_RESPONSES_PATH,
    DEFAULT_TEMPLATES_PATH,
)

# Define __all__ to specify the intended public API (adjust as needed)
__all__ = [
    # Version
    "__version__",
    # Config
    "settings",
    # Logging
    "setup_logger",
    "LogEntry",
    "LOG_FORMAT",
    # Exceptions
    "CabreaichError",
    "APIError",
    "ValidationError",
    # Flags / Enums
    "VADFlag",
    "EngagementFlag",
    "QualityFlag",
    "EmotionFlag",
    # Models
    "GuardianInputModel",
    "QLogicResponse",
    "QLogicTurnInput",
    "VADEventData",
    "VADEventType",
    "PhonemeData",
    "WordAssessmentData",
    "PronunciationAnalysisResult",
    "VADTimingFlagsData",
    # Clients
    "AsyncBaseClient",
    "AsyncIntegrationClient",
    "AsyncSpeechApiClient",
    "AsyncQLogicClient",
    # Utilities
    "generate_uuid",
    "clean_text",
    "format_datetime_iso",
    "log_structured",
    #Constants
    "PHONEME_SCORE_KEY",
    "AZURE_PRON_SCORE_RANGE",
    "DEFAULT_AUDIO_RING_BUFFER_CHUNKS",
    "FALLBACK_LOG_PATH_DEFAULT",
    "ALLOWED_LOG_ROTATION_BYTES",
    "ALLOWED_LOG_BACKUPS",
    "LOG_TYPE_TURN",
    "LOG_TYPE_ERROR",
    "MODE_SCORED",
    "MODE_OPEN",
    "MODE_CHAT",
    "MODE_AUTO",
    "PromptMode",
    "FALLBACK_RESPONSES_PATH",
    "DEFAULT_TEMPLATES_PATH",
]