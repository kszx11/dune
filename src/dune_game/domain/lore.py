from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

from dune_game.domain.models import AreaProfile, LocationProfile, NpcState, PlayerProfile, Rumor, ShopProfile


@dataclass
class LoreCatalog:
    player: PlayerProfile
    locations: dict[str, LocationProfile]
    areas: dict[str, AreaProfile]
    npcs: dict[str, NpcState]
    rumors: list[Rumor]
    shops: dict[str, ShopProfile]

    @classmethod
    def load(cls) -> "LoreCatalog":
        base = Path(__file__).resolve().parents[1] / "content"
        locations_raw = _read_structured(base / "locations.yaml")
        areas_raw = _read_structured(base / "areas.yaml")
        npcs_raw = _read_structured(base / "npcs.yaml")
        rumors_raw = _read_structured(base / "rumors.yaml")
        shops_raw = _read_structured(base / "shops.yaml")
        player = PlayerProfile(**npcs_raw["player"])
        locations = {item["id"]: LocationProfile(**item) for item in locations_raw["locations"]}
        areas = {item["id"]: AreaProfile(**item) for item in areas_raw["areas"]}
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
                home_area=item.get("home_area", ""),
                current_area=item.get("home_area", ""),
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
        return cls(player=player, locations=locations, areas=areas, npcs=npcs, rumors=rumors, shops=shops)

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

    def find_area(
        self,
        query: str,
        all_areas: dict[str, AreaProfile],
        parent_location_id: str,
        allowed_area_ids: set[str] | None = None,
    ) -> AreaProfile | None:
        needle = query.strip().lower()
        if not needle:
            return None
        for area in all_areas.values():
            if area.parent_location_id != parent_location_id:
                continue
            if allowed_area_ids is not None and area.id not in allowed_area_ids:
                continue
            haystacks = [area.id, area.name, *area.travel_keywords, *area.landmarks]
            if any(needle in value.lower() for value in haystacks):
                return area
        return None

    def find_npc(
        self,
        query: str,
        npc_states: dict[str, NpcState],
        location_id: str | None = None,
        area_id: str | None = None,
    ) -> NpcState | None:
        needle = _normalize_lookup_text(query)
        if not needle:
            return None

        needle_tokens = set(needle.split())
        best_match: tuple[int, NpcState] | None = None
        for npc in npc_states.values():
            if location_id and npc.current_location != location_id:
                continue
            if area_id is not None and npc.current_area != area_id:
                continue
            score = _score_npc_match(needle, needle_tokens, npc)
            if score <= 0:
                continue
            if best_match is None or score > best_match[0]:
                best_match = (score, npc)
        return best_match[1] if best_match is not None else None


def _read_structured(path: Path) -> dict:
    text = path.read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    return json.loads(text)


def _normalize_lookup_text(text: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() or char.isspace() else " " for char in text)
    return " ".join(cleaned.split())


def _score_npc_match(needle: str, needle_tokens: set[str], npc: NpcState) -> int:
    name = _normalize_lookup_text(npc.name)
    title = _normalize_lookup_text(npc.title)
    summary = _normalize_lookup_text(npc.summary)
    haystacks = [name, title, summary]
    candidate_tokens = set(" ".join(haystacks).split())

    if needle == name:
        return 100
    if needle == title:
        return 90
    if needle in {token for token in name.split()}:
        return 85
    if needle in {token for token in title.split()}:
        return 80
    if needle and needle in name:
        return 75
    if needle and needle in title:
        return 72
    if needle_tokens and needle_tokens.issubset(set(name.split())):
        return 70 + len(needle_tokens)
    if needle_tokens and needle_tokens.issubset(set(title.split())):
        return 66 + len(needle_tokens)
    if needle_tokens and needle_tokens.issubset(candidate_tokens):
        return 60 + len(needle_tokens)
    if needle in summary:
        return 40
    return 0
