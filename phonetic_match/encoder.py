# Import the Double Metaphone implementation from the metaphone library
from metaphone import doublemetaphone
# Import typing for type hinting
from typing import List, Optional
# Import the TracedSegment model to structure the encoded output
from .models import TracedSegment

class PhoneticEncoder:
    """
    Handles the phonetic encoding of name segments using the Double Metaphone algorithm.
    Integrates traceability by wraping codes into TracedSegment objects.
    """

    def encode_segments(self, segments: List[str]) -> List[TracedSegment]:
        """
        Calculates Double Metaphone codes for a list of name strings.
        
        Args:
            segments: List of strings (NS or NI units).
        Returns:
            List of TracedSegment objects containing primary and secondary codes.
        """
        # Initialize an empty list to store the results of the encoding process
        traced_segments = []
        
        # Iterate through each token in the input list with its index
        for i, token in enumerate(segments):
            # doublemetaphone returns a tuple: (Primary Phonetic Code, Secondary Phonetic Code)
            # Example: "Robert" -> ("RBRT", "")
            dm_codes = doublemetaphone(token)
            
            # The primary code is always the first element of the tuple
            primary = dm_codes[0]
            
            # The secondary code is optional and may be empty; we store it as None if it's empty
            secondary = dm_codes[1] if len(dm_codes) > 1 and dm_codes[1] else None
            
            # Create a TracedSegment object to keep the original text together with its codes
            traced_segments.append(TracedSegment(
                original_text=token,      # Keep the original word for verification
                index=i,                  # Keep the original order of the word in the name
                primary_code=primary,     # The standard phonetic representation
                secondary_code=secondary  # Potential alternative phonetic representation
            ))
            
        # Return the list of all encoded and traced segments
        return traced_segments
