import dune_game.engine.game as game_module
from dune_game.config import Config
from dune_game.engine.game import GameApp
from dune_game.ui.render import Renderer


def test_talking_to_npc_refreshes_suggestions(monkeypatch, tmp_path) -> None:
    config = Config(api_key=None, text_model="gpt-4.1-mini", typewriter_delay=0.0, reduced_motion=True, root_dir=tmp_path)
    app = GameApp(config)
    app.state = app._new_game()
    app.state.location_id = "market_quarter"
    app.state.area_id = "market_water_counter_interior"
    app.state.discovered_locations.append("market_quarter")
    app.state.discovered_areas.append("market_water_counter_interior")

    monkeypatch.setattr(app.renderer, "system", lambda *args, **kwargs: None)
    monkeypatch.setattr(app.renderer, "npc", lambda *args, **kwargs: None)
    monkeypatch.setattr(app.renderer, "location_card", lambda *args, **kwargs: None)
    monkeypatch.setattr(app.renderer, "show_status", lambda *args, **kwargs: None)

    replies = iter(["hello", "bye"])
    monkeypatch.setattr(game_module.Prompt, "ask", staticmethod(lambda _message: next(replies)))

    app._refresh_suggestions()
    assert any("talk to Harah" in line for line in app.state.suggestions)

    app._talk("Harah")

    assert app.npc_states()["Harah"].memory
    assert not any("talk to Harah" in line for line in app.state.suggestions)


def test_renderer_strips_duplicate_npc_prefix(tmp_path) -> None:
    config = Config(api_key=None, text_model="gpt-4.1-mini", typewriter_delay=0.0, reduced_motion=True, root_dir=tmp_path)
    renderer = Renderer(config)

    assert renderer._clean_npc_text("Harah", "Harah: Water has a long memory.") == "Water has a long memory."
    assert renderer._clean_npc_text("Harah", "Harah says: Water has a long memory.") == "Water has a long memory."
    assert (
        renderer._clean_npc_text("Harah", 'Harah measures each word as if it could cost water. "Keep your voice down."')
        == 'measures each word as if it could cost water. "Keep your voice down."'
    )


def test_go_command_accepts_nearby_location_names(monkeypatch, tmp_path) -> None:
    config = Config(api_key=None, text_model="gpt-4.1-mini", typewriter_delay=0.0, reduced_motion=True, root_dir=tmp_path)
    app = GameApp(config)
    app.state = app._new_game()

    monkeypatch.setattr(app, "_render_scene", lambda *args, **kwargs: None)

    app._go_area("market quarter")

    assert app.state.location_id == "market_quarter"
    assert app.state.area_id == ""
