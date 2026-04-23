from dune_game.domain.lore import LoreCatalog


def test_lore_loads_core_arrakis_content() -> None:
    lore = LoreCatalog.load()
    assert lore.player.name == "Paul Atreides"
    assert "arrakeen_gate" in lore.locations
    assert "market_water_ring_stall" in lore.areas
    assert "Lady Jessica" in lore.npcs
    assert lore.rumors
