"""Iris target: read-only episode and chamber catalog."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_js import read_text, string_values

PROJECT_ROOT = project_root("archive", "iris")
SOURCE = PROJECT_ROOT / "src" / "game" / "levels.js"
_TEXT = read_text(SOURCE)

EPISODES = string_values(_TEXT, "numeral")
CHAMBERS = string_values(_TEXT, "id")

TARGET = TargetFacts(
    game_id="iris",
    display_name="Iris",
    project_root=PROJECT_ROOT,
    lifecycle="archived",
    engine="javascript",
    test_command="node --test",
    pack_major=1,
    content=(
        ContentSurface("episodes", "catalog", ("src/game/levels.js",), EPISODES),
        ContentSurface("chambers", "catalog", ("src/game/levels.js",), CHAMBERS),
    ),
)
