"""Primordia target: read-only genome, shock and hunter-trait catalogs."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_py import call_first_args, dict_keys, top_level_functions

PROJECT_ROOT = project_root("primordia")
GENOME_SOURCE = PROJECT_ROOT / "primordia" / "genome.py"
SHOCKS_SOURCE = PROJECT_ROOT / "primordia" / "shocks.py"

GENES = call_first_args(GENOME_SOURCE, "GeneSpec")
SHOCKS = top_level_functions(SHOCKS_SOURCE)
HUNTER_TRAITS = dict_keys(SHOCKS_SOURCE, "HUNTER_TRAITS")

TARGET = TargetFacts(
    game_id="primordia",
    display_name="Primordia",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="python",
    test_command="python -m unittest discover",
    pack_major=1,
    content=(
        ContentSurface("genes", "catalog", ("primordia/genome.py",), GENES),
        ContentSurface("shocks", "catalog", ("primordia/shocks.py",), SHOCKS),
        ContentSurface("hunter_traits", "catalog", ("primordia/shocks.py",), HUNTER_TRAITS),
    ),
)
