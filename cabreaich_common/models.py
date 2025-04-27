# /home/reaich/CAB_ReAIch_Cloud/cabreaich-common/cabreaich_common/models.py
# Defines shared Pydantic models for data transfer objects (DTOs) and API contracts.

import uuid
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any # Added Dict, Any

# --- Base Models (Optional, for common fields like timestamps) ---
class TimestampedModel(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))

# --- Enums ---

class VADEventType(str, Enum):
    """Enum for VAD event types emitted by the Speech Container."""
    SPEECH_START = "vad_speech_start"
    SPEECH_END = "vad_speech_end"

# --- API Data Models ---

class PhonemeData(BaseModel):
    """Represents phoneme information from pronunciation assessment."""
    phoneme: str = Field(..., description="The phoneme identifier (e.g., 'er').")
    score: float = Field(..., description="Accuracy score for the phoneme (0-100).")
    # Optional fields from Azure SDK if needed downstream
    # start_time: Optional[float] = Field(None, description="Start time in seconds from beginning of audio.")
    # end_time: Optional[float] = Field(None, description="End time in seconds from beginning of audio.")

class WordAssessmentData(BaseModel):
    """Represents word-level pronunciation assessment details."""
    word: str = Field(..., description="The word assessed.")
    accuracy: float = Field(..., description="Overall accuracy score for the word (0-100).")
    error_type: str = Field("None", description="Type of error (e.g., 'None', 'Mispronunciation', 'Omission').")
    phonemes: List[PhonemeData] = Field([], description="List of phoneme details for the word.")

class PronunciationAnalysisResult(BaseModel):
    """Structured result from pronunciation analysis."""
    recognized_text: str = Field("", description="The text recognized by the STT engine.")
    overall_score: float = Field(0.0, description="Overall accuracy score (0-100).")
    pronunciation_score: float = Field(0.0, description="Pronunciation accuracy score (0-100).")
    completeness_score: float = Field(0.0, description="Completeness score (0-100).")
    fluency_score: float = Field(0.0, description="Fluency score (0-100).")
    words: List[WordAssessmentData] = Field([], description="List of word-level assessment details.")
    # Optional: Add overall error message if analysis failed at a higher level
    error: Optional[str] = Field(None, description="Error message if analysis failed.")

class QLogicTurnInput(TimestampedModel):
    """
    Standardized data structure sent FROM Speech Container TO QLogic for routing.
    Refined based on session_turn_handler refactor.
    """
    child_id: uuid.UUID
    session_id: uuid.UUID
    target_phrase: Optional[str] = None
    stt_text: Optional[str] = None
    # Use the detailed analysis result model
    analysis_result: Optional[PronunciationAnalysisResult] = None
    # VAD/Emotion flags are now added by Integration layer, not sent from Speech
    # vad_flags: Optional[Dict[str, Any]] = Field(default_factory=dict)
    # emotion_tag: Optional[str] = None
    module_context: str = Field("speech_handler", description="Identifier of the calling module.")
    # last_action: Optional[str] = None # QLogic likely tracks history internally

class QLogicResponse(BaseModel):
    """
    Standardized data structure received FROM QLogic.
    Matches existing definition.
    """
    type: str = Field(..., description="The type of action QLogic decided (e.g., 'prompt', 'feedback', 'game').")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Data needed to execute the action.")

class VADEventData(TimestampedModel):
    """
    Data structure for VAD events sent FROM Speech Container TO Integration Container.
    """
    event_type: VADEventType = Field(..., description="The type of VAD event.")
    session_id: uuid.UUID = Field(..., description="The session this event belongs to.")
    # Inherits timestamp from TimestampedModel

class VADTimingFlagsData(TimestampedModel):
    """
    Data structure for sending generated VAD timing flags (e.g., from Integration to QLogic).
    """
    session_id: uuid.UUID
    # Flags are typically strings based on VADFlag enum values
    flags: List[str] = Field(..., description="List of detected VAD timing flags (e.g., ['false_start', 'syllable_gap']).")

class GuardianInputModel(BaseModel):
    """
    Standardized model for capturing guardian input data.
    """
    # Change type to uuid.UUID
    child_id: uuid.UUID = Field(..., alias="childId", description="Unique identifier for the child")
    source_id: str     = Field(..., alias="sourceId", description="Origin of guardian input")
    guardian_name: str = Field(..., alias="guardianName", description="Name of the person providing input")
    notes: str           = Field("", description="Additional comments or observations")
    timestamp: datetime  = Field(default_factory=datetime.utcnow)

    # Optional field for any extra, less structured data if needed in the future
    # For now, the primary fields cover the form data.
    details: Dict[str, Any] = Field(default_factory=dict, description="Any extra metadata")

    class Config:
        allow_population_by_field_name = True # Allows using 'childId' etc. during initialization
        json_encoders = {
             # Custom encoder to ensure ISO format with Z for UTC
             datetime: lambda v: v.isoformat(timespec='milliseconds') + "Z"
        }
        # Example for Pydantic v2 if needed:
        # populate_by_name = True
        # json_encoders = {datetime: lambda v: v.isoformat(timespec='milliseconds') + "Z"}

# --- Models for Audio Control API (Optional - if structure needed) ---
# Example: If pause/resume endpoints need specific bodies or return values

# class AudioControlRequest(BaseModel):
#     session_id: uuid.UUID # Usually part of the path, might not be needed in body
#     action: str # 'pause' or 'resume', usually part of path

# class AudioControlResponse(BaseModel):
#     session_id: uuid.UUID
#     status: str # e.g., "pause_request_accepted", "resume_request_accepted"
#     message: Optional[str] = None

# Add other shared Pydantic models here as needed (e.g., for Game Engine interactions)
