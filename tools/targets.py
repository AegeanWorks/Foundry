"""Target cockpit: list registered targets, write manifests, verify freshness."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.base import TargetFacts  # noqa: E402
from adapters.registry import all_targets  # noqa: E402
from generators.target import DEFAULT_OUT, check_manifests, write_manifest  # noqa: E402


def list_targets() -> None:
    print(f"{'TARGET':<16} {'LIFECYCLE':<10} {'ENGINE':<10} {'SURFACES':>8} {'ITEMS':>6}  PROJECT")
    for target in all_targets():
        surfaces = len(target.content)
        items = sum(len(surface.items) for surface in target.content)
        print(
            f"{target.game_id:<16} {target.lifecycle:<10} {target.engine:<10} "
            f"{surfaces:>8} {items:>6}  {target.project_root.name}"
        )


def _selected(targets: List[TargetFacts], out_dir: Path, check: bool) -> int:
    if check:
        problems = check_manifests(out_dir)
        for problem in problems:
            print(f"STALE {problem}")
        print(f"{len(targets) - len(problems)}/{len(targets)} up to date")
        return 0 if not problems else 2
    for target in targets:
        print(f"WROTE {write_manifest(target, out_dir)}")
    return 0


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="List, write or check foundry targets.")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--write", action="store_true", help="write every target manifest")
    ap.add_argument("--check", action="store_true", help="verify checked-in manifests")
    args = ap.parse_args(argv)
    targets = list(all_targets())
    if args.write or args.check:
        return _selected(targets, Path(args.out), args.check)
    list_targets()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
