from dune_game.ai.world_ai import WorldAI
from dune_game.config import Config
from dune_game.ai.client import OpenAIClient
from dune_game.domain.models import LocationProfile


def test_fallback_region_generation_returns_multi_location_region(tmp_path) -> None:
    config = Config(api_key=None, text_model="gpt-4.1-mini", typewriter_delay=0.0, reduced_motion=True, root_dir=tmp_path)
    ai = WorldAI(OpenAIClient(config))
    frontier = LocationProfile(
        id="desert_edge",
        name="Desert Edge",
        region="Arrakeen Fringe",
        kind="desert",
        summary="The open desert waits beyond the last stone.",
        atmosphere=["exposed"],
    )
    region = ai.generate_region(frontier, "broken terrace")
    assert len(region["locations"]) == 3
    assert len(region["npcs"]) == 2
