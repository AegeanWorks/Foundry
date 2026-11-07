"""Target manifest generator: deterministic bytes from read-only adapter facts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.base import TargetFacts  # noqa: E402
from adapters.layout import PORTFOLIO_ROOT  # noqa: E402
from adapters.registry import all_targets  # noqa: E402

DEFAULT_OUT = FOUNDRY_ROOT / "targets"


def manifest(target: TargetFacts) -> dict:
    """Build the canonical manifest dict for one target."""
    return target.as_manifest(PORTFOLIO_ROOT)


def manifest_bytes(target: TargetFacts) -> bytes:
    """Serialize canonically so regeneration is byte-identical."""
    return (json.dumps(manifest(target), sort_keys=True, indent=2) + "\n").encode("utf-8")


def manifest_path(target: TargetFacts, out_dir: Path) -> Path:
    return out_dir / f"{target.game_id}.json"


def write_manifest(target: TargetFacts, out_dir: Path) -> Path:
    path = manifest_path(target, out_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(manifest_bytes(target))
    return path


def check_manifests(out_dir: Path) -> List[str]:
    """Return one ``path: reason`` line per stale or missing manifest."""
    problems: List[str] = []
    for target in all_targets():
        path = manifest_path(target, out_dir)
        try:
            actual = path.read_bytes()
        except FileNotFoundError:
            problems.append(f"{path.name}: missing manifest")
            continue
        except OSError as exc:
            problems.append(f"{path.name}: cannot read: {exc}")
            continue
        if actual != manifest_bytes(target):
            problems.append(f"{path.name}: stale manifest; run generators/target.py")
    return problems


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate and check foundry target manifests.")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--check", action="store_true", help="verify checked-in manifests")
    args = ap.parse_args(argv)
    out_dir = Path(args.out)
    if args.check:
        problems = check_manifests(out_dir)
        for problem in problems:
            print(f"STALE {problem}")
        print(f"{len(all_targets()) - len(problems)}/{len(all_targets())} up to date")
        return 0 if not problems else 2
    for target in all_targets():
        print(f"WROTE {write_manifest(target, out_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
