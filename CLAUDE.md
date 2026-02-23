# CLAUDE.md - Play Shape Diagnostic

## What This Is

Play Shape Diagnostic is a tool that helps game designers and experience creators analyse the experiential qualities of their play concepts. Users select 3 of 12 experiential qualities and describe their concept — the tool reveals the "shape" of their design through relationship analysis and narrative interpretation.

---

## Architecture

This tool follows Koher's three-layer architecture:

| Layer | What It Does | Implementation |
|-------|-------------|----------------|
| **Qualification** | AI reads language patterns, extracts signals | Not used in this tool (qualities are pre-defined) |
| **Rules** | Deterministic code converts signals into judgments | `qualities.py` — embedding similarities + thresholds |
| **Language** | AI narrates decisions already made | `narrator.py` — Claude Haiku via OpenRouter |

**Key insight:** The AI never judges whether a quality combination is "good" or "bad". It only describes the shape that emerges from the relationships.

---

## Project Structure

```
play-shape-diagnostic/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── narrator.py      # Narrative generation (OpenRouter)
│   └── requirements.txt
├── frontend/
│   └── index.html       # Single-page application
├── src/
│   └── qualities.py     # Quality definitions and analysis
├── data/
│   └── quality_similarities.json  # Pre-computed embeddings
├── scripts/
│   └── compute_similarities.py    # Recompute embeddings
└── .env.example         # Environment template
```

---

## The 12 Experiential Qualities

| Quality | Description |
|---------|-------------|
| anticipation | Waiting for something to happen — the held breath before the reveal |
| presence | Being fully absorbed in the moment — flow state, immersion |
| yearning | Longing for something distant — nostalgia, desire, unreachable goals |
| tension | Uncertainty about what comes next — suspense, unease |
| dread | Fear of what lurks ahead — horror, impending threat |
| relief | Release from pressure — the exhale after danger passes |
| mischief | Playful rule-breaking — cleverness, pranks, subversion |
| discovery | Finding something new — exploration, revelation, wonder |
| mastery | Growing skill and competence — the satisfaction of getting better |
| belonging | Connection to others or place — community, home, togetherness |
| transgression | Crossing boundaries — taboo, forbidden action, moral ambiguity |
| triumph | Victory and accomplishment — winning, overcoming, celebration |

---

## Shape Classifications

Based on tension/synergy counts between the 3 selected qualities:

| Shape | Pattern | Description |
|-------|---------|-------------|
| **harmonic** | High synergy, no tension | Qualities reinforce naturally |
| **distinct** | Low synergy, no tension | Qualities coexist independently |
| **dynamic** | Some tension, some synergy | Productive push and pull |
| **complex** | Multiple forces | Rich experiential landscape |
| **paradoxical** | High tension | Opposites held together |

---

## Running Locally

**Requirements:** Python 3.11+, OpenRouter API key

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your OPENROUTER_API_KEY
uvicorn main:app --reload --port 8000

# Frontend
# Serve frontend/index.html via any static server
python -m http.server 3000 -d ../frontend
```

---

## Study Module

The Study Module (`study.py`) is a CLI walkthrough for design students. It explains how the tool works, step by step, with live examples.

**Usage:**
```bash
python study.py              # Full walkthrough
python study.py --stage 1    # Stage 1: The 12 qualities
python study.py --stage 2    # Stage 2: Relationship rules
python study.py --stage 3    # Stage 3: AI narrator
python study.py --flow       # Complete analysis trace
python study.py --explore    # Interactive explorer
```

**Design principles:**
- Written for DESIGN students, not CS students
- Explains WHY, not just WHAT
- Shows actual similarity scores and thresholds
- No API key required (except for live narration)

**What each stage covers:**
- **Stage 1:** Why user selection matters; what each quality means
- **Stage 2:** How embeddings work; how thresholds classify relationships; how shape is determined
- **Stage 3:** What the narrator receives; what it does (describe, not judge)
- **Flow:** Complete trace from input to output
- **Explore:** Try combinations interactively, see scores in real-time

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/qualities` | GET | List all 12 qualities with descriptions |
| `/api/analyse` | POST | Analyse a quality combination |
| `/api/samples` | GET | Get example concepts |
| `/health` | GET | Health check |

**POST /api/analyse:**
```json
{
  "qualities": ["anticipation", "dread", "relief"],
  "context": "A horror game where players wait in darkness..."
}
```

---

## Writing Conventions

British English spellings (organise, colour, centre).

---

*Open source release — no authentication, no analytics, no usage limits.*
