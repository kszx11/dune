from dune_game.domain.models import GameState
from dune_game.engine.saves import load_state, save_state


def test_save_roundtrip(tmp_path) -> None:
    path = tmp_path / "savegame.json"
    state = GameState(
        player_name="Paul Atreides",
        player_title="Duke's Son",
        location_id="arrakeen_gate",
        time_index=1,
        inventory=["stillsuit"],
    )
    save_state(path, state)
    loaded = load_state(path)
    assert loaded.player_name == "Paul Atreides"
    assert loaded.location_id == "arrakeen_gate"
