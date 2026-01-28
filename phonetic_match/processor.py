# Import regular expressions module for text manipulation
import re
# Import typing for type hinting complex structures
from typing import List, Tuple, Dict, Set, Optional, Any
# Import the configuration constants for normalization rules
from .config import NameConfig

class NameProcessor:
    """
    Handles the transformation of raw name strings into structured components.
    Responsible for normalization, tokenization, and segmentation.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Applies basic text normalization: lowercasing, space collapsing, and stripping.
        
        Args:
            text: Raw input name string.
        Returns:
            Normalized lowercase string.
        """
        # Convert the entire string to lowercase for case-insensitive matching
        text = text.lower()
        # Use regex to find any sequence of whitespace (tabs, newlines, multiple spaces)
        # and replace it with a single standard space.
        text = re.sub(r"\s+", " ", text)
        # Remove any leading or trailing whitespace from the string
        return text.strip()

    @staticmethod
    def extract_alpha_tokens(text: str) -> List[str]:
        """
        Extracts only alphabetic sequences from the text, ignoring symbols/numbers.
        
        Args:
            text: Normalized text string.
        Returns:
            List of alphabetic words/tokens.
        """
        # Use regex to find all contiguous sequences of alphabetic characters (a-z, A-Z)
        # This effectively removes punctuation, numbers, and special characters.
        return re.findall(r"[a-zA-Z]+", text)

    @staticmethod
    def remove_duplicates_preserve_order(items: List[str]) -> List[str]:
        """
        Utility to remove duplicate strings while maintaining the original sequence.
        
        Args:
            items: List of strings.
        Returns:
            Unique list of strings in original order.
        """
        # Track items we've already encountered using a set for O(1) lookups
        seen: Set[str] = set()
        # Maintain the order of appearance in a new list
        result: List[str] = []
        for item in items:
            # If the item hasn't been seen yet, add it to both the set and the result list
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def normalize_muhammad(token: str) -> Optional[str]:
        """
        Checks if a token is a known variant of 'Muhammad' and returns the standard form.
        
        Args:
            token: A lowercase alphabetic token.
        Returns:
            'Muhammad' if it's a variant, otherwise None.
        """
        # Check if the lowercase token exists in the predefined MUHAMMAD_VARIANTS set
        if token in NameConfig.MUHAMMAD_VARIANTS:
            # Return the canonical 'Muhammad' string if a match is found
            return NameConfig.STANDARD_MUHAMMAD
        # Return None if the token is not a recognized variant
        return None

    def extract_name_segments(self, tokens: List[str]) -> List[str]:
        """
        Extracts Name Segments (NS) which are meaningful full words (>1 char or Muhammad).
        
        Args:
            tokens: List of alphabetic tokens.
        Returns:
            List of capitalized name segments.
        """
        # Initialize list for full name parts (Name Segments)
        segments: List[str] = []
        for token in tokens:
            # First, check if the token is a variant of 'Muhammad' (e.g., 'Md', 'Mohd')
            normalized = self.normalize_muhammad(token)
            if normalized:
                # If it's a Muhammad variant, add the standard form
                segments.append(normalized)
            elif len(token) > 1:
                # If it's not Muhammad but longer than 1 character, treat it as a standard name part.
                # Standard name parts are capitalized (e.g., 'john' -> 'John') for consistent representation.
                segments.append(token.capitalize())
        
        # Remove duplicates while preserving the order of name parts (e.g., 'John John Smith' -> 'John Smith')
        return self.remove_duplicates_preserve_order(segments)

    def extract_initials(self, tokens: List[str]) -> Tuple[List[str], List[str]]:
        """
        Extracts Name Initials (NI) categorized into joined and individual initials.
        
        Args:
            tokens: List of alphabetic tokens.
        Returns:
            Tuple containing:
                - List of joined initials (e.g., ['JK'])
                - List of individual initials (e.g., ['J', 'K'])
        """
        # Storage for joined initials (sequences of single characters like 'A' 'B' -> 'AB')
        ni_joined: List[str] = []
        # Storage for individual initials ('A', 'B')
        ni_individual: List[str] = []
        # Temporary buffer to collect sequences of single letters
        buffer: List[str] = []

        for token in tokens:
            # A token is considered an initial if it is exactly one character long
            if len(token) == 1:
                # Convert the character to uppercase for consistency
                char = token.upper()
                # Add to the current sequence buffer
                buffer.append(char)
                # Add to the list of all individual initials encountered
                ni_individual.append(char)
            else:
                # If we encounter a full word (>1 char), it breaks any sequence of initials.
                if len(buffer) >= 1:
                    # Join the collected initials in the buffer and add to ni_joined
                    ni_joined.append("".join(buffer))
                # Clear the buffer for the next potential sequence
                buffer = []

        # After the loop, check if any initials remain in the buffer
        if len(buffer) >= 1:
            ni_joined.append("".join(buffer))

        # Return unique joined and individual initials, preserving original order
        return (
            self.remove_duplicates_preserve_order(ni_joined),
            self.remove_duplicates_preserve_order(ni_individual)
        )

    def process_name(self, name: str) -> Dict[str, Any]:
        """
        Full pipeline to process a raw name into NS and NI components.
        
        Args:
            name: Raw person name string.
        Returns:
            Dictionary with 'NS' list and 'NI' (nested list containing joined/individual).
        """
        # Step 1: Clean and normalize the raw input string
        normalized = self.normalize_text(name)
        # Step 2: Split the string into purely alphabetic tokens
        tokens = self.extract_alpha_tokens(normalized)
        
        # Step 3: Extract the full Name Segments (NS)
        ns = self.extract_name_segments(tokens)
        # Step 4: Extract the Name Initials (NI1 = joined, NI2 = individual)
        ni1, ni2 = self.extract_initials(tokens)

        # Return the structured data dictionary
        return {
            "NS": ns,
            "NI": [ni1, ni2]
        }
