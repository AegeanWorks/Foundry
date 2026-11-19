"""Install a validated game asset pack into a consumer project.

The install is engine-agnostic: it copies the pack's files and manifest into
the destination, never edits consumer code, and re-validates the result. Use
``--dry-run`` to see the plan and ``--force`` to replace an existing install.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from validators.game_assets import MANIFEST_NAME, validate_pack  # noqa: E402


def install(
    pack_dir: Path,
    dest_dir: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> List[str]:
    """Validate, plan and optionally perform an install; return the plan lines.

    Raises ``ValueError`` for an invalid pack or when a target file already
    exists and ``force`` is false. Nothing is written on a refusal or dry run.
    """
    pack_dir = Path(pack_dir)
    dest_dir = Path(dest_dir)
    problems = validate_pack(pack_dir)
    if problems:
        raise ValueError("invalid pack: " + "; ".join(problems))

    manifest = json.loads((pack_dir / MANIFEST_NAME).read_text(encoding="utf-8"))
    copies = [(pack_dir / asset["path"], dest_dir / asset["path"]) for asset in manifest["assets"]]
    targets = [destination for _, destination in copies] + [dest_dir / MANIFEST_NAME]
    for target in targets:
        if target.exists() and not force:
            raise ValueError(f"refusing to overwrite existing file: {target}")

    lines = [f"copy {source} -> {destination}" for source, destination in copies]
    lines.append(f"write {dest_dir / MANIFEST_NAME}")
    if dry_run:
        return lines

    for source, destination in copies:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / MANIFEST_NAME).write_bytes((pack_dir / MANIFEST_NAME).read_bytes())

    problems = validate_pack(dest_dir)
    if problems:
        raise ValueError("installed pack failed validation: " + "; ".join(problems))
    return lines


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Install a Foundry game asset pack.")
    sub = ap.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="validate a pack directory")
    check.add_argument("--pack", required=True)
    install_ap = sub.add_parser("install", help="copy a pack into a consumer project")
    install_ap.add_argument("--pack", required=True)
    install_ap.add_argument("--dest", required=True)
    install_ap.add_argument("--dry-run", action="store_true")
    install_ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    if args.command == "check":
        problems = validate_pack(Path(args.pack))
        for problem in problems:
            print(f"REJECT {problem}")
        print("OK" if not problems else f"{len(problems)} error(s)")
        return 0 if not problems else 2
    try:
        for line in install(
            Path(args.pack),
            Path(args.dest),
            force=args.force,
            dry_run=args.dry_run,
        ):
            print(line)
    except (OSError, ValueError) as exc:
        print(f"REFUSED {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
