# cabreaich-common/cabreaich_common/flags.py
# Defines shared flag constants used across different CAB ReAIch containers.
# Using Enums helps ensure consistency and prevents typos.

from enum import Enum

class VADFlag(Enum):
    """
    Flags related to Voice Activity Detection (VAD) and speech timing analysis.
    These might be generated by the speech container or related components.
    """
    FALSE_START = "false_start"     # Indicates speech started but was too short.
    SYLLABLE_GAP = "syllable_gap"   # Indicates a potentially disruptive pause within speech.
    # Add other VAD-related flags here as needed, e.g.:
    # TOO_SLOW = "too_slow"
    # TOO_FAST = "too_fast"
    # INTERJECTION = "interjection"

class EngagementFlag(Enum):
    """
    Flags related to the user's engagement level.
    These might be inferred from speech patterns, interaction history, or other sensors.
    """
    LOW_ENGAGEMENT = "low_engagement" # Indicates the user may be disengaged.
    # Add other engagement-related flags here, e.g.:
    # HIGH_ENGAGEMENT = "high_engagement"
    # DISTRACTED = "distracted"

class QualityFlag(Enum):
    """
    Flags related to the quality or characteristics of the speech input.
    """
    LOW_CONFIDENCE_STT = "low_confidence_stt" # STT result has low confidence score.
    BACKGROUND_NOISE = "background_noise"     # Significant background noise detected.
    # Add other quality flags...

class EmotionFlag(Enum):
    """
    Flags representing detected emotions (can also be direct strings if preferred,
    but Enum enforces consistency if specific flag values are needed).
    Note: Your current code seems to pass emotion tags directly as strings (e.g., "frustrated"),
    which is fine. This Enum is an alternative if you want stricter control via flags.
    """
    FRUSTRATED = "frustrated"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    # Add other emotion flags...

# --- How to use these flags ---
#
# 1. In the container GENERATING the flag:
#    from cabreaich_common.flags import VADFlag, EngagementFlag
#    generated_flags = []
#    if vad_analyzer.detect_false_start():
#        generated_flags.append(VADFlag.FALSE_START.value) # .value gives the string "false_start"
#    if engagement_monitor.is_low():
#        generated_flags.append(EngagementFlag.LOW_ENGAGEMENT.value)
#    # Pass generated_flags (or a structured dict) to the consuming container.
#
# 2. In the container CONSUMING the flag (e.g., QLogic):
#    from cabreaich_common.flags import VADFlag, EngagementFlag
#    # Assuming received_flags is a list or dict containing flag strings
#    if VADFlag.FALSE_START.value in received_flags:
#        # Handle false start...
#    elif EngagementFlag.LOW_ENGAGEMENT.value in received_flags:
#        # Handle low engagement...


