# Codebase Map & Symbol Catalog 🗺️

> **AUTO-GENERATED & VERIFIED BY `scripts/update_knowledge_base.py`**
> This document provides an automated, up-to-date registry of all modules, classes, and exported functions across this repository.

---

## 📊 Codebase Metrics
- **Total Python Modules**: `37`
- **Total Classes**: `16`
- **Total Top-Level Functions**: `110`
- **Total Class Methods**: `85`
- **Total Source Lines**: `3897`

---

## 📦 Modules & Exported Symbols

### [`adapters/__init__.py`](adapters/__init__.py)
**Size**: `0` lines (`0` bytes)

---

### [`adapters/afterimage.py`](adapters/afterimage.py)
> *Afterimage target: read-only authored modes and scripts.*

**Size**: `28` lines (`803` bytes)

---

### [`adapters/aldervale.py`](adapters/aldervale.py)
> *Aldervale target: read-only item and equipment tables.*

**Size**: `31` lines (`1101` bytes)

---

### [`adapters/base.py`](adapters/base.py)
> *Frozen target facts shared by adapters, validators and generators.*

**Size**: `54` lines (`1543` bytes)

**Classes:**
- `class ContentSurface` - *One authored content surface a target exposes to foundry.*
- `class TargetFacts` - *The read-only facts foundry needs to target one consumer project.*
  - Method `.as_manifest(portfolio_root)` - *Serialize the facts as the canonical target manifest.*

---

### [`adapters/crypt_crawler.py`](adapters/crypt_crawler.py)
> *crypt-crawler adapter: the versioned boundary foundry never crosses.*

**Size**: `54` lines (`1661` bytes)

**Functions:**
- `def _load_game_tables()`

---

### [`adapters/cyberpulse.py`](adapters/cyberpulse.py)
> *Cyberpulse target: read-only puzzle, story-act and campaign-quest catalogs.*

**Size**: `30` lines (`1108` bytes)

---

### [`adapters/dustline.py`](adapters/dustline.py)
> *Dustline target: read-only maps, weapons, enemies, bosses and run modes.*

**Size**: `45` lines (`1576` bytes)

---

### [`adapters/fold.py`](adapters/fold.py)
> *Fold target: read-only board rules and direction set.*

**Size**: `31` lines (`959` bytes)

---

### [`adapters/iris.py`](adapters/iris.py)
> *Iris target: read-only episode and chamber catalog.*

**Size**: `28` lines (`842` bytes)

---

### [`adapters/keystone.py`](adapters/keystone.py)
> *Keystone target: read-only engine asset kinds, primitives and graph nodes.*

**Size**: `38` lines (`1406` bytes)

---

### [`adapters/layout.py`](adapters/layout.py)
> *Filesystem boundaries shared by the target adapters (read-only).*

**Size**: `14` lines (`482` bytes)

**Functions:**
- `def project_root(*parts)` - *Resolve a consumer project below the portfolio's projects/ directory.*

---

### [`adapters/memoryreconstruction.py`](adapters/memoryreconstruction.py)
> *Memory Reconstruction target: read-only authored JSON content tables.*

**Size**: `85` lines (`2430` bytes)

**Functions:**
- `def _load(name)`
- `def _ids(items)`

---

### [`adapters/primordia.py`](adapters/primordia.py)
> *Primordia target: read-only genome, shock and hunter-trait catalogs.*

**Size**: `30` lines (`1088` bytes)

---

### [`adapters/prism_relay.py`](adapters/prism_relay.py)
> *Prism Relay target: read-only episodes, chambers and emitter directions.*

**Size**: `43` lines (`1416` bytes)

---

### [`adapters/registry.py`](adapters/registry.py)
> *Target registry: every consumer foundry can emit content for.*

**Size**: `62` lines (`1392` bytes)

**Functions:**
- `def all_targets()` - *Registered targets in stable order.*
- `def target_ids()` - *Registered target ids in stable order.*
- `def get_target(game_id)` - *Return one target or fail loud with the known ids.*

---

### [`adapters/shooter.py`](adapters/shooter.py)
> *Shooter target: read-only JSON content tables.*

**Size**: `51` lines (`1519` bytes)

**Functions:**
- `def _load(name)`
- `def _ids(payload, key)`

---

### [`adapters/source_js.py`](adapters/source_js.py)
> *Read-only JavaScript source probes for the target adapters.*

**Size**: `174` lines (`6134` bytes)

**Functions:**
- `def read_text(path)`
- `def object_keys(text, const_name)` - *Top-level keys of a `const NAME = { ... }` object literal.*
- `def string_values(text, field)` - *Every quoted value assigned to `field:` in source order.*
- `def array_strings(text, const_name)` - *Quoted strings inside a `const NAME = [ ... ]` array literal.*
- `def array_object_ids(text, const_name, field)` - *Quoted `field:` values inside a `const NAME = [ ... ]` array literal.*
- `def int_values(text, field)` - *Every integer value assigned to `field:` in source order.*
- `def _object_body(text, const_name)`
- `def _array_body(text, const_name)`
- `def _balanced_body(text, start, opener, closer, label)`
- `def _mask(text)` - *Blank strings, template literals and comments without moving offsets.*

---

### [`adapters/source_py.py`](adapters/source_py.py)
> *Read-only Python AST probes for the target adapters.*

**Size**: `134` lines (`5289` bytes)

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

### [`adapters/voidfarer.py`](adapters/voidfarer.py)
> *VoidFarer target: read-only weapons, enemies, factions, drones and systems.*

**Size**: `38` lines (`1649` bytes)

---

### [`adapters/weft.py`](adapters/weft.py)
> *Weft target: read-only chamber catalog and size ladder.*

**Size**: `28` lines (`873` bytes)

---

### [`generators/__init__.py`](generators/__init__.py)
**Size**: `0` lines (`0` bytes)

---

### [`generators/boss.py`](generators/boss.py)
> *Foundry boss generator: seeded, deterministic, valid-by-construction.*

**Size**: `162` lines (`5152` bytes)

**Functions:**
- `def _clamp(value, lo, hi)`
- `def generate(seed)` - *Build the canonical boss pack for a seed (pure, deterministic).*
- `def pack_bytes(pack)`
- `def write_pack(seed, out_dir)`
- `def main(argv)`

---

### [`generators/keystone_assets.py`](generators/keystone_assets.py)
> *Keystone asset-pack generator: deterministic meshes, textures, materials, prefab.*

**Size**: `447` lines (`15554` bytes)

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

**Size**: `79` lines (`2679` bytes)

**Functions:**
- `def manifest(target)` - *Build the canonical manifest dict for one target.*
- `def manifest_bytes(target)` - *Serialize canonically so regeneration is byte-identical.*
- `def manifest_path(target, out_dir)`
- `def write_manifest(target, out_dir)`
- `def check_manifests(out_dir)` - *Return one ``path: reason`` line per stale or missing manifest.*
- `def main(argv)`

---

### [`tests/test_generator.py`](tests/test_generator.py)
> *Generator tests: determinism, validity, uniqueness, catalog honesty.*

**Size**: `74` lines (`2599` bytes)

**Classes:**
- `class TestGenerator`
  - Method `.test_deterministic_per_seed()`
  - Method `.test_distinct_seeds_distinct_packs()`
  - Method `.test_baseline_seeds_valid()`
  - Method `.test_wide_seed_range_valid()`
  - Method `.test_boss_ids_unique_over_range()`
  - Method `.test_loot_resolves_in_catalog()`
  - Method `.test_no_one_shot_over_range()`
  - Method `.test_empty_loot_pool_fails_loud()`
  - Method `.test_spawn_claims_own_seed()`

---

### [`tests/test_keystone_assets.py`](tests/test_keystone_assets.py)
> *Keystone asset-pack tests: determinism, integrity and engine compatibility.*

**Size**: `178` lines (`7030` bytes)

**Classes:**
- `class TestKeystonePackGenerator`
  - Method `.test_generate_is_deterministic()`
  - Method `.test_distinct_seeds_change_content()`
  - Method `.test_generated_pack_validates()`
  - Method `.test_checked_in_pack_is_fresh()`
  - Method `.test_manifest_records_every_file()`
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

### [`tests/test_portfolio_analysis.py`](tests/test_portfolio_analysis.py)
> *Portfolio analysis tests: every playable project is covered by a target.*

**Size**: `50` lines (`1611` bytes)

**Classes:**
- `class TestPortfolioAnalysis`
  - Method `.setUpClass()`
  - Method `.test_every_playable_project_is_targeted()`
  - Method `.test_scan_finds_the_remaining_game_projects()`
  - Method `.test_classification_separates_games_from_tools()`
  - Method `.test_report_is_json_safe()`

---

### [`tests/test_targets.py`](tests/test_targets.py)
> *Target registry tests: every requested consumer is present and read-only.*

**Size**: `254` lines (`8583` bytes)

**Classes:**
- `class TestTargetRegistry`
  - Method `.test_portfolio_targets_are_registered()`
  - Method `.test_engine_target_is_registered()`
  - Method `.test_registry_ids_are_unique()`
  - Method `.test_every_target_project_exists()`
  - Method `.test_every_source_exists()`
  - Method `.test_every_surface_is_non_empty_and_unique()`
  - Method `.test_authored_content_counts()`
  - Method `.test_lifecycle_is_known_and_archived_projects_stay_read_only()`
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

### [`tests/test_validator.py`](tests/test_validator.py)
> *Validator tests: valid packs pass, broken packs fail with field + reason.*

**Size**: `268` lines (`8390` bytes)

**Classes:**
- `class TestValidatorAccepts`
  - Method `.test_good_pack_is_valid()`
- `class TestValidatorRejects`
  - Method `.check(mutate, field_prefix)`
  - Method `.test_rejects_unknown_top_field()`
  - Method `.test_rejects_missing_field()`
  - Method `.test_rejects_bad_pack_version()`
  - Method `.test_rejects_wrong_game()`
  - Method `.test_rejects_bad_boss_id()`
  - Method `.test_rejects_empty_name()`
  - Method `.test_rejects_out_of_band_stat()`
  - Method `.test_rejects_bool_stat()`
  - Method `.test_rejects_one_shot_attack()`
  - Method `.test_cap_math_matches_schema_doc()`
  - Method `.test_rejects_wrong_phase_count()`
  - Method `.test_rejects_off_envelope_threshold()`
  - Method `.test_rejects_custom_effect()`
  - Method `.test_rejects_empty_tell()`
  - Method `.test_rejects_unknown_loot()`
  - Method `.test_rejects_wrong_depth()`
  - Method `.test_rejects_vault_anchor()`
  - Method `.test_rejects_empty_seeds()`
  - Method `.test_rejects_non_object_pack()`
  - Method `.test_rejects_deliberately_unfair_generated_pack()`
- `class TestValidatorHardening`
  - Method `.test_rejects_version_trailing_newline()`
  - Method `.test_rejects_boss_id_trailing_newline()`
  - Method `.test_mixed_type_unknown_fields_no_crash()`
  - Method `.test_rejects_float_depth()`
  - Method `.test_validate_file_directory_returns_error()`
  - Method `.test_validate_file_invalid_utf8_returns_error()`

**Functions:**
- `def good_pack()`

---

### [`tools/bot_clear.py`](tools/bot_clear.py)
> *Bot-clear proof: a reference policy beats a generated boss in the real game.*

**Size**: `225` lines (`8759` bytes)

**Functions:**
- `def _sign(value)`
- `def _boss(monsters, boss_id)`
- `def clear_pack(pack_path)`
- `def main(argv)`

---

### [`tools/keystone_assets.py`](tools/keystone_assets.py)
> *Keystone asset cockpit: validate a pack and prove it loads in the engine.*

**Size**: `164` lines (`6004` bytes)

**Functions:**
- `def _import_keystone()`
- `def load_pack(pack_dir)` - *Register every asset in manifest order and return (registry, manifest).*
- `def verify_pack(pack_dir)` - *Validate a pack, load it through Keystone and instantiate its prefab.*
- `def main(argv)`

---

### [`tools/portfolio_analysis.py`](tools/portfolio_analysis.py)
> *Portfolio analysis: classify every project and prove target coverage.*

**Size**: `142` lines (`4817` bytes)

**Classes:**
- `class ProjectAnalysis` - *One project's manifest facts and portfolio classification.*
  - Property `.kind`

**Functions:**
- `def scan(projects_root)` - *Read every project.json under projects/ and projects/archive/.*
- `def target_paths()` - *Map each registered target's project directory to its target id.*
- `def analyze(projects)` - *Return one JSON-safe row per project, including target coverage.*
- `def check(projects)` - *Return coverage problems: playable projects without a target, dead targets.*
- `def main(argv)`

---

### [`tools/targets.py`](tools/targets.py)
> *Target cockpit: list registered targets, write manifests, verify freshness.*

**Size**: `56` lines (`2012` bytes)

**Functions:**
- `def list_targets()`
- `def _selected(targets, out_dir, check)`
- `def main(argv)`

---

### [`validators/__init__.py`](validators/__init__.py)
**Size**: `0` lines (`0` bytes)

---

### [`validators/boss.py`](validators/boss.py)
> *Foundry boss-pack validator: every generated pack validates before it ships.*

**Size**: `249` lines (`9468` bytes)

**Functions:**
- `def _is_int(value)`
- `def max_theoretical_hit(attack)` - *Worst-case single-turn damage for a slice-1 boss: phase-3 attack.*
- `def validate(pack)` - *Return a list of ``field: reason`` violations (empty == valid).*
- `def validate_file(path)`
- `def main(argv)`

---

### [`validators/keystone_assets.py`](validators/keystone_assets.py)
> *Keystone asset-pack validator: manifest shape, file digests and load order.*

**Size**: `290` lines (`11282` bytes)

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

**Size**: `261` lines (`9461` bytes)

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
