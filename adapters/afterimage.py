"""Afterimage target: read-only authored modes and scripts."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_js import object_keys, read_text

PROJECT_ROOT = project_root("afterimage")
SOURCE = PROJECT_ROOT / "game.js"
_TEXT = read_text(SOURCE)

MODES = object_keys(_TEXT, "MODES")
SCRIPTS = object_keys(_TEXT, "SCRIPTS")

TARGET = TargetFacts(
    game_id="afterimage",
    display_name="After Image",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="javascript",
    test_command="node --test tests",
    pack_major=1,
    content=(
        ContentSurface("modes", "catalog", ("game.js",), MODES),
        ContentSurface("scripts", "catalog", ("game.js",), SCRIPTS),
    ),
)
