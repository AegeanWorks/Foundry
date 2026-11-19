"""Shooter target: read-only JSON content tables."""

from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root

PROJECT_ROOT = project_root("shooter")
DATA = PROJECT_ROOT / "shooter" / "data"


def _load(name: str) -> Dict[str, Any]:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def _ids(payload: Dict[str, Any], key: str) -> Tuple[str, ...]:
    return tuple(str(item["id"]) for item in payload[key])


def _fields(payload: Dict[str, Any]) -> Tuple[str, ...]:
    """The tuned field names of a table, without metadata or prose."""
    return tuple(sorted(key for key in payload if key not in ("schema", "notes")))


_ENEMIES = _load("enemies.json")
_WEAPONS = _load("weapons.json")
_LEVELS = _load("levels.json")
_ENGAGEMENT = _load("engagement.json")
_GRADE = _load("grade.json")
_JUICE = _load("juice.json")
_CORE_MATERIAL = _load("core_material.json")

TARGET = TargetFacts(
    game_id="shooter",
    display_name="Shooter",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="python",
    test_command="python -m pytest -q",
    pack_major=1,
    content=(
        ContentSurface("enemies", "catalog", ("shooter/data/enemies.json",), _ids(_ENEMIES, "enemies")),
        ContentSurface("weapons", "catalog", ("shooter/data/weapons.json",), _ids(_WEAPONS, "weapons")),
        ContentSurface(
            "waves",
            "catalog",
            ("shooter/data/levels.json",),
            tuple(f"wave-{index}" for index in range(1, len(_LEVELS["waves"]) + 1)),
        ),
        ContentSurface(
            "arena_covers",
            "catalog",
            ("shooter/data/levels.json",),
            tuple(f"cover-{index}" for index in range(1, len(_LEVELS["arena"]["covers"]) + 1)),
        ),
        ContentSurface("engagement", "rules", ("shooter/data/engagement.json",), _fields(_ENGAGEMENT)),
        ContentSurface("grade", "rules", ("shooter/data/grade.json",), _fields(_GRADE)),
        ContentSurface("juice", "rules", ("shooter/data/juice.json",), _fields(_JUICE)),
        ContentSurface(
            "core_material",
            "catalog",
            ("shooter/data/core_material.json",),
            _ids(_CORE_MATERIAL, "nodes"),
        ),
    ),
)
