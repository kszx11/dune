from dune_game.engine.commands import parse_command


def test_parse_ask_command() -> None:
    parsed = parse_command("ask Stilgar about water")
    assert parsed.kind == "ask"
    assert parsed.target == "Stilgar"
    assert parsed.topic == "water"


def test_parse_move_command() -> None:
    parsed = parse_command("move market quarter")
    assert parsed.kind == "move"
    assert parsed.target == "market quarter"


def test_parse_menu_command() -> None:
    parsed = parse_command("menu")
    assert parsed.kind == "menu"


def test_parse_hint_command() -> None:
    parsed = parse_command("hint")
    assert parsed.kind == "hint"


def test_parse_go_area_command() -> None:
    parsed = parse_command("go water ring stall")
    assert parsed.kind == "go_area"
    assert parsed.target == "water ring stall"


def test_parse_enter_command() -> None:
    parsed = parse_command("enter Harah's Water Counter")
    assert parsed.kind == "enter"


def test_parse_leave_command() -> None:
    parsed = parse_command("leave")
    assert parsed.kind == "leave"


def test_parse_talk_with_command() -> None:
    parsed = parse_command("talk with Jessica")
    assert parsed.kind == "talk"
    assert parsed.target == "Jessica"
