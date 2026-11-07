"""Prism Relay target: read-only episodes, chambers and emitter directions."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_js import array_object_ids, object_keys, read_text

PROJECT_ROOT = project_root("prism-relay")
LEVELS = PROJECT_ROOT / "src" / "game" / "levels.js"
ENGINE = PROJECT_ROOT / "src" / "game" / "engine.js"

_LEVEL_TEXT = read_text(LEVELS)
_ENGINE_TEXT = read_text(ENGINE)

EPISODES = array_object_ids(_LEVEL_TEXT, "EPISODES")
CHAMBERS = (
    array_object_ids(_LEVEL_TEXT, "IGNITION_LEVELS")
    + array_object_ids(_LEVEL_TEXT, "REFRACTION_LEVELS")
    + array_object_ids(_LEVEL_TEXT, "CROSSING_LEVELS")
    + array_object_ids(_LEVEL_TEXT, "CONFLUENCE_LEVELS")
)
EMITTER_DIRECTIONS = object_keys(_ENGINE_TEXT, "EMITTER_DIRECTIONS")

TARGET = TargetFacts(
    game_id="prism-relay",
    display_name="Prism Relay",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="javascript",
    test_command="npm test",
    pack_major=1,
    content=(
        ContentSurface("episodes", "catalog", ("src/game/levels.js",), EPISODES),
        ContentSurface("chambers", "catalog", ("src/game/levels.js",), CHAMBERS),
        ContentSurface(
            "emitter_directions",
            "catalog",
            ("src/game/engine.js",),
            EMITTER_DIRECTIONS,
        ),
    ),
)
