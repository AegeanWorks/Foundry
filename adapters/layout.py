"""Filesystem boundaries shared by the target adapters (read-only)."""

from __future__ import annotations

from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
# foundry lives at <portfolio>/projects/foundry; consumers sit beside it.
PORTFOLIO_ROOT = FOUNDRY_ROOT.parent.parent


def project_root(*parts: str) -> Path:
    """Resolve a consumer project below the portfolio's projects/ directory.

    An archived consumer is moved to ``projects/archive/<name>`` but stays a
    read-only source for Foundry's adapters and pack generator. Prefer the
    active checkout when it exists, fall back to the archived one, and return
    the active path otherwise so error messages keep naming the canonical
    location.
    """
    active = PORTFOLIO_ROOT.joinpath("projects", *parts)
    if active.exists():
        return active
    archived = PORTFOLIO_ROOT.joinpath("projects", "archive", *parts)
    if archived.exists():
        return archived
    return active
