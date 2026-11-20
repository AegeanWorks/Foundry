"""Keystone proof gate: load the generated pack through the real AssetRegistry.

`aikit check foundry` runs this as its `verify` gate. The unittest suite is a
separate `test` gate in .aikit/project.json, so the two checks do not repeat
each other. A failure here means Foundry emitted a pack Keystone cannot use.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))


def run_keystone_proof() -> int:
    from generators.keystone_assets import DEFAULT_OUT
    from tools.keystone_assets import verify_pack

    print(verify_pack(DEFAULT_OUT))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Load the Foundry pack through Keystone.")
    ap.add_argument(
        "--verify",
        action="store_true",
        help="explicit name for the Keystone load-proof gate",
    )
    ap.parse_args(argv)
    return run_keystone_proof()


if __name__ == "__main__":
    raise SystemExit(main())
