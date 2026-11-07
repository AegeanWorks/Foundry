"""crypt-crawler adapter: the versioned boundary foundry never crosses.

Foundry emits canonical boss JSON; it never dictates the game's format.
This adapter exposes the consumer facts the validator and generator need
(catalog ids, target identity, supported pack major) by reading the
game's own tables, so a game-side data edit is picked up without a
foundry change. The reverse mapping (canonical pack -> BOSS_TEMPLATES
entry + spawn post) lives game-side in crawler/foundry_packs.py, which
is the adapter's other half pinned by the same pack_version.
"""

from __future__ import annotations

import sys
from typing import Dict, FrozenSet

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root

GAME_ROOT = project_root("crypt-crawler")

TARGET_GAME = "crypt-crawler"
SUPPORTED_MAJOR = 1
ECONOMY_NOTE = "ITEM_CATALOG ids; xp 20-400 / gold 10-300 per schema bands"


def _load_game_tables() -> Dict[str, FrozenSet[str]]:
    if str(GAME_ROOT) not in sys.path:
        sys.path.insert(0, str(GAME_ROOT))
    from crawler.entities import ITEM_CATALOG  # type: ignore[import]

    return {"items": frozenset(ITEM_CATALOG)}


_TABLES = _load_game_tables()
ITEM_IDS: FrozenSet[str] = _TABLES["items"]

TARGET = TargetFacts(
    game_id=TARGET_GAME,
    display_name="Crypt Crawler",
    project_root=GAME_ROOT,
    lifecycle="active",
    engine="javascript",
    test_command="python -m unittest discover tests",
    pack_major=SUPPORTED_MAJOR,
    content=(
        ContentSurface(
            "items",
            "catalog",
            ("crawler/entities.py",),
            tuple(sorted(ITEM_IDS)),
        ),
    ),
)
