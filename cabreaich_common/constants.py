# /cabreaich-common/cabreaich_common/constants.py
# Centralized, immutable constants used across CAB ReAIch containers.
# These are NOT configurable at runtime and are intended to reduce duplication.

# -------------------
# 🔤 Azure Pronunciation Scoring
# -------------------

PHONEME_SCORE_KEY: str = "AccuracyScore"  # Key used for parsing phoneme-level accuracy from Azure output
AZURE_PRON_SCORE_RANGE: tuple[float, float] = (0.0, 100.0)  # Valid range for pronunciation/fluency scores
MINIMUM_VALID_SCORE: float = 0.0  # Defensive bound
MAXIMUM_VALID_SCORE: float = 100.0  # Defensive bound

# -------------------
# 🔁 Ring Buffer Settings
# -------------------

DEFAULT_AUDIO_RING_BUFFER_CHUNKS: int = 100  # Max number of audio chunks stored in SharedRingBuffer

# -------------------
# 📁 Logging / File Output
# -------------------

FALLBACK_LOG_PATH_DEFAULT: str = "/app/logs/speech_sdk.log"  # Default path for fallback logging
ALLOWED_LOG_ROTATION_BYTES: int = 2_000_000  # Max file size before rotation
ALLOWED_LOG_BACKUPS: int = 3  # Number of rotated log files to keep
LOG_TYPE_TURN: str = "turn"
LOG_TYPE_ERROR: str = "error"

# -------------------
# 🧠 Prompt Modes (String Constants)
# Use in configs, defaults, logging
# -------------------
MODE_SCORED: str = "scored"
MODE_OPEN: str = "open"
MODE_CHAT: str = "chat"
MODE_AUTO: str = "auto"


# -------------------
# 📂 Template & Fallback Paths (if not dynamic)
# -------------------

# These should match config_speech.py or speech_settings.*
FALLBACK_RESPONSES_PATH: str = "/app/fallback_responses.json"
DEFAULT_TEMPLATES_PATH: str = "/app/prompt_templates.json"

# -------------------
# ⏱️ Timing Thresholds (if VAD/scoring thresholds are added)
# -------------------
MIN_SPEECH_DURATION_MS: int = 300  # Minimum speech segment duration (ms)
MAX_SILENCE_DURATION_MS: int = 2000  # Max allowed silence between utterances (ms)
GAP_THRESHOLD_MS: int = 150  # Max allowed gap between syllables or phonemes (ms)

# -------------------
# 🗃️ Logging Types (for Cosmos + File Logs)
# -------------------
LOG_TYPE_TURN: str = "turn"
LOG_TYPE_ERROR: str = "error"

# -------------------
# 🚦 Prompt Mode Enum (Structured validation)
# Use with Pydantic or structured matching
# -------------------
from enum import Enum
class PromptMode(str, Enum):
    SCORED = "scored"
    OPEN = "open"
    CHAT = "chat"
    AUTO = "auto"

# --- Audio Queue / Pull Stream Constants ---
PREBUFFER_MAX_FRAMES = 20          # Frames to buffer before flushing to STT
QUEUE_PUT_TIMEOUT_SECONDS = 1.0    # Timeout for audio_capture put() operations
QUEUE_GET_TIMEOUT_SECONDS = 1.0    # Timeout for PullAudioInputStream read() ops
INITIAL_DATA_WAIT_SECONDS = 2.0    # How long to wait for first frame after enabling STT


# -------------------
# 🧾 Default Log Format (optional centralization)
# -------------------
DEFAULT_LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"

# ⏱️ Timing Thresholds (if VAD/scoring thresholds are added)
MIN_SPEECH_DURATION_MS: int = 300
MAX_SILENCE_DURATION_MS: int = 2000
GAP_THRESHOLD_MS: int = 150

# Energy-Based Detection (EBD)
EBD_SILENCE_THRESHOLD_DB: float = -40.0  # dBFS threshold to consider “silence”
EBD_MAX_SILENT_FRAMES: int = 20          # Number of consecutive silent frames