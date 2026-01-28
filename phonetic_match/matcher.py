# Import typing for structural type hints
from typing import Dict, List, Any
# Import the internal components of the matching pipeline
from .processor import NameProcessor
from .encoder import PhoneticEncoder
from .engine import SimilarityEngine
from .models import LabeledSegment
from .config import NameConfig

class PhoneticMatcher:
    """
    Orchestration class that coordinates the full name matching pipeline.
    Connects processing, encoding, and similarity scoring.
    """

    def __init__(self):
        # Initialize the three core workers: Processor, Encoder, and Engine.
        self.processor = NameProcessor()
        self.encoder = PhoneticEncoder()
        self.engine = SimilarityEngine()

    def _format_matches_for_display(self, matches: List[Dict]) -> str:
        """Internal helper to produce a human-readable trace of matches for debugging."""
        lines = []
        for m in matches:
            t = m['target_segment']
            r = m['reference_segment']
            # Create a string detailing which target part matched which reference part
            lines.append(f"  Target {t.label} '{t.original_text}' matched Reference {r.label} '{r.original_text}'")
            # Include the match logic (e.g., Primary-Primary) and the resulting score
            lines.append(f"    (Code Match: {m['match_type']} | Score: {m['score']*100:.2f}%)")
        return "\n".join(lines)

    def match(self, target_name: str, reference_name: str, debug: bool = True) -> Dict[str, Any]:
        """
        Executes the matching process between two names.
        
        Steps:
        1. Process names into NS (Name Segments) and NI (Name Initials).
        2. Encode all units phonetically.
        3. Wrap units with labels for traceability.
        4. Generate cross-component match candidates.
        5. Solve assignment and calculate final F1 score.
        
        Args:
            target_name: The name we are searching for.
            reference_name: The name we are matching against.
            debug: If True, prints status messages to console.
            
        Returns:
            A dictionary containing the final score, metadata, and match details.
        """
        if debug:
            # Print a visual header for the match operation
            print(f"\n{'='*60}")
            print(f"Matcher: '{target_name}' vs '{reference_name}'")
            print(f"{'='*60}")

        # 1. Processing: Split raw names into structured components (NS and NI groups)
        t_data = self.processor.process_name(target_name)
        r_data = self.processor.process_name(reference_name)

        # 2. Encoding & Unification: Convert words into phonetic codes and wrap them for tracing
        
        # Process Target Pool
        # Encode full name parts (NS)
        t_ns_traced = self.encoder.encode_segments(t_data["NS"])
        # Encode joined initials (NI1)
        t_ni_traced = self.encoder.encode_segments(t_data["NI"][0]) 
        # Combine them into a single list of units, adding labels [NS] or [NI]
        t_units = [LabeledSegment(s, "[NS]") for s in t_ns_traced] + \
                  [LabeledSegment(s, "[NI]") for s in t_ni_traced]

        # Process Reference Pool
        # Encode full name parts (NS)
        r_ns_traced = self.encoder.encode_segments(r_data["NS"])
        # Encode joined initials (NI)
        r_ni_traced = self.encoder.encode_segments(r_data["NI"][0])
        # Combine reference units with labels
        r_units = [LabeledSegment(s, "[NS]") for s in r_ns_traced] + \
                  [LabeledSegment(s, "[NI]") for s in r_ni_traced]

        # 3. Candidate Generation (All-vs-All): Calculate potential scores for every pair
        candidates = []
        for t in t_units:
            for r in r_units:
                # Calculate the phonetic similarity score for this specific pair of units
                score, mtype = self.engine.calculate_pair_score(
                    t.segment, r.segment, target_name, reference_name
                )
                # If there's any similarity, add it as a candidate for the final selection
                if score > 0:
                    candidates.append({
                        "t_seg": t,
                        "r_seg": r,
                        "score": score,
                        "match_type": mtype
                    })

        # 4. Solve Assignment: Pick the best non-overlapping set of matches
        matches = self.engine.solve_greedy_assignment(candidates)
        
        if debug:
            # Print diagnostic info about the candidate pool and selected matches
            print(f"  Generated {len(candidates)} candidates.")
            print("\n  Matches Selected:")
            print(self._format_matches_for_display(matches))

        # 5. Scoring: Calculate the overall similarity (F1-inspired average)
        
        # N represents the total number of parts in the Target name that we are trying to find.
        N = len(t_units)
        # Extract the numeric scores and scale them to 0-100
        scores = [m["score"] * NameConfig.SCORE_MULTIPLIER for m in matches]
        # Sort score values descending to easily take the top performers
        scores.sort(reverse=True)
        # We take up to N scores (matching the target name's complexity)
        top_n_scores = scores[:N]
        
        final_score = 0.0
        # Average the top scores against the total number of target parts N
        if N > 0:
            final_score = sum(top_n_scores) / N

        if debug:
            # Print the final calculated percentage
            print(f"\n  Final Score: {final_score:.2f} (N={N})")

        # Return a comprehensive results dictionary
        return {
            "F1": round(final_score, 2),        # Final similarity percentage
            "N": N,                             # Target name length (complexity)
            "Target": target_name,              # Original target string
            "Reference": reference_name,        # Original reference string
            "Matches": matches,                 # List of specific segment pairings
            "AllScores": top_n_scores           # Individual scores used for the average
        }
