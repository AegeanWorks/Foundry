"""Frozen target facts shared by adapters, validators and generators."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple


@dataclass(frozen=True)
class ContentSurface:
    """One authored content surface a target exposes to foundry."""

    id: str
    kind: str
    sources: Tuple[str, ...]
    items: Tuple[str, ...]


@dataclass(frozen=True)
class TargetFacts:
    """The read-only facts foundry needs to target one consumer project."""

    game_id: str
    display_name: str
    project_root: Path
    lifecycle: str
    engine: str
    test_command: str
    pack_major: int
    content: Tuple[ContentSurface, ...]

    def as_manifest(self, portfolio_root: Path) -> Dict:
        """Serialize the facts as the canonical target manifest."""
        project = self.project_root.relative_to(portfolio_root).as_posix()
        return {
            "schema": 1,
            "target_game": self.game_id,
            "display_name": self.display_name,
            "project": project,
            "lifecycle": self.lifecycle,
            "engine": self.engine,
            "test_command": self.test_command,
            "pack_major": self.pack_major,
            "content": [
                {
                    "id": surface.id,
                    "kind": surface.kind,
                    "sources": list(surface.sources),
                    "items": list(surface.items),
                }
                for surface in self.content
            ],
        }
