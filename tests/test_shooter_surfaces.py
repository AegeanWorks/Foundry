"""Shooter target surfaces: every authored table is exposed read-only.

The four tuning tables are as much part of the game's content as its catalogs;
a manifest that omits them makes Foundry's view of Shooter incomplete.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.shooter import TARGET  # noqa: E402


EXPECTED_SURFACES = {
    "arena_covers": ("catalog", 7, "shooter/data/levels.json"),
    "core_material": ("catalog", 2, "shooter/data/core_material.json"),
    "enemies": ("catalog", 4, "shooter/data/enemies.json"),
    "engagement": ("rules", 5, "shooter/data/engagement.json"),
    "grade": ("rules", 1, "shooter/data/grade.json"),
    "juice": ("rules", 32, "shooter/data/juice.json"),
    "waves": ("catalog", 5, "shooter/data/levels.json"),
    "weapons": ("catalog", 4, "shooter/data/weapons.json"),
}


class TestShooterSurfaces(unittest.TestCase):
    def test_every_authored_table_is_a_surface(self):
        surfaces = {surface.id: surface for surface in TARGET.content}
        self.assertEqual(set(surfaces), set(EXPECTED_SURFACES))
        for surface_id, (kind, count, source) in EXPECTED_SURFACES.items():
            with self.subTest(surface=surface_id):
                self.assertEqual(surfaces[surface_id].kind, kind)
                self.assertEqual(surfaces[surface_id].sources, (source,))
                self.assertEqual(len(surfaces[surface_id].items), count)

    def test_rule_items_are_tuning_fields_not_prose(self):
        surfaces = {surface.id: surface for surface in TARGET.content}
        for surface_id in ("engagement", "grade", "juice"):
            for item in surfaces[surface_id].items:
                with self.subTest(surface=surface_id, item=item):
                    self.assertNotIn(" ", item)
                    self.assertLessEqual(len(item), 120)
