"""Target registry: the two consumers Foundry serves — Shooter and Keystone."""

from __future__ import annotations

from typing import Dict, Tuple

from adapters import keystone, shooter
from adapters.base import TargetFacts

TARGETS: Tuple[TargetFacts, ...] = (
    shooter.TARGET,
    keystone.TARGET,
)

_BY_ID: Dict[str, TargetFacts] = {target.game_id: target for target in TARGETS}


def all_targets() -> Tuple[TargetFacts, ...]:
    """Registered targets in stable order."""
    return TARGETS


def target_ids() -> Tuple[str, ...]:
    """Registered target ids in stable order."""
    return tuple(target.game_id for target in TARGETS)


def get_target(game_id: str) -> TargetFacts:
    """Return one target or fail loud with the known ids."""
    try:
        return _BY_ID[game_id]
    except KeyError:
        raise KeyError(
            f"unknown target {game_id!r}; known targets: {', '.join(target_ids())}"
        ) from None
