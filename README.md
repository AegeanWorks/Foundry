# foundry

<!-- aegean:media:start -->
<p align="center"><img src="assets/social-preview.svg" alt="Foundry social preview" width="100%"></p>
<p align="center"><a href="LICENSE"><img src="https://img.shields.io/badge/license-AL--1.1-1c7ed6" alt="License"></a> <a href="https://github.com/AegeanWorks/AIKit"><img src="https://img.shields.io/badge/AIKit-integrated-6f42c1" alt="AIKit Integrated"></a></p>
<!-- aegean:media:end -->

A **Keystone extension** for faster game creation. It emits canonical target
manifests, deterministic Keystone asset packs that Keystone loads through its
real registry, and generic asset packs copied from Shooter that a consumer can
install as files plus a digest-verified manifest. Keystone is a consumer here,
never an import source: its own assets stay owned by the engine. Generation
and validation are stdlib-only; the runtime proof loads Keystone when present.

## Cold-Start Quick Reference

- **Runtime Prerequisites**: Python 3.10+ (Keystone's pinned stack only for
  `tools/keystone_assets.py --verify`; everything else is stdlib).
- **Sibling projects**: `projects/shooter` and `projects/keystone` must be
  checked out — the adapters read their authored files and the tests assert
  those sources exist. No other project is required.
- **Canonical Regression Shield Gate**:
  ```bash
  python -m unittest discover tests
  ```

```powershell
cd projects/foundry
python -m unittest discover tests            # full suite, must stay green
python tools/targets.py                      # list targets and their surfaces
python generators/target.py --check          # manifests match the sources
python validators/target.py "targets/*.json" # every manifest passes
```

Keystone asset pack (deterministic meshes, textures, materials and prefab;
the verifier loads them through Keystone's real AssetRegistry):

```powershell
python generators/keystone_assets.py --seed 42 --out packs/keystone/starter
python generators/keystone_assets.py --check
python validators/keystone_assets.py
python tools/keystone_assets.py --verify
```

Reusable game-asset packs (Shooter is the only import source; Keystone consumes
packs, its own assets are not copied. The source project is never written):

```powershell
python generators/game_assets.py --source shooter --out packs/shooter/runtime
python generators/game_assets.py --check
python validators/game_assets.py packs/shooter/runtime
python tools/game_assets.py install --pack packs/shooter/runtime --dest <game-dir> --dry-run
python tools/game_assets.py install --pack packs/shooter/runtime --dest <game-dir>
python tools/game_assets.py check --pack <game-dir>
```

The installer copies files and the manifest only; it never edits consumer
code. It refuses to overwrite an existing install unless `--force` is given,
and re-validates the destination after writing.

## What's Inside

```text
foundry/
├── README.md
├── .gitignore
├── COMMERCIAL.md
├── LICENSE
├── LICENSES/
├── REUSE.toml
├── assets/
├── .aikit/
│   ├── codebase_map.md
│   ├── decisions.md
│   ├── guidelines.md
│   ├── media.json
│   ├── project.json
│   ├── reforge.json
│   ├── task_ledger.json
│   └── task_ledger_archive.jsonl
├── adapters/
│   ├── __init__.py
│   ├── base.py
│   ├── keystone.py
│   ├── layout.py
│   ├── registry.py
│   ├── shooter.py
│   └── source_py.py
├── generators/
│   ├── __init__.py
│   ├── game_assets.py
│   ├── keystone_assets.py
│   └── target.py
├── schemas/
│   ├── game_assets.schema.json
│   ├── keystone_assets.schema.json
│   └── target.schema.json
├── targets/
│   ├── keystone.json
│   └── shooter.json
├── tests/
│   ├── test_game_assets.py
│   ├── test_keystone_assets.py
│   ├── test_shooter_surfaces.py
│   └── test_targets.py
├── tools/
│   ├── game_assets.py
│   ├── keystone_assets.py
│   ├── targets.py
│   └── verify.py
├── validators/
│   ├── __init__.py
│   ├── game_assets.py
│   ├── keystone_assets.py
│   └── target.py
└── packs/
    ├── keystone/
    │   └── starter/
    │       ├── keystone-assets.json
    │       ├── meshes/
    │       │   ├── mesh_cube.obj
    │       │   ├── mesh_crystal.obj
    │       │   ├── mesh_octahedron.obj
    │       │   └── mesh_plane.obj
    │       ├── prefabs/
    │       │   └── prefab_starter.kprefab
    │       └── textures/
    │           ├── texture_checker.png
    │           └── texture_gradient.png
    └── shooter/
        └── runtime/
            ├── game-assets.json
            ├── camera_paths/
            │   └── campaign_clear.kpath
            ├── materials/
            │   └── cache_material.kmaterial
            ├── meshes/
            │   └── cache_crate.obj
            ├── prefabs/
            │   └── pickup_beacon.kprefab
            └── states/
                └── warden_core.kstate
```

- `schemas/target.schema.json` — canonical target manifest.
- `schemas/keystone_assets.schema.json` — canonical Keystone asset pack.
- `schemas/game_assets.schema.json` — canonical reusable game-asset pack (v2).
- `validators/target.py` — target gate: registered id, safe paths, non-empty
  unique surfaces.
- `validators/keystone_assets.py` — Keystone pack gate: shape, digests, load
  order and prefab references.
- `validators/game_assets.py` — generic pack gate: provenance, kinds, digests
  and dependency order.
- `generators/target.py` — canonical target manifests, byte-identical on
  regeneration.
- `generators/keystone_assets.py` — seeded OBJ/PNG/KPREFAB pack generator.
- `generators/game_assets.py` — deterministic copy generator for authored
  game files.
- `adapters/registry.py` — the two registered consumers.
- `adapters/keystone.py` — engine asset kinds, suffixes, primitives and
  material-graph nodes.
- `adapters/shooter.py` — read-only authored JSON tables and tuning fields.
- `packs/keystone/starter/` — baselined Keystone assets (seed 42).
- `packs/shooter/runtime/` — baselined generic pack copied from Shooter;
  Keystone's own assets are never imported.
- `targets/` — checked-in manifests for both registered targets.
- `tools/targets.py` — list targets, write manifests, verify freshness.
- `tools/keystone_assets.py` — validate and load a pack through Keystone.
- `tools/game_assets.py` — validate and install a generic pack (dry-run,
  overwrite protection, post-install verification).
- `tools/verify.py` — Keystone AssetRegistry proof gate; the suite runs as the
  separate `test` gate.
- `.aikit/decisions.md` — ADRs, append-only.

## Registered Targets

| Target | Project | Lifecycle | Authored surfaces |
|---|---|---|---|
| shooter | `projects/shooter` | active | enemies, weapons, waves, arena covers, engagement, grade, juice, core material |
| keystone | `projects/keystone` | active | asset kinds, file suffixes, primitives, material nodes |

Foundry only reads these two projects; neither is ever written.

## Gates (never lowered)

1. Suite green (`python -m unittest discover tests`).
2. Every pack validates before it ships; invalid packs fail with field+reason.
3. Both target manifests are fresh and valid (`python generators/target.py
   --check`, `python validators/target.py "targets/*.json"`).
4. The Keystone starter pack is fresh and valid (`python generators/keystone_assets.py
   --check`, `python validators/keystone_assets.py`), and the runtime proof
   loads the starter pack (`python tools/keystone_assets.py --verify`).
5. The Shooter generic pack is valid (`python generators/game_assets.py --check`)
   and an installed copy re-validates after install.

<!-- aegean:brand-assets:start -->
## 🎨 Brand Assets

> **AI-Generated Brand Artwork.** The banner and logo are **AI-generated brand assets**. They are illustrative and may not literally depict every feature or the full project scope.
<!-- aegean:brand-assets:end -->

## 📜 License

<!-- aegean:license:start -->
Free for personal use under the Aegean License 1.1 (AL-1.1); see [LICENSE](LICENSE). Any commercial use needs the Aegean Commercial License 1.0 (ACL-1.0); see [COMMERCIAL.md](COMMERCIAL.md).
<!-- aegean:license:end -->
