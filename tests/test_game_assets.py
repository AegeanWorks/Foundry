"""Generic game-asset packs: deterministic generation, validation and install.

The point of the format is reuse: a pack authored from one game must install
into any other project as files plus a digest-verified manifest.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from generators.game_assets import (  # noqa: E402
    DEFAULT_OUT,
    MANIFEST_NAME,
    check_pack,
    generate,
    write_pack,
)
from tools.game_assets import install  # noqa: E402
from validators.game_assets import validate_pack  # noqa: E402


class TestGameAssetPack(unittest.TestCase):
    def test_generated_pack_is_deterministic(self):
        first = generate()
        second = generate()
        self.assertEqual(first.manifest_bytes(), second.manifest_bytes())
        self.assertEqual(first.files, second.files)

    def test_generated_pack_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = write_pack(Path(tmp) / "runtime")
            self.assertEqual(validate_pack(out), [])

    def test_checked_in_pack_is_fresh(self):
        self.assertEqual(check_pack(DEFAULT_OUT), [])

    def test_checked_in_pack_is_self_contained(self):
        manifest = json.loads((DEFAULT_OUT / MANIFEST_NAME).read_text(encoding="utf-8"))
        for asset in manifest["assets"]:
            path = asset["path"]
            with self.subTest(asset=asset["id"]):
                self.assertFalse(Path(path).is_absolute())
                self.assertNotIn("..", Path(path).parts)
                target = DEFAULT_OUT / path
                self.assertTrue(target.is_file())
                self.assertEqual(
                    hashlib.sha256(target.read_bytes()).hexdigest(), asset["sha256"]
                )

    def test_checked_in_pack_installs_without_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "game"
            install(DEFAULT_OUT, dest)
            self.assertEqual(validate_pack(dest), [])

    def test_generation_leaves_the_source_unchanged(self):
        from generators.game_assets import PACKS

        root = PACKS["shooter"]["root"]

        def snapshot():
            return {
                path.name: (
                    path.stat().st_size,
                    path.stat().st_mtime_ns,
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
                for path in root.iterdir()
                if path.is_file()
            }

        before = snapshot()
        generate()
        self.assertEqual(snapshot(), before)

    def test_relocating_the_source_does_not_change_the_pack(self):
        from generators.game_assets import PACKS

        spec = PACKS["shooter"]
        baseline = generate()
        with tempfile.TemporaryDirectory() as tmp:
            relocated = Path(tmp) / "moved" / "data"
            relocated.mkdir(parents=True)
            for _, _, source_file, _, _ in spec["assets"]:
                shutil.copy2(spec["root"] / source_file, relocated / source_file)
            PACKS["shooter"] = {**spec, "root": relocated}
            try:
                moved = generate()
            finally:
                PACKS["shooter"] = spec
        self.assertEqual(moved.files, baseline.files)
        self.assertEqual(moved.manifest_bytes(), baseline.manifest_bytes())
        self.assertEqual(moved.manifest_bytes(), (DEFAULT_OUT / MANIFEST_NAME).read_bytes())

    def test_every_runtime_asset_is_packed(self):
        manifest = generate().manifest
        kinds = {asset["kind"] for asset in manifest["assets"]}
        self.assertEqual(kinds, {"mesh", "material", "camera_path", "prefab", "state"})
        ids = {asset["id"] for asset in manifest["assets"]}
        self.assertEqual(
            ids,
            {
                "mesh.cache_crate",
                "material.cache",
                "camera_path.campaign_clear",
                "prefab.pickup_beacon",
                "state.warden_core",
            },
        )

    def test_rejects_digest_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = write_pack(Path(tmp) / "runtime")
            target = out / "meshes" / "cache_crate.obj"
            target.write_bytes(target.read_bytes() + b"\n")
            self.assertTrue(any("digest mismatch" in line for line in validate_pack(out)))

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = write_pack(Path(tmp) / "runtime")
            manifest = json.loads((out / MANIFEST_NAME).read_text(encoding="utf-8"))
            manifest["assets"][0]["path"] = "../escape.obj"
            (out / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
            self.assertTrue(any("invalid relative path" in line for line in validate_pack(out)))

    def test_rejects_forward_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = write_pack(Path(tmp) / "runtime")
            manifest = json.loads((out / MANIFEST_NAME).read_text(encoding="utf-8"))
            manifest["assets"][0]["dependencies"] = ["state.warden_core"]
            (out / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
            self.assertTrue(any("later-loaded asset" in line for line in validate_pack(out)))


class TestShooterSourcePack(unittest.TestCase):
    def test_provenance_names_the_owning_game(self):
        source = generate().manifest["source"]
        self.assertEqual(source["project"], "projects/shooter")
        self.assertEqual(source["root"], "shooter/data")

    def test_keystone_is_not_an_import_source(self):
        from generators.game_assets import PACKS

        self.assertEqual(set(PACKS), {"shooter"})
        with self.assertRaises(ValueError):
            generate(source="keystone")


class TestGameAssetInstall(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = write_pack(root / "pack")
            dest = root / "game"
            lines = install(pack, dest, dry_run=True)
            self.assertTrue(lines)
            self.assertFalse(dest.exists())

    def test_install_copies_files_and_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = write_pack(root / "pack")
            dest = root / "game"
            install(pack, dest)
            self.assertEqual(validate_pack(dest), [])
            for asset in json.loads((dest / MANIFEST_NAME).read_text(encoding="utf-8"))["assets"]:
                path = dest / asset["path"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), asset["sha256"])

    def test_install_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = write_pack(root / "pack")
            dest = root / "game"
            install(pack, dest)
            with self.assertRaises(ValueError):
                install(pack, dest)
            install(pack, dest, force=True)
            self.assertEqual(validate_pack(dest), [])

    def test_install_refuses_invalid_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = write_pack(root / "pack")
            (pack / "meshes" / "cache_crate.obj").write_bytes(b"tampered")
            dest = root / "game"
            with self.assertRaises(ValueError):
                install(pack, dest)
            self.assertFalse(dest.exists())

    def test_install_preserves_source_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = write_pack(root / "pack")
            source = (pack / "meshes" / "cache_crate.obj").read_bytes()
            install(pack, root / "game")
            self.assertEqual((pack / "meshes" / "cache_crate.obj").read_bytes(), source)
