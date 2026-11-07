"""Filesystem boundaries shared by the target adapters (read-only)."""

from __future__ import annotations

from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
# foundry lives at <portfolio>/projects/foundry; consumers sit beside it.
PORTFOLIO_ROOT = FOUNDRY_ROOT.parent.parent


def project_root(*parts: str) -> Path:
    """Resolve a consumer project below the portfolio's projects/ directory."""
    return PORTFOLIO_ROOT.joinpath("projects", *parts)
