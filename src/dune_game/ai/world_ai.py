from __future__ import annotations

import json
from random import choice

from dune_game.ai.client import OpenAIClient
from dune_game.domain.models import AreaProfile, LocationProfile, Mission, NpcState, Rumor, ShopProfile


class WorldAI:
    def __init__(self, client: OpenAIClient) -> None:
        self.client = client

    @property
    def enabled(self) -> bool:
        return self.client.enabled

    def describe_location(
        self,
        location: LocationProfile,
        npcs: list[NpcState],
        shops: list[ShopProfile],
        rumors: list[Rumor],
        missions: list[Mission],
    ) -> str:
        instructions = (
            "Write like a restrained Dune scene description. Stress scarcity, hierarchy, ecology, rumor, "
            "and political pressure. Avoid generic fantasy and modern phrasing. Keep to 4-6 sentences."
        )
        prompt = (
            f"Location: {location.name}\n"
            f"Region: {location.region}\n"
            f"Summary: {location.summary}\n"
            f"Atmosphere: {', '.join(location.atmosphere)}\n"
            f"Landmarks: {', '.join(location.landmarks)}\n"
            f"Nearby people: {', '.join(f'{npc.name} ({npc.title})' for npc in npcs) or 'none'}\n"
            f"Nearby shops: {', '.join(shop.name for shop in shops) or 'none'}\n"
            f"Heard rumors: {', '.join(r.text for r in rumors[:2]) or 'none'}\n"
            f"Active pressures: {', '.join(m.title for m in missions[:2]) or 'none'}"
        )
        text = self.client.text(instructions=instructions, prompt=prompt, temperature=0.95)
        if text:
            return text
        return self._fallback_location(location, npcs, shops, rumors, missions)

    def describe_area(
        self,
        location: LocationProfile,
        area: AreaProfile,
        npcs: list[NpcState],
        shops: list[ShopProfile],
        rumors: list[Rumor],
        missions: list[Mission],
    ) -> str:
        instructions = (
            "Write like a restrained Dune scene description for a smaller explorable area within a larger place. "
            "Keep the scale intimate and spatially specific. Use 3-5 sentences."
        )
        prompt = (
            f"Parent location: {location.name}\n"
            f"Area: {area.name}\n"
            f"Area summary: {area.summary}\n"
            f"Atmosphere: {', '.join(area.atmosphere)}\n"
            f"Landmarks: {', '.join(area.landmarks)}\n"
            f"Nearby people: {', '.join(f'{npc.name} ({npc.title})' for npc in npcs) or 'none'}\n"
            f"Nearby shops: {', '.join(shop.name for shop in shops) or 'none'}\n"
            f"Heard rumors: {', '.join(r.text for r in rumors[:2]) or 'none'}\n"
            f"Active pressures: {', '.join(m.title for m in missions[:2]) or 'none'}"
        )
        text = self.client.text(instructions=instructions, prompt=prompt, temperature=0.95)
        if text:
            return text
        return self._fallback_area(location, area, npcs, shops, rumors, missions)

    def npc_reply(self, npc: NpcState, location: LocationProfile, player_line: str) -> str:
        instructions = (
            "You are roleplaying a Dune-world NPC speaking with Paul Atreides. Stay in-world. "
            "Keep the line compact, tense, and socially aware. Never mention being an AI."
        )
        memory = "\n".join(f"{entry['speaker']}: {entry['text']}" for entry in npc.memory[-6:])
        prompt = (
            f"NPC: {npc.name}, {npc.title}\n"
            f"Faction: {npc.faction}\n"
            f"Summary: {npc.summary}\n"
            f"Traits: {', '.join(npc.traits)}\n"
            f"Troubles: {', '.join(npc.troubles) or 'none'}\n"
            f"Secrets: {', '.join(npc.secrets) or 'none'}\n"
            f"Location: {location.name} - {location.summary}\n"
            f"Recent exchange:\n{memory or '(none)'}\n"
            f"Paul says: {player_line}"
        )
        text = self.client.text(instructions=instructions, prompt=prompt, temperature=0.98)
        if text:
            return text
        tone = choice(
            [
                "measures each word as if it could cost water",
                "glances aside before answering, aware that walls have listeners",
                "answers carefully, as one who has survived by speaking only as much as necessary",
            ]
        )
        return f"{tone}. \"{self._fallback_speech(npc, player_line)}\""

    def narrate_action(self, location: LocationProfile, action_text: str) -> str:
        instructions = (
            "Narrate the outcome of one grounded action on Arrakis. Stay concise and plausible. "
            "No combat spectacle. Use 2-4 sentences."
        )
        prompt = f"Location: {location.name}\nSummary: {location.summary}\nAction: {action_text}"
        text = self.client.text(instructions=instructions, prompt=prompt, temperature=0.85)
        if text:
            return text
        return (
            f"In {location.name}, your action shifts the balance of attention around you. "
            "On Arrakis even small gestures are observed, weighed, and remembered."
        )

    def generate_region(self, frontier: LocationProfile, requested_name: str) -> dict:
        instructions = (
            "Create a lore-compatible major Arrakis region. Return strict JSON with keys: "
            "region_name, summary, locations, npcs, rumor. "
            "locations is an array of 3 items with keys id, name, kind, summary, atmosphere, landmarks, travel_keywords. "
            "npcs is an array of 2 items with keys name, title, faction, summary, traits, troubles, secrets."
        )
        prompt = (
            f"Create a new Arrakis region branching from {frontier.name}. "
            f"Requested clue or name: {requested_name}. "
            "The result should feel politically and ecologically specific, not generic."
        )
        raw = self.client.text(instructions=instructions, prompt=prompt, temperature=1.0)
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        slug = _slug(requested_name or "broken basin")
        return {
            "region_name": requested_name.title() if requested_name else "Broken Basin",
            "summary": "A rough basin of wind-carved stone, hidden works, and water-poor settlements held together by fear and necessity.",
            "locations": [
                {
                    "id": f"{slug}_approach",
                    "name": f"{requested_name.title() if requested_name else 'Broken Basin'} Approach",
                    "kind": "desert",
                    "summary": "A hard approach of rock shelves and sand-scoured ledges where watchers can see a traveler long before he sees them.",
                    "atmosphere": ["watchful", "dry", "politically strained"],
                    "landmarks": ["marker cairns", "old crawler scars"],
                    "travel_keywords": ["approach", "cairns"],
                },
                {
                    "id": f"{slug}_works",
                    "name": f"{requested_name.title() if requested_name else 'Broken Basin'} Works",
                    "kind": "industrial",
                    "summary": "A knot of salvage frames, spice sieves, and hidden store pits worked by people who have learned to make necessity look like obedience.",
                    "atmosphere": ["laboring", "secretive", "tense"],
                    "landmarks": ["sieve towers", "hidden cistern doors"],
                    "travel_keywords": ["works", "salvage", "cistern"],
                },
                {
                    "id": f"{slug}_hollow",
                    "name": f"{requested_name.title() if requested_name else 'Broken Basin'} Hollow",
                    "kind": "settlement",
                    "summary": "A concealed hollow where fugitives, traders, and scouts meet beneath stone overhangs to exchange warnings, favors, and lies.",
                    "atmosphere": ["guarded", "crowded", "hungry for news"],
                    "landmarks": ["shadow bazaar", "wind screen wall"],
                    "travel_keywords": ["hollow", "bazaar"],
                },
            ],
            "npcs": [
                {
                    "name": "Tarek Esmar",
                    "title": "Salvage Overseer",
                    "faction": "Independent",
                    "summary": "A hard practical man trying to keep workers fed without drawing too much notice from stronger powers.",
                    "traits": ["pragmatic", "tired", "unwilling to kneel too easily"],
                    "troubles": ["owes water to dangerous men", "fears a worker informant"],
                    "secrets": ["hides a private store ledger"],
                },
                {
                    "name": "Lichna",
                    "title": "Desert Go-Between",
                    "faction": "Fremen-aligned",
                    "summary": "A quiet negotiator who moves between camps carrying warnings and measuring loyalties.",
                    "traits": ["controlled", "observant", "unsentimental"],
                    "troubles": ["must protect a courier path", "distrusts off-world bargains"],
                    "secrets": ["meets with someone in Arrakeen"],
                },
            ],
            "rumor": "People in the basin speak of water hidden where no tax-master has yet counted it.",
        }

    def generate_local_npc(self, location: LocationProfile, existing_names: list[str]) -> dict:
        instructions = (
            "Create one non-canon but lore-compatible Arrakis NPC in strict JSON with keys: "
            "name, title, faction, summary, traits, troubles, secrets."
        )
        prompt = (
            f"Location: {location.name}\n"
            f"Region: {location.region}\n"
            f"Kind: {location.kind}\n"
            f"Atmosphere: {', '.join(location.atmosphere)}\n"
            f"Existing names nearby: {', '.join(existing_names) or 'none'}"
        )
        raw = self.client.text(instructions=instructions, prompt=prompt, temperature=0.95)
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        role_map = {
            "city": ("Street Factor", "Independent"),
            "palace": ("House Servitor", "Palace"),
            "industrial": ("Spice Tally Clerk", "Independent"),
            "research": ("Field Assistant", "Fremen-aligned"),
            "desert": ("Route Watcher", "Fremen-aligned"),
            "settlement": ("Water Keeper", "Fremen-aligned"),
        }
        title, faction = role_map.get(location.kind, ("Bystander", "Independent"))
        base_name = choice(["Rafik", "Marella", "Tarek", "Sihaya", "Omman", "Lichna", "Brolin"])
        if base_name in existing_names:
            base_name = f"{base_name} {len(existing_names) + 1}"
        return {
            "name": base_name,
            "title": title,
            "faction": faction,
            "summary": f"A person shaped by the demands of {location.name.lower()}, accustomed to hearing more than is safe to repeat.",
            "traits": ["watchful", "practical", "socially cautious"],
            "troubles": [f"Needs help navigating a quiet pressure building in {location.name}."],
            "secrets": [f"Knows a private detail about movement through {location.region}."],
        }

    def generate_area_npc(self, location: LocationProfile, area: AreaProfile, existing_names: list[str]) -> dict:
        raw = self.generate_local_npc(location, existing_names)
        raw["summary"] = f"A person shaped by the demands of {area.name.lower()}, used to reading a room before speaking in it."
        raw["troubles"] = [f"Needs help with a quiet trouble tied to {area.name}."]
        raw["secrets"] = [f"Knows something withheld inside {area.name}."]
        return raw

    @staticmethod
    def _fallback_location(
        location: LocationProfile,
        npcs: list[NpcState],
        shops: list[ShopProfile],
        rumors: list[Rumor],
        missions: list[Mission],
    ) -> str:
        mood = ", ".join(location.atmosphere[:3])
        people = f" Nearby stand {', '.join(npc.name for npc in npcs[:3])}." if npcs else ""
        shops_line = f" Trade gathers around {', '.join(shop.name for shop in shops[:2])}." if shops else ""
        rumor_line = f" The place carries rumor: {rumors[0].text}" if rumors else ""
        mission_line = f" Pressure gathers around {missions[0].title}." if missions else ""
        return (
            f"{location.summary} The air of the place feels {mood}, and every arrangement of shade, stone, and movement "
            "suggests that survival here is political as much as physical."
            f"{people}{shops_line}{rumor_line}{mission_line}"
        )

    @staticmethod
    def _fallback_area(
        location: LocationProfile,
        area: AreaProfile,
        npcs: list[NpcState],
        shops: list[ShopProfile],
        rumors: list[Rumor],
        missions: list[Mission],
    ) -> str:
        mood = ", ".join(area.atmosphere[:3])
        people = f" Nearby stand {', '.join(npc.name for npc in npcs[:3])}." if npcs else ""
        shops_line = f" Trade or service here centers on {', '.join(shop.name for shop in shops[:2])}." if shops else ""
        rumor_line = f" The local air carries pressure from {rumors[0].text}" if rumors else ""
        mission_line = f" The place now feels tied to {missions[0].title}." if missions else ""
        return (
            f"{area.summary} Inside {location.name}, this smaller space feels {mood}. "
            "Details matter more here: who watches, who waits, and which object is placed to be seen."
            f"{people}{shops_line}{rumor_line}{mission_line}"
        )

    @staticmethod
    def _fallback_speech(npc: NpcState, player_line: str) -> str:
        if "water" in player_line.lower():
            return "On Arrakis, a man learns quickly who speaks of water lightly and who does not."
        if "trouble" in player_line.lower() or "problem" in player_line.lower():
            return f"You have eyes. Trouble is common enough here. The rarer thing is a hand willing to touch it."
        if npc.troubles:
            return f"I have my burdens, as everyone here does. Some of them would profit from remaining unspoken."
        return "Words are easy. On Arrakis it is consequences that cost."


def _slug(text: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in text)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")
