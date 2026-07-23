#!/usr/bin/env python3
"""
mut.py — mutation test runner for lerxml.

For each foo.xml / foo.yml pair under tests/data/ (skipping archive/),
generates each mutation on the fly by running its XQuery Update Facility
expression against a running basex server, and validates the result with
the lerxml xsd and xta validators.

Modes:
  default   Fail if any expected code is missing from the found codes (subset check)
  --strict  Fail if found codes don't match expected codes exactly
  --report  Never fail; print a full table of mutations and their found codes

Usage:
  python mut.py
  python mut.py --strict
  python mut.py --report
  python mut.py -k elledning_2022
  python mut.py -k srsDimension -r
  python mut.py -k restriktioner

-k/--filter matches test IDs (e.g. "restriktioner/elledning_2022-03") by
substring, the same way pytest's -k does; only mutations whose test ID
contains the given string are run. Since the test ID includes the path
relative to mut/, this also lets you filter by folder (e.g. -k restriktioner
or -k andre_krav).

Requires a basex server to be running first, e.g.:
  basexserver -p1984

Requires a low-privilege basex user (one-time setup, run locally without a
running server):
  basex -c "CREATE USER lerxml lerxml"
  basex -c "GRANT CREATE TO lerxml"
CREATE is the lowest permission that allows running doc() and XQuery Update
expressions against arbitrary files; ADMIN is not needed.
"""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from lxml import etree

sys.path.insert(0, str(Path(__file__).parent / "vendor" / "basexclient"))
from BaseXClient import Session

from lerxml.xsd import validate_string as xsd_validate_string
from lerxml.xta import validate_string as xta_validate_string

DATA_DIR = Path(__file__).parent / "mut"

BASEX_HOST = "localhost"
BASEX_PORT = 1984
BASEX_USER = "lerxml"
BASEX_PASSWORD = "lerxml"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class MutationResult:
    test_id: str
    xml_path: Path
    xquery: str
    expected_codes: list[str]
    found_codes: set[str] = field(default_factory=set)
    error: str | None = None

    def check_subset(self) -> bool:
        return set(self.expected_codes).issubset(self.found_codes)

    def check_exact(self) -> bool:
        return set(self.expected_codes) == self.found_codes


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def collect_mutations(filter_str: str | None = None) -> list[tuple[str, Path, str, list[str]]]:
    mutations = []
    for yml_path in sorted(DATA_DIR.rglob("*.yml")):
        if "archive" in yml_path.parts:
            continue
        xml_path = yml_path.with_suffix(".xml")
        if not xml_path.exists():
            continue
        entries = yaml.safe_load(yml_path.read_text()) or []
        for entry in entries:
            entry_id     = str(entry["id"])
            xquery       = entry.get("xquery", "()")
            expected     = entry.get("expected", [])
            rel_path     = xml_path.relative_to(DATA_DIR).with_suffix("")
            test_id      = f"{rel_path}-{entry_id}"
            if filter_str is not None and filter_str not in test_id:
                continue
            mutations.append((test_id, xml_path, xquery, expected))
    return mutations


# ---------------------------------------------------------------------------
# Mutation generation (XQuery Update Facility via basex)
# ---------------------------------------------------------------------------

def generate_mutation(session: Session, xml_path: Path, xquery: str) -> str:
    """Run an XQuery Update Facility expression against xml_path via a
    running basex server and return the resulting XML as a string."""
    root = etree.parse(str(xml_path)).getroot()
    ns_decls = "".join(
        f"declare namespace {prefix}='{uri}';\n"
        for prefix, uri in root.nsmap.items()
        if prefix is not None
    )
    abs_xml = str(xml_path.resolve()).replace("'", "\\'")

    if xquery in (None, "", "()"):
        query = ns_decls + f"doc('{abs_xml}')"
    else:
        mutation = xquery.replace("$doc", "$d")
        query = (
            ns_decls
            + f"let $doc := doc('{abs_xml}')\n"
            + f"let $result := copy $d := $doc modify ({mutation}) return $d\n"
            + "return $result"
        )

    return session.query(query).execute()


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def connect() -> Session:
    try:
        return Session(BASEX_HOST, BASEX_PORT, BASEX_USER, BASEX_PASSWORD)
    except OSError as e:
        print(
            f"ERROR: Could not connect to a basex server at "
            f"{BASEX_HOST}:{BASEX_PORT} ({e}).\n"
            f"Start one first, e.g.: basexserver -p{BASEX_PORT}",
            file=sys.stderr,
        )
        sys.exit(1)


def run_mutations(filter_str: str | None = None) -> list[MutationResult]:
    session = connect()
    try:
        results = []
        for test_id, xml_path, xquery, expected in collect_mutations(filter_str):
            try:
                xml = generate_mutation(session, xml_path, xquery)
                found = (
                    {e.code for e in xsd_validate_string(xml)}
                    | {e.code for e in xta_validate_string(xml)}
                )
                results.append(MutationResult(
                    test_id=test_id,
                    xml_path=xml_path,
                    xquery=xquery,
                    expected_codes=expected,
                    found_codes=found,
                ))
            except Exception as e:
                results.append(MutationResult(
                    test_id=test_id,
                    xml_path=xml_path,
                    xquery=xquery,
                    expected_codes=expected,
                    error=str(e),
                ))
        return results
    finally:
        session.close()


# ---------------------------------------------------------------------------
# ANSI colors
# ---------------------------------------------------------------------------

RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RESET  = "\033[0m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def fmt(codes: set[str] | list[str]) -> str:
    return ", ".join(sorted(codes)) if codes else "(none)"


def fmt_cell(expected: list[str], found: set[str]) -> str:
    """Return a colored string for a found-codes cell."""
    text = fmt(found)
    expected_set = set(expected)
    if expected_set == found:
        return colorize(text, GREEN)
    elif expected_set.issubset(found):
        # Expected codes present but extra codes also fired
        return colorize(text, YELLOW)
    else:
        return colorize(text, RED)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(results: list[MutationResult]) -> None:
    col_id = max(len(r.test_id) for r in results)
    header = f"{'TEST':<{col_id}}  {'EXPECTED':<30}  FOUND"
    print(header)
    print("-" * len(header))

    for r in results:
        if r.error:
            print(f"{r.test_id:<{col_id}}  {colorize('ERROR: ' + r.error, RED)}")
            continue
        print(
            f"{r.test_id:<{col_id}}"
            f"  {fmt(r.expected_codes):<30}"
            f"  {fmt_cell(r.expected_codes, r.found_codes)}"
        )


def print_summary(results: list[MutationResult], strict: bool) -> tuple[int, int]:
    failures = 0
    for r in results:
        if r.error:
            print(f"  ERROR  {r.test_id}: {r.error}")
            failures += 1
            continue

        ok = r.check_exact() if strict else r.check_subset()
        if not ok:
            lines = [f"  FAIL   {r.test_id}:"]
            missing = set(r.expected_codes) - r.found_codes
            extra   = r.found_codes - set(r.expected_codes)
            if strict:
                if missing: lines.append(f"           missing={sorted(missing)}")
                if extra:   lines.append(f"           unexpected={sorted(extra)}")
            else:
                if missing: lines.append(f"           missing={sorted(missing)}, got={sorted(r.found_codes)}")
            print("\n".join(lines))
            failures += 1
        else:
            extra = r.found_codes - set(r.expected_codes)
            extra_str = f"  (also triggered: {sorted(extra)})" if extra and not strict else ""
            print(f"  PASS   {r.test_id}{extra_str}")

    return len(results), failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--strict",
        action="store_true",
        help="Fail if found codes don't match expected codes exactly",
    )
    mode.add_argument(
        "-r", "--report",
        action="store_true",
        help="Print a full table of mutations and found codes; never fail",
    )
    parser.add_argument(
        "-k", "--filter",
        dest="filter_str",
        default=None,
        help="Only run mutations whose test ID contains this substring",
    )
    args = parser.parse_args()

    results = run_mutations(args.filter_str)
    if not results:
        print(f"No mutations matched filter {args.filter_str!r}", file=sys.stderr)
        sys.exit(1)

    if args.report:
        print_report(results)
        sys.exit(0)

    total, failures = print_summary(results, strict=args.strict)
    mode_str = "strict" if args.strict else "subset"
    print(f"\n{total - failures}/{total} passed ({mode_str} mode)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
