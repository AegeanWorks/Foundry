"""Generic game-asset packs: deterministic generation, validation and install.

The point of the format is reuse: a pack authored from one game must install
into any other project as files plus a digest-verified manifest.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from generators.game_assets import (  # noqa: E402
    DEFAULT_OUT,
    DEFAULT_OUT_KEYSTONE,
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


class TestSecondSourcePack(unittest.TestCase):
    def test_keystone_pack_generates_and_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = write_pack(Path(tmp) / "runtime", source="keystone")
            self.assertEqual(validate_pack(out), [])

    def test_keystone_checked_in_pack_is_fresh(self):
        self.assertEqual(check_pack(DEFAULT_OUT_KEYSTONE, source="keystone"), [])

    def test_provenance_names_the_owning_game(self):
        shooter = generate().manifest["source"]
        keystone = generate(source="keystone").manifest["source"]
        self.assertEqual(shooter["project"], "projects/shooter")
        self.assertEqual(keystone["project"], "projects/keystone")
        self.assertNotEqual(shooter["root"], keystone["root"])

    def test_one_installer_serves_two_games(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shooter = write_pack(root / "shooter-pack")
            keystone = write_pack(root / "keystone-pack", source="keystone")
            for pack, game in ((shooter, "game-a"), (keystone, "game-b")):
                with self.subTest(game=game):
                    dest = root / game
                    install(pack, dest)
                    self.assertEqual(validate_pack(dest), [])


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
