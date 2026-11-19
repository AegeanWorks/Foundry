"""Target registry tests: every requested consumer is present and read-only."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.base import TargetFacts  # noqa: E402
from adapters.layout import PORTFOLIO_ROOT  # noqa: E402
from adapters.registry import all_targets, get_target, target_ids  # noqa: E402
from generators.target import (  # noqa: E402
    check_manifests,
    manifest,
    manifest_bytes,
    manifest_path,
    write_manifest,
)
from validators.target import validate  # noqa: E402

PORTFOLIO_GAME_TARGETS = (
    "afterimage",
    "aldervale",
    "crypt-crawler",
    "cyberpulse",
    "dustline",
    "fold",
    "iris",
    "memoryreconstruction",
    "primordia",
    "prism-relay",
    "shooter",
    "voidfarer",
    "weft",
)

EXPECTED_SURFACES = {
    "crypt-crawler": {"items": 25},
    "keystone": {
        "asset_kinds": 4,
        "file_suffixes": 3,
        "primitives": 5,
        "material_nodes": 7,
    },
    "afterimage": {"modes": 6, "scripts": 3},
    "aldervale": {"items": 12, "shop_stock": 7, "weapons": 4, "armor": 4},
    "shooter": {
        "enemies": 4,
        "weapons": 4,
        "waves": 5,
        "arena_covers": 7,
        "engagement": 5,
        "grade": 1,
        "juice": 32,
        "core_material": 2,
    },
    "weft": {"chambers": 24, "sizes": 8},
    "iris": {"episodes": 3, "chambers": 12},
    "primordia": {"genes": 12, "shocks": 7, "hunter_traits": 10},
    "cyberpulse": {"puzzle_types": 3, "story_acts": 5, "main_quests": 4},
    "fold": {"directions": 4, "rules": 2},
    "dustline": {
        "maps": 7,
        "weapons": 6,
        "enemies": 24,
        "bosses": 5,
        "mega_bosses": 3,
        "operators": 10,
        "modes": 3,
        "mutators": 8,
    },
    "memoryreconstruction": {
        "player_abilities": 9,
        "enemy_abilities": 31,
        "biomes": 16,
        "enemies": 105,
        "equipment": 28,
        "items": 14,
        "lore_entries": 13,
        "memory_fragments": 53,
    },
    "prism-relay": {"episodes": 4, "chambers": 18, "emitter_directions": 4},
    "voidfarer": {
        "weapons": 8,
        "enemies": 5,
        "factions": 9,
        "drones": 3,
        "systems": 32,
        "surface_types": 4,
    },
}


def _source_paths(target: TargetFacts):
    for surface in target.content:
        for source in surface.sources:
            yield target.project_root / source


def _snapshot(targets):
    return {
        str(path): (path.stat().st_size, path.stat().st_mtime_ns)
        for target in targets
        for path in _source_paths(target)
    }


class TestTargetRegistry(unittest.TestCase):
    def test_portfolio_targets_are_registered(self):
        self.assertTrue(set(PORTFOLIO_GAME_TARGETS).issubset(target_ids()))

    def test_engine_target_is_registered(self):
        self.assertIn("keystone", target_ids())

    def test_registry_ids_are_unique(self):
        ids = target_ids()
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_target_project_exists(self):
        for target in all_targets():
            with self.subTest(target=target.game_id):
                self.assertTrue(target.project_root.is_dir(), target.project_root)
                self.assertTrue(target.project_root.is_relative_to(PORTFOLIO_ROOT))

    def test_every_source_exists(self):
        for target in all_targets():
            for path in _source_paths(target):
                with self.subTest(target=target.game_id, source=str(path)):
                    self.assertTrue(path.is_file(), path)

    def test_every_surface_is_non_empty_and_unique(self):
        for target in all_targets():
            for surface in target.content:
                with self.subTest(target=target.game_id, surface=surface.id):
                    self.assertTrue(surface.items)
                    self.assertEqual(len(surface.items), len(set(surface.items)))

    def test_authored_content_counts(self):
        for target in all_targets():
            with self.subTest(target=target.game_id):
                counts = {surface.id: len(surface.items) for surface in target.content}
                self.assertEqual(counts, EXPECTED_SURFACES[target.game_id])

    def test_lifecycle_is_known_and_archived_projects_stay_read_only(self):
        archived = {"aldervale", "iris", "fold"}
        for target in all_targets():
            with self.subTest(target=target.game_id):
                self.assertIn(target.lifecycle, {"active", "archived"})
                self.assertEqual(target.lifecycle == "archived", target.game_id in archived)


class TestTargetManifests(unittest.TestCase):
    def test_checked_in_manifests_match_the_registry(self):
        for target in all_targets():
            path = manifest_path(target, FOUNDRY_ROOT / "targets")
            with self.subTest(target=target.game_id):
                self.assertEqual(path.read_bytes(), manifest_bytes(target))

    def test_every_manifest_validates(self):
        for target in all_targets():
            with self.subTest(target=target.game_id):
                self.assertEqual(validate(manifest(target), target_ids()), [])

    def test_manifest_generation_is_read_only(self):
        before = _snapshot(all_targets())
        for target in all_targets():
            manifest(target)
        self.assertEqual(_snapshot(all_targets()), before)

    def test_check_reports_missing_manifests(self):
        with tempfile.TemporaryDirectory() as tmp:
            problems = check_manifests(Path(tmp))
        self.assertEqual(len(problems), len(all_targets()))
        self.assertTrue(all("missing manifest" in problem for problem in problems))

    def test_check_reports_stale_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for target in all_targets():
                write_manifest(target, out)
            stale = out / "afterimage.json"
            stale.write_text("{}\n", encoding="utf-8")
            problems = check_manifests(out)
        self.assertEqual(len(problems), 1)
        self.assertIn("afterimage.json: stale manifest", problems[0])


class TestTargetValidation(unittest.TestCase):
    def good(self):
        return copy.deepcopy(manifest(get_target("afterimage")))

    def check(self, mutate, field_prefix):
        value = mutate(self.good())
        errors = validate(value, target_ids())
        self.assertTrue(errors, f"expected rejection for {field_prefix}")
        self.assertTrue(
            any(error.startswith(field_prefix) for error in errors),
            f"no error names {field_prefix!r}: {errors}",
        )

    def test_rejects_unknown_target(self):
        self.check(lambda m: m.update(target_game="unknown") or m, "target_game:")

    def test_rejects_unknown_lifecycle(self):
        self.check(lambda m: m.update(lifecycle="retired") or m, "lifecycle:")

    def test_rejects_missing_field(self):
        def drop(manifest):
            del manifest["engine"]
            return manifest

        self.check(drop, "engine:")

    def test_rejects_project_traversal(self):
        self.check(lambda m: m.update(project="projects/../afterimage") or m, "project:")

    def test_rejects_missing_source(self):
        def mutate(manifest):
            manifest["content"][0]["sources"] = ["missing.js"]
            return manifest

        self.check(mutate, "content[0].sources:")

    def test_rejects_duplicate_items(self):
        def mutate(manifest):
            items = manifest["content"][0]["items"]
            items.append(items[0])
            return manifest

        self.check(mutate, "content[0].items:")

    def test_rejects_duplicate_surface(self):
        def mutate(manifest):
            manifest["content"].append(copy.deepcopy(manifest["content"][0]))
            return manifest

        self.check(mutate, "content[2].id:")

    def test_rejects_non_object(self):
        self.assertEqual(validate([]), ["manifest: must be a JSON object"])

    def test_rejects_bad_schema_version(self):
        self.check(lambda m: m.update(schema=2) or m, "schema:")


class TestTargetFiles(unittest.TestCase):
    def test_schema_is_valid_json(self):
        schema = json.loads(
            (FOUNDRY_ROOT / "schemas" / "target.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema"]["const"], 1)
        self.assertIn("target_game", schema["required"])


if __name__ == "__main__":
    unittest.main()
