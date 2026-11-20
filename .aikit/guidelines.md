# Project Guidelines

Rules for this project only, written by people or AI agents. They add to AIKit's principles and
rank below them: a guideline never overrides a principle (PRINCIPLE-000 R6, PRINCIPLE-001 R4).
Add one with `python aikit.py guideline <name> "<rule>" --source <user|ADR-NNN|person>`, or by
hand as one line below in the form `- **G-NNN** (source): rule`; IDs are never reused.

Persisted state carries a format version. A loader refuses a version it does not support,
without modifying or quarantining that file; older versions migrate when a migration exists.

## Rules
- **G-001** (user): Publish only through python aikit.py publish foundry; never create or push the repository with raw gh or git commands.
- **G-002** (user): Foundry exists to accelerate game creation with reusable, validated asset packs: prefer a generic, versioned install path and coverage of the asset kinds games actually use over one-off per-game content.
- **G-003** (user): Foundry's product is material other projects reuse, not a live source path: capture each reusable asset byte-for-byte into a versioned, digest-verified pack under packs/ with a checked-in manifest, keep source projects read-only, resolve any source by project id through adapters.layout.project_root (active path first, archive fallback), and verify a consumer can install the pack with no source project present so a path change or archive never changes what ships.
