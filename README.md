# Dune AI Text Adventure

Python text adventure set on Arrakis with AI-generated NPCs, vendors, locations, dialogue, and character-specific quests.

## Features
- Play as major Dune characters (Paul, Jessica, Stilgar, Chani, Gurney, Duncan, Irulan).
- Start in Arrakeen (main city), including an intricate palace zone network.
- `look`, `move`, `travel`, `people`, `talk`, `do`, `rideworm`, `quests`, `map`, and more.
- Dynamic generation of people, places, shops, and adventures via OpenAI API.
- NPC dialogue constrained to in-world behavior and knowledge.
- Conversation mode: choose a character once with `talk <number>` or `talk <name>`, then type naturally until `leave`.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your OpenAI key:
   - PowerShell:
     ```powershell
     $env:OPENAI_API_KEY="your_key_here"
     ```

## Run
```bash
python game.py
```

## Notes
- Without `OPENAI_API_KEY`, the game still runs with basic fallback content.
- Dynamic travel to brand-new locations requires OpenAI API enabled.
