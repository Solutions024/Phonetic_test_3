# Import JaroWinkler similarity metric from rapidfuzz library
from rapidfuzz.distance import JaroWinkler
# Import typing for complex type signatures
from typing import List, Tuple, Optional, Dict
# Import internal models for data representation
from .models import TracedSegment, MatchResult, LabeledSegment
# Import configuration for weighted scoring constants
from .config import NameConfig

class SimilarityEngine:
    """
    Core engine responsible for calculating similarity scores between name segments
    and solving the global matching assignment problem.
    """

    def calculate_pair_score(
        self, 
        t_seg: TracedSegment, 
        r_seg: TracedSegment, 
        t_full_name: Optional[str] = None, 
        r_full_name: Optional[str] = None
    ) -> Tuple[float, str]:
        """
        Calculates the best Jaro-Winkler score between two segments considering
        all possible Primary/Secondary phonetic code combinations.
        
        Applies a penalty/weighted rule (85:15) if a perfect phonetic match (1.0) occurs.
        
        Args:
            t_seg: Target segment to compare.
            r_seg: Reference segment to compare.
            t_full_name: Optional full target name for secondary similarity.
            r_full_name: Optional full reference name for secondary similarity.
            
        Returns:
            Tuple of (final_score, match_type_description).
        """
        # Initialize the baseline score and label
        best_score = 0.0
        match_label = "None"
        
        # Cross-check all combinations of primary and secondary phonetic codes.
        # This accounts for cases where the primary code doesn't match but the secondary does.
        combinations = [
            (t_seg.primary_code, r_seg.primary_code, "Primary-Primary"),
            (t_seg.primary_code, r_seg.secondary_code, "Primary-Secondary"),
            (t_seg.secondary_code, r_seg.primary_code, "Secondary-Primary"),
            (t_seg.secondary_code, r_seg.secondary_code, "Secondary-Secondary")
        ]
        
        for c1, c2, label in combinations:
            # Only compare if both codes in the pair exist (secondary codes can be None)
            if c1 and c2:
                # Calculate Jaro-Winkler similarity between phonetic codes
                sim = JaroWinkler.similarity(c1, c2)
                # Keep track of the highest score found among all combinations
                if sim > best_score:
                    best_score = sim
                    match_label = label
        
        # Apply 85:15 Weighted Scoring for Perfect Phonetic Matches.
        # This prevents "false positives" where phonetically identical words are semantically different.
        if best_score == 1.0:
            if t_full_name and r_full_name:
                # If full names are provided, calculate word similarity based on the full normalized strings.
                from .processor import NameProcessor
                # Normalize and remove spaces to compare the global "shape" of the names.
                norm_t = NameProcessor.normalize_text(t_full_name).replace(" ", "")
                norm_r = NameProcessor.normalize_text(r_full_name).replace(" ", "")
                word_sim = JaroWinkler.similarity(norm_t, norm_r)
            else:
                # Fallback: compare the original literal words if full names aren't available.
                word_sim = JaroWinkler.similarity(t_seg.original_text.lower(), r_seg.original_text.lower())
            
            # Weighted Formula: (1.0 * 0.85) + (Literal Similarity * 0.15)
            # This ensures that 'Md' vs 'Mohammad' (same phonetic code) scores slightly less than 'Mohammad' vs 'Mohammad'.
            weighted_score = (best_score * NameConfig.PHONETIC_WEIGHT) + (word_sim * NameConfig.WORD_SIM_WEIGHT)
            
            # Update the score with the weighted result
            best_score = weighted_score
            # Annotate the label to indicate weighting was applied
            match_label += f" (Weighted: 1.0->{best_score:.4f})"
        
        # Return the final calculated score and its diagnostic label
        return best_score, match_label

    def solve_greedy_assignment(self, candidates: List[Dict]) -> List[MatchResult]:
        """
        Solves the bipartite matching problem using a greedy approach.
        Assigns the highest scoring pairs first until no more unique matches can be made.
        
        Args:
            candidates: List of dictionaries with 't_seg', 'r_seg', 'score', and 'match_type'.
        Returns:
            List of MatchResult objects representing the chosen optimal matches.
        """
        # Sort all potential segment pairings by score in descending order.
        # We want to lock in our strongest matches first.
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Sets to track which segments from target and reference pools have already been 'used'.
        taken_target_ids = set()
        taken_ref_ids = set()
        # List of final selected matches
        matches = []
        
        for cand in candidates:
            # Use the Python object memory ID to uniquely identify each segment instance.
            t_id = id(cand["t_seg"])
            r_id = id(cand["r_seg"])
            
            # If neither the target segment nor the reference segment has been matched yet:
            if t_id not in taken_target_ids and r_id not in taken_ref_ids:
                # Record this pairing as a valid match
                matches.append({
                    "target_segment": cand["t_seg"],
                    "reference_segment": cand["r_seg"],
                    "score": cand["score"],
                    "match_type": cand["match_type"]
                })
                
                # Mark both segments as 'taken' so they cannot be reused in other matches.
                taken_target_ids.add(t_id)
                taken_ref_ids.add(r_id)
        
        # Return the set of unique, highest-scoring pairings found.
        return matches
