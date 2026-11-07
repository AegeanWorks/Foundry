"""Dustline target: read-only maps, weapons, enemies, bosses and run modes."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_js import (
    array_object_ids,
    array_strings,
    object_keys,
    read_text,
)

PROJECT_ROOT = project_root("dustline")
SOURCE = PROJECT_ROOT / "game.js"
_TEXT = read_text(SOURCE)

MAPS = array_strings(_TEXT, "MAP_ORDER")
WEAPONS = array_strings(_TEXT, "WEAPON_ORDER")
ENEMIES = object_keys(_TEXT, "ENEMY_TYPES")
BOSSES = array_strings(_TEXT, "BOSS_ORDER")
MEGA_BOSSES = array_strings(_TEXT, "MEGA_ORDER")
OPERATORS = array_strings(_TEXT, "OPERATOR_ORDER")
MODES = array_object_ids(_TEXT, "MODES")
MUTATORS = array_strings(_TEXT, "MUTATOR_ORDER")

TARGET = TargetFacts(
    game_id="dustline",
    display_name="Dustline",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="javascript",
    test_command="node --test tests",
    pack_major=1,
    content=(
        ContentSurface("maps", "catalog", ("game.js",), MAPS),
        ContentSurface("weapons", "catalog", ("game.js",), WEAPONS),
        ContentSurface("enemies", "catalog", ("game.js",), ENEMIES),
        ContentSurface("bosses", "catalog", ("game.js",), BOSSES),
        ContentSurface("mega_bosses", "catalog", ("game.js",), MEGA_BOSSES),
        ContentSurface("operators", "catalog", ("game.js",), OPERATORS),
        ContentSurface("modes", "catalog", ("game.js",), MODES),
        ContentSurface("mutators", "catalog", ("game.js",), MUTATORS),
    ),
)
