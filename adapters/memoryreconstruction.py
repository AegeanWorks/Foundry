"""Memory Reconstruction target: read-only authored JSON content tables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root

PROJECT_ROOT = project_root("MemoryReconstruction")
DATA = PROJECT_ROOT / "src" / "data"


def _load(name: str) -> Dict[str, Any]:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def _ids(items: Any) -> Tuple[str, ...]:
    return tuple(str(item["id"]) for item in items)


_ABILITIES = _load("abilities.json")
_BIOMES = _load("biomes.json")
_ENEMIES = _load("enemies.json")
_EQUIPMENT = _load("equipment.json")
_ITEMS = _load("items.json")
_LORE = _load("lore.json")["lore"]

_ITEM_IDS = tuple(
    str(item["id"])
    for group in ("weapons", "armor", "accessories", "consumables", "keys")
    for item in _ITEMS[group]
)
_MEMORY_IDS = tuple(
    str(key)
    for group in ("memoryFragments", "coreMemories", "primordialMemories")
    for key in _LORE[group]
)

TARGET = TargetFacts(
    game_id="memoryreconstruction",
    display_name="Memory Reconstruction",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="javascript",
    test_command="npm test",
    pack_major=1,
    content=(
        ContentSurface(
            "player_abilities",
            "catalog",
            ("src/data/abilities.json",),
            _ids(_ABILITIES["playerAbilities"]),
        ),
        ContentSurface(
            "enemy_abilities",
            "catalog",
            ("src/data/abilities.json",),
            _ids(_ABILITIES["enemyAbilities"]),
        ),
        ContentSurface("biomes", "catalog", ("src/data/biomes.json",), _ids(_BIOMES["biomes"])),
        ContentSurface("enemies", "catalog", ("src/data/enemies.json",), _ids(_ENEMIES["enemies"])),
        ContentSurface(
            "equipment",
            "catalog",
            ("src/data/equipment.json",),
            _ids(_EQUIPMENT["items"]),
        ),
        ContentSurface("items", "catalog", ("src/data/items.json",), _ITEM_IDS),
        ContentSurface(
            "lore_entries",
            "catalog",
            ("src/data/lore.json",),
            _ids(_LORE["entries"]),
        ),
        ContentSurface(
            "memory_fragments",
            "catalog",
            ("src/data/lore.json",),
            _MEMORY_IDS,
        ),
    ),
)
