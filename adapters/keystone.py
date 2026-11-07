"""Keystone target: read-only engine asset kinds, primitives and graph nodes."""

from __future__ import annotations

from adapters.base import ContentSurface, TargetFacts
from adapters.layout import project_root
from adapters.source_py import dict_keys, top_level_functions, tuple_strings

PROJECT_ROOT = project_root("keystone")
ASSET_IO = PROJECT_ROOT / "keystone" / "asset_io.py"
PRIMITIVES = PROJECT_ROOT / "keystone" / "primitives.py"
MATERIAL_GRAPH = PROJECT_ROOT / "keystone" / "material_graph.py"

ASSET_KINDS = tuple_strings(ASSET_IO, "ASSET_KINDS")
FILE_SUFFIXES = dict_keys(ASSET_IO, "SUFFIX_KINDS")
PRIMITIVE_NAMES = top_level_functions(PRIMITIVES)
MATERIAL_NODE_KINDS = tuple_strings(MATERIAL_GRAPH, "NODE_KINDS")

TARGET = TargetFacts(
    game_id="keystone",
    display_name="Keystone",
    project_root=PROJECT_ROOT,
    lifecycle="active",
    engine="python",
    test_command="python -m pytest -q",
    pack_major=1,
    content=(
        ContentSurface("asset_kinds", "catalog", ("keystone/asset_io.py",), ASSET_KINDS),
        ContentSurface("file_suffixes", "catalog", ("keystone/asset_io.py",), FILE_SUFFIXES),
        ContentSurface("primitives", "catalog", ("keystone/primitives.py",), PRIMITIVE_NAMES),
        ContentSurface(
            "material_nodes",
            "catalog",
            ("keystone/material_graph.py",),
            MATERIAL_NODE_KINDS,
        ),
    ),
)
