# Codebase Map & Symbol Catalog 🗺️

> **AUTO-GENERATED & VERIFIED BY `scripts/update_knowledge_base.py`**
> This document catalogues Python modules, classes, and exported functions. See Map Coverage for any stack it does not index.

---

## 📊 Codebase Metrics
- **Total Python Modules**: `23`
- **Total Classes**: `15`
- **Total Top-Level Functions**: `98`
- **Total Class Methods**: `59`
- **Total Source Lines**: `2782`

## 🧭 Map Coverage
- **Indexed**: python (`23` module(s))
- **Not indexed by this map**: none (no non-Python source files were found)

---

## 📦 Modules & Exported Symbols

### [`adapters/__init__.py`](adapters/__init__.py)
**Size**: `0` lines

---

### [`adapters/base.py`](adapters/base.py)
> *Frozen target facts shared by adapters, validators and generators.*

**Size**: `54` lines

**Classes:**
- `class ContentSurface` - *One authored content surface a target exposes to foundry.*
- `class TargetFacts` - *The read-only facts foundry needs to target one consumer project.*
  - Method `.as_manifest(portfolio_root)` - *Serialize the facts as the canonical target manifest.*

---

### [`adapters/keystone.py`](adapters/keystone.py)
> *Keystone target: read-only engine asset kinds, primitives and graph nodes.*

**Size**: `38` lines

---

### [`adapters/layout.py`](adapters/layout.py)
> *Filesystem boundaries shared by the target adapters (read-only).*

**Size**: `14` lines

**Functions:**
- `def project_root(*parts)` - *Resolve a consumer project below the portfolio's projects/ directory.*

---

### [`adapters/registry.py`](adapters/registry.py)
> *Target registry: the two consumers Foundry serves — Shooter and Keystone.*

**Size**: `35` lines

**Functions:**
- `def all_targets()` - *Registered targets in stable order.*
- `def target_ids()` - *Registered target ids in stable order.*
- `def get_target(game_id)` - *Return one target or fail loud with the known ids.*

---

### [`adapters/shooter.py`](adapters/shooter.py)
> *Shooter target: read-only JSON content tables.*

**Size**: `69` lines

**Functions:**
- `def _load(name)`
- `def _ids(payload, key)`
- `def _fields(payload)` - *The tuned field names of a table, without metadata or prose.*

---

### [`adapters/source_py.py`](adapters/source_py.py)
> *Read-only Python AST probes for the target adapters.*

**Size**: `134` lines

**Functions:**
- `def dict_keys(path, name)` - *String-or-int keys of a module-level dict literal, in source order.*
- `def tuple_strings(path, name)` - *String items of a module-level tuple or list literal.*
- `def set_strings(path, name)` - *String items of a module-level set literal.*
- `def list_tuple_first_strings(path, name)` - *First string of every tuple in a module-level list of tuples.*
- `def call_first_args(path, call_name)` - *First positional string argument of every `call_name(...)` in source order.*
- `def top_level_functions(path)` - *Public function names defined at module level, in source order.*
- `def int_constants(path, names)` - *Module-level integer constants by name.*
- `def _parse(path)`
- `def _assigned_value(tree, name)`

---

### [`generators/__init__.py`](generators/__init__.py)
**Size**: `0` lines

---

### [`generators/game_assets.py`](generators/game_assets.py)
> *Generic game-asset-pack generator: file-backed assets copied verbatim.*

**Size**: `179` lines

**Classes:**
- `class GameAssetPack` - *A generated pack: relative file bytes plus the canonical manifest.*
  - Method `.manifest_bytes()`

**Functions:**
- `def generate(name, source)` - *Build one deterministic asset pack from a source project's files.*
- `def write_pack(out_dir, name, source)` - *Write the generated pack, creating directories as needed.*
- `def check_pack(out_dir, name, source)` - *Return one ``path: reason`` line per stale or missing pack file.*
- `def _canonical_json(payload)`
- `def main(argv)`

---

### [`generators/keystone_assets.py`](generators/keystone_assets.py)
> *Keystone asset-pack generator: deterministic meshes, textures, materials, prefab.*

**Size**: `469` lines

**Classes:**
- `class KeystonePack` - *A generated pack: relative file bytes plus the canonical manifest.*
  - Method `.manifest_bytes()`

**Functions:**
- `def generate(seed, name)` - *Build one deterministic Keystone asset pack.*
- `def write_pack(seed, out_dir, name)` - *Write the generated pack, creating directories as needed.*
- `def check_pack(out_dir, seed, name)` - *Return one ``path: reason`` line per stale or missing pack file.*
- `def _add_file(assets, asset_id, kind, relative, files, dependencies)`
- `def _material(color, specular, shininess, checker_scale, metallic, roughness, emissive, texture)`
- `def _palette(rng)`
- `def _prefab()`
- `def _obj_cube(size)`
- `def _obj_plane(size)`
- `def _obj_crystal(seed)`
- `def _obj_octahedron(radius)` - *The engine's flat-shaded unit octahedron, generated with UVs and normals.*
- `def _obj_from_quads(name, quads)`
- `def _obj_from_triangles(name, triangles)`
- `def _index(values, value)`
- `def _normal(a, b, c)`
- `def _png_checker(size, cell, dark, light)`
- `def _png_gradient(size, accent)`
- `def _rgba(color)`
- `def _channel(value)`
- `def _png_bytes(width, height, rgba)`
- `def _chunk(kind, payload)`
- `def _canonical_json(payload)`
- `def main(argv)`

---

### [`generators/target.py`](generators/target.py)
> *Target manifest generator: deterministic bytes from read-only adapter facts.*

**Size**: `79` lines

**Functions:**
- `def manifest(target)` - *Build the canonical manifest dict for one target.*
- `def manifest_bytes(target)` - *Serialize canonically so regeneration is byte-identical.*
- `def manifest_path(target, out_dir)`
- `def write_manifest(target, out_dir)`
- `def check_manifests(out_dir)` - *Return one ``path: reason`` line per stale or missing manifest.*
- `def main(argv)`

---

### [`tests/test_game_assets.py`](tests/test_game_assets.py)
> *Generic game-asset packs: deterministic generation, validation and install.*

**Size**: `148` lines

**Classes:**
- `class TestGameAssetPack`
  - Method `.test_generated_pack_is_deterministic()`
  - Method `.test_generated_pack_validates()`
  - Method `.test_checked_in_pack_is_fresh()`
  - Method `.test_every_runtime_asset_is_packed()`
  - Method `.test_rejects_digest_mismatch()`
  - Method `.test_rejects_path_traversal()`
  - Method `.test_rejects_forward_dependency()`
- `class TestShooterSourcePack`
  - Method `.test_provenance_names_the_owning_game()`
  - Method `.test_keystone_is_not_an_import_source()`
- `class TestGameAssetInstall`
  - Method `.test_dry_run_writes_nothing()`
  - Method `.test_install_copies_files_and_validates()`
  - Method `.test_install_refuses_overwrite_without_force()`
  - Method `.test_install_refuses_invalid_pack()`
  - Method `.test_install_preserves_source_files()`

---

### [`tests/test_keystone_assets.py`](tests/test_keystone_assets.py)
> *Keystone asset-pack tests: determinism, integrity and engine compatibility.*

**Size**: `186` lines

**Classes:**
- `class TestKeystonePackGenerator`
  - Method `.test_generate_is_deterministic()`
  - Method `.test_distinct_seeds_change_content()`
  - Method `.test_generated_pack_validates()`
  - Method `.test_checked_in_pack_is_fresh()`
  - Method `.test_manifest_records_every_file()`
  - Method `.test_pack_includes_octahedron_mesh()`
- `class TestKeystonePackValidation`
  - Method `.pack(tmp)`
  - Method `.test_rejects_tampered_texture()`
  - Method `.test_rejects_missing_material_dependency()`
  - Method `.test_rejects_missing_prefab_dependency()`
  - Method `.test_rejects_later_loaded_dependency()`
  - Method `.test_rejects_duplicate_asset()`
  - Method `.test_schema_file_is_valid_json()`
- `class TestKeystoneRuntime`
  - Method `.test_checked_in_pack_loads_and_instantiates()`
  - Method `.test_mesh_winding_matches_normals()`
  - Method `.test_texture_png_roundtrip()`

**Functions:**
- `def _keystone_available()`
- `def _sub(a, b)`
- `def _cross(a, b)`
- `def _dot(a, b)`

---

### [`tests/test_shooter_surfaces.py`](tests/test_shooter_surfaces.py)
> *Shooter target surfaces: every authored table is exposed read-only.*

**Size**: `48` lines

**Classes:**
- `class TestShooterSurfaces`
  - Method `.test_every_authored_table_is_a_surface()`
  - Method `.test_rule_items_are_tuning_fields_not_prose()`

---

### [`tests/test_targets.py`](tests/test_targets.py)
> *Target registry tests: only Shooter and Keystone are in scope, read-only.*

**Size**: `207` lines

**Classes:**
- `class TestTargetRegistry`
  - Method `.test_only_shooter_and_keystone_are_registered()`
  - Method `.test_registry_ids_are_unique()`
  - Method `.test_every_target_project_exists()`
  - Method `.test_every_source_exists()`
  - Method `.test_every_surface_is_non_empty_and_unique()`
  - Method `.test_authored_content_counts()`
  - Method `.test_lifecycle_is_known()`
- `class TestTargetManifests`
  - Method `.test_checked_in_manifests_match_the_registry()`
  - Method `.test_every_manifest_validates()`
  - Method `.test_manifest_generation_is_read_only()`
  - Method `.test_check_reports_missing_manifests()`
  - Method `.test_check_reports_stale_manifest()`
- `class TestTargetValidation`
  - Method `.good()`
  - Method `.check(mutate, field_prefix)`
  - Method `.test_rejects_unknown_target()`
  - Method `.test_rejects_unknown_lifecycle()`
  - Method `.test_rejects_missing_field()`
  - Method `.test_rejects_project_traversal()`
  - Method `.test_rejects_missing_source()`
  - Method `.test_rejects_duplicate_items()`
  - Method `.test_rejects_duplicate_surface()`
  - Method `.test_rejects_non_object()`
  - Method `.test_rejects_bad_schema_version()`
- `class TestTargetFiles`
  - Method `.test_schema_is_valid_json()`

**Functions:**
- `def _source_paths(target)`
- `def _snapshot(targets)`

---

### [`tools/game_assets.py`](tools/game_assets.py)
> *Install a validated game asset pack into a consumer project.*

**Size**: `98` lines

**Functions:**
- `def install(pack_dir, dest_dir, *, force, dry_run)` - *Validate, plan and optionally perform an install; return the plan lines.*
- `def main(argv)`

---

### [`tools/keystone_assets.py`](tools/keystone_assets.py)
> *Keystone asset cockpit: validate a pack and prove it loads in the engine.*

**Size**: `164` lines

**Functions:**
- `def _import_keystone()`
- `def load_pack(pack_dir)` - *Register every asset in manifest order and return (registry, manifest).*
- `def verify_pack(pack_dir)` - *Validate a pack, load it through Keystone and instantiate its prefab.*
- `def main(argv)`

---

### [`tools/targets.py`](tools/targets.py)
> *Target cockpit: list registered targets, write manifests, verify freshness.*

**Size**: `56` lines

**Functions:**
- `def list_targets()`
- `def _selected(targets, out_dir, check)`
- `def main(argv)`

---

### [`tools/verify.py`](tools/verify.py)
> *Keystone proof gate: load the generated pack through the real AssetRegistry.*

**Size**: `39` lines

**Functions:**
- `def run_keystone_proof()`
- `def main(argv)`

---

### [`validators/__init__.py`](validators/__init__.py)
**Size**: `0` lines

---

### [`validators/game_assets.py`](validators/game_assets.py)
> *Generic game-asset-pack validator: shape, provenance, digests and load order.*

**Size**: `214` lines

**Functions:**
- `def _is_int(value)`
- `def _safe_relative(value)`
- `def validate_pack(pack_dir)` - *Validate one pack directory and return ``field: reason`` lines.*
- `def validate_manifest(manifest, pack_dir)` - *Validate a parsed manifest against its pack directory.*
- `def _validate_generator(generator, errors)`
- `def _validate_source(source, errors)`
- `def _validate_assets(assets, pack_dir, errors)`
- `def _validate_dependencies(value, field, asset_id, seen, errors)`
- `def _validate_file(asset, field, kind, pack_dir, errors)`
- `def main(argv)`

---

### [`validators/keystone_assets.py`](validators/keystone_assets.py)
> *Keystone asset-pack validator: manifest shape, file digests and load order.*

**Size**: `290` lines

**Functions:**
- `def _is_int(value)`
- `def _is_number(value)`
- `def _safe_relative(value)`
- `def validate_pack(pack_dir)` - *Validate one pack directory and return ``field: reason`` lines.*
- `def validate_manifest(manifest, pack_dir)` - *Validate a parsed manifest against its pack directory.*
- `def _validate_generator(generator, errors)`
- `def _validate_assets(assets, pack_dir, errors)`
- `def _dependencies(value, field, asset_id, seen, errors)`
- `def _validate_path(asset, field, kind, pack_dir, errors)`
- `def _validate_material(asset, field, dependencies, seen, errors)`
- `def _validate_prefab(asset, field, dependencies, pack_dir, seen, errors)`
- `def _prefab_asset_ids(prefab)`
- `def main(argv)`

---

### [`validators/target.py`](validators/target.py)
> *Target-manifest validator: every registered target ships a truthful manifest.*

**Size**: `261` lines

**Functions:**
- `def _is_int(value)`
- `def _relative_parts(value)`
- `def _inside(path, parent)`
- `def validate(manifest, known_ids, portfolio_root)` - *Return a list of ``field: reason`` violations (empty == valid).*
- `def _validate_surface(surface, index, project_dir, seen_surfaces, errors)`
- `def _validate_source(source, field, project_dir, seen_sources, errors)`
- `def validate_file(path, known_ids)`
- `def main(argv)`

---
