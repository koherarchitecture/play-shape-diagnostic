"""
FastAPI application for Play Shape Diagnostic.

Open source version — no authentication, no analytics logging.

This file is the main entry point for the backend server. It defines:
- API endpoints that the frontend calls
- Request/response data structures (using Pydantic models)
- Sample game concepts for demonstration

Architecture note:
This file is the "glue" — it connects the frontend to the analysis logic.
The actual analysis happens in src/qualities.py (deterministic rules)
and backend/narrator.py (AI language generation).

Endpoints:
- GET /: Serve frontend
- GET /health: Health check
- GET /api/qualities: Return quality definitions
- GET /api/samples: Return sample game concepts
- POST /api/analyse: Generate play shape narrative
"""

import os
import random
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

# Import our domain logic
# - QualityAnalyser: computes relationships between qualities (deterministic)
# - get_quality_definitions: returns the list of 12 qualities
# - validate_selection: checks that the user's input is valid
# - QUALITIES: the raw dictionary of quality definitions
from src.qualities import (
    QualityAnalyser,
    get_quality_definitions,
    validate_selection,
    QUALITIES,
)

# Import the AI narrator (calls Claude via OpenRouter)
from backend.narrator import PlayShapeNarrator

# Load environment variables from .env file
# This is where your OPENROUTER_API_KEY should be defined
load_dotenv(Path(__file__).parent.parent / ".env")


# =============================================================================
# Configuration
# =============================================================================

# Path to project root (one level up from backend/)
PROJECT_ROOT = Path(__file__).parent.parent

# Path to frontend files
FRONTEND_DIR = PROJECT_ROOT / "frontend"


# =============================================================================
# FastAPI Application
# =============================================================================

# Create the FastAPI app instance
# This is what uvicorn runs when you start the server
app = FastAPI(
    title="Play Shape Diagnostic",
    description="Articulate and understand the experiential shape of your game concepts",
    version="2.0.0",
)

# Lazy-loaded components
# We create these once and reuse them for efficiency
# None initially — created on first request
_analyser: QualityAnalyser | None = None
_narrator: PlayShapeNarrator | None = None


def get_analyser() -> QualityAnalyser:
    """
    Get or create the quality analyser.

    This is a singleton pattern — we only create one analyser
    and reuse it for all requests. The analyser loads pre-computed
    embedding similarities from data/quality_similarities.json.
    """
    global _analyser
    if _analyser is None:
        _analyser = QualityAnalyser()
    return _analyser


def get_narrator() -> PlayShapeNarrator:
    """
    Get or create the AI narrator.

    This is also a singleton. The narrator connects to OpenRouter
    to access Claude Haiku for generating narrative explanations.
    """
    global _narrator
    if _narrator is None:
        _narrator = PlayShapeNarrator()
    return _narrator


# =============================================================================
# Request/Response Models (Pydantic)
# =============================================================================
#
# Pydantic models define the shape of data going in and out of the API.
# FastAPI uses these for:
# - Automatic request validation (reject bad input)
# - Automatic response serialisation (convert Python objects to JSON)
# - Auto-generated API documentation (see /docs)

class AnalyseRequest(BaseModel):
    """
    Request body for /api/analyse.

    The user sends:
    - qualities: exactly 3 quality names (e.g. ["dread", "anticipation", "relief"])
    - context: their game description (20-500 characters)
    """
    qualities: list[str] = Field(
        ...,  # ... means required
        min_length=3,
        max_length=3,
        description="Exactly 3 quality names",
    )
    context: str = Field(
        ...,
        min_length=20,
        max_length=500,
        description="Game description (20-500 characters)",
    )


class QualityPairResponse(BaseModel):
    """
    A pair of qualities with their relationship.

    Example: {"pair": ["dread", "relief"], "description": "dread reinforces relief", "similarity": 0.82}
    """
    pair: list[str]
    description: str
    similarity: float  # The embedding similarity score (0.0 to 1.0)


class ShapeResponse(BaseModel):
    """
    Shape classification result.

    Example: {"classification": "harmonic", "description": "Qualities reinforce naturally..."}
    """
    classification: str  # One of: harmonic, distinct, dynamic, complex, paradoxical
    description: str


class RelationshipsResponse(BaseModel):
    """
    Quality relationships — which pairs are in tension vs synergy.

    For 3 qualities, there are exactly 3 pairs:
    - A-B, A-C, B-C

    Each pair is classified as tension, synergy, or neutral
    based on their embedding similarity score.
    """
    tensions: list[QualityPairResponse]
    synergies: list[QualityPairResponse]


class NarrativeResponse(BaseModel):
    """
    Narrative from the AI.

    The AI generates:
    - explanation: 4-8 sentences explaining what this shape means
    - implications: 2-3 design implications specific to the game
    """
    explanation: str
    implications: list[str]


class MetadataResponse(BaseModel):
    """
    Response metadata — which model was used, when was this generated.

    Useful for debugging and transparency.
    """
    model: str  # e.g. "anthropic/claude-haiku-4.5"
    timestamp: str  # ISO format timestamp


class AnalyseResponse(BaseModel):
    """
    Complete response body for /api/analyse.

    This is the full analysis result that the frontend displays.
    """
    qualities: list[str]  # The 3 qualities (sorted alphabetically)
    combination_key: str  # e.g. "anticipation+dread+relief"
    shape: ShapeResponse  # The overall shape classification
    relationships: RelationshipsResponse  # Tensions and synergies
    narrative: NarrativeResponse  # AI-generated explanation
    metadata: MetadataResponse  # Model info and timestamp


class QualityDefinition(BaseModel):
    """A single quality definition."""
    name: str
    description: str


class QualitiesResponse(BaseModel):
    """Response body for /api/qualities."""
    qualities: list[QualityDefinition]


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    details: str | None = None


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """
    Serve the frontend HTML.

    When you visit http://localhost:8000/ in your browser,
    this endpoint returns the index.html file.
    """
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_path)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Use this to verify the server is running.
    Returns version info and confirms qualities are loaded.
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "qualities_loaded": len(QUALITIES),
    }


@app.get("/api/qualities", response_model=QualitiesResponse)
async def get_qualities():
    """
    Return all quality definitions.

    The frontend calls this to populate the quality selection cards.
    Returns all 12 qualities with their descriptions.
    """
    return QualitiesResponse(
        qualities=[
            QualityDefinition(name=q["name"], description=q["description"])
            for q in get_quality_definitions()
        ]
    )


@app.post("/api/analyse", response_model=AnalyseResponse, responses={400: {"model": ErrorResponse}})
async def analyse_play_shape(request_body: AnalyseRequest):
    """
    Analyse a combination of 3 qualities and generate a narrative.

    This is the main endpoint — it does the actual analysis.

    The three-stage pipeline:

    Stage 1: QUALIFICATION (already done)
        The user has selected their 3 qualities. This stage is "free" because
        we use pre-defined quality cards rather than parsing free text.

    Stage 2: RULES (deterministic)
        The QualityAnalyser computes relationships between the 3 qualities.
        It uses pre-computed embedding similarities (from data/quality_similarities.json)
        to determine which pairs are in tension vs synergy.
        This is deterministic — same input always gives same output.

    Stage 3: LANGUAGE (AI)
        The PlayShapeNarrator generates a narrative explanation.
        It takes the deterministic analysis from Stage 2 and writes
        a human-readable explanation using Claude Haiku.
        This is where AI adds value — converting structure to prose.
    """

    # Validate the user's selection
    # Checks: exactly 3 qualities, no duplicates, all valid quality names, context length
    is_valid, error_msg = validate_selection(request_body.qualities, request_body.context)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Stage 2: Deterministic analysis of relationships
    # This computes which quality pairs are tensions, synergies, or neutral
    # and determines the overall shape classification
    analyser = get_analyser()
    analysis = analyser.analyse(request_body.qualities)

    # Stage 3: AI narration
    # Takes the structural analysis and generates human-readable prose
    try:
        narrator = get_narrator()
        narrative = narrator.narrate(analysis, request_body.context)
    except ValueError as e:
        # Missing API key or configuration error
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # API call failed (network error, rate limit, etc.)
        raise HTTPException(status_code=500, detail=f"Narration failed: {str(e)}")

    # Build and return the response
    # We convert our internal data structures to the API response format
    return AnalyseResponse(
        qualities=analysis.qualities,
        combination_key=analysis.combination_key,
        shape=ShapeResponse(
            classification=analysis.shape,
            description=analysis.shape_description,
        ),
        relationships=RelationshipsResponse(
            tensions=[
                QualityPairResponse(
                    pair=[t.quality_a, t.quality_b],
                    description=t.description,
                    similarity=t.similarity,
                )
                for t in analysis.tensions
            ],
            synergies=[
                QualityPairResponse(
                    pair=[s.quality_a, s.quality_b],
                    description=s.description,
                    similarity=s.similarity,
                )
                for s in analysis.synergies
            ],
        ),
        narrative=NarrativeResponse(
            explanation=narrative.explanation,
            implications=narrative.implications,
        ),
        metadata=MetadataResponse(
            model=narrative.model,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
    )


# =============================================================================
# Sample Game Concepts
# =============================================================================
#
# These are example game concepts that demonstrate the tool.
# The frontend can load these for quick testing and inspiration.
# Each sample has pre-selected qualities and a game description.

SAMPLE_GAMES = [
    {
        "name": "Roguelike Dungeon Crawler",
        "qualities": ["tension", "discovery", "mastery"],
        "context": "A procedurally generated dungeon crawler where each run is different. Players explore dark corridors, find rare items, and learn enemy patterns through repeated deaths.",
    },
    {
        "name": "Cozy Farm Sim",
        "qualities": ["presence", "belonging", "relief"],
        "context": "A gentle farming game where players cultivate crops, befriend villagers, and restore an abandoned farmhouse. No fail states, just peaceful progress.",
    },
    {
        "name": "Horror Escape Room",
        "qualities": ["dread", "anticipation", "relief"],
        "context": "Players are trapped in a haunted mansion and must solve puzzles to escape before something finds them. Every unlocked door might reveal safety or terror.",
    },
    {
        "name": "Stealth Sandbox",
        "qualities": ["mischief", "mastery", "tension"],
        "context": "An open-world game where players infiltrate heavily guarded locations. Multiple approaches — disguises, hacking, social engineering — all viable.",
    },
    {
        "name": "Narrative Walking Sim",
        "qualities": ["yearning", "discovery", "presence"],
        "context": "Players explore the abandoned childhood home of a missing person, piecing together memories through objects and environmental storytelling.",
    },
    {
        "name": "Competitive Arena Fighter",
        "qualities": ["triumph", "mastery", "tension"],
        "context": "A 1v1 fighting game with deep combo systems. Ranked matches determine global standing. Every frame counts.",
    },
    {
        "name": "Morally Grey RPG",
        "qualities": ["transgression", "belonging", "yearning"],
        "context": "A choice-driven RPG where players lead a band of outlaws. Every decision strengthens some bonds while breaking others. No clean victories.",
    },
    {
        "name": "Puzzle Platformer",
        "qualities": ["discovery", "mastery", "anticipation"],
        "context": "Physics-based puzzles in dreamlike environments. Each new mechanic is introduced wordlessly. The joy is in the 'aha' moment.",
    },
]


class SampleGame(BaseModel):
    """A sample game concept."""
    name: str
    qualities: list[str]
    context: str


class SamplesResponse(BaseModel):
    """Response body for /api/samples."""
    samples: list[SampleGame]
    random_pick: SampleGame


@app.get("/api/samples", response_model=SamplesResponse)
async def get_samples():
    """
    Get sample game concepts for testing.

    Returns all 8 samples plus a random pick for quick loading.
    The frontend can use this to populate the "Try an example" feature.
    """
    samples = [SampleGame(**s) for s in SAMPLE_GAMES]
    random_pick = random.choice(samples)

    return SamplesResponse(
        samples=samples,
        random_pick=random_pick,
    )


# =============================================================================
# Error handlers
# =============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    return HTTPException(status_code=400, detail=str(exc))


# =============================================================================
# Main entry point
# =============================================================================
#
# This runs when you execute: python main.py
# In production, use: uvicorn main:app --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    import uvicorn

    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
