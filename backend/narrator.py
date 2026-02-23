"""
Stage 3: AI narrator for Play Shape Diagnostic.

This module is the LANGUAGE layer of the architecture.
It takes the deterministic analysis from Stage 2 (qualities.py)
and generates human-readable narrative explanations.

The AI's role is specifically:
- Describe what the shape means for THIS specific game
- Weave together the relationships identified by the rules layer
- Suggest design implications

The AI does NOT:
- Judge whether the design is "good" or "bad"
- Suggest adding more qualities
- Override the deterministic relationship classifications

This separation is intentional. The rules layer (qualities.py) handles
judgment — which qualities create tension, which create synergy.
This layer only handles language — converting that structure to prose.

API:
- Uses Claude Haiku via OpenRouter
- OpenRouter is a proxy service that provides pay-as-you-go access to Claude
- You need an OPENROUTER_API_KEY in your .env file
"""

import os
from dataclasses import dataclass
from openai import OpenAI  # We use the OpenAI client library — OpenRouter is API-compatible

from src.qualities import QUALITIES, ShapeAnalysis


# =============================================================================
# System Prompt
# =============================================================================
#
# This prompt defines the AI's behaviour. It's the "personality" and "rules"
# that shape how the AI responds. Notice:
# - Clear instructions about what TO do
# - Explicit instructions about what NOT to do
# - Specific output format to ensure parseable responses

SYSTEM_PROMPT = """You are an expert game design critic and experiential analyst. Your role is to narrate the experiential shape of a game based on the designer's selected qualities and the structural analysis provided.

You will receive:
1. Three experiential qualities selected by the user
2. A shape classification (harmonic, dynamic, paradoxical, distinct, or complex)
3. Any tensions between qualities (pairs that pull in opposite directions)
4. Any synergies between qualities (pairs that reinforce each other)
5. The designer's game concept

Your task:
1. Narrate what this shape means for *this specific game* — weave together the qualities, tensions, and synergies
2. If tensions exist, explain how they create productive friction or require design resolution
3. If synergies exist, explain how they compound the experience
4. Offer 2-3 brief design implications specific to this game

Guidelines:
- Write in clear, engaging prose (4-8 sentences for the main explanation)
- Reference the specific qualities, tensions, and synergies by name
- Always ground the explanation in the user's game concept
- Do not judge the selection as "good" or "bad"
- Do not suggest adding more qualities
- Tensions are not problems — they are design opportunities
- Focus on illumination, not prescription

Voice: thoughtful, precise, generative. You are a colleague thinking alongside the designer.

Format your response exactly like this:
EXPLANATION:
[Your 4-8 sentence explanation here]

IMPLICATIONS:
- [First implication]
- [Second implication]
- [Third implication]"""


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class NarratorResponse:
    """
    The response from the narrator.

    Contains:
    - explanation: The main narrative (4-8 sentences)
    - implications: Design suggestions (2-3 bullet points)
    - model: Which model generated this (for transparency)
    """
    explanation: str
    implications: list[str]
    model: str


# =============================================================================
# Narrator Class
# =============================================================================

class PlayShapeNarrator:
    """
    Generates narrative explanations using Claude Haiku.

    This class:
    1. Connects to OpenRouter (Claude API proxy)
    2. Builds prompts from the ShapeAnalysis
    3. Parses responses into structured output

    Usage:
        narrator = PlayShapeNarrator()  # Uses OPENROUTER_API_KEY from environment
        response = narrator.narrate(analysis, "A horror game where...")
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialise with OpenRouter API key.

        Args:
            api_key: OpenRouter API key. If None, reads from OPENROUTER_API_KEY env var.

        Raises:
            ValueError: If no API key is found.
        """
        # Get API key from argument or environment
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable required")

        # Create OpenAI client pointing to OpenRouter
        # OpenRouter uses the same API format as OpenAI, so we can use their client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

        # Which model to use
        # Claude Haiku is fast and cheap — good for this use case
        self.model = "anthropic/claude-haiku-4.5"

    def _build_user_prompt(self, analysis: ShapeAnalysis, context: str) -> str:
        """
        Build the user prompt from the analysis.

        This converts the ShapeAnalysis object into a text prompt
        that the AI can understand. We include:
        - The 3 qualities with their descriptions
        - The shape classification
        - Any tensions (pairs that pull against each other)
        - Any synergies (pairs that reinforce each other)
        - The user's game concept

        Args:
            analysis: The ShapeAnalysis from Stage 2 (deterministic rules)
            context: The user's game description

        Returns:
            The formatted prompt string
        """
        # Build numbered list of qualities with descriptions
        quality_lines = []
        for i, q in enumerate(analysis.qualities, 1):
            quality_lines.append(f"{i}. {q}: {QUALITIES[q]}")

        # Format tensions (or "None" if no tensions)
        if analysis.tensions:
            tensions_text = "\n".join(
                f"- {t.quality_a} ↔ {t.quality_b}: {t.description}"
                for t in analysis.tensions
            )
        else:
            tensions_text = "None"

        # Format synergies (or "None" if no synergies)
        if analysis.synergies:
            synergies_text = "\n".join(
                f"- {s.quality_a} ↔ {s.quality_b}: {s.description}"
                for s in analysis.synergies
            )
        else:
            synergies_text = "None"

        # Combine into full prompt
        # chr(10) is newline — needed because f-strings can't contain backslashes
        return f"""The designer has selected these three experiential qualities for their game:

{chr(10).join(quality_lines)}

**Shape:** {analysis.shape} — {analysis.shape_description}

**Tensions:**
{tensions_text}

**Synergies:**
{synergies_text}

**Their game concept:** "{context}"

Narrate what this combination means for this specific game."""

    def _parse_response(self, content: str) -> tuple[str, list[str]]:
        """
        Parse the model response into explanation and implications.

        The model is instructed to respond in a specific format:
            EXPLANATION:
            [text]

            IMPLICATIONS:
            - [item 1]
            - [item 2]
            - [item 3]

        This method extracts those sections.

        Args:
            content: The raw text response from the model

        Returns:
            Tuple of (explanation_text, list_of_implications)
        """
        explanation = ""
        implications = []

        # Check if response follows expected format
        if "EXPLANATION:" in content and "IMPLICATIONS:" in content:
            # Split at IMPLICATIONS: marker
            parts = content.split("IMPLICATIONS:")
            explanation_part = parts[0].replace("EXPLANATION:", "").strip()
            implications_part = parts[1].strip() if len(parts) > 1 else ""

            explanation = explanation_part

            # Parse implications (lines starting with - or •)
            for line in implications_part.split("\n"):
                line = line.strip()
                if line.startswith("-"):
                    implications.append(line[1:].strip())
                elif line.startswith("•"):
                    implications.append(line[1:].strip())
        else:
            # Fallback: treat entire response as explanation
            # This handles cases where the model doesn't follow the format
            explanation = content
            implications = []

        return explanation, implications

    def narrate(self, analysis: ShapeAnalysis, context: str) -> NarratorResponse:
        """
        Generate a narrative explanation for the play shape.

        This is the main public method. It:
        1. Builds a prompt from the analysis
        2. Calls Claude via OpenRouter
        3. Parses the response
        4. Returns structured data

        Args:
            analysis: ShapeAnalysis from the rules layer (Stage 2)
            context: The user's game description

        Returns:
            NarratorResponse with explanation, implications, and model info
        """
        # Build the prompt
        user_prompt = self._build_user_prompt(analysis, context)

        # Call the API
        # We use the chat completions endpoint with system + user messages
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,  # Some creativity, but not too wild
            max_tokens=800,   # Enough for explanation + implications
        )

        # Extract the text content
        content = response.choices[0].message.content or ""

        # Parse into structured format
        explanation, implications = self._parse_response(content)

        # Return structured response
        return NarratorResponse(
            explanation=explanation,
            implications=implications,
            model=self.model,
        )
