from dune_game.config import Config
from dune_game.engine.game import GameApp


def main() -> None:
    GameApp(Config.load()).run()
