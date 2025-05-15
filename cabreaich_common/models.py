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

    class Config:
        populate_by_name = True # Allows population by field name as well as alias
        extra = "allow" # Or "ignore" if preferred

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
    # start_time: Optional[float] = Field(None, alias="startTime", description="Start time in seconds from beginning of audio.")
    # duration: Optional[float] = Field(None, description="Duration in seconds.") # Azure uses "Duration", not "endTime" typically for this level

    class Config:
        populate_by_name = True
        extra = "allow"

class WordAssessmentData(BaseModel):
    """Represents word-level pronunciation assessment details."""
    word: str = Field(..., description="The word assessed.")
    accuracy: float = Field(..., description="Overall accuracy score for the word (0-100).") # Already snake_case
    error_type: str = Field("None", alias="errorType", description="Type of error (e.g., 'None', 'Mispronunciation', 'Omission').")
    phonemes: List[PhonemeData] = Field([], description="List of phoneme details for the word.")

    class Config:
        populate_by_name = True
        extra = "allow"

class PronunciationAnalysisResult(BaseModel):
    """Structured result from pronunciation analysis."""
    recognized_text: str = Field("", alias="recognizedText", description="The text recognized by the STT engine.")
    overall_score: float = Field(0.0, alias="overallScore", description="Overall accuracy score (0-100).")
    pronunciation_score: float = Field(0.0, alias="pronunciationScore", description="Pronunciation accuracy score (0-100).")
    completeness_score: float = Field(0.0, alias="completenessScore", description="Completeness score (0-100).")
    fluency_score: float = Field(0.0, alias="fluencyScore", description="Fluency score (0-100).")
    words: List[WordAssessmentData] = Field([], description="List of word-level assessment details.")
    error: Optional[str] = Field(None, description="Error message if analysis failed.")

    class Config:
        populate_by_name = True
        extra = "allow"

class QLogicTurnInput(TimestampedModel):
    """
    Standardized data structure sent FROM Speech Container TO QLogic for routing.
    Refined based on session_turn_handler refactor.
    """
    child_id: uuid.UUID # Already snake_case, no alias needed if JSON key is 'child_id'
                         # If JSON key must be "childId", then:
                         # child_id: uuid.UUID = Field(..., alias="childId")
    session_id: uuid.UUID # Already snake_case
    target_phrase: Optional[str] = Field(None, alias="targetPhrase")
    stt_text: Optional[str] = Field(None, alias="sttText")
    analysis_result: Optional[PronunciationAnalysisResult] = Field(None, alias="analysisResult")
    module_context: str = Field("speech_handler", alias="moduleContext", description="Identifier of the calling module.")
    # timestamp is inherited from TimestampedModel and is already snake_case

    class Config:
        populate_by_name = True
        extra = "allow"
        # json_encoders can be inherited from TimestampedModel if not overridden,
        # or defined here if specific encoding is needed.

class QLogicResponse(BaseModel):
    """
    Standardized data structure received FROM QLogic.
    Matches existing definition.
    """
    type: str = Field(..., description="The type of action QLogic decided (e.g., 'prompt', 'feedback', 'game').") # 'type' is fine
    payload: Dict[str, Any] = Field(default_factory=dict, description="Data needed to execute the action.") # 'payload' is fine

    class Config:
        populate_by_name = True
        extra = "allow"

class VADEventData(TimestampedModel):
    """
    Data structure for VAD events sent FROM Speech Container TO Integration Container.
    """
    event_type: VADEventType = Field(..., alias="eventType", description="The type of VAD event.")
    session_id: uuid.UUID # Already snake_case
    # timestamp is inherited from TimestampedModel

    class Config:
        populate_by_name = True
        extra = "allow"

class VADTimingFlagsData(TimestampedModel):
    """
    Data structure for sending generated VAD timing flags (e.g., from Integration to QLogic).
    """
    session_id: uuid.UUID # Already snake_case
    flags: List[str] = Field(..., description="List of detected VAD timing flags (e.g., ['false_start', 'syllable_gap']).") # 'flags' is fine
    # timestamp is inherited from TimestampedModel

    class Config:
        populate_by_name = True
        extra = "allow"

class GuardianInputModel(BaseModel):
    """
    Standardized model for capturing guardian input data.
    """
    child_id: uuid.UUID = Field(..., alias="childId", description="Unique identifier for the child")
    source_id: str = Field(..., alias="sourceId", description="Origin of guardian input")
    guardian_name: str = Field(..., alias="guardianName", description="Name of the person providing input")
    notes: str = Field("", description="Additional comments or observations") # 'notes' is fine
    timestamp: datetime = Field(default_factory=datetime.utcnow) # 'timestamp' is fine
    details: Dict[str, Any] = Field(default_factory=dict, description="Any extra metadata") # 'details' is fine

    class Config:
        populate_by_name = True # Allows using 'childId', 'child_id' etc. during initialization
                                # Changed from allow_population_by_field_name to Pydantic v2's populate_by_name
        extra = "allow"         # Allows extra fields not defined in the model
        json_encoders = {
             # Custom encoder to ensure ISO format with Z for UTC
             datetime: lambda v: v.isoformat(timespec='milliseconds').rstrip("000").replace(".000", "") + "Z" if isinstance(v, datetime) else v
        }
        # For Pydantic v1, it was allow_population_by_field_name = True
        # The provided snippet had allow_population_by_field_name. If you are on Pydantic v1, keep that.
        # If on Pydantic v2, populate_by_name is the correct way.
        # Given the example "populate_by_name = True" in your instructions, I'm using that.

# --- Models for Audio Control API (Optional - if structure needed) ---
# Example: If pause/resume endpoints need specific bodies or return values

# class AudioControlRequest(BaseModel):
#     session_id: uuid.UUID = Field(..., alias="sessionId") 
#     action: str 

#     class Config:
#         populate_by_name = True
#         extra = "allow"

# class AudioControlResponse(BaseModel):
#     session_id: uuid.UUID = Field(..., alias="sessionId")
#     status: str 
#     message: Optional[str] = None

#     class Config:
#         populate_by_name = True
#         extra = "allow"

# Add other shared Pydantic models here as needed (e.g., for Game Engine interactions)