"""Portfolio analysis tests: every playable project is covered by a target."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from tools.portfolio_analysis import analyze, check, scan  # noqa: E402


class TestPortfolioAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects = {project.name: project for project in scan()}

    def test_every_playable_project_is_targeted(self):
        self.assertEqual(check(), [])

    def test_scan_finds_the_remaining_game_projects(self):
        for name in ("dustline", "voidfarer", "MemoryReconstruction", "prism-relay", "keystone"):
            with self.subTest(project=name):
                self.assertIn(name, self.projects)

    def test_classification_separates_games_from_tools(self):
        expected = {
            "dustline": "game",
            "iris": "game",
            "keystone": "engine",
            "Atlas": "non-game",
            "chronos": "non-game",
            "photo-harbor": "non-game",
        }
        for name, kind in expected.items():
            with self.subTest(project=name):
                self.assertEqual(self.projects[name].kind, kind)

    def test_report_is_json_safe(self):
        rows = analyze(self.projects.values())
        self.assertIsInstance(json.dumps(rows), str)
        self.assertTrue(any(row["target"] == "dustline" for row in rows))


if __name__ == "__main__":
    unittest.main()
