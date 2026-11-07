"""Aldervale target: read-only item and equipment tables."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_py import call_first_args, tuple_strings

PROJECT_ROOT = project_root("archive", "aldervale")
SOURCE = PROJECT_ROOT / "aldervale" / "rules.py"

ITEMS = call_first_args(SOURCE, "_i")
SHOP_STOCK = tuple_strings(SOURCE, "SHOP_STOCK")
WEAPONS = tuple_strings(SOURCE, "WEAPON_ORDER")
ARMOR = tuple_strings(SOURCE, "ARMOR_ORDER")

TARGET = TargetFacts(
    game_id="aldervale",
    display_name="Aldervale",
    project_root=PROJECT_ROOT,
    lifecycle="archived",
    engine="python",
    test_command="python -m unittest discover",
    pack_major=1,
    content=(
        ContentSurface("items", "catalog", ("aldervale/rules.py",), ITEMS),
        ContentSurface("shop_stock", "catalog", ("aldervale/rules.py",), SHOP_STOCK),
        ContentSurface("weapons", "catalog", ("aldervale/rules.py",), WEAPONS),
        ContentSurface("armor", "catalog", ("aldervale/rules.py",), ARMOR),
    ),
)
