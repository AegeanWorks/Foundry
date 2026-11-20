"""Consumer source resolution: an archived sibling still backs a live target.

Shooter was archived from ``projects/shooter`` to ``projects/archive/shooter``.
Foundry must keep resolving its read-only source so the adapter and the pack
generator stay fresh against the canonical (now archived) files.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.layout import PORTFOLIO_ROOT, project_root  # noqa: E402


class TestConsumerSourceResolution(unittest.TestCase):
    def test_shooter_source_resolves_to_an_existing_directory(self):
        root = project_root("shooter")
        self.assertTrue(root.is_dir(), f"no shooter source at {root}")
        self.assertTrue((root / "shooter" / "data" / "enemies.json").is_file())

    def test_active_location_wins_over_archive(self):
        active = PORTFOLIO_ROOT / "projects" / "shooter"
        if active.is_dir():
            self.assertEqual(project_root("shooter"), active)


if __name__ == "__main__":
    unittest.main()
