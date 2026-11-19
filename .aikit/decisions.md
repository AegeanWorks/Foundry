# foundry decisions (append-only)

### ADR-001: crypt-crawler is the first consumer, bosses the first content type
- Date: 2026-11-03. Status: accepted.
- Decision: Slice 1 targets crypt-crawler (stdlib-only, data-table precedent
  ITEM_CATALOG/GUARDIAN_TEMPLATES/BOSS_TEMPLATES, single boss spawn call
  site, existing ai_harness + validate_fairness) with boss packs (phases,
  tells, loot). dustline (JS, no bot surface), voidfarer (large surface),
  MemoryReconstruction (npm toolchain) deferred to later slices.
- Consequences: All foundry contracts are proven against one real loader
  before the loop repeats per content type and per game.

### ADR-002: "no code change" means loader-once, data-after
- Date: 2026-11-03. Status: accepted.
- Decision: Stage 2 refuted literal zero-code-change loading (no JSON
  loading in the game, hardcoded spawn sites in server.py, per-type engine
  specials). The one-time integration is crawler/foundry_packs.py (loader,
  slice-1 structural checks, skip-with-recorded-error) + a spawn hook in
  server.py. After it lands, each pack ships as a JSON file only; Stage 4
  proves this with a clean git status apart from packs/.
- Consequences: Per-pack content work is a data task. Loader/hook changes
  are versioned integration work, not content.

### ADR-003: slice-1 bosses live inside the generic is_boss envelope
- Date: 2026-11-03. Status: accepted.
- Decision: The engine applies fixed phase behavior to ANY is_boss monster
  (50%: summon <=2 skeletons + log tell; 25%: attack x1.3 + log tell).
  Slice-1 packs are constrained to exactly this envelope (thresholds 50/25,
  effects summon_skeletons/enrage); custom specials (drain/hymn-class) need
  a data-driven interpreter deferred to slice 2. Pack `tell` strings are
  required and the bot asserts a tell fires, but slice-1 engine log text
  stays canonical (known cosmetic gap: fixed log lines name Malakor).
- Consequences: New bosses get telegraphed phases with no engine edits.
  Slice 2 adds the interpreter; the schema's envelope check is the seam.

### ADR-004: replacement spawning preserves consumer invariants
- Date: 2026-11-03. Status: accepted.
- Decision: Pack spawn claims (depth 3, anchor stairs, replaces boss_lich,
  seeds [...]). The server spawns the pack boss INSTEAD of the lich for
  claimed seeds, keeping the enforced invariants (exactly 1 boss, on the
  stairs) that test_depth_three_boss_guards_the_stairs and
  validate_fairness.py assert. Duplicate (depth, seed) claims resolve by
  sorted filename, first wins, recorded as an error.
- Consequences: Baselines can overlap the consumer's own sweep seeds
  (42/777) and both suites stay green.

### ADR-005: loudness is split across the boundary
- Date: 2026-11-03. Status: accepted.
- Decision: foundry's validators/boss.py is the shipping gate (exit 2 +
  `field: reason` lines; full semantic checks incl. catalog membership and
  the one-hit cap). The game loader repeats only structural checks and
  skips bad packs with a stderr warning + recorded error (never raises),
  so one bad pack cannot brick the game; tests assert the recording.
- Consequences: Fail-fast at generation time, fail-safe at load time.

### ADR-006: the proof bot plays the shipped engine with a stated loadout
- Date: 2026-11-03. Status: accepted.
- Decision: Keystone playtest.py uses an ActionState contract crypt-crawler
  does not implement (not landed for this consumer), so the proof bot runs
  through tools/ai_harness.py (Playwright Edge, deterministic RNG) against
  the real JS engine. Python crawler/combat.py is not the live loop and is
  never the proof surface. The bot uses a documented level-5 paladin with
  equipped starters (depth-3-expected), because a naked level-1 hero is not
  the winnability question; the loadout is recorded in every report.
- Consequences: Bot clears prove the shipped game. Pre-existing harness
  selftest failures (2 omen checks, unrelated to bosses) are baselined, not
  fixed here.

### ADR-007: empty loot overlap fails loud at generation time
- Date: 2026-11-03. Status: accepted.
- Decision: If no LOOT_POOL id resolves in the consumer ITEM_CATALOG,
  generate() raises ValueError naming the cause instead of crashing in
  random.choice with a bare IndexError. The non-empty path is untouched
  (same list, same single choice), so baselined packs regenerate
  byte-identically.
- Consequences: A game-side catalog edit that drops every pool id surfaces
  as `loot pool has no ITEM_CATALOG overlap` with a fix direction, covered
  by test_empty_loot_pool_fails_loud.

### ADR-008: validator hardening without contract change
- Date: 2026-11-03. Status: accepted.
- Decision: Harden validators/boss.py only: fullmatch for pack_version and
  boss_id (close trailing-newline bypass), int-type guard for spawn.depth
  (reject 3.0), repr-sorted unknown-field reporting (no TypeError on
  mixed-type keys), OSError/UnicodeDecodeError parity in validate_file,
  recursive glob, drop unused Container/Dict imports. Baselines regenerate
  byte-identically; no schema or pack change.
- Consequences: Six new TestValidatorHardening tests lock the fixes;
  validator stays the shipping gate with field+reason lines.

### ADR-009: attach to AIKit and conform README to the scaffold
- Date: 2026-11-03. Status: accepted.
- Decision: Register the existing folder via `aikit attach` (badge under
  the README title) so `aikit check foundry` runs; rename README headings
  to `Cold-Start Quick Reference` / `What's Inside` with a `text` tree and
  keep every cold-start command byte-identical. Mark the bot teleport probe
  `except` with `hygiene: allow` instead of refactoring it: failed offsets
  are expected probes, and recording them as errors would wrongly fail fair
  runs (`fair` requires an empty error list).
- Consequences: All four `aikit check` gates run; README stays the
  cold-start contract with scaffold headings.

### ADR-010: every consumer is a read-only target with a checked-in manifest
- Date: 2026-11-08. Status: accepted.
- Decision: Add After Image, Aldervale, Shooter, Weft, Iris, Primordia,
  Cyberpulse and Fold to foundry as targets beside crypt-crawler. Each target
  gets a frozen `TargetFacts` adapter (project root, lifecycle, engine, test
  command, authored content surfaces) and a generated manifest under
  `targets/` validated against `schemas/target.schema.json`. The new adapters
  parse JSON, Python AST and JavaScript source text without importing or
  executing the consumer project; the pre-existing crypt-crawler adapter
  keeps its live `ITEM_CATALOG` import. No adapter writes a consumer project.
  Archived consumers (Aldervale, Iris, Fold) are registered but marked
  read-only.
- Rationale: Foundry needs one truthful registry before it can emit content
  for more games; a manifest plus freshness check makes drift visible without
  coupling foundry to each consumer's runtime.
- Consequences: `python tools/targets.py` lists targets; `generators/target.py
  --check` and `validators/target.py "targets/*.json"` are the new gate.
  Adding a target means adding one adapter and regenerating its manifest.
  No consumer project file is modified by this slice.

### ADR-011: foundry emits Keystone asset packs, proven by the real registry
- Date: 2026-11-08. Status: accepted.
- Decision: Add a Keystone asset mode beside the boss-pack and target-manifest
  slices. `generators/keystone_assets.py` deterministically emits OBJ meshes,
  RGBA PNG textures, material descriptors and a `.kprefab`, plus
  `keystone-assets.json` with file digests and dependency order.
  `validators/keystone_assets.py` gates the manifest, file hashes, load order
  and prefab references. `tools/keystone_assets.py --verify` registers the
  pack through Keystone's `AssetRegistry`, checks material parameters and
  instantiates the prefab; Keystone stays an external read-only project.
- Rationale: A Keystone game needs file-backed meshes, textures and prefabs,
  not game-rule JSON. Producing them here gives the engine portfolio one
  deterministic asset pipeline without hard-coding assets into each game.
- Consequences: `packs/keystone/starter/` is the baselined seed-42 pack.
  Generation remains stdlib-only; only the runtime proof imports Keystone.
  The target registry now also exposes Keystone's asset kinds, suffixes,
  primitives and material-graph node kinds as read-only target facts.

### ADR-012: complete the playable portfolio as targets
- Date: 2026-11-08. Status: accepted.
- Decision: Finish the project analysis by adding Dustline, VoidFarer,
  Memory Reconstruction and Prism Relay as read-only targets. Every playable
  project now has a target adapter: After Image, Aldervale, crypt-crawler,
  Cyberpulse, Dustline, Fold, Iris, Memory Reconstruction, Primordia,
  Prism Relay, Shooter, VoidFarer and Weft, plus the Keystone engine.
  Non-game projects remain out of scope because they expose tools, science,
  user data or generated media rather than authored game-content surfaces.
- Rationale: A target is only useful when it can name stable authored ids and
  source files. Extending the same TargetFacts contract to the remaining
  games completes the portfolio map without inventing content for tools.
- Consequences: 14 target manifests are checked in. The new adapters parse
  Dustline's JS tables, VoidFarer's Python catalogs and Memory
  Reconstruction's JSON data; none imports or writes those projects.
  `tools/portfolio_analysis.py --check` now gates the classification so a
  future game project cannot silently fall outside the target registry.

### ADR-013: publish only through AIKit, with approved media, license and topics
- Date: 2026-11-08. Status: accepted.
- Decision: Foundry is published with `python aikit.py publish foundry`;
  raw `gh repo create` and `git push` are forbidden by project guideline
  G-001. The tree now carries the AL-1.1 software license
  (`LICENSE`, `LICENSES/`, `COMMERCIAL.md`, `REUSE.toml`), approved brand
  media, recorded GitHub topics and the AegeanWorks dossier entry.
- Rationale: the first publish used raw GitHub CLI commands, which skipped
  AIKit's media review, license state, topic policy, dossier sync and
  publish-time gate sequence. A future agent must not repeat that shortcut.
- Consequences: `aikit media status foundry` shows both assets approved;
  `aikit topics foundry --review` reports no policy problem; publishing the
  committed tree runs the full AIKit sequence. The AegeanWorks dossier media
  files are committed in their own repository.

### ADR-014: reusable asset packs are the acceleration strategy
- **Date**: 2026-11-19
- **Status**: Accepted
- **Context**: The user's purpose for Foundry is to use assets to speed up future game creation. Today Foundry generates validated Keystone packs but has only one documented consumer install hook (crypt-crawler); Shooter has none, and Keystone's registry recognizes only mesh, texture and prefab while games already author material, state and camera-path files.
- **Decision**: Treat a generic, versioned pack format plus a consumer-side install path and broader asset-kind coverage as the program's north star. Work proceeds in bounded milestones, starting with the pack schema and installer, with Shooter as the first real consumer.
- **Consequences**: New pack schema, generator and installer surfaces with deterministic tests; per-game one-off content work is deprioritized. The uncommitted Shooter/Keystone surface change set stays suspended and is not folded into this program.
