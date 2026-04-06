from __future__ import annotations

import json
import os
import random
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from openai import OpenAI


CHARACTER_ARCHETYPES: Dict[str, Dict[str, str]] = {
    "paul_atreides": {
        "display": "Paul Atreides",
        "title": "Duke's Heir",
        "style": "Perceptive, strategic, burdened by prescience.",
    },
    "lady_jessica": {
        "display": "Lady Jessica",
        "title": "Bene Gesserit Adept",
        "style": "Composed, sharp, politically and psychologically adept.",
    },
    "stilgar": {
        "display": "Stilgar",
        "title": "Naib of Sietch Tabr",
        "style": "Direct, honor-bound, pragmatic Fremen leadership.",
    },
    "chani": {
        "display": "Chani",
        "title": "Fremen Scout",
        "style": "Observant, fierce, grounded in desert survival.",
    },
    "gurney_halleck": {
        "display": "Gurney Halleck",
        "title": "Warmaster and Troubadour",
        "style": "Gruff, loyal, tactical with dry humor.",
    },
    "duncan_idaho": {
        "display": "Duncan Idaho",
        "title": "Swordmaster",
        "style": "Bold, honorable, adaptable under pressure.",
    },
    "princess_irulan": {
        "display": "Princess Irulan",
        "title": "Imperial Scholar",
        "style": "Analytical, diplomatic, politically precise.",
    },
}


@dataclass
class Zone:
    name: str
    summary: str
    kind: str
    neighbors: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    shops: List[str] = field(default_factory=list)


@dataclass
class NPC:
    npc_id: str
    name: str
    role: str
    faction: str
    location: str
    personality: str
    secret: str
    inventory_hint: str
    chat_history: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class Shop:
    shop_id: str
    name: str
    owner: str
    goods: List[str]
    location: str
    flavor: str


@dataclass
class Quest:
    title: str
    objective: str
    steps: List[str]
    reward: str
    status: str = "active"
    progress: int = 0


@dataclass
class Player:
    archetype_key: str
    display_name: str
    title: str
    style: str
    location: str = "arrakeen_gate"
    inventory: List[str] = field(default_factory=lambda: ["stillsuit", "crysknife"])
    quests: List[Quest] = field(default_factory=list)
    discovered_locations: List[str] = field(default_factory=lambda: ["arrakeen_gate"])
    riding_worm: bool = False


class AIWorld:
    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @property
    def enabled(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))

    def _chat_json(self, system: str, user: str) -> Dict:
        if not self.enabled:
            return {}
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.9,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            raw = (response.choices[0].message.content or "").strip()
            return json.loads(raw) if raw else {}
        except Exception:
            return {}

    def _chat_text(self, system: str, user: str, temperature: float = 0.8) -> str:
        if not self.enabled:
            return ""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return (response.choices[0].message.content or "").strip()
        except Exception:
            return ""

    def generate_zone(
        self, zone_name: str, planet_context: str, neighbor_hint: str
    ) -> Optional[Dict]:
        system = (
            "You generate concise in-world locations for a Dune universe text adventure. "
            "Stay aligned with canonical tone and constraints: pre-computer feudal culture, "
            "Arrakis ecology, spice economy, Imperium politics. Never mention modern Earth tech. "
            "Return strict JSON."
        )
        user = (
            f"Generate a new location named '{zone_name}' on Arrakis.\n"
            f"Context: {planet_context}\n"
            f"Neighbor hint: {neighbor_hint}\n"
            "Return JSON with keys: name, summary, kind, neighbors (array of short location keys)."
        )
        data = self._chat_json(system, user)
        return data or None

    def generate_npc(self, location_name: str, player_role: str) -> Optional[Dict]:
        system = (
            "You create NPCs for a Dune universe RPG. Keep names and roles believable in-universe. "
            "No anachronisms. Keep each field compact. Return strict JSON."
        )
        user = (
            f"Create one NPC currently in {location_name}. "
            f"The player is {player_role}. "
            "Return JSON keys: name, role, faction, personality, secret, inventory_hint."
        )
        data = self._chat_json(system, user)
        return data or None

    def generate_shop(self, location_name: str) -> Optional[Dict]:
        system = (
            "You create in-universe shops/vendors for Arrakis in Dune. "
            "Goods must fit setting. Return strict JSON."
        )
        user = (
            f"Create one vendor or shop in {location_name}. "
            "Return JSON keys: name, owner, goods (array of 3-5), flavor."
        )
        data = self._chat_json(system, user)
        return data or None

    def character_dialogue(
        self,
        npc: NPC,
        player: Player,
        location: Zone,
        player_message: str,
        chat_history: List[Tuple[str, str]],
    ) -> str:
        system = (
            "You roleplay as an NPC in a Dune-universe game. "
            "Stay strictly in character and in setting knowledge. "
            "Never reveal being an AI. "
            "Never mention events/characters outside this world. "
            "Reply with 3-7 lines max, rich in atmosphere and intent."
        )
        history_blob = "\n".join([f"Player: {p}\nNPC: {n}" for p, n in chat_history[-5:]])
        user = (
            f"NPC profile:\n"
            f"- Name: {npc.name}\n"
            f"- Role: {npc.role}\n"
            f"- Faction: {npc.faction}\n"
            f"- Personality: {npc.personality}\n"
            f"- Secret: {npc.secret}\n\n"
            f"Scene:\n"
            f"- Player is {player.display_name} ({player.title})\n"
            f"- Location: {location.name} - {location.summary}\n\n"
            f"Recent exchange:\n{history_blob if history_blob else '(none)'}\n\n"
            f"Player says: {player_message}\n"
            "Respond as the NPC."
        )
        text = self._chat_text(system, user, temperature=0.95)
        return text or f"{npc.name} studies you in silence, then gives a cautious nod."

    def generate_quest(self, player: Player, location: Zone) -> Optional[Dict]:
        system = (
            "You generate character-specific quests for a Dune RPG. "
            "Quest should align with lore, politics, and ecology of Arrakis. Return strict JSON."
        )
        user = (
            f"Player: {player.display_name} ({player.title}); style: {player.style}\n"
            f"Current location: {location.name}\n"
            "Return JSON with keys: title, objective, steps (array of 2-4), reward."
        )
        data = self._chat_json(system, user)
        return data or None

    def describe_location(
        self,
        player: Player,
        location: Zone,
        npcs: List[NPC],
        shops: List[Shop],
        active_quest: Optional[Quest],
        riding_worm: bool,
    ) -> str:
        system = (
            "You write immersive location descriptions for a Dune text adventure. "
            "Stay strictly within the tone and knowledge of the Dune novels. "
            "Focus on sensory detail, political tension, water discipline, spice culture, and survival. "
            "Write 4-6 sentences. Do not use bullet points."
        )
        user = (
            f"Player: {player.display_name} ({player.title})\n"
            f"Location: {location.name}\n"
            f"Location summary: {location.summary}\n"
            f"Location type: {location.kind}\n"
            f"Nearby people: {', '.join(f'{npc.name} ({npc.role})' for npc in npcs) or 'none'}\n"
            f"Nearby vendors: {', '.join(shop.name for shop in shops) or 'none'}\n"
            f"Active quest: {active_quest.title if active_quest else 'none'}\n"
            f"Riding sandworm: {'yes' if riding_worm else 'no'}\n"
            "Describe what the player notices when they stop and look carefully."
        )
        return self._chat_text(system, user, temperature=0.95)

    def resolve_action(
        self, player: Player, location: Zone, action_text: str, active_quest: Optional[Quest]
    ) -> str:
        system = (
            "You narrate outcomes for player actions in a Dune text adventure. "
            "Stay grounded in setting logic and physical constraints. Keep to 2-6 sentences."
        )
        user = (
            f"Player: {player.display_name} ({player.title}).\n"
            f"Location: {location.name} - {location.summary}\n"
            f"Inventory: {', '.join(player.inventory)}\n"
            f"Active quest: {active_quest.title if active_quest else 'none'}\n"
            f"Attempted action: {action_text}\n"
            "Narrate plausible result, including consequences."
        )
        text = self._chat_text(system, user, temperature=0.85)
        return text or "The wind shifts over the stone and sand, and your move changes the balance of the moment."


class DuneGame:
    def __init__(self) -> None:
        self.ai = AIWorld()
        self.zones: Dict[str, Zone] = {}
        self.npcs: Dict[str, NPC] = {}
        self.shops: Dict[str, Shop] = {}
        self.player: Optional[Player] = None
        self.active_conversation_npc_id: Optional[str] = None
        self.should_exit = False
        self._seed_world()

    def _seed_world(self) -> None:
        self.zones["arrakeen_gate"] = Zone(
            name="Arrakeen Gate",
            summary="A fortified stone gate where hawks circle above guards and spice wagons.",
            kind="city",
            neighbors=["market_quarter", "palace_outer_court", "caravan_square"],
        )
        self.zones["market_quarter"] = Zone(
            name="Market Quarter",
            summary="Crowded stalls of water merchants, stillsuit fitters, spice factors, and rumor sellers.",
            kind="city",
            neighbors=["arrakeen_gate", "caravan_square", "sietch_envoy_house"],
        )
        self.zones["caravan_square"] = Zone(
            name="Caravan Square",
            summary="Caravans unload under watchful banners while contracts are whispered under awnings.",
            kind="city",
            neighbors=["arrakeen_gate", "market_quarter", "desert_edge"],
        )
        self.zones["sietch_envoy_house"] = Zone(
            name="Sietch Envoy House",
            summary="A quiet diplomatic compound where Fremen envoys watch and listen.",
            kind="city",
            neighbors=["market_quarter", "palace_outer_court"],
        )
        self.zones["palace_outer_court"] = Zone(
            name="Palace Outer Court",
            summary="White stone courtyards with carved channels for reclaimed moisture.",
            kind="palace",
            neighbors=["arrakeen_gate", "sietch_envoy_house", "palace_hall_of_banners"],
        )
        self.zones["palace_hall_of_banners"] = Zone(
            name="Hall of Banners",
            summary="Long vaulted hall lined with Atreides, Imperial, and household standards.",
            kind="palace",
            neighbors=["palace_outer_court", "palace_war_room", "palace_hidden_gallery"],
        )
        self.zones["palace_war_room"] = Zone(
            name="Palace War Room",
            summary="An intricate command chamber of relief maps, intelligence ledgers, and guarded strategy alcoves.",
            kind="palace",
            neighbors=["palace_hall_of_banners", "palace_water_garden", "palace_scriptorium"],
        )
        self.zones["palace_hidden_gallery"] = Zone(
            name="Hidden Gallery",
            summary="A concealed overlook behind lattice stone for private observation of the court.",
            kind="palace",
            neighbors=["palace_hall_of_banners", "palace_scriptorium"],
        )
        self.zones["palace_scriptorium"] = Zone(
            name="Palace Scriptorium",
            summary="Shelves of coded reports, genealogies, and sealed Imperial correspondence.",
            kind="palace",
            neighbors=["palace_war_room", "palace_hidden_gallery", "palace_private_chamber"],
        )
        self.zones["palace_private_chamber"] = Zone(
            name="Private Chamber",
            summary="A meticulously arranged chamber where statecraft and private burdens intersect.",
            kind="palace",
            neighbors=["palace_scriptorium", "palace_water_garden"],
        )
        self.zones["palace_water_garden"] = Zone(
            name="Palace Water Garden",
            summary="An astonishing and political display of pools and shade trees in the heart of the dry world.",
            kind="palace",
            neighbors=["palace_war_room", "palace_private_chamber", "desert_edge"],
        )
        self.zones["desert_edge"] = Zone(
            name="Desert Edge",
            summary="The last hard stone before open erg; wind combs the dunes into knife ridges.",
            kind="desert",
            neighbors=["caravan_square", "palace_water_garden", "deep_desert"],
        )
        self.zones["deep_desert"] = Zone(
            name="Deep Desert",
            summary="Vast dunes and open sky, where every step risks drawing a maker.",
            kind="desert",
            neighbors=["desert_edge", "sietch_tabr_route"],
        )
        self.zones["sietch_tabr_route"] = Zone(
            name="Sietch Route",
            summary="A concealed path of rock outcrops and coded Fremen markers.",
            kind="desert",
            neighbors=["deep_desert"],
        )

    def run(self) -> None:
        self._banner()
        self._choose_character()
        self._ensure_zone_population(self.player.location)
        print(self._render_location(detailed=True))

        while True:
            cmd = input(f"\n{self._prompt()}").strip()
            if not cmd:
                continue
            if self.active_conversation_npc_id:
                if cmd.lower() in {"quit", "exit"}:
                    print("Leave the conversation first with `leave`, or use `/exit` to quit the game.")
                    continue
                print(self._handle_conversation_input(cmd))
                if self.should_exit:
                    break
                continue
            if cmd.lower() in {"quit", "exit"}:
                print("The sands remember your passage.")
                break
            print(self._handle_command(cmd))

    def _banner(self) -> None:
        print(
            textwrap.dedent(
                """
                =========================================================
                DUNE: SANDS OF ARRAKIS (AI TEXT ADVENTURE)
                Commands: help, look, move <place>, go <place>, travel <place>,
                people, talk <name|number>, do <action>, quests, rideworm,
                character, inventory, map, exit
                =========================================================
                """
            ).strip()
        )
        if not self.ai.enabled:
            print(
                "\n[Notice] OPENAI_API_KEY is not set. The game runs with minimal fallback narration.\n"
            )

    def _choose_character(self) -> None:
        print("\nChoose your character:")
        keys = list(CHARACTER_ARCHETYPES.keys())
        for idx, key in enumerate(keys, start=1):
            c = CHARACTER_ARCHETYPES[key]
            print(f"{idx}. {c['display']} - {c['title']}")

        while True:
            pick = input("\nNumber: ").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(keys):
                key = keys[int(pick) - 1]
                c = CHARACTER_ARCHETYPES[key]
                self.player = Player(
                    archetype_key=key,
                    display_name=c["display"],
                    title=c["title"],
                    style=c["style"],
                )
                self._assign_initial_quest()
                return
            print("Choose a valid number.")

    def _assign_initial_quest(self) -> None:
        assert self.player is not None
        location = self.zones[self.player.location]
        generated = self.ai.generate_quest(self.player, location)
        if generated:
            quest = Quest(
                title=generated.get("title", "Shadows Over Arrakeen"),
                objective=generated.get("objective", "Discover a hidden threat in the city."),
                steps=generated.get(
                    "steps",
                    [
                        "Gather rumors in the market quarter.",
                        "Inspect palace intelligence logs.",
                        "Confront the orchestrator.",
                    ],
                ),
                reward=generated.get("reward", "Influence with a major faction."),
            )
        else:
            quest = Quest(
                title="Whispers in Arrakeen",
                objective="Identify a smuggling line threatening Atreides control.",
                steps=[
                    "Question caravan factors in Caravan Square.",
                    "Secure proof in the Palace Scriptorium.",
                    "Deliver findings to a trusted ally.",
                ],
                reward="Access to sensitive city routes.",
            )
        self.player.quests.append(quest)

    def _active_quest(self) -> Optional[Quest]:
        assert self.player is not None
        for q in self.player.quests:
            if q.status == "active":
                return q
        return None

    def _ensure_zone_population(self, zone_id: str) -> None:
        assert self.player is not None
        zone = self.zones[zone_id]

        if not zone.npcs:
            for _ in range(2):
                npc = self._create_npc_for_zone(zone_id)
                zone.npcs.append(npc.npc_id)

        if not zone.shops and zone.kind in {"city", "palace"}:
            shop = self._create_shop_for_zone(zone_id)
            zone.shops.append(shop.shop_id)

    def _create_npc_for_zone(self, zone_id: str) -> NPC:
        assert self.player is not None
        zone = self.zones[zone_id]
        npc_data = self.ai.generate_npc(zone.name, self.player.display_name) or {}
        name = npc_data.get("name") or random.choice(
            ["Harah", "Otheym", "Yueh's Clerk", "Esmar Tuek", "Kynes' Aide", "Rafik"]
        )
        name = self._unique_npc_name(zone_id, name)
        role = npc_data.get("role", "Local Operative")
        faction = npc_data.get("faction", "Neutral")
        personality = npc_data.get("personality", "Guarded and practical")
        secret = npc_data.get("secret", "Knows of hidden movement between factions.")
        inventory_hint = npc_data.get("inventory_hint", "ciphers, spice satchel")
        npc_id = self._slug(f"{zone_id}_{name}_{len(self.npcs)}")
        npc = NPC(
            npc_id=npc_id,
            name=name,
            role=role,
            faction=faction,
            location=zone_id,
            personality=personality,
            secret=secret,
            inventory_hint=inventory_hint,
        )
        self.npcs[npc_id] = npc
        return npc

    def _create_shop_for_zone(self, zone_id: str) -> Shop:
        zone = self.zones[zone_id]
        shop_data = self.ai.generate_shop(zone.name) or {}
        name = shop_data.get("name", "Sandwind Outfitters")
        owner = shop_data.get("owner", "Master Ghedi")
        goods = shop_data.get("goods", ["stillsuit patches", "water rings", "desert hooks"])
        flavor = shop_data.get("flavor", "A cool alcove where every drop and tool is counted.")
        shop_id = self._slug(f"{zone_id}_{name}_{len(self.shops)}")
        shop = Shop(shop_id=shop_id, name=name, owner=owner, goods=goods, location=zone_id, flavor=flavor)
        self.shops[shop_id] = shop
        return shop

    def _render_location(self, detailed: bool = False) -> str:
        assert self.player is not None
        zone = self.zones[self.player.location]
        self._ensure_zone_population(self.player.location)
        npcs = self._zone_npcs(zone)
        shops = [self.shops[sid] for sid in zone.shops if sid in self.shops]
        lines = [f"\n[{zone.name}]"]
        if detailed:
            lines.append(self._scene_description(zone, npcs, shops))
        else:
            lines.append(zone.summary)
        lines.append("Paths: " + ", ".join(self.zones[n].name for n in zone.neighbors if n in self.zones))
        if npcs:
            lines.append("People:")
            for idx, npc in enumerate(npcs, start=1):
                lines.append(f"  [{idx}] {npc.name} - {npc.role}")
        if shops:
            shop_list = [shop.name for shop in shops]
            lines.append("Vendors: " + ", ".join(shop_list))
        if self.player.riding_worm:
            lines.append("Status: You are mounted on a sandworm.")
        if npcs:
            lines.append("Talk: use `talk <number>` or `talk <name>`.")
        return "\n".join(lines)

    def _handle_command(self, cmd: str) -> str:
        assert self.player is not None
        lower = cmd.lower().strip()
        if lower == "help":
            return self._help()
        if lower == "look":
            return self._render_location(detailed=True)
        if lower == "character":
            return f"{self.player.display_name} - {self.player.title}\nStyle: {self.player.style}"
        if lower == "inventory":
            return "Inventory: " + ", ".join(self.player.inventory)
        if lower == "map":
            return self._map()
        if lower == "people":
            return self._people_text()
        if lower in {"quest", "quests"}:
            return self._quest_text()
        if lower.startswith("move ") or lower.startswith("go "):
            _, _, target = cmd.partition(" ")
            return self._move(target.strip())
        if lower.startswith("travel "):
            return self._travel_anywhere(cmd[7:].strip())
        if lower == "talk":
            return self._talk("")
        if lower.startswith("talk "):
            return self._talk(cmd[5:].strip())
        if lower.startswith("do "):
            return self._do_action(cmd[3:].strip())
        if lower == "rideworm":
            return self._ride_worm()
        return "Unknown command. Type `help`."

    def _help(self) -> str:
        return textwrap.dedent(
            """
            Commands:
            - look: Give a fuller, more immersive description of your current area.
            - people: List nearby characters with numbers for quick selection.
            - move <place> / go <place>: Move to connected locations.
            - travel <place>: Attempt long-range travel anywhere on Arrakis.
            - talk: Show nearby people and conversation options.
            - talk <name|number>: Start a conversation mode.
            - talk <name|number> <message>: Send one line directly in the old format.
            - do <action>: Attempt a free-form action.
            - rideworm: Summon and ride a sandworm in the open desert.
            - quest / quests: Show active and completed adventures.
            - In conversation mode, type your line directly.
            - Use `leave` to end a conversation, or `/help`, `/look`, `/move ...` for normal commands.
            - character, inventory, map, help, exit
            """
        ).strip()

    def _map(self) -> str:
        assert self.player is not None
        discovered = [self.zones[z].name for z in self.player.discovered_locations if z in self.zones]
        return "Discovered locations: " + ", ".join(discovered)

    def _quest_text(self) -> str:
        assert self.player is not None
        if not self.player.quests:
            return "No quests."
        out: List[str] = []
        for q in self.player.quests:
            step_text = q.steps[q.progress] if q.progress < len(q.steps) else "All steps complete."
            out.append(
                f"- {q.title} [{q.status}]\n"
                f"  Objective: {q.objective}\n"
                f"  Current Step: {step_text}\n"
                f"  Reward: {q.reward}"
            )
        return "\n".join(out)

    def _find_zone_by_name(self, raw: str) -> Optional[str]:
        raw = raw.lower().strip()
        if raw in self.zones:
            return raw
        for zone_id, zone in self.zones.items():
            if raw == zone.name.lower():
                return zone_id
            if raw in zone.name.lower():
                return zone_id
        return None

    def _move(self, target: str) -> str:
        assert self.player is not None
        if not target:
            return "Move where?"
        current = self.zones[self.player.location]
        target_id = self._find_zone_by_name(target)
        if not target_id:
            return "No such nearby place."
        if target_id not in current.neighbors:
            return f"You cannot move directly to {self.zones[target_id].name} from here."

        self.active_conversation_npc_id = None
        self.player.location = target_id
        if target_id not in self.player.discovered_locations:
            self.player.discovered_locations.append(target_id)
        self.player.riding_worm = False if self.zones[target_id].kind != "desert" else self.player.riding_worm
        self._ensure_zone_population(target_id)
        self._maybe_progress_quest("move")
        return self._render_location(detailed=True)

    def _travel_anywhere(self, destination: str) -> str:
        assert self.player is not None
        if not destination:
            return "Travel where on Arrakis?"

        existing = self._find_zone_by_name(destination)
        if existing:
            self.active_conversation_npc_id = None
            self.player.location = existing
            if existing not in self.player.discovered_locations:
                self.player.discovered_locations.append(existing)
            self._ensure_zone_population(existing)
            self._maybe_progress_quest("travel")
            return f"You complete a long route across Arrakis.\n{self._render_location(detailed=True)}"

        if not self.ai.enabled:
            return (
                "That location is unknown and dynamic generation needs OPENAI_API_KEY. "
                "Try traveling to a known zone first."
            )

        made = self.ai.generate_zone(
            zone_name=destination,
            planet_context=(
                "Main city Arrakeen, nearby deep desert, sietch routes, spice operations, "
                "and political compounds."
            ),
            neighbor_hint=self.zones[self.player.location].name,
        )
        if not made:
            return "The route is obscured by storm signs. Try again."

        zone_id = self._slug(made.get("name", destination))
        neighbor_guess = made.get("neighbors", [])
        neighbors = []
        for n in neighbor_guess:
            found = self._find_zone_by_name(str(n))
            if found:
                neighbors.append(found)
        if self.player.location not in neighbors:
            neighbors.append(self.player.location)

        new_zone = Zone(
            name=made.get("name", destination.title()),
            summary=made.get("summary", "A newly charted sector of Arrakis."),
            kind=made.get("kind", "desert"),
            neighbors=list(dict.fromkeys(neighbors)),
        )
        self.zones[zone_id] = new_zone
        for n in new_zone.neighbors:
            if zone_id not in self.zones[n].neighbors:
                self.zones[n].neighbors.append(zone_id)

        self.active_conversation_npc_id = None
        self.player.location = zone_id
        self.player.discovered_locations.append(zone_id)
        self._ensure_zone_population(zone_id)
        self._maybe_progress_quest("travel")
        return f"New region discovered.\n{self._render_location(detailed=True)}"

    def _talk(self, payload: str) -> str:
        assert self.player is not None
        if not payload:
            return self._people_text()

        npc, message = self._parse_talk_target(payload)
        if not npc:
            return self._people_text("No one by that name or number is here.")

        if message:
            return self._say_to_npc(npc, message)

        self.active_conversation_npc_id = npc.npc_id
        opener = self.ai.character_dialogue(
            npc,
            self.player,
            self.zones[self.player.location],
            "I approach and ask to speak with you.",
            npc.chat_history,
        )
        npc.chat_history.append(("I approach and ask to speak with you.", opener))
        return (
            f"You turn to {npc.name}, {npc.role}.\n"
            f"{npc.name}: {opener}\n"
            "Type your line directly. Use `leave` to end the conversation."
        )

    def _do_action(self, action_text: str) -> str:
        assert self.player is not None
        if not action_text:
            return "Do what?"
        zone = self.zones[self.player.location]
        result = self.ai.resolve_action(self.player, zone, action_text, self._active_quest())
        self._maybe_progress_quest("do")
        return result

    def _ride_worm(self) -> str:
        assert self.player is not None
        zone = self.zones[self.player.location]
        if zone.kind != "desert":
            return "You need open desert to call a maker."
        if "maker hooks" not in self.player.inventory:
            self.player.inventory.append("maker hooks")
        self.player.riding_worm = True
        self._maybe_progress_quest("rideworm")
        return (
            "You plant the hooks and feel the immense body turn beneath you. "
            "The maker rises and you ride the dunes under a burning sky."
        )

    def _maybe_progress_quest(self, trigger: str) -> None:
        quest = self._active_quest()
        if not quest:
            return
        # Lightweight progression model: meaningful actions may advance quest.
        if trigger in {"talk", "do", "travel", "rideworm", "move"} and random.random() < 0.35:
            quest.progress += 1
            if quest.progress >= len(quest.steps):
                quest.status = "completed"

    def _prompt(self) -> str:
        npc = self._current_conversation_npc()
        if npc:
            return f"{npc.name}> "
        return "> "

    def _zone_npcs(self, zone: Zone) -> List[NPC]:
        return [self.npcs[nid] for nid in zone.npcs if nid in self.npcs]

    def _people_text(self, intro: Optional[str] = None) -> str:
        zone = self.zones[self.player.location]
        npcs = self._zone_npcs(zone)
        lines: List[str] = []
        if intro:
            lines.append(intro)
        if not npcs:
            lines.append("No one is available to speak with here.")
            return "\n".join(lines)
        lines.append(f"People in {zone.name}:")
        for idx, npc in enumerate(npcs, start=1):
            lines.append(f"  [{idx}] {npc.name} - {npc.role} ({npc.faction})")
        lines.append("Use `talk <number>` or `talk <name>` to start speaking.")
        return "\n".join(lines)

    def _parse_talk_target(self, payload: str) -> Tuple[Optional[NPC], Optional[str]]:
        payload = payload.strip()
        zone = self.zones[self.player.location]
        npcs = self._zone_npcs(zone)
        if not payload or not npcs:
            return None, None

        if payload.isdigit():
            idx = int(payload) - 1
            if 0 <= idx < len(npcs):
                return npcs[idx], None
            return None, None

        parts = payload.split(" ", 1)
        if parts[0].isdigit():
            idx = int(parts[0]) - 1
            if 0 <= idx < len(npcs):
                message = parts[1].strip() if len(parts) > 1 else None
                return npcs[idx], message
            return None, None

        lowered = payload.lower()
        for npc in npcs:
            npc_name = npc.name.lower()
            if lowered == npc_name:
                return npc, None
            if lowered.startswith(npc_name + " "):
                return npc, payload[len(npc.name) :].strip() or None

        for npc in npcs:
            if lowered in npc.name.lower():
                return npc, None

        return None, None

    def _current_conversation_npc(self) -> Optional[NPC]:
        if not self.active_conversation_npc_id:
            return None
        npc = self.npcs.get(self.active_conversation_npc_id)
        if not npc:
            self.active_conversation_npc_id = None
            return None
        if npc.location != self.player.location:
            self.active_conversation_npc_id = None
            return None
        return npc

    def _handle_conversation_input(self, cmd: str) -> str:
        npc = self._current_conversation_npc()
        if not npc:
            return "The conversation has ended."

        lowered = cmd.lower().strip()
        if lowered in {"leave", "bye", "goodbye", "back"}:
            self.active_conversation_npc_id = None
            return f"You step away from {npc.name}."

        if cmd.startswith("/"):
            routed = cmd[1:].strip()
            if not routed:
                return "Use `/help` for commands, or type your line directly."
            if routed.lower() in {"exit", "quit"}:
                self.active_conversation_npc_id = None
                self.should_exit = True
                return "The sands remember your passage."
            return self._handle_command(routed)

        return self._say_to_npc(npc, cmd)

    def _say_to_npc(self, npc: NPC, message: str) -> str:
        zone = self.zones[self.player.location]
        reply = self.ai.character_dialogue(npc, self.player, zone, message, npc.chat_history)
        npc.chat_history.append((message, reply))
        self._maybe_progress_quest("talk")
        return f"{npc.name}: {reply}"

    def _scene_description(self, zone: Zone, npcs: List[NPC], shops: List[Shop]) -> str:
        assert self.player is not None
        active_quest = self._active_quest()
        ai_text = self.ai.describe_location(
            self.player,
            zone,
            npcs,
            shops,
            active_quest,
            self.player.riding_worm,
        )
        if ai_text:
            return ai_text
        return self._fallback_scene_description(zone, npcs, shops, active_quest)

    def _fallback_scene_description(
        self,
        zone: Zone,
        npcs: List[NPC],
        shops: List[Shop],
        active_quest: Optional[Quest],
    ) -> str:
        assert self.player is not None
        kind_mood = {
            "city": (
                "Heat hangs against the stone and the air tastes faintly of spice dust. "
                "Voices stay measured here, because every bargain, glance, and hesitation can carry political weight on Arrakis."
            ),
            "palace": (
                "The architecture presses its purpose on you at once: beauty used as strategy, ceremony used as power. "
                "Even the coolness feels deliberate, as if every shadow has been placed to remind visitors who commands water and law."
            ),
            "desert": (
                "The open desert strips away every false comfort. "
                "Wind rasps across sand and rock with a patient violence, and the horizon seems less like distance than a warning."
            ),
        }
        people_line = ""
        if npcs:
            people_line = (
                " Nearby, "
                + ", ".join(f"{npc.name} watches as a {npc.role.lower()}" for npc in npcs[:2])
                + "."
            )
        shop_line = ""
        if shops:
            shop_names = ", ".join(shop.name for shop in shops[:2])
            shop_line = (
                f" Trade gathers around {shop_names}, where necessity is priced with the hard clarity of a water-poor world."
            )
        quest_line = ""
        if active_quest:
            quest_line = (
                f" Beneath the surface of the scene runs the pressure of your current task, {active_quest.title}, "
                "turning ordinary details into possible signals."
            )
        worm_line = ""
        if self.player.riding_worm:
            worm_line = (
                " The rhythm under you is alive and immense, a reminder that Arrakis is never truly mastered, only survived for a time."
            )

        return "".join(
            [
                zone.summary + " ",
                kind_mood.get(zone.kind, "Arrakis feels watchful here, as if the world itself is measuring your worth. "),
                people_line,
                shop_line,
                quest_line,
                worm_line,
            ]
        ).strip()

    def _unique_npc_name(self, zone_id: str, proposed_name: str) -> str:
        existing_names = {
            self.npcs[nid].name.lower() for nid in self.zones[zone_id].npcs if nid in self.npcs
        }
        if proposed_name.lower() not in existing_names:
            return proposed_name

        fallback_names = ["Harah", "Otheym", "Yueh's Clerk", "Esmar Tuek", "Kynes' Aide", "Rafik"]
        for candidate in fallback_names:
            if candidate.lower() not in existing_names:
                return candidate

        suffix = 2
        while True:
            candidate = f"{proposed_name} {suffix}"
            if candidate.lower() not in existing_names:
                return candidate
            suffix += 1

    @staticmethod
    def _slug(text: str) -> str:
        clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in text)
        while "__" in clean:
            clean = clean.replace("__", "_")
        return clean.strip("_")


if __name__ == "__main__":
    game = DuneGame()
    game.run()
