# Codebase Map & Symbol Catalog 🗺️

> **AUTO-GENERATED & VERIFIED BY `scripts/update_knowledge_base.py`**
> This document provides an automated, up-to-date registry of all modules, classes, and exported functions across this repository.

---

## 📊 Codebase Metrics
- **Total Python Modules**: `9`
- **Total Classes**: `4`
- **Total Top-Level Functions**: `16`
- **Total Class Methods**: `37`
- **Total Source Lines**: `1015`

---

## 📦 Modules & Exported Symbols

### [`adapters/__init__.py`](adapters/__init__.py)
**Size**: `0` lines (`0` bytes)

---

### [`adapters/crypt_crawler.py`](adapters/crypt_crawler.py)
> *crypt-crawler adapter: the versioned boundary foundry never crosses.*

**Size**: `37` lines (`1345` bytes)

**Functions:**
- `def _load_game_tables()`

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
