"""Read-only Python AST probes for the target adapters.

Parsing beats importing here: the consumer's modules never execute inside
foundry, so target discovery cannot create files, touch saves or depend on
the consumer's runtime stack.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def dict_keys(path: Path, name: str) -> Tuple[str, ...]:
    """String-or-int keys of a module-level dict literal, in source order."""
    value = _assigned_value(_parse(path), name)
    if not isinstance(value, ast.Dict):
        raise ValueError(f"{name}: assignment is not a dict literal")
    keys = []
    for key in value.keys:
        if not isinstance(key, ast.Constant) or not isinstance(key.value, (str, int)):
            raise ValueError(f"{name}: non-literal dict key")
        keys.append(str(key.value))
    if not keys:
        raise ValueError(f"{name}: dict literal has no keys")
    return tuple(keys)


def tuple_strings(path: Path, name: str) -> Tuple[str, ...]:
    """String items of a module-level tuple or list literal."""
    value = _assigned_value(_parse(path), name)
    if not isinstance(value, (ast.Tuple, ast.List)):
        raise ValueError(f"{name}: assignment is not a tuple/list literal")
    items = []
    for item in value.elts:
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            raise ValueError(f"{name}: non-string item")
        items.append(item.value)
    if not items:
        raise ValueError(f"{name}: literal has no items")
    return tuple(items)


def set_strings(path: Path, name: str) -> Tuple[str, ...]:
    """String items of a module-level set literal."""
    value = _assigned_value(_parse(path), name)
    if not isinstance(value, ast.Set):
        raise ValueError(f"{name}: assignment is not a set literal")
    items = sorted(
        item.value for item in value.elts
        if isinstance(item, ast.Constant) and isinstance(item.value, str)
    )
    if not items:
        raise ValueError(f"{name}: set literal has no strings")
    return tuple(items)


def call_first_args(path: Path, call_name: str) -> Tuple[str, ...]:
    """First positional string argument of every `call_name(...)` in source order."""
    tree = _parse(path)
    items = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != call_name:
            continue
        if node.args and isinstance(node.args[0], ast.Constant):
            if isinstance(node.args[0].value, str):
                items.append(node.args[0].value)
    if not items:
        raise ValueError(f"{call_name}: no calls with a string first argument")
    return tuple(items)


def top_level_functions(path: Path) -> Tuple[str, ...]:
    """Public function names defined at module level, in source order."""
    names = [
        node.name for node in _parse(path).body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    if not names:
        raise ValueError(f"{path.name}: no public top-level functions")
    return tuple(names)


def int_constants(path: Path, names: Iterable[str]) -> Dict[str, int]:
    """Module-level integer constants by name."""
    tree = _parse(path)
    found: Dict[str, int] = {}
    for name in names:
        value = _assigned_value(tree, name)
        if not isinstance(value, ast.Constant) or type(value.value) is not int:
            raise ValueError(f"{name}: assignment is not an integer constant")
        found[name] = value.value
    return found


def _parse(path: Path) -> ast.Module:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        raise ValueError(f"{path.name}: cannot parse Python source: {exc}") from exc


def _assigned_value(tree: ast.Module, name: str) -> ast.expr:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name
            for target in node.targets
        ):
            return node.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == name and node.value is not None:
                return node.value
    raise ValueError(f"{name}: module-level assignment not found")
