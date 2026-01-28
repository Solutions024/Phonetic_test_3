class ScoreNormalizer:
    """
    Utility class to map numeric similarity scores to human-readable labels.
    """

    @staticmethod
    def get_label(score: float) -> str:
        """
        Maps a 0-100 score to a categorical label based on defined ranges.
        
        Range       | Label
        ------------|--------------------
        0–30        | Names Do Not Match
        31–60       | Weak Match
        61–75       | Possible Match
        76–88       | Probable Match
        89–94       | Strong Match
        95–99       | Likely Same Name
        100         | Same Name
        """
        if score <= 30:
            return "Names Do Not Match"
        elif 30 < score <= 60:
            return "Weak Match"
        elif 60 < score <= 75:
            return "Slightly Similar"
        elif 75 < score <= 88:
            return "Somewhat Similar"
        elif 88 < score <= 94:
            return "Highly Similar"
        elif 94 < score < 100:
            return "Almost Identical"
        elif score == 100:
            return "Identical Name"
        
        return "Unknown"
