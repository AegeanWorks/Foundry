"""Weft target: read-only chamber catalog and size ladder."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_js import int_values, read_text, string_values

PROJECT_ROOT = project_root("weft")
SOURCE = PROJECT_ROOT / "src" / "game" / "levels.js"
_TEXT = read_text(SOURCE)

CHAMBERS = string_values(_TEXT, "id")
SIZES = tuple(str(value) for value in dict.fromkeys(int_values(_TEXT, "size")))

TARGET = TargetFacts(
    game_id="weft",
    display_name="Weft",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="javascript",
    test_command="npm test",
    pack_major=1,
    content=(
        ContentSurface("chambers", "catalog", ("src/game/levels.js",), CHAMBERS),
        ContentSurface("sizes", "catalog", ("src/game/levels.js",), SIZES),
    ),
)
