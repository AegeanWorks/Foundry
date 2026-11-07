"""Keystone asset-pack validator: manifest shape, file digests and load order.

Stdlib only. Structural rules mirror schemas/keystone_assets.schema.json; the
filesystem, digest and dependency-order checks live here because JSON Schema
cannot express them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

ASSET_KINDS = ("mesh", "material", "texture", "prefab")
SUFFIX_KINDS = {".obj": "mesh", ".png": "texture", ".kprefab": "prefab"}
ID_RE = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
PACK_RE = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
TOP_FIELDS = {"schema", "pack", "seed", "generator", "assets"}
ASSET_FIELDS = {"id", "kind", "path", "sha256", "dependencies", "material"}
MATERIAL_FIELDS = {
    "color",
    "specular",
    "shininess",
    "checker_scale",
    "metallic",
    "roughness",
    "emissive",
    "texture",
}


def _is_int(value: Any) -> bool:
    return type(value) is int


def _is_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def _safe_relative(value: str) -> Optional[PurePosixPath]:
    if not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return None
    return path


def validate_pack(pack_dir: Path) -> List[str]:
    """Validate one pack directory and return ``field: reason`` lines."""
    manifest_path = Path(pack_dir) / "keystone-assets.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ["keystone-assets.json: file not found"]
    except UnicodeDecodeError as exc:
        return [f"keystone-assets.json: invalid encoding: {exc}"]
    except OSError as exc:
        return [f"keystone-assets.json: cannot read: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"keystone-assets.json: invalid JSON: {exc}"]
    return validate_manifest(manifest, Path(pack_dir))


def validate_manifest(manifest: Any, pack_dir: Path) -> List[str]:
    """Validate a parsed manifest against its pack directory."""
    errors: List[str] = []
    if not isinstance(manifest, dict):
        return ["manifest: must be a JSON object"]
    unknown = sorted(set(manifest) - TOP_FIELDS, key=repr)
    if unknown:
        errors.append(f"manifest: unknown fields {unknown}")
    for field in sorted(TOP_FIELDS):
        if field not in manifest:
            errors.append(f"{field}: missing required field")

    if "schema" in manifest and (not _is_int(manifest["schema"]) or manifest["schema"] != 1):
        errors.append(f"schema: must be 1, got {manifest.get('schema')!r}")
    pack = manifest.get("pack")
    if "pack" in manifest and (not isinstance(pack, str) or not PACK_RE.fullmatch(pack)):
        errors.append(f"pack: invalid pack name {pack!r}")
    seed = manifest.get("seed")
    if "seed" in manifest and (not _is_int(seed) or seed < 0):
        errors.append(f"seed: must be a non-negative integer, got {seed!r}")
    _validate_generator(manifest.get("generator"), errors)

    assets = manifest.get("assets")
    if "assets" in manifest:
        if not isinstance(assets, list) or not assets:
            errors.append("assets: must be a non-empty list")
        else:
            _validate_assets(assets, Path(pack_dir), errors)
    return errors


def _validate_generator(generator: Any, errors: List[str]) -> None:
    if not isinstance(generator, dict):
        errors.append("generator: must be an object")
        return
    unknown = sorted(set(generator) - {"name", "version"}, key=repr)
    if unknown:
        errors.append(f"generator: unknown fields {unknown}")
    name = generator.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("generator.name: must be a non-blank string")
    version = generator.get("version")
    if not _is_int(version) or version < 1:
        errors.append(f"generator.version: must be a positive integer, got {version!r}")


def _validate_assets(assets: List[Any], pack_dir: Path, errors: List[str]) -> None:
    seen: Dict[str, Dict] = {}
    for index, asset in enumerate(assets):
        field = f"assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{field}: must be an object")
            continue
        unknown = sorted(set(asset) - ASSET_FIELDS, key=repr)
        if unknown:
            errors.append(f"{field}: unknown fields {unknown}")
        for required in ("id", "kind", "path", "dependencies"):
            if required not in asset:
                errors.append(f"{field}.{required}: missing required field")
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not ID_RE.fullmatch(asset_id):
            errors.append(f"{field}.id: invalid asset id {asset_id!r}")
            continue
        if asset_id in seen:
            errors.append(f"{field}.id: duplicate asset id {asset_id!r}")
            continue
        seen[asset_id] = asset
        kind = asset.get("kind")
        if kind not in ASSET_KINDS:
            errors.append(f"{field}.kind: must be one of {ASSET_KINDS}, got {kind!r}")
            continue
        dependencies = _dependencies(asset.get("dependencies"), field, asset_id, seen, errors)
        _validate_path(asset, field, kind, pack_dir, errors)
        if kind == "material":
            _validate_material(asset, field, dependencies, seen, errors)
        elif kind == "prefab":
            _validate_prefab(asset, field, dependencies, pack_dir, seen, errors)


def _dependencies(
    value: Any,
    field: str,
    asset_id: str,
    seen: Dict[str, Dict],
    errors: List[str],
) -> List[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{field}.dependencies: must be a list of asset ids")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{field}.dependencies: duplicate dependency id")
    for dependency in value:
        if dependency == asset_id:
            errors.append(f"{field}.dependencies: asset cannot depend on itself")
        elif dependency not in seen:
            errors.append(f"{field}.dependencies: unknown or later-loaded asset {dependency!r}")
    return value


def _validate_path(asset: Dict, field: str, kind: str, pack_dir: Path, errors: List[str]) -> None:
    path = asset.get("path")
    if kind == "material":
        if path is not None:
            errors.append(f"{field}.path: material assets have no file path")
        if "sha256" in asset:
            errors.append(f"{field}.sha256: material assets have no file digest")
        return
    if not isinstance(path, str) or _safe_relative(path) is None:
        errors.append(f"{field}.path: invalid relative path {path!r}")
        return
    expected = SUFFIX_KINDS.get(PurePosixPath(path).suffix.lower())
    if expected != kind:
        errors.append(f"{field}.path: suffix does not match kind {kind!r}")
        return
    digest = asset.get("sha256")
    if not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
        errors.append(f"{field}.sha256: missing or invalid digest")
        return
    target = pack_dir / path
    if not target.is_file():
        errors.append(f"{field}.path: file does not exist: {path}")
        return
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual != digest:
        errors.append(f"{field}.sha256: digest mismatch for {path}")


def _validate_material(
    asset: Dict,
    field: str,
    dependencies: List[str],
    seen: Dict[str, Dict],
    errors: List[str],
) -> None:
    material = asset.get("material")
    if not isinstance(material, dict):
        errors.append(f"{field}.material: material assets need a material object")
        return
    unknown = sorted(set(material) - MATERIAL_FIELDS, key=repr)
    if unknown:
        errors.append(f"{field}.material: unknown fields {unknown}")
    for key in ("color", "emissive"):
        value = material.get(key)
        if not isinstance(value, list) or len(value) != 3 or not all(_is_number(v) for v in value):
            errors.append(f"{field}.material.{key}: must be three finite numbers")
    for key in ("specular", "shininess", "checker_scale", "metallic", "roughness"):
        if not _is_number(material.get(key)):
            errors.append(f"{field}.material.{key}: must be a finite number")
    texture = material.get("texture")
    if texture is not None:
        if not isinstance(texture, str) or texture not in seen:
            errors.append(f"{field}.material.texture: unknown or later-loaded texture {texture!r}")
        elif seen[texture].get("kind") != "texture":
            errors.append(f"{field}.material.texture: {texture!r} is not a texture")
        elif texture not in dependencies:
            errors.append(f"{field}.dependencies: missing material texture {texture!r}")


def _validate_prefab(
    asset: Dict,
    field: str,
    dependencies: List[str],
    pack_dir: Path,
    seen: Dict[str, Dict],
    errors: List[str],
) -> None:
    path = asset.get("path")
    if not isinstance(path, str):
        return
    try:
        prefab = json.loads((pack_dir / path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{field}.path: cannot read prefab: {exc}")
        return
    referenced = _prefab_asset_ids(prefab)
    for asset_id, kind in referenced:
        if asset_id not in seen:
            errors.append(f"{field}.path: prefab references unknown asset {asset_id!r}")
        elif seen[asset_id].get("kind") != kind:
            errors.append(f"{field}.path: prefab reference {asset_id!r} is not a {kind}")
        elif asset_id not in dependencies:
            errors.append(f"{field}.dependencies: missing prefab reference {asset_id!r}")


def _prefab_asset_ids(prefab: Any) -> List[tuple]:
    found: List[tuple] = []

    def visit(node: Any) -> None:
        if not isinstance(node, dict):
            return
        if node.get("mesh") is not None:
            found.append((node["mesh"], "mesh"))
        if node.get("material") is not None:
            found.append((node["material"], "material"))
        for child in node.get("children", []):
            visit(child)

    if isinstance(prefab, dict):
        for root in prefab.get("roots", []):
            visit(root)
    return found


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a Keystone asset pack.")
    ap.add_argument("pack", nargs="?", default=str(FOUNDRY_ROOT / "packs" / "keystone" / "starter"))
    args = ap.parse_args(argv)
    errors = validate_pack(Path(args.pack))
    for error in errors:
        print(f"REJECT {error}")
    print(f"{'OK' if not errors else 'INVALID'} {args.pack}")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
