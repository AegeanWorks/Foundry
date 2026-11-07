"""Portfolio analysis: classify every project and prove target coverage."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

from adapters.layout import PORTFOLIO_ROOT  # noqa: E402
from adapters.registry import all_targets  # noqa: E402

PLAYABLE_TOPICS = {
    "game",
    "browser-game",
    "roguelike",
    "rpg",
    "puzzle",
    "shooter",
    "artificial-life",
}
ENGINE_TOPICS = {"game-engine"}


@dataclass(frozen=True)
class ProjectAnalysis:
    """One project's manifest facts and portfolio classification."""

    name: str
    path: Path
    topics: Tuple[str, ...]
    ui_kind: str
    test_command: str
    archived: bool

    @property
    def kind(self) -> str:
        if ENGINE_TOPICS.intersection(self.topics):
            return "engine"
        if PLAYABLE_TOPICS.intersection(self.topics):
            return "game"
        return "non-game"


def scan(projects_root: Path = PORTFOLIO_ROOT) -> Tuple[ProjectAnalysis, ...]:
    """Read every project.json under projects/ and projects/archive/."""
    found: List[ProjectAnalysis] = []
    for base in (projects_root / "projects", projects_root / "projects" / "archive"):
        if not base.is_dir():
            continue
        for directory in sorted(base.iterdir()):
            manifest = directory / ".aikit" / "project.json"
            if not directory.is_dir() or not manifest.is_file() or directory.name == "foundry":
                continue
            data = json.loads(manifest.read_text(encoding="utf-8"))
            found.append(
                ProjectAnalysis(
                    name=directory.name,
                    path=directory,
                    topics=tuple(str(topic) for topic in data.get("topics", [])),
                    ui_kind=str(data.get("ui_kind", "-")),
                    test_command=str(data.get("test_command", "-")),
                    archived=base.name == "archive",
                )
            )
    return tuple(found)


def target_paths() -> Dict[Path, str]:
    """Map each registered target's project directory to its target id."""
    return {target.project_root.resolve(): target.game_id for target in all_targets()}


def analyze(projects: Iterable[ProjectAnalysis] | None = None) -> List[Dict[str, object]]:
    """Return one JSON-safe row per project, including target coverage."""
    rows = []
    targets = target_paths()
    for project in scan() if projects is None else projects:
        target = targets.get(project.path.resolve())
        rows.append(
            {
                "project": project.name,
                "kind": project.kind,
                "target": target,
                "archived": project.archived,
                "ui": project.ui_kind,
                "topics": list(project.topics),
            }
        )
    return rows


def check(projects: Iterable[ProjectAnalysis] | None = None) -> List[str]:
    """Return coverage problems: playable projects without a target, dead targets."""
    projects = scan() if projects is None else tuple(projects)
    targets = target_paths()
    known_paths = {project.path.resolve() for project in projects}
    problems = [
        f"{project.name}: {project.kind} project has no foundry target"
        for project in projects
        if project.kind in {"game", "engine"} and project.path.resolve() not in targets
    ]
    problems.extend(
        f"{game_id}: target path is not a scanned project: {path}"
        for path, game_id in sorted(targets.items())
        if path not in known_paths
    )
    return problems


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Classify portfolio projects and target coverage.")
    ap.add_argument("--json", action="store_true", help="emit JSON rows")
    ap.add_argument("--check", action="store_true", help="fail when a playable project is not a target")
    args = ap.parse_args(argv)
    if args.check:
        problems = check()
        for problem in problems:
            print(f"MISSING {problem}")
        print(f"{'OK' if not problems else 'INCOMPLETE'} portfolio coverage")
        return 0 if not problems else 2
    rows = analyze()
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    print(f"{'PROJECT':<28} {'KIND':<10} {'TARGET':<24} ARCHIVED")
    for row in rows:
        print(
            f"{row['project']:<28} {row['kind']:<10} "
            f"{row['target'] or '-':<24} {'yes' if row['archived'] else 'no'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
