# Import the Set type from typing module for type hinting
from typing import Set

# Define a class-based configuration to group name-related settings
class NameConfig:
    """
    Configuration settings for name normalization and phonetic matching.
    This class centralizes all constants to make the system easily tunable.
    """
    
    # MUHAMMAD_VARIANTS: A set of common spelling variations for the name 'Muhammad'.
    # Using a set provides O(1) lookup time for normalization checks.
    MUHAMMAD_VARIANTS: Set[str] = {
        "md",         # Abbreviation for 'Mohammed/Mohammad'
        "mohd",       # Abbreviation for 'Mohammed/Mohammad'
        "muhd",       # Abbreviation for 'Muhammad'
        "moham",      # Truncated version
        "muhammad",   # Standard English spelling 1
        "mohammad",   # Standard English spelling 2
        "muhammed",   # Standard English spelling 3
        "mohammed",   # Standard English spelling 4
        "mohamad",    # Common variation
        "mohamed"     # Common variation
    }

    # STANDARD_MUHAMMAD: The canonical form that all variants will be converted to.
    # Centralizing this ensures that phonetically similar variants yield identical codes.
    STANDARD_MUHAMMAD: str = "Muhammad"

    # Weighted Scoring Constants: These define the balance between phonetic similarity
    # and literal word similarity when a perfect phonetic match (1.0) is detected.
    
    # PHONETIC_WEIGHT (0.85): Phonetic similarity contributes 85% to the final pair score.
    PHONETIC_WEIGHT: float = 0.85
    
    # WORD_SIM_WEIGHT (0.15): Literal string similarity contributes 15% to the final pair score.
    WORD_SIM_WEIGHT: float = 0.15

    # SCORE_MULTIPLIER: Factor to scale the 0.0-1.0 similarity range to a 0-100 percentage.
    SCORE_MULTIPLIER: float = 100.0
