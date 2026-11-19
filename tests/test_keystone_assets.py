"""Keystone asset-pack tests: determinism, integrity and engine compatibility."""

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

from generators.keystone_assets import (  # noqa: E402
    DEFAULT_OUT,
    DEFAULT_SEED,
    MANIFEST_NAME,
    check_pack,
    generate,
    write_pack,
)
from validators.keystone_assets import validate_pack  # noqa: E402


def _keystone_available() -> bool:
    try:
        from adapters.layout import PORTFOLIO_ROOT

        sys.path.insert(0, str(PORTFOLIO_ROOT / "projects" / "keystone"))
        from keystone.assets import AssetRegistry  # noqa: F401
    except ImportError:
        return False
    return True


class TestKeystonePackGenerator(unittest.TestCase):
    def test_generate_is_deterministic(self):
        first = generate(42)
        second = generate(42)
        self.assertEqual(first.manifest_bytes(), second.manifest_bytes())
        self.assertEqual(first.files, second.files)

    def test_distinct_seeds_change_content(self):
        self.assertNotEqual(generate(42).manifest_bytes(), generate(43).manifest_bytes())

    def test_generated_pack_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "starter"
            write_pack(DEFAULT_SEED, out)
            self.assertEqual(validate_pack(out), [])

    def test_checked_in_pack_is_fresh(self):
        self.assertEqual(check_pack(DEFAULT_OUT), [])

    def test_manifest_records_every_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "starter"
            write_pack(DEFAULT_SEED, out)
            manifest = json.loads((out / MANIFEST_NAME).read_text(encoding="utf-8"))
            paths = {asset["path"] for asset in manifest["assets"] if asset["path"]}
            for relative in paths:
                self.assertTrue((out / relative).is_file(), relative)
            self.assertEqual(len(paths), 7)

    def test_pack_includes_octahedron_mesh(self):
        pack = generate(DEFAULT_SEED)
        assets = {asset["id"]: asset for asset in pack.manifest["assets"]}
        self.assertIn("mesh.octahedron", assets)
        octahedron = assets["mesh.octahedron"]
        self.assertEqual(octahedron["kind"], "mesh")
        self.assertEqual(pack.files[octahedron["path"]].count(b"f "), 8)


class TestKeystonePackValidation(unittest.TestCase):
    def pack(self, tmp: str) -> Path:
        out = Path(tmp) / "starter"
        write_pack(DEFAULT_SEED, out)
        return out

    def test_rejects_tampered_texture(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.pack(tmp)
            texture = out / "textures" / "texture_checker.png"
            texture.write_bytes(texture.read_bytes() + b"x")
            errors = validate_pack(out)
        self.assertTrue(any("digest mismatch" in error for error in errors), errors)

    def test_rejects_missing_material_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.pack(tmp)
            manifest_path = out / MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for asset in manifest["assets"]:
                if asset["id"] == "material.base":
                    asset["dependencies"] = []
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_pack(out)
        self.assertTrue(any("missing material texture" in error for error in errors), errors)

    def test_rejects_missing_prefab_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.pack(tmp)
            manifest_path = out / MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for asset in manifest["assets"]:
                if asset["id"] == "prefab.starter":
                    asset["dependencies"] = [
                        item for item in asset["dependencies"] if item != "material.base"
                    ]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_pack(out)
        self.assertTrue(any("missing prefab reference" in error for error in errors), errors)

    def test_rejects_later_loaded_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.pack(tmp)
            manifest_path = out / MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"] = list(reversed(manifest["assets"]))
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_pack(out)
        self.assertTrue(any("later-loaded" in error for error in errors), errors)

    def test_rejects_duplicate_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.pack(tmp)
            manifest_path = out / MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"].append(copy.deepcopy(manifest["assets"][0]))
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_pack(out)
        self.assertTrue(any("duplicate asset id" in error for error in errors), errors)

    def test_schema_file_is_valid_json(self):
        schema = json.loads(
            (FOUNDRY_ROOT / "schemas" / "keystone_assets.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema"]["const"], 1)
        self.assertIn("assets", schema["required"])


@unittest.skipUnless(_keystone_available(), "Keystone is not importable")
class TestKeystoneRuntime(unittest.TestCase):
    def test_checked_in_pack_loads_and_instantiates(self):
        from tools.keystone_assets import verify_pack

        summary = verify_pack(DEFAULT_OUT)
        self.assertIn("OK", summary)
        self.assertIn("prefab nodes=5", summary)

    def test_mesh_winding_matches_normals(self):
        from keystone.obj_loader import load_obj

        for name in ("mesh_cube", "mesh_plane", "mesh_crystal", "mesh_octahedron"):
            with self.subTest(mesh=name):
                mesh = load_obj(DEFAULT_OUT / "meshes" / f"{name}.obj")
                for offset in range(0, len(mesh.indices), 3):
                    a, b, c = (mesh.positions[i] for i in mesh.indices[offset:offset + 3])
                    normal = mesh.normals[mesh.indices[offset]]
                    cross = _cross(_sub(b, a), _sub(c, a))
                    self.assertGreaterEqual(_dot(cross, normal), -1e-6, f"{name} winding")

    def test_texture_png_roundtrip(self):
        from keystone.texture import TextureData

        texture = TextureData.from_png(DEFAULT_OUT / "textures" / "texture_checker.png")
        self.assertEqual((texture.width, texture.height), (32, 32))
        self.assertEqual(len(texture.rgba), 32 * 32 * 4)


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


if __name__ == "__main__":
    unittest.main()
