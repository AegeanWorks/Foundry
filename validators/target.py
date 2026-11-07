"""Target-manifest validator: every registered target ships a truthful manifest.

Stdlib only. Structural rules mirror schemas/target.schema.json; the
filesystem checks (project and source paths exist, no traversal) live here
because JSON Schema cannot express them.
"""

from __future__ import annotations

import argparse
import glob as _glob
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, List, Optional

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.layout import PORTFOLIO_ROOT  # noqa: E402
from adapters.registry import target_ids  # noqa: E402

TARGET_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,31}$")
SURFACE_RE = re.compile(r"^[a-z][a-z0-9_]{1,31}$")
PROJECT_RE = re.compile(r"^projects/[A-Za-z0-9._/-]+$")
SOURCE_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
LIFECYCLES = {"active", "archived"}
KINDS = {"catalog", "rules"}

TOP_FIELDS = {
    "schema",
    "target_game",
    "display_name",
    "project",
    "lifecycle",
    "engine",
    "test_command",
    "pack_major",
    "content",
}
SURFACE_FIELDS = {"id", "kind", "sources", "items"}


def _is_int(value: Any) -> bool:
    return type(value) is int


def _relative_parts(value: str) -> Optional[PurePosixPath]:
    if not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return None
    return path


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except (OSError, ValueError):
        return False
    return True


def validate(
    manifest: Any,
    known_ids: Iterable[str] | None = None,
    portfolio_root: Path = PORTFOLIO_ROOT,
) -> List[str]:
    """Return a list of ``field: reason`` violations (empty == valid)."""
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

    game = manifest.get("target_game")
    if "target_game" in manifest:
        if not isinstance(game, str) or not TARGET_RE.fullmatch(game):
            errors.append(f"target_game: invalid target id {game!r}")
        elif known_ids is not None and game not in set(known_ids):
            errors.append(f"target_game: unknown target {game!r}")

    display = manifest.get("display_name")
    if "display_name" in manifest:
        if not isinstance(display, str) or not (1 <= len(display) <= 60):
            errors.append("display_name: must be a 1-60 character string")

    project = manifest.get("project")
    project_dir: Optional[Path] = None
    if "project" in manifest:
        if not isinstance(project, str) or not PROJECT_RE.fullmatch(project):
            errors.append(f"project: must be a projects/ relative path, got {project!r}")
        elif _relative_parts(project) is None:
            errors.append(f"project: path traversal is not allowed, got {project!r}")
        else:
            project_dir = portfolio_root / project
            if not project_dir.is_dir() or not _inside(project_dir, portfolio_root):
                errors.append(f"project: directory does not exist: {project}")
                project_dir = None

    lifecycle = manifest.get("lifecycle")
    if "lifecycle" in manifest and lifecycle not in LIFECYCLES:
        errors.append(f"lifecycle: must be one of {sorted(LIFECYCLES)}, got {lifecycle!r}")

    engine = manifest.get("engine")
    if "engine" in manifest:
        if not isinstance(engine, str) or not (1 <= len(engine) <= 40):
            errors.append("engine: must be a 1-40 character string")

    test_command = manifest.get("test_command")
    if "test_command" in manifest:
        if not isinstance(test_command, str) or not (1 <= len(test_command) <= 200):
            errors.append("test_command: must be a 1-200 character string")

    major = manifest.get("pack_major")
    if "pack_major" in manifest:
        if not _is_int(major) or not (1 <= major <= 9):
            errors.append(f"pack_major: must be an integer within [1, 9], got {major!r}")

    content = manifest.get("content")
    if "content" in manifest:
        if not isinstance(content, list) or not content:
            errors.append("content: must be a non-empty list")
        else:
            seen_surfaces = set()
            for index, surface in enumerate(content):
                _validate_surface(
                    surface, index, project_dir, seen_surfaces, errors
                )
    return errors


def _validate_surface(
    surface: Any,
    index: int,
    project_dir: Optional[Path],
    seen_surfaces: set,
    errors: List[str],
) -> None:
    field = f"content[{index}]"
    if not isinstance(surface, dict):
        errors.append(f"{field}: must be an object")
        return
    unknown = sorted(set(surface) - SURFACE_FIELDS, key=repr)
    if unknown:
        errors.append(f"{field}: unknown fields {unknown}")
    for required in sorted(SURFACE_FIELDS):
        if required not in surface:
            errors.append(f"{field}.{required}: missing required field")

    surface_id = surface.get("id")
    if "id" in surface:
        if not isinstance(surface_id, str) or not SURFACE_RE.fullmatch(surface_id):
            errors.append(f"{field}.id: invalid content id {surface_id!r}")
        elif surface_id in seen_surfaces:
            errors.append(f"{field}.id: duplicate content id {surface_id!r}")
        else:
            seen_surfaces.add(surface_id)

    kind = surface.get("kind")
    if "kind" in surface and kind not in KINDS:
        errors.append(f"{field}.kind: must be one of {sorted(KINDS)}, got {kind!r}")

    sources = surface.get("sources")
    if "sources" in surface:
        if not isinstance(sources, list) or not sources:
            errors.append(f"{field}.sources: must be a non-empty list")
        else:
            seen_sources = set()
            for source in sources:
                _validate_source(source, field, project_dir, seen_sources, errors)

    items = surface.get("items")
    if "items" in surface:
        if not isinstance(items, list) or not items:
            errors.append(f"{field}.items: must be a non-empty list")
        else:
            seen_items = set()
            for item in items:
                if not isinstance(item, str) or not (1 <= len(item) <= 120):
                    errors.append(f"{field}.items: every item must be a 1-120 character string")
                    continue
                if item in seen_items:
                    errors.append(f"{field}.items: duplicate item {item!r}")
                    continue
                seen_items.add(item)


def _validate_source(
    source: Any,
    field: str,
    project_dir: Optional[Path],
    seen_sources: set,
    errors: List[str],
) -> None:
    if not isinstance(source, str) or not SOURCE_RE.fullmatch(source):
        errors.append(f"{field}.sources: invalid source path {source!r}")
        return
    parts = _relative_parts(source)
    if parts is None:
        errors.append(f"{field}.sources: path traversal is not allowed, got {source!r}")
        return
    if source in seen_sources:
        errors.append(f"{field}.sources: duplicate source {source!r}")
        return
    seen_sources.add(source)
    if project_dir is None:
        return
    target = project_dir / source
    if not target.is_file() or not _inside(target, project_dir):
        errors.append(f"{field}.sources: file does not exist: {source}")


def validate_file(path: Path, known_ids: Iterable[str] | None = None) -> List[str]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{path.name}: file not found"]
    except UnicodeDecodeError as exc:
        return [f"{path.name}: invalid encoding (must be utf-8): {exc}"]
    except OSError as exc:
        return [f"{path.name}: cannot read file: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON: {exc}"]
    return [f"{path.name}: {error}" for error in validate(manifest, known_ids)]


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate foundry target manifests.")
    ap.add_argument("manifests", nargs="+", help="Manifest JSON files to validate")
    args = ap.parse_args(argv)
    files: List[str] = []
    for pattern in args.manifests:
        hits = sorted(_glob.glob(pattern, recursive=True))
        files.extend(hits if hits else [pattern])
    failures = 0
    known = target_ids()
    for name in files:
        errors = validate_file(Path(name), known)
        if errors:
            failures += 1
            for error in errors:
                print(f"REJECT {error}")
        else:
            print(f"OK {name}")
    print(f"{len(files) - failures}/{len(files)} valid")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
