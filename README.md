# Dune Sandbox

Terminal-first exploration game set on Arrakis from Paul's perspective.

The game now centers on a handcrafted Arrakis sandbox with:

- authored districts, compounds, desert routes, and hidden regions
- canon and recurring non-canon NPCs with memory and personal troubles
- rumors, favors, small missions, and faction tension
- dynamic AI-generated regions that can become permanent major expansions
- richer terminal presentation with `rich`
- save and autosave support

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Optional environment variables:

```env
OPENAI_API_KEY=your_key_here
OPENAI_TEXT_MODEL=gpt-4.1-mini
TYPEWRITER_DELAY=0.005
REDUCED_MOTION=false
```

## Run

```bash
python game.py
```

or:

```bash
python -m dune_game
```

## Commands

- `look`
- `inspect <thing>`
- `listen`
- `people`
- `talk <name>`
- `ask <name> about <topic>`
- `move <place>`
- `travel <place>`
- `where`
- `map`
- `rumors`
- `journal`
- `save`
- `load`
- `help`
- `quit`

## Notes

- The world stays playable without `OPENAI_API_KEY` using local fallback narration and fallback dynamic region generation.
- Dynamic regions, NPC memory, rumors, missions, and discovered locations persist in saves.
