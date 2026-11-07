"""Read-only JavaScript source probes for the target adapters.

The probes are deliberately small and strict: they read the authored module
text and fail loud when a known anchor disappears, so a consumer refactor
surfaces as a foundry error instead of a silently empty target manifest.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def object_keys(text: str, const_name: str) -> Tuple[str, ...]:
    """Top-level keys of a `const NAME = { ... }` object literal."""
    body = _object_body(text, const_name)
    keys: List[str] = []
    depth = 0
    index = 0
    masked = _mask(body)
    while index < len(masked):
        char = masked[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif depth == 0 and (char.isalpha() or char in "_$"):
            end = index + 1
            while end < len(masked) and (masked[end].isalnum() or masked[end] in "_$"):
                end += 1
            probe = end
            while probe < len(masked) and masked[probe].isspace():
                probe += 1
            if probe < len(masked) and masked[probe] == ":":
                keys.append(masked[index:end])
            index = end
            continue
        index += 1
    if not keys:
        raise ValueError(f"{const_name}: object literal has no keys")
    return tuple(keys)


def string_values(text: str, field: str) -> Tuple[str, ...]:
    """Every quoted value assigned to `field:` in source order."""
    values = tuple(re.findall(rf"\b{re.escape(field)}\s*:\s*\"([^\"]+)\"", text))
    if not values:
        raise ValueError(f"{field}: no quoted values found")
    return values


def int_values(text: str, field: str) -> Tuple[int, ...]:
    """Every integer value assigned to `field:` in source order."""
    values = tuple(int(value) for value in re.findall(
        rf"\b{re.escape(field)}\s*:\s*(\d+)", text
    ))
    if not values:
        raise ValueError(f"{field}: no integer values found")
    return values


def _object_body(text: str, const_name: str) -> str:
    match = re.search(rf"\b(?:const|let|var)\s+{re.escape(const_name)}\s*=\s*\{{", text)
    if match is None:
        raise ValueError(f"{const_name}: object anchor not found")
    start = match.end() - 1
    depth = 0
    masked = _mask(text)
    for index in range(start, len(masked)):
        if masked[index] == "{":
            depth += 1
        elif masked[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:index]
    raise ValueError(f"{const_name}: object literal is not closed")


def _mask(text: str) -> str:
    """Blank strings, template literals and comments without moving offsets."""
    chars = list(text)
    index = 0
    while index < len(chars):
        char = chars[index]
        if char in "'\"`":
            quote = char
            index += 1
            while index < len(chars):
                if chars[index] == "\\":
                    chars[index] = " "
                    if index + 1 < len(chars):
                        chars[index + 1] = " "
                    index += 2
                    continue
                if chars[index] == quote:
                    break
                chars[index] = " "
                index += 1
        elif char == "/" and index + 1 < len(chars) and chars[index + 1] == "/":
            while index < len(chars) and chars[index] != "\n":
                chars[index] = " "
                index += 1
            continue
        elif char == "/" and index + 1 < len(chars) and chars[index + 1] == "*":
            chars[index] = chars[index + 1] = " "
            index += 2
            while index + 1 < len(chars) and not (
                chars[index] == "*" and chars[index + 1] == "/"
            ):
                chars[index] = " "
                index += 1
            if index + 1 < len(chars):
                chars[index] = chars[index + 1] = " "
            index += 1
        index += 1
    return "".join(chars)
