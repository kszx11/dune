from dune_game.domain.lore import LoreCatalog


def test_lore_loads_core_arrakis_content() -> None:
    lore = LoreCatalog.load()
    assert lore.player.name == "Paul Atreides"
    assert "arrakeen_gate" in lore.locations
    assert "market_water_ring_stall" in lore.areas
    assert "Lady Jessica" in lore.npcs
    assert lore.rumors


def test_find_npc_matches_first_name_and_title() -> None:
    lore = LoreCatalog.load()

    jessica = lore.find_npc("Jessica", lore.npcs, "palace_outer_court", "palace_receiving_colonnade")
    assert jessica is not None
    assert jessica.name == "Lady Jessica"

    harah = lore.find_npc("water seller", lore.npcs, "market_quarter", "market_water_counter_interior")
    assert harah is not None
    assert harah.name == "Harah"
