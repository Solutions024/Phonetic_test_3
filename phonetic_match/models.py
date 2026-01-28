# Import necessary typing constructs for robust type hinting
from typing import Optional, NamedTuple, Dict, List, Any

# TracedSegment: A lightweight, immutable data structure to hold phonetic metadata
class TracedSegment(NamedTuple):
    """
    Represents a name segment with its original text, index, and Double Metaphone codes.
    This structure ensures we can trace a phonetic code back to its source word.
    
    Attributes:
        original_text: The original word from the input Name Segment (NS) or Initial (NI).
        index: The position of this word in its original list.
        primary_code: The Primary Double Metaphone code.
        secondary_code: The Secondary Double Metaphone code (if it exists).
    """
    original_text: str       # Stores the literal word before phonetic encoding
    index: int               # Stores the original sequence position for debugging/tracing
    primary_code: str        # The first (standard) phonetic representation
    secondary_code: Optional[str] # The second (alternative) phonetic representation (e.g., for foreign names)

# LabeledSegment: A wrapper that adds classification metadata to a TracedSegment
class LabeledSegment:
    """
    A wrapper around TracedSegment that adds a label (e.g., "[NS]", "[NI]").
    This is used for better transparency in match results and logs.
    
    Attributes:
        segment: The underlying TracedSegment object.
        label: The classification of the segment (NS for name segment, NI for initial).
    """
    def __init__(self, segment: TracedSegment, label: str):
        # Store the core segment data
        self.segment = segment
        # Store the label (e.g., '[NS]' for Name Segment or '[NI]' for Name Initial)
        self.label = label
        
        # Proxy attributes: Expose inner segment attributes directly on this object for convenience
        self.original_text = segment.original_text
        self.primary_code = segment.primary_code
        self.secondary_code = segment.secondary_code
        self.index = segment.index

    def __getattr__(self, name):
        """
        Delegate attribute access to the wrapped TracedSegment.
        This allows LabeledSegment to behave like the TracedSegment it wraps.
        """
        return getattr(self.segment, name)

# MatchResult: A dictionary subclass for storing and serializing match details
class MatchResult(Dict):
    """
    Structure to hold match results.
    Inherits from Dict for easy serialization to JSON.
    
    Expected keys:
        "target_segment": The LabeledSegment from the target name.
        "reference_segment": The LabeledSegment from the reference name.
        "score": The calculated similarity score.
        "match_type": Description of the match (e.g., "Primary-Primary").
    """
    # This class is basically a typed dictionary for match output
    pass
