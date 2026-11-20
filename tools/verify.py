"""Canonical Foundry verification: full suite plus the Keystone load proof.

`aikit check foundry` runs this as its `verify` gate. It first runs the same
unittest discovery as `test_command`, then loads the generated starter pack
through Keystone's real AssetRegistry. A failure in either half fails the gate.
"""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
if str(FOUNDRY_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDRY_ROOT))


def run_suite() -> int:
    suite = unittest.defaultTestLoader.discover(str(FOUNDRY_ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 2


def run_keystone_proof() -> int:
    from generators.keystone_assets import DEFAULT_OUT
    from tools.keystone_assets import verify_pack

    print(verify_pack(DEFAULT_OUT))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run Foundry's canonical verification gate.")
    ap.add_argument(
        "--verify",
        action="store_true",
        help="also load the generated pack through Keystone's AssetRegistry",
    )
    args = ap.parse_args(argv)
    status = run_suite()
    if status != 0:
        return status
    if args.verify:
        return run_keystone_proof()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
