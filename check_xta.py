#!/usr/bin/env python3
"""
check_xta.py — static variable-scope check for src/lerxml/xta/{version}/*.yml.

Builds xta.get_cache() for every known LER version. Each cache build already
runs xta._check_variable_scope() internally (every '$variable' referenced by
an assertion/sub_assertion, or by a later variable's own expression, must be
defined earlier in that element's variable chain) - this script just forces
that check to run for all versions without needing a BaseX server or a
single XML fixture, so it can run in CI on every change to the xta rule
files.

A '$variable' crashes the real validator (elementpath.exceptions.
ElementPathNameError) instead of failing as a Violation when it's missing,
so catching this at generation/CI time beats discovering it when a random
user's document happens to hit the broken branch.

Usage:
  python check_xta.py
"""

import sys

from lerxml import xsd, xta


def main() -> int:
    failed = False
    for version in sorted(xsd.VERSIONS, reverse=True):
        try:
            xta.get_cache(version)
        except ValueError as e:
            failed = True
            print(f"{version}: FEJL\n{e}\n", file=sys.stderr)
        else:
            print(f"{version}: OK")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
