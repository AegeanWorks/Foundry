"""Generic game-asset-pack generator: file-backed assets copied verbatim.

Foundry is a Keystone extension: it generates Keystone-consumable packs and
copies authored files from game projects such as Shooter. Keystone's own assets
are never imported here; they stay owned by the engine. Each pack carries exact
bytes, provenance and digests so a consumer can install and verify it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.layout import project_root  # noqa: E402

MANIFEST_NAME = "game-assets.json"
SCHEMA_VERSION = 2
GENERATOR_NAME = "foundry.game-assets"
GENERATOR_VERSION = 1
DEFAULT_NAME = "runtime"
DEFAULT_SOURCE = "shooter"
DEFAULT_OUT = FOUNDRY_ROOT / "packs" / "shooter" / DEFAULT_NAME

# (asset id, kind, source file relative to root, path inside the pack, dependencies)
PACKS: Dict[str, Dict] = {
    "shooter": {
        "root": project_root("shooter") / "shooter" / "data",
        "project": "projects/shooter",
        "source_dir": "shooter/data",
        "assets": (
            ("mesh.cache_crate", "mesh", "cache_crate.obj", "meshes/cache_crate.obj", ()),
            (
                "material.cache",
                "material",
                "cache_material.kmaterial",
                "materials/cache_material.kmaterial",
                (),
            ),
            (
                "camera_path.campaign_clear",
                "camera_path",
                "campaign_clear.kpath",
                "camera_paths/campaign_clear.kpath",
                (),
            ),
            (
                "prefab.pickup_beacon",
                "prefab",
                "pickup_beacon.kprefab",
                "prefabs/pickup_beacon.kprefab",
                (),
            ),
            (
                "state.warden_core",
                "state",
                "warden_core.kstate",
                "states/warden_core.kstate",
                (),
            ),
        ),
    },
}


@dataclass(frozen=True)
class GameAssetPack:
    """A generated pack: relative file bytes plus the canonical manifest."""

    name: str
    files: Dict[str, bytes]
    manifest: Dict

    def manifest_bytes(self) -> bytes:
        return _canonical_json(self.manifest)


def generate(name: str = DEFAULT_NAME, source: str = DEFAULT_SOURCE) -> GameAssetPack:
    """Build one deterministic asset pack from a source project's files."""
    if not name or not all(char.islower() or char.isdigit() or char == "-" for char in name):
        raise ValueError("pack name must use lowercase letters, digits and dashes")
    if source not in PACKS:
        raise ValueError(f"unknown source {source!r}; expected one of {sorted(PACKS)}")
    spec = PACKS[source]
    files: Dict[str, bytes] = {}
    assets: List[Dict] = []
    for asset_id, kind, source_file, relative, dependencies in spec["assets"]:
        content = (spec["root"] / source_file).read_bytes()
        files[relative] = content
        assets.append(
            {
                "id": asset_id,
                "kind": kind,
                "path": relative,
                "sha256": hashlib.sha256(content).hexdigest(),
                "source": f"{spec['source_dir']}/{source_file}",
                "dependencies": list(dependencies),
            }
        )
    manifest = {
        "schema": SCHEMA_VERSION,
        "pack": name,
        "generator": {"name": GENERATOR_NAME, "version": GENERATOR_VERSION},
        "source": {"project": spec["project"], "root": spec["source_dir"]},
        "assets": assets,
    }
    return GameAssetPack(name=name, files=files, manifest=manifest)


def write_pack(out_dir: Path, name: str = DEFAULT_NAME, source: str = DEFAULT_SOURCE) -> Path:
    """Write the generated pack, creating directories as needed."""
    pack = generate(name, source)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for relative in sorted(pack.files):
        path = out_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pack.files[relative])
    (out_dir / MANIFEST_NAME).write_bytes(pack.manifest_bytes())
    return out_dir


def check_pack(out_dir: Path, name: str = DEFAULT_NAME, source: str = DEFAULT_SOURCE) -> List[str]:
    """Return one ``path: reason`` line per stale or missing pack file."""
    try:
        pack = generate(name, source)
    except OSError as exc:
        return [f"source files: cannot generate pack: {exc}"]
    out_dir = Path(out_dir)
    expected = dict(pack.files)
    expected[MANIFEST_NAME] = pack.manifest_bytes()
    problems: List[str] = []
    for relative in sorted(expected):
        path = out_dir / relative
        try:
            actual = path.read_bytes()
        except FileNotFoundError:
            problems.append(f"{relative}: missing file")
            continue
        except OSError as exc:
            problems.append(f"{relative}: cannot read: {exc}")
            continue
        if actual != expected[relative]:
            problems.append(f"{relative}: stale or modified; run generators/game_assets.py")
    return problems


def _canonical_json(payload: Dict) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate and check generic game asset packs.")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--name", default=DEFAULT_NAME)
    ap.add_argument("--source", default=DEFAULT_SOURCE, choices=sorted(PACKS))
    ap.add_argument("--check", action="store_true", help="verify the checked-in pack")
    args = ap.parse_args(argv)
    out_dir = Path(args.out)
    if args.check:
        problems = check_pack(out_dir, args.name, args.source)
        for problem in problems:
            print(f"STALE {problem}")
        print("OK" if not problems else f"{len(problems)} problem(s)")
        return 0 if not problems else 2
    print(f"WROTE {write_pack(out_dir, args.name, args.source)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
