# Dune: Arrakis

Dune: Arrakis is a terminal-first exploration game set on Arrakis from Paul's perspective.

Move through markets, palace courts, hidden routes, worker districts, and the open desert while dealing with rumor, suspicion, survival, and the pressure of being Paul Atreides. The game aims for a tone closer to the novel than to a conventional RPG: more political, more watchful, and more concerned with water, power, secrecy, and consequence.

If you want a Dune game that feels exploratory rather than railroaded, this is the pitch: walk the world, listen carefully, talk to people who have their own burdens, and let Arrakis open outward into stranger and larger regions over time.

Current highlights:

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
- `hint`
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
- `menu`
- `save`
- `load`
- `help`
- `quit`

## Notes

- The world stays playable without `OPENAI_API_KEY` using local fallback narration and fallback dynamic region generation.
- Dynamic regions, NPC memory, rumors, missions, and discovered locations persist in saves.
