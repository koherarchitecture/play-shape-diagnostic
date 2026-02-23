"""
Quality definitions, validation, and relationship analysis for Play Shape Diagnostic.

This module is the RULES layer of the architecture.
It handles all deterministic judgment — no AI involved.

The key insight:
- We use pre-computed embedding similarities to determine relationships
- The same input ALWAYS produces the same output
- This makes the analysis reproducible, auditable, and debuggable

How relationships are computed:
1. Each quality has a description (e.g., "Waiting for something to happen...")
2. These descriptions were embedded using OpenAI's text-embedding model
3. Similarity scores between all pairs were pre-computed and stored in JSON
4. At runtime, we just look up the score — no API calls needed

Thresholds:
- synergy_threshold (0.82): Pairs with similarity >= 0.82 reinforce each other
- tension_threshold (0.72): Pairs with similarity < 0.72 pull against each other
- Between these: neutral (coexist independently)

These thresholds were calibrated by reviewing the results across all 220 possible
quality combinations and adjusting until the classifications felt right.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


# =============================================================================
# The 12 Experiential Qualities
# =============================================================================
#
# These are the core vocabulary of the tool. Each quality represents
# a distinct experiential dimension that can be present in play.
#
# The descriptions are carefully written to be:
# - Evocative (help designers feel what the quality means)
# - Distinct (each quality has a unique semantic space)
# - Embeddable (work well when converted to vector representations)

QUALITIES = {
    "anticipation": "Waiting for something to happen — the held breath before the reveal",
    "presence": "Being fully absorbed in the moment — flow state, immersion",
    "yearning": "Longing for something distant — nostalgia, desire, unreachable goals",
    "tension": "Uncertainty about what comes next — suspense, unease",
    "dread": "Fear of what lurks ahead — horror, impending threat",
    "relief": "Release from pressure — the exhale after danger passes",
    "mischief": "Playful rule-breaking — cleverness, pranks, subversion",
    "discovery": "Finding something new — exploration, revelation, wonder",
    "mastery": "Growing skill and competence — the satisfaction of getting better",
    "belonging": "Connection to others or place — community, home, togetherness",
    "transgression": "Crossing boundaries — taboo, forbidden action, moral ambiguity",
    "triumph": "Victory and accomplishment — winning, overcoming, celebration",
}


# =============================================================================
# Shape Classifications
# =============================================================================
#
# Based on the count of tensions and synergies among the 3 quality pairs,
# we classify the overall "shape" of the play experience.
#
# This mapping was designed to capture meaningful design patterns:
# - Harmonic: All qualities work together — unified experience
# - Distinct: Qualities don't interact much — parallel tracks
# - Dynamic: Some push, some pull — interesting but manageable
# - Complex: Multiple forces at play — rich but potentially confusing
# - Paradoxical: High contradiction — powerful but demanding to design

SHAPE_CLASSIFICATIONS = {
    # (tension_count, synergy_count) -> (shape_name, description)

    # No tensions — how much synergy?
    (0, 3): ("harmonic", "Qualities reinforce naturally — a unified experiential palette"),
    (0, 2): ("harmonic", "Qualities reinforce naturally — a unified experiential palette"),
    (0, 1): ("distinct", "Qualities coexist independently — parallel tracks of experience"),
    (0, 0): ("distinct", "Qualities coexist independently — parallel tracks of experience"),

    # One tension — what's the balance?
    (1, 2): ("dynamic", "Productive tension with support — push and pull with grounding"),
    (1, 1): ("dynamic", "Productive tension with support — push and pull with grounding"),
    (1, 0): ("dynamic", "Productive tension with support — push and pull with grounding"),

    # Two tensions — more complex
    (2, 2): ("complex", "Multiple forces in play — a rich experiential landscape"),
    (2, 1): ("paradoxical", "Strong internal contradiction — opposites held together"),
    (2, 0): ("paradoxical", "Strong internal contradiction — opposites held together"),

    # Three tensions — maximum contradiction
    (3, 0): ("paradoxical", "Strong internal contradiction — opposites held together"),
    (3, 1): ("paradoxical", "Strong internal contradiction — opposites held together"),
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class QualityPair:
    """
    A pair of qualities with their relationship.

    This represents the analysis of one pair (e.g., "dread" + "relief").
    For 3 qualities, there are exactly 3 pairs.
    """
    quality_a: str  # First quality (alphabetically earlier)
    quality_b: str  # Second quality (alphabetically later)
    relationship: Literal["tension", "synergy", "neutral"]  # The classification
    similarity: float  # Raw similarity score (0.0 to 1.0)

    @property
    def description(self) -> str:
        """
        Generate a human-readable description of the relationship.

        Examples:
            "dread reinforces relief"
            "mischief pulls against belonging"
            "discovery and mastery coexist"
        """
        if self.relationship == "synergy":
            return f"{self.quality_a} reinforces {self.quality_b}"
        elif self.relationship == "tension":
            return f"{self.quality_a} pulls against {self.quality_b}"
        else:
            return f"{self.quality_a} and {self.quality_b} coexist"


@dataclass
class ShapeAnalysis:
    """
    The complete result of analysing a quality combination.

    This is the output of the RULES layer — all the deterministic
    information needed to understand the play shape.
    """
    qualities: list[str]       # The 3 qualities (sorted alphabetically)
    combination_key: str       # e.g., "anticipation+dread+relief"
    shape: str                 # e.g., "harmonic", "paradoxical"
    shape_description: str     # Human-readable description
    tensions: list[QualityPair]   # Pairs that pull against each other
    synergies: list[QualityPair]  # Pairs that reinforce each other
    neutrals: list[QualityPair]   # Pairs that coexist independently


# =============================================================================
# Quality Analyser
# =============================================================================

class QualityAnalyser:
    """
    Analyses quality combinations using pre-computed embedding similarities.

    This class loads similarity data from JSON and uses it to:
    1. Classify relationships between quality pairs
    2. Determine the overall shape of the combination

    All operations are deterministic — no AI calls, no randomness.
    Same input always produces same output.
    """

    def __init__(self, similarities_path: Path | None = None):
        """
        Load pre-computed similarities from JSON.

        Args:
            similarities_path: Path to the JSON file. If None, uses default location.

        The JSON file contains:
        - similarities: dict mapping "quality1+quality2" -> similarity score
        - thresholds: dict with "synergy" and "tension" threshold values
        """
        if similarities_path is None:
            # Default path: data/quality_similarities.json relative to project root
            similarities_path = Path(__file__).parent.parent / "data" / "quality_similarities.json"

        # Load the pre-computed data
        with open(similarities_path) as f:
            data = json.load(f)

        # Store similarities and thresholds
        self.similarities = data["similarities"]  # Dict: "a+b" -> float
        self.thresholds = data["thresholds"]      # Dict: "synergy" -> float, "tension" -> float
        self.synergy_threshold = self.thresholds["synergy"]  # e.g., 0.82
        self.tension_threshold = self.thresholds["tension"]  # e.g., 0.72

    def _get_similarity(self, q1: str, q2: str) -> float:
        """
        Get the pre-computed similarity between two qualities.

        Args:
            q1: First quality name
            q2: Second quality name

        Returns:
            Similarity score (0.0 to 1.0). Higher = more similar.

        Note:
            Keys are stored as "quality1+quality2" in alphabetical order.
            So "dread+relief" and "relief+dread" both look up "dread+relief".
        """
        # Create key with qualities in alphabetical order
        key = "+".join(sorted([q1, q2]))
        return self.similarities.get(key, 0.0)

    def _classify_relationship(self, similarity: float) -> Literal["tension", "synergy", "neutral"]:
        """
        Classify a relationship based on similarity threshold.

        Args:
            similarity: The similarity score (0.0 to 1.0)

        Returns:
            "synergy" if >= synergy_threshold
            "tension" if < tension_threshold
            "neutral" otherwise

        The thresholds create three zones:
            [0.0 -------- tension_threshold -------- synergy_threshold -------- 1.0]
                  tension          neutral               synergy
        """
        if similarity >= self.synergy_threshold:
            return "synergy"
        elif similarity < self.tension_threshold:
            return "tension"
        else:
            return "neutral"

    def _classify_shape(self, tension_count: int, synergy_count: int) -> tuple[str, str]:
        """
        Determine shape classification based on tension/synergy counts.

        Args:
            tension_count: Number of pairs in tension (0-3)
            synergy_count: Number of pairs in synergy (0-3)

        Returns:
            Tuple of (shape_name, shape_description)

        Uses the SHAPE_CLASSIFICATIONS mapping with fallback logic
        for any edge cases not explicitly defined.
        """
        key = (tension_count, synergy_count)

        # Look up in the classification table
        if key in SHAPE_CLASSIFICATIONS:
            return SHAPE_CLASSIFICATIONS[key]

        # Fallback for unexpected combinations
        # (shouldn't happen with 3 qualities, but defensive coding)
        if tension_count > synergy_count:
            return ("paradoxical", "Strong internal contradiction — opposites held together")
        elif synergy_count > tension_count:
            return ("harmonic", "Qualities reinforce naturally — a unified experiential palette")
        else:
            return ("complex", "Multiple forces in play — a rich experiential landscape")

    def analyse(self, qualities: list[str]) -> ShapeAnalysis:
        """
        Analyse a combination of 3 qualities.

        This is the main public method. It:
        1. Validates the input
        2. Analyses all 3 pairs
        3. Classifies relationships and overall shape
        4. Returns the complete analysis

        Args:
            qualities: List of exactly 3 quality names

        Returns:
            ShapeAnalysis with all relationship and shape information

        Raises:
            ValueError: If not exactly 3 qualities, or if any quality is invalid
        """
        # Validate: must be exactly 3 qualities
        if len(qualities) != 3:
            raise ValueError(f"Exactly 3 qualities required, received {len(qualities)}")

        # Validate: all qualities must be valid
        for q in qualities:
            if q not in QUALITIES:
                raise ValueError(f"Unknown quality: {q}")

        # Sort for consistent key generation
        # This ensures "dread+relief+anticipation" and "anticipation+dread+relief"
        # produce the same combination_key
        sorted_qualities = sorted(qualities)
        combination_key = "+".join(sorted_qualities)

        # Analyse all 3 pairs
        # For qualities [A, B, C], the pairs are: A-B, A-C, B-C
        tensions = []
        synergies = []
        neutrals = []

        pairs = [
            (sorted_qualities[0], sorted_qualities[1]),  # A-B
            (sorted_qualities[0], sorted_qualities[2]),  # A-C
            (sorted_qualities[1], sorted_qualities[2]),  # B-C
        ]

        for q1, q2 in pairs:
            # Look up pre-computed similarity
            similarity = self._get_similarity(q1, q2)

            # Classify the relationship
            relationship = self._classify_relationship(similarity)

            # Create the pair object
            pair = QualityPair(
                quality_a=q1,
                quality_b=q2,
                relationship=relationship,
                similarity=similarity,
            )

            # Sort into appropriate list
            if relationship == "tension":
                tensions.append(pair)
            elif relationship == "synergy":
                synergies.append(pair)
            else:
                neutrals.append(pair)

        # Classify the overall shape based on counts
        shape, shape_description = self._classify_shape(len(tensions), len(synergies))

        # Return the complete analysis
        return ShapeAnalysis(
            qualities=sorted_qualities,
            combination_key=combination_key,
            shape=shape,
            shape_description=shape_description,
            tensions=tensions,
            synergies=synergies,
            neutrals=neutrals,
        )


# =============================================================================
# Validation Functions
# =============================================================================

def validate_selection(qualities: list[str], context: str) -> tuple[bool, str | None]:
    """
    Validate a user's quality selection and context.

    This is used by the API to check input before processing.

    Args:
        qualities: List of quality names (should be exactly 3)
        context: The game description (should be 20-500 characters)

    Returns:
        Tuple of (is_valid, error_message).
        If valid: (True, None)
        If invalid: (False, "description of problem")
    """
    # Check quality count
    if len(qualities) != 3:
        return False, f"Exactly 3 qualities required, received {len(qualities)}"

    # Check for duplicates
    if len(set(qualities)) != 3:
        return False, "Duplicate qualities not allowed"

    # Check all qualities are valid
    for q in qualities:
        if q not in QUALITIES:
            return False, f"Unknown quality: {q}"

    # Check context length (minimum)
    if len(context) < 20:
        return False, f"Context must be at least 20 characters, received {len(context)}"

    # Check context length (maximum)
    if len(context) > 500:
        return False, f"Context must be at most 500 characters, received {len(context)}"

    return True, None


# =============================================================================
# Helper Functions
# =============================================================================

def get_quality_definitions() -> list[dict]:
    """
    Return quality definitions for the API.

    This converts the QUALITIES dict into a list of dicts
    that's easier to iterate over in the frontend.

    Returns:
        List of {"name": "quality_name", "description": "quality description"}
    """
    return [
        {"name": name, "description": desc}
        for name, desc in QUALITIES.items()
    ]
