"""Cyberpulse target: read-only puzzle, story-act and campaign-quest catalogs."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_py import dict_keys, set_strings

PROJECT_ROOT = project_root("cyberpulse")
PUZZLES_SOURCE = PROJECT_ROOT / "cyberpulse" / "puzzles.py"
STORY_SOURCE = PROJECT_ROOT / "cyberpulse" / "story.py"

PUZZLE_TYPES = dict_keys(PUZZLES_SOURCE, "PUZZLE_TYPES")
STORY_ACTS = dict_keys(STORY_SOURCE, "STORY_ACTS")
MAIN_QUESTS = set_strings(STORY_SOURCE, "MAIN_QUEST_IDS")

TARGET = TargetFacts(
    game_id="cyberpulse",
    display_name="Cyberpulse",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="python",
    test_command="python -m unittest discover",
    pack_major=1,
    content=(
        ContentSurface("puzzle_types", "catalog", ("cyberpulse/puzzles.py",), PUZZLE_TYPES),
        ContentSurface("story_acts", "catalog", ("cyberpulse/story.py",), STORY_ACTS),
        ContentSurface("main_quests", "catalog", ("cyberpulse/story.py",), MAIN_QUESTS),
    ),
)
