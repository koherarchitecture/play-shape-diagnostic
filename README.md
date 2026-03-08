# Play Shape Diagnostic

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Koher](https://img.shields.io/badge/koher-tool-fb7185)

**Reveal the shape of your play experience.**

Play Shape Diagnostic helps game designers and experience creators understand the experiential architecture of their concepts. Select 3 of 12 experiential qualities, describe your concept, and discover whether your design creates harmony, tension, paradox, or something more complex.

---

## Before You Start: Bring Your Own Key

This tool requires an **OpenRouter API key** to generate narrative interpretations. OpenRouter provides access to Claude Haiku, which powers the language layer.

**Get your key:**
1. Create an account at [openrouter.ai](https://openrouter.ai)
2. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
3. Create a new API key
4. Add credit to your account (pay-as-you-go, typically pennies per use)

**Cost:** Each analysis costs approximately $0.001–0.002 USD (less than a tenth of a cent). A few dollars of credit will last hundreds of analyses.

**Why OpenRouter?** It provides simple, pay-as-you-go access to Claude without requiring an Anthropic enterprise account. Students can start with minimal credit and scale as needed.

---

## Running Locally (Recommended for Students)

This tool is designed to run on your own machine. No server deployment required.

### Requirements

- **Python 3.11+** (check with `python --version`)
- **OpenRouter API key** (see above)
- A terminal and text editor

### Step-by-Step Setup

**1. Download the code**

```bash
# Clone the repository
git clone https://github.com/koher-architecture/play-shape-diagnostic.git
cd play-shape-diagnostic
```

Or download as ZIP from GitHub and extract.

**2. Set up Python environment**

```bash
cd backend
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure your API key**

```bash
# Copy the example environment file
cp ../.env.example .env

# Edit .env and add your OpenRouter API key
# The file should look like:
# OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

**5. Start the backend**

```bash
uvicorn main:app --reload --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**6. Start the frontend** (new terminal window)

```bash
cd play-shape-diagnostic/frontend
python -m http.server 3000
```

**7. Open the tool**

Visit [http://localhost:3000](http://localhost:3000) in your browser.

### Stopping the Tool

Press `Ctrl+C` in each terminal window to stop the servers.

### Restarting Later

```bash
# Terminal 1
cd play-shape-diagnostic/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000

# Terminal 2
cd play-shape-diagnostic/frontend
python -m http.server 3000
```

---

## How It Works

1. **Select 3 qualities** from 12 experiential dimensions
2. **Describe your concept** — what play experience are you designing?
3. **Receive analysis** — the tool reveals:
   - The **shape** of your design (harmonic, dynamic, paradoxical, etc.)
   - **Relationships** between qualities (synergies, tensions, coexistence)
   - **Narrative interpretation** of what this shape means for your design

---

## The Architecture

This tool separates AI from judgment:

| Layer | Role | Implementation |
|-------|------|----------------|
| **Qualification** | Extract signals from input | Pre-defined quality selection (no AI needed) |
| **Rules** | Deterministic judgment | `qualities.py` — embedding similarities + thresholds |
| **Language** | Narrate decisions already made | `narrator.py` — Claude Haiku via OpenRouter |

**The AI never judges whether your design is "good" or "bad".** It only describes the shape that emerges from the relationships between your chosen qualities. The judgment layer (which qualities create tension, which create synergy) is computed from pre-calculated embeddings — deterministic, auditable, reproducible.

---

## The 12 Experiential Qualities

| Quality | Description |
|---------|-------------|
| **anticipation** | Waiting for something to happen — the held breath before the reveal |
| **presence** | Being fully absorbed in the moment — flow state, immersion |
| **yearning** | Longing for something distant — nostalgia, desire, unreachable goals |
| **tension** | Uncertainty about what comes next — suspense, unease |
| **dread** | Fear of what lurks ahead — horror, impending threat |
| **relief** | Release from pressure — the exhale after danger passes |
| **mischief** | Playful rule-breaking — cleverness, pranks, subversion |
| **discovery** | Finding something new — exploration, revelation, wonder |
| **mastery** | Growing skill and competence — the satisfaction of getting better |
| **belonging** | Connection to others or place — community, home, togetherness |
| **transgression** | Crossing boundaries — taboo, forbidden action, moral ambiguity |
| **triumph** | Victory and accomplishment — winning, overcoming, celebration |

---

## Shape Classifications

The tool classifies your quality combination based on relationships between pairs:

| Shape | Pattern | What It Means |
|-------|---------|---------------|
| **Harmonic** | High synergy, no tension | Qualities reinforce naturally — a unified experiential palette |
| **Distinct** | Low synergy, no tension | Qualities coexist independently — parallel tracks of experience |
| **Dynamic** | Some tension, some synergy | Productive push and pull with grounding |
| **Complex** | Multiple forces | A rich experiential landscape |
| **Paradoxical** | High tension | Opposites held together — powerful but demanding |

---

## Troubleshooting

### "OPENROUTER_API_KEY environment variable required"

Your `.env` file is missing or the key isn't set correctly.

1. Check that `.env` exists in the `backend/` folder
2. Check that it contains `OPENROUTER_API_KEY=sk-or-v1-...` (your actual key)
3. Restart the backend server

### "Connection refused" or blank page

Make sure both servers are running:
- Backend on port 8000 (`uvicorn main:app --reload --port 8000`)
- Frontend on port 3000 (`python -m http.server 3000`)

### "Module not found" errors

Make sure your virtual environment is activated (you should see `(venv)` in your prompt) and dependencies are installed:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### API errors or slow responses

- Check your OpenRouter account has credit
- Check your API key is correct (no extra spaces)
- OpenRouter occasionally has brief outages — wait and retry

---

## Study Module: Understanding How It Works

The **Study Module** is a CLI walkthrough designed for design students (not computer scientists). It explains not just WHAT the tool does, but WHY each part exists.

### Running the Study Module

```bash
# From the project root
python study.py              # Full walkthrough (recommended first time)
python study.py --all        # Same as above

# Explore specific stages
python study.py --stage 1    # Stage 1: The 12 qualities
python study.py --stage 2    # Stage 2: Relationship rules (the core logic)
python study.py --stage 3    # Stage 3: AI narrator

# Other options
python study.py --flow       # See a complete analysis step-by-step
python study.py --explore    # Interactive: try your own combinations
python study.py --help       # Show all options
```

### What You'll Learn

**Stage 1** — Why user selection matters, and what each quality represents.

**Stage 2** — How relationships are computed using embeddings and thresholds. This is the heart of the system — you'll see actual similarity scores, understand how thresholds classify relationships, and watch shape classification happen.

**Stage 3** — What the AI narrator receives and what it does with that information. The AI only DESCRIBES; it never JUDGES.

**Full Flow** — A complete trace from input to output, showing every step of the analysis.

**Interactive Explorer** — Try quality combinations without running the full tool. See similarity scores and relationship classifications in real-time.

### No API Key Required

The Study Module runs entirely locally (except Stage 3 narrative examples, which are pre-written). You can understand the entire architecture without any API keys.

---

## Project Structure

```
play-shape-diagnostic/
├── backend/
│   ├── main.py              # FastAPI application — API endpoints
│   ├── narrator.py          # Narrative generation — calls Claude via OpenRouter
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── index.html           # Single-page application — all UI in one file
├── src/
│   └── qualities.py         # Quality definitions and relationship analysis
├── data/
│   └── quality_similarities.json   # Pre-computed embedding similarities
├── scripts/
│   └── compute_similarities.py     # Script to recompute embeddings (optional)
├── study.py                 # Study Module — CLI walkthrough for students
└── .env.example             # Template for your API key configuration
```

---

## API Reference (For Developers)

If you want to integrate with the tool programmatically:

### GET `/api/qualities`

Returns all 12 qualities with descriptions.

### POST `/api/analyse`

Analyse a quality combination.

**Request:**
```json
{
  "qualities": ["anticipation", "dread", "relief"],
  "context": "A horror game where players wait in darkness, dreading what might emerge, then experience relief when the threat passes."
}
```

**Response:**
```json
{
  "qualities": ["anticipation", "dread", "relief"],
  "shape": "harmonic",
  "shape_description": "Qualities reinforce naturally — a unified experiential palette",
  "tensions": [],
  "synergies": [
    {"quality_a": "anticipation", "quality_b": "dread", "description": "anticipation reinforces dread"},
    {"quality_a": "dread", "quality_b": "relief", "description": "dread reinforces relief"}
  ],
  "neutrals": [...],
  "narrative": {
    "explanation": "Your play shape creates a classic horror rhythm...",
    "implications": ["...", "...", "..."]
  }
}
```

### GET `/api/samples`

Returns example concepts for inspiration.

### GET `/health`

Health check endpoint.

---

## Recomputing Embeddings (Advanced)

Quality relationships are based on semantic similarity of their descriptions, computed using OpenAI embeddings. The pre-computed values in `data/quality_similarities.json` work out of the box.

If you want to modify the quality definitions and recompute:

```bash
cd scripts
# Requires OPENAI_API_KEY environment variable
python compute_similarities.py
```

This outputs new similarity values to `data/quality_similarities.json`.

---

## Philosophy

This tool embodies a specific stance on AI in creative tools:

1. **AI handles language, not judgment** — the AI describes what you've built; it doesn't evaluate whether it's "good"
2. **Deterministic where possible** — relationships are computed from embeddings, not generated on-the-fly
3. **Transparency over magic** — you can see exactly how the shape classification works in `qualities.py`
4. **Your design, your decisions** — the tool illuminates; you decide what to do with the insight

---

## Credits

Part of the [Koher](https://koher.app) collection of design tools.

*Co-created by [Prayas Abhinav](https://prayasabhinav.net) + [Claude Code](https://claude.ai/code)*

Built for game design students and experience creators who want to understand the experiential architecture of their work.

---

## Licence

MIT — use freely, modify freely, no attribution required.
