"""Generic game-asset-pack validator: shape, provenance, digests and load order.

Stdlib only. Structural rules mirror schemas/game_assets.schema.json; the
filesystem, digest and dependency checks live here because JSON Schema cannot
express them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

MANIFEST_NAME = "game-assets.json"
SCHEMA_VERSION = 2
ASSET_KINDS = ("mesh", "texture", "material", "prefab", "state", "camera_path")
SUFFIX_KINDS = {
    ".obj": "mesh",
    ".png": "texture",
    ".kmaterial": "material",
    ".kprefab": "prefab",
    ".kstate": "state",
    ".kpath": "camera_path",
}
ID_RE = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
PACK_RE = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
PROJECT_RE = re.compile(r"^projects/[A-Za-z0-9._/-]+$")
TOP_FIELDS = {"schema", "pack", "generator", "source", "assets"}
ASSET_FIELDS = {"id", "kind", "path", "sha256", "source", "dependencies"}


def _is_int(value: Any) -> bool:
    return type(value) is int


def _safe_relative(value: Any) -> Optional[PurePosixPath]:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return None
    return path


def validate_pack(pack_dir: Path) -> List[str]:
    """Validate one pack directory and return ``field: reason`` lines."""
    manifest_path = Path(pack_dir) / MANIFEST_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{MANIFEST_NAME}: file not found"]
    except UnicodeDecodeError as exc:
        return [f"{MANIFEST_NAME}: invalid encoding: {exc}"]
    except OSError as exc:
        return [f"{MANIFEST_NAME}: cannot read: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_NAME}: invalid JSON: {exc}"]
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

    if "schema" in manifest and (not _is_int(manifest["schema"]) or manifest["schema"] != SCHEMA_VERSION):
        errors.append(f"schema: must be {SCHEMA_VERSION}, got {manifest.get('schema')!r}")
    pack = manifest.get("pack")
    if "pack" in manifest and (not isinstance(pack, str) or not PACK_RE.fullmatch(pack)):
        errors.append(f"pack: invalid pack name {pack!r}")
    _validate_generator(manifest.get("generator"), errors)
    _validate_source(manifest.get("source"), errors)

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


def _validate_source(source: Any, errors: List[str]) -> None:
    if not isinstance(source, dict):
        errors.append("source: must be an object")
        return
    unknown = sorted(set(source) - {"project", "root"}, key=repr)
    if unknown:
        errors.append(f"source: unknown fields {unknown}")
    project = source.get("project")
    if not isinstance(project, str) or not PROJECT_RE.fullmatch(project):
        errors.append(f"source.project: must be a projects/ relative path, got {project!r}")
    root = source.get("root")
    if _safe_relative(root) is None:
        errors.append(f"source.root: invalid relative path {root!r}")


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
        for required in sorted(ASSET_FIELDS):
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
        _validate_dependencies(asset.get("dependencies"), field, asset_id, seen, errors)
        _validate_file(asset, field, kind, pack_dir, errors)
        if _safe_relative(asset.get("source")) is None:
            errors.append(f"{field}.source: invalid relative path {asset.get('source')!r}")


def _validate_dependencies(
    value: Any,
    field: str,
    asset_id: str,
    seen: Dict[str, Dict],
    errors: List[str],
) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{field}.dependencies: must be a list of asset ids")
        return
    if len(value) != len(set(value)):
        errors.append(f"{field}.dependencies: duplicate dependency id")
    for dependency in value:
        if dependency == asset_id:
            errors.append(f"{field}.dependencies: asset cannot depend on itself")
        elif dependency not in seen:
            errors.append(f"{field}.dependencies: unknown or later-loaded asset {dependency!r}")


def _validate_file(asset: Dict, field: str, kind: str, pack_dir: Path, errors: List[str]) -> None:
    path = asset.get("path")
    relative = _safe_relative(path)
    if relative is None:
        errors.append(f"{field}.path: invalid relative path {path!r}")
        return
    expected = SUFFIX_KINDS.get(relative.suffix.lower())
    if expected != kind:
        errors.append(f"{field}.path: suffix does not match kind {kind!r}")
        return
    digest = asset.get("sha256")
    if not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
        errors.append(f"{field}.sha256: missing or invalid digest")
        return
    target = pack_dir / relative
    if not target.is_file():
        errors.append(f"{field}.path: file does not exist: {path}")
        return
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        errors.append(f"{field}.sha256: digest mismatch for {path}")


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a generic Foundry game asset pack.")
    ap.add_argument("pack", help="pack directory")
    args = ap.parse_args(argv)
    errors = validate_pack(Path(args.pack))
    for error in errors:
        print(f"REJECT {error}")
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
