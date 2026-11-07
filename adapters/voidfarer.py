"""VoidFarer target: read-only weapons, enemies, factions, drones and systems."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_py import (
    call_first_args,
    dict_keys,
    list_tuple_first_strings,
    tuple_strings,
)

PROJECT_ROOT = project_root("voidfarer")
WEAPONS = PROJECT_ROOT / "voidfarer" / "weapons.py"
ENEMIES = PROJECT_ROOT / "voidfarer" / "enemies.py"
FACTIONS = PROJECT_ROOT / "voidfarer" / "factions.py"
UPGRADES = PROJECT_ROOT / "voidfarer" / "upgrades.py"
GALAXY = PROJECT_ROOT / "voidfarer" / "galaxy.py"
SURFACE = PROJECT_ROOT / "voidfarer" / "surface.py"

TARGET = TargetFacts(
    game_id="voidfarer",
    display_name="VoidFarer",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="python",
    test_command="python -m unittest discover",
    pack_major=1,
    content=(
        ContentSurface("weapons", "catalog", ("voidfarer/weapons.py",), call_first_args(WEAPONS, "WeaponSpec")),
        ContentSurface("enemies", "catalog", ("voidfarer/enemies.py",), dict_keys(ENEMIES, "ENEMY_ARCHETYPES")),
        ContentSurface("factions", "catalog", ("voidfarer/factions.py",), dict_keys(FACTIONS, "CANONICAL_FACTIONS")),
        ContentSurface("drones", "catalog", ("voidfarer/upgrades.py",), dict_keys(UPGRADES, "CATALOG_DRONE_TEMPLATES")),
        ContentSurface("systems", "catalog", ("voidfarer/galaxy.py",), list_tuple_first_strings(GALAXY, "SYSTEM_ARCHETYPES")),
        ContentSurface("surface_types", "catalog", ("voidfarer/surface.py",), tuple_strings(SURFACE, "GAS_SURFACE_TYPES")),
    ),
)
