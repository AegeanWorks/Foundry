"""Fold target: read-only board rules and direction set."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_py import int_constants, tuple_strings

PROJECT_ROOT = project_root("archive", "fold")
SOURCE = PROJECT_ROOT / "fold" / "board.py"

DIRECTIONS = tuple_strings(SOURCE, "DIRECTIONS")
_RULES = int_constants(SOURCE, ("SIZE", "WINNING_VALUE"))
RULE_IDS = (
    f"board-{_RULES['SIZE']}x{_RULES['SIZE']}",
    f"winning-{_RULES['WINNING_VALUE']}",
)

TARGET = TargetFacts(
    game_id="fold",
    display_name="Fold",
    project_root=PROJECT_ROOT,
    lifecycle="archived",
    engine="python",
    test_command="python -m unittest discover -s tests -t .",
    pack_major=1,
    content=(
        ContentSurface("directions", "catalog", ("fold/board.py",), DIRECTIONS),
        ContentSurface("rules", "rules", ("fold/board.py",), RULE_IDS),
    ),
)
