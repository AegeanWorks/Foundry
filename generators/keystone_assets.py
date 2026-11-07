"""Keystone asset-pack generator: deterministic meshes, textures, materials, prefab.

The pack is stdlib-only on the producer side. Its manifest records every file
digest and dependency so Keystone's AssetRegistry can load it in order; the
runtime proof lives in tools/keystone_assets.py and never writes the engine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))

PACK_VERSION = 1
GENERATOR_NAME = "foundry.keystone-assets"
GENERATOR_VERSION = 1
DEFAULT_SEED = 42
DEFAULT_NAME = "starter"
DEFAULT_OUT = FOUNDRY_ROOT / "packs" / "keystone" / DEFAULT_NAME
MANIFEST_NAME = "keystone-assets.json"

MESH_CUBE = "meshes/mesh_cube.obj"
MESH_PLANE = "meshes/mesh_plane.obj"
MESH_CRYSTAL = "meshes/mesh_crystal.obj"
TEXTURE_CHECKER = "textures/texture_checker.png"
TEXTURE_GRADIENT = "textures/texture_gradient.png"
PREFAB_STARTER = "prefabs/prefab_starter.kprefab"


@dataclass(frozen=True)
class KeystonePack:
    """A generated pack: relative file bytes plus the canonical manifest."""

    name: str
    seed: int
    files: Dict[str, bytes]
    manifest: Dict

    def manifest_bytes(self) -> bytes:
        return _canonical_json(self.manifest)


def generate(seed: int = DEFAULT_SEED, name: str = DEFAULT_NAME) -> KeystonePack:
    """Build one deterministic Keystone asset pack."""
    if type(seed) is not int:
        raise TypeError("seed must be an integer")
    if seed < 0:
        raise ValueError("seed must be non-negative")
    if not name or not all(char.islower() or char.isdigit() or char == "-" for char in name):
        raise ValueError("pack name must use lowercase letters, digits and dashes")
    rng = random.Random(seed)
    palette = _palette(rng)
    files: Dict[str, bytes] = {}
    assets: List[Dict] = []

    files[TEXTURE_CHECKER] = _png_checker(32, 4, palette["dark"], palette["light"])
    _add_file(assets, "texture.checker", "texture", TEXTURE_CHECKER, files, ())
    files[TEXTURE_GRADIENT] = _png_gradient(32, palette["accent"])
    _add_file(assets, "texture.gradient", "texture", TEXTURE_GRADIENT, files, ())

    files[MESH_CUBE] = _obj_cube()
    _add_file(assets, "mesh.cube", "mesh", MESH_CUBE, files, ())
    files[MESH_PLANE] = _obj_plane()
    _add_file(assets, "mesh.plane", "mesh", MESH_PLANE, files, ())
    files[MESH_CRYSTAL] = _obj_crystal(seed)
    _add_file(assets, "mesh.crystal", "mesh", MESH_CRYSTAL, files, ())

    materials = (
        (
            "material.base",
            _material(palette["base"], 0.3, 32.0, 0.0, 0.0, 0.7, (0.0, 0.0, 0.0), "texture.checker"),
            ("texture.checker",),
        ),
        (
            "material.accent",
            _material(palette["accent"], 0.6, 64.0, 0.0, 0.0, 0.6, palette["accent"], None),
            (),
        ),
        (
            "material.crystal",
            _material(palette["crystal"], 0.5, 48.0, 0.0, 0.4, 0.25, palette["crystal"], "texture.gradient"),
            ("texture.gradient",),
        ),
    )
    for asset_id, material, dependencies in materials:
        assets.append(
            {
                "id": asset_id,
                "kind": "material",
                "path": None,
                "dependencies": list(dependencies),
                "material": material,
            }
        )

    files[PREFAB_STARTER] = _canonical_json(_prefab())
    _add_file(
        assets,
        "prefab.starter",
        "prefab",
        PREFAB_STARTER,
        files,
        ("mesh.cube", "mesh.plane", "mesh.crystal", "material.base", "material.accent", "material.crystal"),
    )

    manifest = {
        "schema": PACK_VERSION,
        "pack": name,
        "seed": seed,
        "generator": {"name": GENERATOR_NAME, "version": GENERATOR_VERSION},
        "assets": assets,
    }
    return KeystonePack(name=name, seed=seed, files=files, manifest=manifest)


def write_pack(seed: int = DEFAULT_SEED, out_dir: Path = DEFAULT_OUT, name: str = DEFAULT_NAME) -> Path:
    """Write the generated pack, creating directories as needed."""
    pack = generate(seed, name)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for relative in sorted(pack.files):
        path = out_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pack.files[relative])
    (out_dir / MANIFEST_NAME).write_bytes(pack.manifest_bytes())
    return out_dir


def check_pack(out_dir: Path, seed: int = DEFAULT_SEED, name: str = DEFAULT_NAME) -> List[str]:
    """Return one ``path: reason`` line per stale or missing pack file."""
    pack = generate(seed, name)
    out_dir = Path(out_dir)
    problems: List[str] = []
    expected = dict(pack.files)
    expected[MANIFEST_NAME] = pack.manifest_bytes()
    for relative in sorted(expected):
        path = out_dir / relative
        try:
            actual = path.read_bytes()
        except FileNotFoundError:
            problems.append(f"{relative}: missing file")
            continue
        except OSError as exc:
            problems.append(f"{relative}: cannot read: {exc}")
            continue
        if actual != expected[relative]:
            problems.append(f"{relative}: stale or modified; run generators/keystone_assets.py")
    return problems


def _add_file(
    assets: List[Dict],
    asset_id: str,
    kind: str,
    relative: str,
    files: Dict[str, bytes],
    dependencies: Sequence[str],
) -> None:
    assets.append(
        {
            "id": asset_id,
            "kind": kind,
            "path": relative,
            "sha256": hashlib.sha256(files[relative]).hexdigest(),
            "dependencies": list(dependencies),
        }
    )


def _material(
    color: Sequence[float],
    specular: float,
    shininess: float,
    checker_scale: float,
    metallic: float,
    roughness: float,
    emissive: Sequence[float],
    texture: str | None,
) -> Dict:
    return {
        "color": [round(float(value), 6) for value in color],
        "specular": round(float(specular), 6),
        "shininess": round(float(shininess), 6),
        "checker_scale": round(float(checker_scale), 6),
        "metallic": round(float(metallic), 6),
        "roughness": round(float(roughness), 6),
        "emissive": [round(float(value), 6) for value in emissive],
        "texture": texture,
    }


def _palette(rng: random.Random) -> Dict[str, Tuple[float, ...]]:
    def color() -> Tuple[float, float, float]:
        return tuple(round(0.2 + rng.random() * 0.7, 6) for _ in range(3))  # type: ignore[return-value]

    return {
        "dark": color(),
        "light": color(),
        "accent": color(),
        "base": color(),
        "crystal": color(),
    }


def _prefab() -> Dict:
    def node(
        node_id: str,
        name: str,
        mesh: str | None = None,
        material: str | None = None,
        position: Sequence[float] = (0.0, 0.0, 0.0),
        scale: Sequence[float] = (1.0, 1.0, 1.0),
        tags: Sequence[str] = (),
        children: Sequence[Dict] = (),
    ) -> Dict:
        return {
            "id": node_id,
            "name": name,
            "visible": True,
            "tags": list(tags),
            "layer": "default",
            "transform": {
                "position": [round(float(value), 6) for value in position],
                "rotation": [0.0, 0.0, 0.0, 1.0],
                "scale": [round(float(value), 6) for value in scale],
            },
            "mesh": mesh,
            "material": material,
            "components": [],
            "children": list(children),
        }

    floor = node("foundry-floor", "Floor", "mesh.plane", "material.base", scale=(4.0, 1.0, 4.0), tags=("floor",))
    block = node("foundry-block", "Block", "mesh.cube", "material.base", position=(0.0, 0.5, 0.0), tags=("block",))
    crystal = node(
        "foundry-crystal",
        "Crystal",
        "mesh.crystal",
        "material.crystal",
        position=(1.4, 0.8, 0.0),
        scale=(0.7, 1.0, 0.7),
        tags=("crystal",),
    )
    marker = node(
        "foundry-marker",
        "Marker",
        "mesh.cube",
        "material.accent",
        position=(-1.3, 0.3, 0.6),
        scale=(0.3, 0.6, 0.3),
        tags=("marker",),
    )
    root = node("foundry-starter", "Foundry Starter", tags=("foundry", "generated"), children=(floor, block, crystal, marker))
    return {"schema": 1, "name": "Foundry Starter", "roots": [root]}


def _obj_cube(size: float = 1.0) -> bytes:
    half = size / 2.0
    faces = (
        (((-half, -half, half), (half, -half, half), (half, half, half), (-half, half, half)), "front"),
        (((half, -half, -half), (-half, -half, -half), (-half, half, -half), (half, half, -half)), "back"),
        (((half, -half, half), (half, -half, -half), (half, half, -half), (half, half, half)), "right"),
        (((-half, -half, -half), (-half, -half, half), (-half, half, half), (-half, half, -half)), "left"),
        (((-half, half, half), (half, half, half), (half, half, -half), (-half, half, -half)), "top"),
        (((-half, -half, -half), (half, -half, -half), (half, -half, half), (-half, -half, half)), "bottom"),
    )
    return _obj_from_quads("cube", faces)


def _obj_plane(size: float = 1.0) -> bytes:
    half = size / 2.0
    return _obj_from_quads(
        "plane",
        (
            (((-half, 0.0, -half), (-half, 0.0, half), (half, 0.0, half), (half, 0.0, -half)), "top"),
        ),
    )


def _obj_crystal(seed: int) -> bytes:
    rng = random.Random(seed)
    height = 1.0 + rng.uniform(-0.15, 0.15)
    radius = 0.45 + rng.uniform(-0.08, 0.08)
    top = (0.0, height, 0.0)
    bottom = (0.0, -height, 0.0)
    equator = [
        (radius * rng.uniform(0.85, 1.15), 0.0, 0.0),
        (0.0, 0.0, radius * rng.uniform(0.85, 1.15)),
        (-radius * rng.uniform(0.85, 1.15), 0.0, 0.0),
        (0.0, 0.0, -radius * rng.uniform(0.85, 1.15)),
    ]
    faces: List[Tuple[Tuple[Tuple[float, float, float], ...], str]] = []
    for index in range(4):
        first = equator[index]
        second = equator[(index + 1) % 4]
        faces.append(((top, second, first), f"top-{index}"))
        faces.append(((bottom, first, second), f"bottom-{index}"))
    return _obj_from_triangles("crystal", faces)


def _obj_from_quads(name: str, quads: Sequence[Tuple[Tuple[Tuple[float, float, float], ...], str]]) -> bytes:
    triangles = []
    for (a, b, c, d), _label in quads:
        triangles.append(((a, b, c), _label))
        triangles.append(((a, c, d), _label))
    return _obj_from_triangles(name, triangles)


def _obj_from_triangles(
    name: str,
    triangles: Sequence[Tuple[Tuple[Tuple[float, float, float], ...], str]],
) -> bytes:
    lines = [f"# {GENERATOR_NAME} {name}", f"o {name}"]
    normals: List[Tuple[float, float, float]] = []
    normal_indices: List[int] = []
    uvs = ((0.0, 0.0), (1.0, 0.0), (0.5, 1.0))
    for (a, b, c), _label in triangles:
        normal = _normal(a, b, c)
        normal_indices.append(_index(normals, normal))
        for vertex, uv in zip((a, b, c), uvs):
            lines.append(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}")
            lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")
    for normal in normals:
        lines.append(f"vn {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}")
    for triangle_index, normal_index in enumerate(normal_indices):
        base = triangle_index * 3 + 1
        lines.append(
            f"f {base}/{base}/{normal_index} "
            f"{base + 1}/{base + 1}/{normal_index} "
            f"{base + 2}/{base + 2}/{normal_index}"
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _index(values: List[Tuple[float, float, float]], value: Tuple[float, float, float]) -> int:
    try:
        return values.index(value) + 1
    except ValueError:
        values.append(value)
        return len(values)


def _normal(
    a: Tuple[float, float, float],
    b: Tuple[float, float, float],
    c: Tuple[float, float, float],
) -> Tuple[float, float, float]:
    u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    cross = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    length = (cross[0] ** 2 + cross[1] ** 2 + cross[2] ** 2) ** 0.5
    if length == 0.0:
        raise ValueError("degenerate triangle")
    return (round(cross[0] / length, 6), round(cross[1] / length, 6), round(cross[2] / length, 6))


def _png_checker(size: int, cell: int, dark: Sequence[float], light: Sequence[float]) -> bytes:
    dark_rgba = _rgba(dark)
    light_rgba = _rgba(light)
    pixels = bytearray()
    for y in range(size):
        for x in range(size):
            pixels.extend(light_rgba if (x // cell + y // cell) % 2 == 0 else dark_rgba)
    return _png_bytes(size, size, bytes(pixels))


def _png_gradient(size: int, accent: Sequence[float]) -> bytes:
    pixels = bytearray()
    for y in range(size):
        for x in range(size):
            pixels.extend(
                (
                    round(255 * (0.15 + 0.85 * x / (size - 1))),
                    round(255 * (0.15 + 0.85 * y / (size - 1))),
                    _channel(accent[2] * (0.4 + 0.6 * x / (size - 1))),
                    255,
                )
            )
    return _png_bytes(size, size, bytes(pixels))


def _rgba(color: Sequence[float]) -> bytes:
    return bytes((_channel(color[0]), _channel(color[1]), _channel(color[2]), 255))


def _channel(value: float) -> int:
    return max(0, min(255, round(float(value) * 255.0)))


def _png_bytes(width: int, height: int, rgba: bytes) -> bytes:
    if len(rgba) != width * height * 4:
        raise ValueError("RGBA payload does not match width and height")
    rows = [rgba[row * width * 4 : (row + 1) * width * 4] for row in range(height)]
    raw = b"".join(b"\x00" + row for row in rows)
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _canonical_json(payload: Dict) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate a Keystone asset pack.")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--name", default=DEFAULT_NAME)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--check", action="store_true", help="verify the checked-in pack")
    args = ap.parse_args(argv)
    out_dir = Path(args.out)
    if args.check:
        problems = check_pack(out_dir, args.seed, args.name)
        for problem in problems:
            print(f"STALE {problem}")
        print(f"{len(problems) == 0 and 'up to date' or f'{len(problems)} problem(s)'}")
        return 0 if not problems else 2
    print(f"WROTE {write_pack(args.seed, out_dir, args.name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
