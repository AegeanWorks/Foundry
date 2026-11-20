"""Keystone asset cockpit: validate a pack and prove it loads in the engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.layout import project_root  # noqa: E402
from generators.keystone_assets import (  # noqa: E402
    DEFAULT_NAME,
    DEFAULT_OUT,
    DEFAULT_SEED,
    check_pack,
)
from validators.keystone_assets import validate_pack  # noqa: E402

KEYSTONE_ROOT = project_root("keystone")


def _import_keystone():
    if str(KEYSTONE_ROOT) not in sys.path:
        sys.path.insert(0, str(KEYSTONE_ROOT))
    try:
        from keystone.assets import AssetRegistry
        from keystone.geometry import Material
        from keystone.math3d import Vec3
        from keystone.prefab import Prefab  # noqa: F401 - imported for its side-effect-free API
        from keystone.scene import Scene
    except ImportError as exc:
        raise RuntimeError(
            f"Keystone is not importable from {KEYSTONE_ROOT}: {exc}. "
            "Fix: run from the AIKit workspace with projects/keystone present."
        ) from exc
    return AssetRegistry, Material, Vec3, Prefab, Scene


def load_pack(pack_dir: Path) -> Tuple[object, Dict]:
    """Register every asset in manifest order and return (registry, manifest)."""
    AssetRegistry, Material, Vec3, Prefab, _Scene = _import_keystone()
    pack_dir = Path(pack_dir)
    manifest = json.loads((pack_dir / "keystone-assets.json").read_text(encoding="utf-8"))
    registry = AssetRegistry()
    for asset in manifest["assets"]:
        asset_id = asset["id"]
        kind = asset["kind"]
        if kind == "material":
            spec = asset["material"]
            payload = Material(
                color=Vec3(*spec["color"]),
                specular=spec["specular"],
                shininess=spec["shininess"],
                checker_scale=spec["checker_scale"],
                metallic=spec["metallic"],
                roughness=spec["roughness"],
                emissive=Vec3(*spec["emissive"]),
                texture=(
                    registry.require(spec["texture"]).payload
                    if spec["texture"] is not None
                    else None
                ),
            )
            registry.register(asset_id, payload, dependencies=asset["dependencies"])
        else:
            if kind == "prefab":
                registry.register_file(
                    asset_id,
                    pack_dir / asset["path"],
                    kind="prefab",
                    dependencies=asset["dependencies"],
                )
            else:
                registry.register_file(asset_id, pack_dir / asset["path"], kind=kind)
    return registry, manifest


def verify_pack(pack_dir: Path) -> str:
    """Validate a pack, load it through Keystone and instantiate its prefab."""
    errors = validate_pack(pack_dir)
    if errors:
        raise ValueError("; ".join(errors))
    registry, manifest = load_pack(pack_dir)
    for asset in manifest["assets"]:
        record = registry.require(asset["id"])
        if record.kind != asset["kind"]:
            raise ValueError(
                f"{asset['id']}: Keystone loaded kind {record.kind!r}, "
                f"manifest says {asset['kind']!r}"
            )
        if asset["kind"] == "material":
            payload = record.payload
            spec = asset["material"]
            actual = (
                list(payload.color),
                payload.specular,
                payload.shininess,
                payload.checker_scale,
                payload.metallic,
                payload.roughness,
                list(payload.emissive),
            )
            expected = (
                spec["color"],
                spec["specular"],
                spec["shininess"],
                spec["checker_scale"],
                spec["metallic"],
                spec["roughness"],
                spec["emissive"],
            )
            if actual != expected:
                raise ValueError(f"{asset['id']}: material parameters drifted on load")
    prefab_record = registry.require("prefab.starter")
    scene = _import_keystone()[4]()
    nodes = prefab_record.payload.instantiate(scene)
    if not nodes:
        raise ValueError("prefab.starter instantiated no roots")
    stats = registry.stats()
    return (
        f"OK {Path(pack_dir)}: {stats['total']} assets "
        f"(mesh={stats['kinds']['mesh']}, texture={stats['kinds']['texture']}, "
        f"material={stats['kinds']['material']}, prefab={stats['kinds']['prefab']}), "
        f"prefab nodes={prefab_record.payload.node_count}"
    )


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate and verify a Keystone asset pack.")
    ap.add_argument("--pack", default=str(DEFAULT_OUT))
    ap.add_argument("--check", action="store_true", help="verify the checked-in pack is fresh")
    ap.add_argument("--verify", action="store_true", help="load the pack through Keystone")
    args = ap.parse_args(argv)
    pack_dir = Path(args.pack)
    if args.check:
        problems = check_pack(pack_dir, DEFAULT_SEED, DEFAULT_NAME)
        for problem in problems:
            print(f"STALE {problem}")
        if problems:
            return 2
        print("OK checked-in pack is fresh")
        return 0
    errors = validate_pack(pack_dir)
    for error in errors:
        print(f"REJECT {error}")
    if errors:
        return 2
    print(f"OK manifest and file digests valid: {pack_dir}")
    if args.verify:
        try:
            print(verify_pack(pack_dir))
        except (ValueError, RuntimeError, OSError) as exc:
            print(f"REJECT {exc}")
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
