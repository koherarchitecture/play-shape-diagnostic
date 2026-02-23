#!/usr/bin/env python3
"""
Play Shape Diagnostic — Study Module

A step-by-step walkthrough of how the tool works.
Designed for design students, not computer scientists.

Run this to see the system in action:
    python study.py

Or explore specific stages:
    python study.py --stage 1
    python study.py --stage 2
    python study.py --stage 3
    python study.py --all

This module explains WHY each step exists, not just WHAT it does.
"""

import json
import random
import sys
import time
from pathlib import Path

# Add project root to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from src.qualities import QUALITIES, QualityAnalyser, SHAPE_CLASSIFICATIONS


# =============================================================================
# PRE-GENERATED NARRATIVES
# =============================================================================
#
# These narratives were generated using Claude Haiku via OpenRouter.
# They're included here so students can see real outputs without
# needing their own API key.

def load_study_narratives() -> dict:
    """
    Load pre-generated narratives from JSON.

    Returns dict mapping combination_key (e.g., "dread+tension+yearning")
    to the full narrative data.
    """
    narratives_path = Path(__file__).parent / "data" / "study_narratives.json"

    if not narratives_path.exists():
        return {}

    with open(narratives_path) as f:
        data = json.load(f)

    # Index by combination key for quick lookup
    return {n["combination_key"]: n for n in data.get("narratives", [])}


def get_narrative_for_qualities(qualities: list[str], narratives: dict) -> dict | None:
    """
    Look up a pre-generated narrative for a quality combination.

    Args:
        qualities: List of 3 quality names
        narratives: Dict from load_study_narratives()

    Returns:
        Narrative dict if found, None otherwise
    """
    key = "+".join(sorted(qualities))
    return narratives.get(key)


def get_random_narrative(narratives: dict, shape: str | None = None) -> dict | None:
    """
    Get a random pre-generated narrative, optionally filtered by shape.

    Args:
        narratives: Dict from load_study_narratives()
        shape: Optional shape filter ("harmonic", "dynamic", etc.)

    Returns:
        Random narrative dict if available, None otherwise
    """
    if not narratives:
        return None

    all_narratives = list(narratives.values())

    if shape:
        all_narratives = [n for n in all_narratives if n["shape"] == shape]

    if not all_narratives:
        return None

    return random.choice(all_narratives)


# Load narratives at module level
STUDY_NARRATIVES = load_study_narratives()


# =============================================================================
# VISUAL HELPERS
# =============================================================================

def clear_screen():
    """Clear terminal for fresh start."""
    print("\033[2J\033[H", end="")


def pause(prompt="Press Enter to continue..."):
    """Wait for user input."""
    input(f"\n{prompt}")


def print_header(title: str):
    """Print a section header."""
    width = 60
    print()
    print("═" * width)
    print(f"  {title}")
    print("═" * width)
    print()


def print_subheader(title: str):
    """Print a subsection header."""
    print()
    print(f"─── {title} ───")
    print()


def print_box(content: str, title: str = ""):
    """Print content in a box."""
    lines = content.strip().split("\n")
    width = max(len(line) for line in lines) + 4
    width = max(width, len(title) + 6)

    print()
    if title:
        print(f"┌─ {title} " + "─" * (width - len(title) - 4) + "┐")
    else:
        print("┌" + "─" * width + "┐")

    for line in lines:
        padding = width - len(line) - 2
        print(f"│ {line}" + " " * padding + "│")

    print("└" + "─" * width + "┘")
    print()


def slow_print(text: str, delay: float = 0.02):
    """Print text with a slight delay for emphasis."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def print_arrow():
    """Print a downward arrow to show flow."""
    print("            │")
    print("            ▼")


# =============================================================================
# INTRODUCTION
# =============================================================================

def show_introduction():
    """Explain what this tool is and why it exists."""
    clear_screen()
    print_header("PLAY SHAPE DIAGNOSTIC — STUDY MODULE")

    print("""This tool helps game designers understand the EXPERIENTIAL SHAPE
of their concepts.

Not genre. Not mechanics. Not theme.
The SHAPE of how it feels to play.

Every game creates a constellation of feelings. This tool helps
you see that constellation — where the tensions are, where things
reinforce, what shape emerges.
""")

    print_box("""The core insight:

When you pick THREE experiential qualities, they don't just
sit next to each other. They RELATE. Some reinforce. Some
pull against each other. The pattern of those relationships
is your game's SHAPE.""", title="Why Shape?")

    pause()

    print_subheader("THE THREE STAGES")

    print("""This tool works in three stages:

  STAGE 1: YOUR INPUT
  You select 3 qualities and describe your game.
  This is YOUR judgment — you know what experience you're creating.

  STAGE 2: RULES
  The system analyses relationships between your qualities.
  This is DETERMINISTIC — same input always gives same output.
  No AI involved. Just math and thresholds.

  STAGE 3: LANGUAGE
  An AI (Claude Haiku) narrates what your shape means.
  It explains — it doesn't judge.
  The analysis was already done in Stage 2.
""")

    print_box("""The principle:

    AI handles LANGUAGE.
    Code handles JUDGMENT.
    Humans handle MEANING.

The AI never decides if your combination is "good" or "bad".
It only describes the shape that emerges.""", title="Architecture")

    pause()


# =============================================================================
# STAGE 1: THE QUALITIES
# =============================================================================

def show_stage_1():
    """Explain the 12 qualities and why user selection matters."""
    clear_screen()
    print_header("STAGE 1: YOUR INPUT")

    print("""In Stage 1, YOU select three experiential qualities.

Why you? Because you're the expert on your own game.
You know what experience you're trying to create.

The tool doesn't try to detect this from your pitch text.
We tried that — it didn't work. Some experiences are too
nuanced to classify automatically.

So we inverted the problem:
Instead of "What can AI detect?"
We ask "What do YOU already know?"
""")

    print_subheader("THE 12 EXPERIENTIAL QUALITIES")

    # Group qualities into themed clusters for easier understanding
    print("These are the building blocks of play experience:\n")

    clusters = [
        ("TEMPORAL", ["anticipation", "presence", "yearning"]),
        ("UNCERTAINTY", ["tension", "dread", "relief"]),
        ("AGENCY", ["mischief", "discovery", "mastery"]),
        ("CONNECTION", ["belonging", "transgression", "triumph"]),
    ]

    for cluster_name, quality_names in clusters:
        print(f"  {cluster_name}:")
        for name in quality_names:
            desc = QUALITIES[name]
            print(f"    • {name}: {desc}")
        print()

    pause()

    print_subheader("WHY THESE 12?")

    print("""These qualities emerged from studying play experiences across:
- Video games (action, puzzle, narrative, horror, cozy)
- Board games (competitive, cooperative, social deduction)
- Physical play (sports, playground games, performances)
- Playful systems (escape rooms, ARGs, treasure hunts)

They're not exhaustive. They're GENERATIVE — distinct enough
to create meaningful combinations, evocative enough to guide design.

Each quality has a DESCRIPTION that captures its essence.
These descriptions become important in Stage 2...
""")

    pause()


# =============================================================================
# STAGE 2: THE RULES
# =============================================================================

def show_stage_2():
    """Explain how relationships are computed."""
    clear_screen()
    print_header("STAGE 2: DETERMINISTIC RULES")

    print("""Stage 2 is where the magic happens — but it's not magic.
It's just rules.

When you select 3 qualities, we analyse the RELATIONSHIPS
between them. With 3 qualities, there are exactly 3 pairs:

    Quality A ←→ Quality B
    Quality A ←→ Quality C
    Quality B ←→ Quality C

Each pair can have one of three relationships:

    SYNERGY:  The qualities reinforce each other
    TENSION:  The qualities pull against each other
    NEUTRAL:  The qualities coexist independently
""")

    pause()

    print_subheader("HOW RELATIONSHIPS ARE DETERMINED")

    print("""Here's the key insight:

We don't hardcode relationships like "dread + relief = tension".
That would encode ONE person's opinion as truth.

Instead, we use SEMANTIC SIMILARITY.

Each quality has a description:
    dread: "Fear of what lurks ahead — horror, impending threat"
    relief: "Release from pressure — the exhale after danger passes"

These descriptions were converted into EMBEDDINGS — numerical
representations that capture meaning. Qualities with similar
meanings have similar embeddings.

The similarity score (0 to 1) tells us how close two qualities are:
    HIGH similarity → they mean similar things → SYNERGY
    LOW similarity  → they mean different things → TENSION
    MIDDLE         → neither close nor far → NEUTRAL
""")

    print_box("""THRESHOLDS (calibrated by reviewing all combinations):

    Similarity ≥ 0.82  →  SYNERGY
    Similarity < 0.72  →  TENSION
    Otherwise          →  NEUTRAL""", title="The Rules")

    pause()

    # Now show a live example
    print_subheader("LIVE EXAMPLE")

    # Load the similarity data
    data_path = Path(__file__).parent / "data" / "quality_similarities.json"
    with open(data_path) as f:
        data = json.load(f)

    similarities = data["similarities"]
    thresholds = data["thresholds"]

    print("Let's analyse: DREAD + DISCOVERY + RELIEF\n")

    example_qualities = ["dread", "discovery", "relief"]
    pairs = [
        ("dread", "discovery"),
        ("dread", "relief"),
        ("discovery", "relief"),
    ]

    print("Step 1: Look up similarity scores\n")

    for q1, q2 in pairs:
        key = "+".join(sorted([q1, q2]))
        sim = similarities.get(key, 0.0)
        print(f"    {q1} + {q2}")
        print(f"    Similarity: {sim:.4f}")
        print()
        time.sleep(0.5)

    pause()

    print("Step 2: Apply thresholds\n")

    analyser = QualityAnalyser()
    analysis = analyser.analyse(example_qualities)

    for q1, q2 in pairs:
        key = "+".join(sorted([q1, q2]))
        sim = similarities.get(key, 0.0)

        if sim >= thresholds["synergy"]:
            rel = "SYNERGY"
            symbol = "↔"
        elif sim < thresholds["tension"]:
            rel = "TENSION"
            symbol = "⇋"
        else:
            rel = "NEUTRAL"
            symbol = "—"

        print(f"    {q1} {symbol} {q2}")
        print(f"    {sim:.4f} → {rel}")
        print()
        time.sleep(0.5)

    pause()

    print_subheader("SHAPE CLASSIFICATION")

    print(f"""Step 3: Count relationships and classify shape

    Tensions:  {len(analysis.tensions)}
    Synergies: {len(analysis.synergies)}
    Neutrals:  {len(analysis.neutrals)}
""")

    print("The SHAPE is determined by this pattern:\n")

    print("    SHAPE CLASSIFICATIONS:")
    print("    ┌──────────────────────────────────────────────────┐")
    print("    │  Tensions  Synergies  →  Shape                   │")
    print("    ├──────────────────────────────────────────────────┤")
    print("    │     0        2-3      →  HARMONIC (unified)      │")
    print("    │     0        0-1      →  DISTINCT (parallel)     │")
    print("    │     1        0-2      →  DYNAMIC (push & pull)   │")
    print("    │     2        2        →  COMPLEX (rich)          │")
    print("    │    2-3       0-1      →  PARADOXICAL (opposites) │")
    print("    └──────────────────────────────────────────────────┘")

    print(f"""
Result for DREAD + DISCOVERY + RELIEF:

    Shape: {analysis.shape.upper()}
    "{analysis.shape_description}"
""")

    pause()

    print_subheader("WHY THIS MATTERS")

    print("""Notice what just happened:

1. We used EMBEDDINGS (AI-generated representations of meaning)
2. But we applied DETERMINISTIC THRESHOLDS (code rules)
3. The same input ALWAYS gives the same output

The AI helped us understand what words MEAN.
The CODE decides what that means for RELATIONSHIPS.

This is auditable. Reproducible. Debuggable.
No black box. No "the AI decided".

Every judgment can be traced back to:
- A similarity score (from embeddings)
- A threshold (from calibration)
- A classification rule (from the shape table)
""")

    pause()


# =============================================================================
# STAGE 3: THE NARRATOR
# =============================================================================

def show_stage_3():
    """Explain how the AI narrator works."""
    clear_screen()
    print_header("STAGE 3: LANGUAGE GENERATION")

    print("""Stage 3 is where AI re-enters — but only for LANGUAGE.

The analysis is already done. The shape is classified.
The tensions and synergies are identified.

Now we need to EXPLAIN what this means for your specific game.
That's what the narrator does.
""")

    print_subheader("WHAT THE NARRATOR RECEIVES")

    print("""The narrator (Claude Haiku) receives:

1. Your three qualities (with descriptions)
2. The shape classification
3. The list of tensions (if any)
4. The list of synergies (if any)
5. Your game concept description

It does NOT receive:
- Raw embedding scores
- Other users' analyses
- Any instructions to judge quality
""")

    # Get a real example narrative
    example_narrative = get_random_narrative(STUDY_NARRATIVES, shape="dynamic")
    if example_narrative:
        example_quals = example_narrative["qualities"]
        example_context = example_narrative["context"]
        example_shape = example_narrative["shape"]
    else:
        # Fallback
        example_quals = ["dread", "discovery", "relief"]
        example_context = "A horror game where players explore an abandoned research facility."
        example_shape = "dynamic"

    print_box(f"""Example prompt to the narrator:

The designer selected: {', '.join(example_quals)}

Shape: {example_shape.upper()}

Their game: "{example_context}"

Narrate what this combination means for this game.""", title="What AI Sees")

    pause()

    print_subheader("WHAT THE NARRATOR DOES")

    print("""The narrator's job:

1. WEAVE together the qualities into a coherent picture
2. EXPLAIN how tensions create productive friction
3. EXPLAIN how synergies compound experience
4. OFFER 2-3 design implications specific to THIS game

What it does NOT do:

- Judge the combination as "good" or "bad"
- Suggest adding different qualities
- Compare to other games
- Generate game design documents
""")

    # Show real narrative output
    if example_narrative:
        explanation = example_narrative["explanation"]
        implications = example_narrative["implications"]

        # Wrap explanation for display (crude word wrap)
        wrapped_explanation = ""
        line = ""
        for word in explanation.split():
            if len(line) + len(word) + 1 > 55:
                wrapped_explanation += line.strip() + "\n"
                line = word + " "
            else:
                line += word + " "
        wrapped_explanation += line.strip()

        impl_text = "\n".join(f"- {imp[:60]}..." if len(imp) > 63 else f"- {imp}" for imp in implications[:3])

        print_box(f"""{wrapped_explanation[:500]}{'...' if len(wrapped_explanation) > 500 else ''}

Design implications:
{impl_text}
""", title="Real Narrator Output")
    else:
        print_box("""[Pre-generated narratives not found. Run the study
narrative generator to populate examples.]""", title="AI Output")

    pause()

    print_subheader("WHY LANGUAGE COMES LAST")

    print("""The sequence matters:

    STAGE 1: Human judgment (you select qualities)
         ↓
    STAGE 2: Code judgment (rules determine relationships)
         ↓
    STAGE 3: AI language (words describe what emerged)

If we let AI do the judging:
- Results would vary unpredictably
- We couldn't explain WHY something was classified
- Users would have to trust a black box

By separating concerns:
- Stage 2 is AUDITABLE (you can see the scores and thresholds)
- Stage 3 is EXPLAINABLE (it's just describing what Stage 2 found)
- The system is TRUSTWORTHY (no hidden judgments)
""")

    pause()


# =============================================================================
# THE FULL FLOW
# =============================================================================

def show_full_flow():
    """Walk through a complete analysis step by step."""
    clear_screen()
    print_header("COMPLETE FLOW: END TO END")

    print("""Let's trace a complete analysis from input to output.

We'll use this example:
    Qualities: TENSION, MASTERY, DISCOVERY
    Concept: "A roguelike dungeon crawler where each run teaches
              you patterns through failure"
""")

    pause()

    # STAGE 1
    print_subheader("STAGE 1: INPUT")

    print("""The user has selected:

    ┌─────────────────────────────────────────────────────────┐
    │  TENSION                                                │
    │  "Uncertainty about what comes next — suspense, unease" │
    ├─────────────────────────────────────────────────────────┤
    │  MASTERY                                                │
    │  "Growing skill and competence — getting better"        │
    ├─────────────────────────────────────────────────────────┤
    │  DISCOVERY                                              │
    │  "Finding something new — exploration, wonder"          │
    └─────────────────────────────────────────────────────────┘

Concept: "A roguelike dungeon crawler where each run
          teaches you patterns through failure"
""")

    print_arrow()
    pause()

    # STAGE 2
    print_subheader("STAGE 2: RULES")

    analyser = QualityAnalyser()
    analysis = analyser.analyse(["tension", "mastery", "discovery"])

    # Load similarities for display
    data_path = Path(__file__).parent / "data" / "quality_similarities.json"
    with open(data_path) as f:
        data = json.load(f)
    similarities = data["similarities"]
    thresholds = data["thresholds"]

    print("Analysing the 3 pairs:\n")

    pairs = [
        ("discovery", "mastery"),
        ("discovery", "tension"),
        ("mastery", "tension"),
    ]

    for q1, q2 in pairs:
        key = "+".join(sorted([q1, q2]))
        sim = similarities.get(key, 0.0)

        if sim >= thresholds["synergy"]:
            rel = "SYNERGY ✓"
        elif sim < thresholds["tension"]:
            rel = "TENSION ⚡"
        else:
            rel = "NEUTRAL ○"

        print(f"    {q1} + {q2}")
        print(f"    Similarity: {sim:.4f} → {rel}")
        print()
        time.sleep(0.3)

    print(f"""Counting relationships:
    Tensions:  {len(analysis.tensions)}
    Synergies: {len(analysis.synergies)}
    Neutrals:  {len(analysis.neutrals)}

Shape classification: {analysis.shape.upper()}
"{analysis.shape_description}"
""")

    print_arrow()
    pause()

    # STAGE 3
    print_subheader("STAGE 3: LANGUAGE")

    print("""The narrator receives:

    Qualities: tension, mastery, discovery
    Shape: {shape}
    Tensions: {tensions}
    Synergies: {synergies}
    Concept: "A roguelike dungeon crawler..."

And generates an explanation...
""".format(
        shape=analysis.shape,
        tensions=len(analysis.tensions),
        synergies=len(analysis.synergies),
    ))

    # Try to find a pre-generated narrative for this combination
    flow_narrative = get_narrative_for_qualities(["tension", "mastery", "discovery"], STUDY_NARRATIVES)

    # If not found, get any narrative with similar shape
    if not flow_narrative:
        flow_narrative = get_random_narrative(STUDY_NARRATIVES, shape=analysis.shape)

    if flow_narrative:
        explanation = flow_narrative["explanation"]
        implications = flow_narrative["implications"]

        # Wrap explanation for display
        wrapped_explanation = ""
        line = ""
        for word in explanation.split():
            if len(line) + len(word) + 1 > 55:
                wrapped_explanation += line.strip() + "\n"
                line = word + " "
            else:
                line += word + " "
        wrapped_explanation += line.strip()

        impl_text = "\n".join(f"- {imp[:55]}..." if len(imp) > 58 else f"- {imp}" for imp in implications[:3])

        print_box(f"""{wrapped_explanation[:600]}{'...' if len(wrapped_explanation) > 600 else ''}

Design implications:
{impl_text}
""", title="Real Narrator Output")
    else:
        print_box("""[Pre-generated narratives not found]

The narrator would generate a 4-8 sentence explanation
of what this combination means for the specific game,
plus 2-3 design implications.
""", title="Narrator Output")

    print_arrow()

    print("""
    ╔══════════════════════════════════════════════════════╗
    ║                    COMPLETE                          ║
    ║                                                      ║
    ║  Input:     3 qualities + concept                    ║
    ║  Analysis:  Deterministic relationship analysis      ║
    ║  Output:    Shape classification + narrative         ║
    ╚══════════════════════════════════════════════════════╝
""")

    pause()


# =============================================================================
# INTERACTIVE EXPLORER
# =============================================================================

def interactive_explorer():
    """Let users explore quality combinations."""
    clear_screen()
    print_header("INTERACTIVE EXPLORER")

    print("Try your own quality combinations.\n")

    # Show quality list
    print("Available qualities:")
    quality_list = list(QUALITIES.keys())
    for i, name in enumerate(quality_list):
        print(f"  {i + 1:2}. {name}")

    print()

    analyser = QualityAnalyser()

    # Load similarities for display
    data_path = Path(__file__).parent / "data" / "quality_similarities.json"
    with open(data_path) as f:
        data = json.load(f)
    similarities = data["similarities"]
    thresholds = data["thresholds"]

    while True:
        print("\nEnter 3 quality numbers (e.g., '4 8 9') or 'q' to quit:")
        choice = input("> ").strip().lower()

        if choice == 'q':
            break

        try:
            nums = [int(x) for x in choice.split()]
            if len(nums) != 3:
                print("Please enter exactly 3 numbers.")
                continue

            selected = [quality_list[n - 1] for n in nums]
        except (ValueError, IndexError):
            print("Invalid input. Use numbers 1-12 separated by spaces.")
            continue

        print(f"\nAnalysing: {selected[0]} + {selected[1]} + {selected[2]}\n")

        try:
            analysis = analyser.analyse(selected)
        except ValueError as e:
            print(f"Error: {e}")
            continue

        # Show pairs
        sorted_q = sorted(selected)
        pairs = [
            (sorted_q[0], sorted_q[1]),
            (sorted_q[0], sorted_q[2]),
            (sorted_q[1], sorted_q[2]),
        ]

        for q1, q2 in pairs:
            key = "+".join(sorted([q1, q2]))
            sim = similarities.get(key, 0.0)

            if sim >= thresholds["synergy"]:
                rel = "SYNERGY"
                symbol = "↔"
            elif sim < thresholds["tension"]:
                rel = "TENSION"
                symbol = "⇋"
            else:
                rel = "NEUTRAL"
                symbol = "—"

            print(f"  {q1} {symbol} {q2}: {sim:.4f} → {rel}")

        print(f"\n  SHAPE: {analysis.shape.upper()}")
        print(f"  {analysis.shape_description}")

        # Check for pre-generated narrative
        narrative = get_narrative_for_qualities(selected, STUDY_NARRATIVES)
        if narrative:
            print("\n  ─── Pre-generated Narrative Available ───")
            print(f"\n  Context: \"{narrative['context'][:60]}...\"")
            explanation = narrative["explanation"]
            # Show first ~200 chars of explanation
            print(f"\n  {explanation[:200]}...")
            print("\n  (Full narrative stored in data/study_narratives.json)")
        else:
            print("\n  [No pre-generated narrative for this combination]")


# =============================================================================
# MAIN
# =============================================================================

def show_help():
    """Show usage information."""
    print("""
Play Shape Diagnostic — Study Module

Usage:
    python study.py              Full walkthrough (recommended first time)
    python study.py --all        Same as above
    python study.py --stage 1    Stage 1: The 12 qualities
    python study.py --stage 2    Stage 2: Relationship rules
    python study.py --stage 3    Stage 3: AI narrator
    python study.py --flow       Complete flow example
    python study.py --explore    Interactive quality explorer
    python study.py --help       Show this message

This module is designed for DESIGN STUDENTS — it explains
the WHY, not just the WHAT.
""")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or "--all" in args:
        show_introduction()
        show_stage_1()
        show_stage_2()
        show_stage_3()
        show_full_flow()

        print_header("WHAT NEXT?")
        print("""You've seen how the system works.

To explore more:
    python study.py --explore    Try your own combinations
    python study.py --stage 2    Deep dive on rules
    python study.py --flow       See another full example

To use the actual tool:
    uvicorn backend.main:app --reload
    Then open http://localhost:8000
""")

    elif "--help" in args or "-h" in args:
        show_help()

    elif "--stage" in args:
        try:
            idx = args.index("--stage")
            stage = int(args[idx + 1])
        except (ValueError, IndexError):
            print("Usage: python study.py --stage [1|2|3]")
            return

        if stage == 1:
            show_stage_1()
        elif stage == 2:
            show_stage_2()
        elif stage == 3:
            show_stage_3()
        else:
            print("Stage must be 1, 2, or 3")

    elif "--flow" in args:
        show_full_flow()

    elif "--explore" in args:
        interactive_explorer()

    else:
        show_help()


if __name__ == "__main__":
    main()
