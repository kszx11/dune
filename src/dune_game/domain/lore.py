from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

from dune_game.domain.models import LocationProfile, NpcState, PlayerProfile, Rumor, ShopProfile


@dataclass
class LoreCatalog:
    player: PlayerProfile
    locations: dict[str, LocationProfile]
    npcs: dict[str, NpcState]
    rumors: list[Rumor]
    shops: dict[str, ShopProfile]

    @classmethod
    def load(cls) -> "LoreCatalog":
        base = Path(__file__).resolve().parents[1] / "content"
        locations_raw = _read_structured(base / "locations.yaml")
        npcs_raw = _read_structured(base / "npcs.yaml")
        rumors_raw = _read_structured(base / "rumors.yaml")
        shops_raw = _read_structured(base / "shops.yaml")
        player = PlayerProfile(**npcs_raw["player"])
        locations = {item["id"]: LocationProfile(**item) for item in locations_raw["locations"]}
        npcs = {
            item["name"]: NpcState(
                name=item["name"],
                title=item["title"],
                faction=item["faction"],
                summary=item["summary"],
                speech_style=item["speech_style"],
                traits=item["traits"],
                home_location=item["home_location"],
                current_location=item["home_location"],
                shop_id=item.get("shop_id", ""),
                canonical=item.get("canonical", False),
                troubles=item.get("troubles", []),
                secrets=item.get("secrets", []),
                rumor_ids=item.get("rumor_ids", []),
            )
            for item in npcs_raw["npcs"]
        }
        rumors = [Rumor(**item) for item in rumors_raw["rumors"]]
        shops = {item["id"]: ShopProfile(**item) for item in shops_raw["shops"]}
        return cls(player=player, locations=locations, npcs=npcs, rumors=rumors, shops=shops)

    def find_location(self, query: str, all_locations: dict[str, LocationProfile]) -> LocationProfile | None:
        needle = query.strip().lower()
        if not needle:
            return None
        if needle in all_locations:
            return all_locations[needle]
        for location in all_locations.values():
            haystacks = [
                location.id,
                location.name,
                location.region,
                *location.travel_keywords,
                *location.landmarks,
            ]
            if any(needle in value.lower() for value in haystacks):
                return location
        return None

    def find_npc(self, query: str, npc_states: dict[str, NpcState], location_id: str | None = None) -> NpcState | None:
        needle = query.strip().lower()
        for npc in npc_states.values():
            if location_id and npc.current_location != location_id:
                continue
            if needle == npc.name.lower() or needle in npc.name.lower():
                return npc
        return None


def _read_structured(path: Path) -> dict:
    text = path.read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    return json.loads(text)
