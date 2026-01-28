# Phonetic Name Matching System

A scalable, modular phonetic matching engine designed for high-accuracy person name comparison. This system uses double-metaphone encoding combined with Jaro-Winkler similarity and a custom greedy assignment strategy.

## Architecture & Modules

The system is refactored into a cohesive `phonetic_match` package for reusability and scalability.

- **`config.py`**: Centralizes tuning parameters like Muhammad variants and scoring weights (85:15 rule).
- **`models.py`**: Defines core data structures like `TracedSegment` and `LabeledSegment` to maintain traceability.
- **`processor.py`**: Handles name normalization, cleaning, and segmentation into Name Segments (NS) and Name Initials (NI).
- **`encoder.py`**: Wraps the Double Metaphone algorithm to generate phonetic codes with full traceability.
- **`engine.py`**: The "brain" of the system. Calculates similarity scores and solves the bipartite assignment problem using a greedy strategy.
- **`matcher.py`**: The orchestration layer that connects all components into a simple `match()` API.

## Algorithm Deep Dive

### 1. Processing & Segmentation
- **Normalization**: Names are lowercased, special characters removed, and whitespace collapsed.
- **Muhammad Handling**: Common variants (Md, Mohd, etc.) are standardized to "Muhammad" to ensure phonetic consistency.
- **Unit Extraction**:
    - **NS (Name Segments)**: Full words (>1 character).
    - **NI (Name Initials)**: Single letters. Adjacent initials are joined into "Blocks" (e.g., "J.K." -> "JK").

### 2. Phonetic Encoding
Each unit (Segment or Initial Block) is encoded using **Double Metaphone**, which produces a primary and an optional secondary phonetic code. This helps handle cross-lingual pronunciation variations.

### 3. Similarity Scoring (The 85:15 Rule)
When comparing two units, we calculate the Jaro-Winkler similarity of their phonetic codes.
If the phonetic match is **perfect (1.0)**, we apply a weighted penalty to account for literal differences:
`Final Score = (Phonetic Score * 0.85) + (Literal Word similarity * 0.15)`

This ensures that while "JK" and "Jacob" might have the same phonetic code, they don't get a perfect 100% score compared to "JK" vs "JK".

### 4. Global Greedy Assignment
To avoid over-matching (e.g., one initial matching multiple segments), the system uses a **Greedy Assignment** solver:
1. Generate all possible pairs between Target units and Reference units.
2. Sort all pairs by score (highest first).
3. Select the best match and "lock" both the target and reference units so they cannot be reused.
4. Repeat until no more unique matches can be made.

### 5. Final F1 Score
The total score is the average of the top match scores, normalized by the number of components in the **Target Name**.
`F1 = Sum(Top Matches) / Count(Target Units)`

## Usage

```python
from phonetic_match.matcher import PhoneticMatcher

matcher = PhoneticMatcher()
result = matcher.match("Muhammad Ali", "Mohd Aly")

print(f"Similarity: {result['F1']}%")
```

## Scaling the System
To add new phonetic algorithms or change cleaning rules, simply extend the `PhoneticEncoder` or `NameProcessor` classes. The modular design ensures that changes in one area do not break the orchestration logic.


## Normalizer
Range       | Label
------------|--------------------
0–30        | Names Do Not Match
31–60       | Weak Match
61–75       | Possible Match
76–88       | Probable Match
89–94       | Strong Match
95–99       | Likely Same Name
100         | Same Name