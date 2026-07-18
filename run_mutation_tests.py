#!/usr/bin/env python3
"""
run_mutation_tests.py — mutation test runner for lerxml.

For each foo.xml / foo.yml pair under tests/data/ (skipping archive/),
generates each mutation on the fly by running its XQuery Update Facility
expression through the `basex` CLI, and validates the result with both the
lerxml XSD and schematron validators.

Modes:
  default   Fail if any expected code is missing from the found codes (subset check)
  --strict  Fail if found codes don't match expected codes exactly
  --report  Never fail; print a full table of mutations and their found codes

Usage:
  python run_mutation_tests.py
  python run_mutation_tests.py --strict
  python run_mutation_tests.py --report

Requires the `basex` CLI to be installed and on PATH.
"""

import argparse
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from lxml import etree

from lerxml.schematron import validate_string as sch_validate_string
from lerxml.xsd import validate_string as xsd_validate_string

DATA_DIR = Path(__file__).parent / "tests" / "data"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class MutationResult:
    test_id: str
    xml_path: Path
    xquery: str
    expected_xsd_codes: list[str]
    expected_sch_codes: list[str]
    found_xsd_codes: set[str] = field(default_factory=set)
    found_sch_codes: set[str] = field(default_factory=set)
    error: str | None = None

    def check_subset(self) -> bool:
        return (
            set(self.expected_xsd_codes).issubset(self.found_xsd_codes)
            and set(self.expected_sch_codes).issubset(self.found_sch_codes)
        )

    def check_exact(self) -> bool:
        return (
            set(self.expected_xsd_codes) == self.found_xsd_codes
            and set(self.expected_sch_codes) == self.found_sch_codes
        )


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def collect_mutations() -> list[tuple[str, Path, str, list[str], list[str]]]:
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
            xsd_codes    = entry.get("xsd_codes", [])
            sch_codes    = entry.get("sch_codes", [])
            test_id      = f"{xml_path.stem}-{entry_id}"
            mutations.append((test_id, xml_path, xquery, xsd_codes, sch_codes))
    return mutations


# ---------------------------------------------------------------------------
# Mutation generation (XQuery Update Facility via basex)
# ---------------------------------------------------------------------------

def generate_mutation(xml_path: Path, xquery: str) -> str:
    """Run an XQuery Update Facility expression against xml_path via the
    basex CLI and return the resulting XML as a string."""
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

    # Written to a temp file rather than passed via -q: XQuery uses '$' for
    # variables, which a shell would otherwise try to expand.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xq", delete=False) as f:
        f.write(query)
        query_path = Path(f.name)

    try:
        result = subprocess.run(
            ["basex", str(query_path)],
            capture_output=True,
            text=True,
        )
    finally:
        query_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"basex failed: {result.stderr.strip()}")

    return result.stdout


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_mutations() -> list[MutationResult]:
    results = []
    for test_id, xml_path, xquery, xsd_codes, sch_codes in collect_mutations():
        try:
            xml = generate_mutation(xml_path, xquery)
            found_xsd = {e.code for e in xsd_validate_string(xml)}
            found_sch = {e.code for e in sch_validate_string(xml)}
            results.append(MutationResult(
                test_id=test_id,
                xml_path=xml_path,
                xquery=xquery,
                expected_xsd_codes=xsd_codes,
                expected_sch_codes=sch_codes,
                found_xsd_codes=found_xsd,
                found_sch_codes=found_sch,
            ))
        except Exception as e:
            results.append(MutationResult(
                test_id=test_id,
                xml_path=xml_path,
                xquery=xquery,
                expected_xsd_codes=xsd_codes,
                expected_sch_codes=sch_codes,
                error=str(e),
            ))
    return results


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


def fmt_cell(expected: list[str], found: set[str], width: int) -> str:
    """Return a padded, colored string for a found-codes cell."""
    text = fmt(found)
    padded = f"{text:<{width}}"
    expected_set = set(expected)
    if expected_set == found:
        return colorize(padded, GREEN)
    elif expected_set.issubset(found):
        # Expected codes present but extra codes also fired
        return colorize(padded, YELLOW)
    else:
        return colorize(padded, RED)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(results: list[MutationResult]) -> None:
    col_id = max(len(r.test_id) for r in results)
    w = 20
    header = f"{'TEST':<{col_id}}  {'XSD expected':<{w}}  {'XSD found':<{w}}  {'SCH expected':<{w}}  SCH found"
    print(header)
    print("-" * len(header))

    for r in results:
        if r.error:
            print(f"{r.test_id:<{col_id}}  {colorize('ERROR: ' + r.error, RED)}")
            continue
        print(
            f"{r.test_id:<{col_id}}"
            f"  {fmt(r.expected_xsd_codes):<{w}}"
            f"  {fmt_cell(r.expected_xsd_codes, r.found_xsd_codes, w)}"
            f"  {fmt(r.expected_sch_codes):<{w}}"
            f"  {fmt_cell(r.expected_sch_codes, r.found_sch_codes, w)}"
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
            if strict:
                xsd_missing = set(r.expected_xsd_codes) - r.found_xsd_codes
                xsd_extra   = r.found_xsd_codes - set(r.expected_xsd_codes)
                sch_missing = set(r.expected_sch_codes) - r.found_sch_codes
                sch_extra   = r.found_sch_codes - set(r.expected_sch_codes)
                if xsd_missing: lines.append(f"           xsd missing={sorted(xsd_missing)}")
                if xsd_extra:   lines.append(f"           xsd unexpected={sorted(xsd_extra)}")
                if sch_missing: lines.append(f"           sch missing={sorted(sch_missing)}")
                if sch_extra:   lines.append(f"           sch unexpected={sorted(sch_extra)}")
            else:
                xsd_missing = set(r.expected_xsd_codes) - r.found_xsd_codes
                sch_missing = set(r.expected_sch_codes) - r.found_sch_codes
                if xsd_missing: lines.append(f"           xsd missing={sorted(xsd_missing)}, got={sorted(r.found_xsd_codes)}")
                if sch_missing: lines.append(f"           sch missing={sorted(sch_missing)}, got={sorted(r.found_sch_codes)}")
            print("\n".join(lines))
            failures += 1
        else:
            extras = []
            xsd_extra = r.found_xsd_codes - set(r.expected_xsd_codes)
            sch_extra = r.found_sch_codes - set(r.expected_sch_codes)
            if xsd_extra: extras.append(f"xsd also triggered: {sorted(xsd_extra)}")
            if sch_extra: extras.append(f"sch also triggered: {sorted(sch_extra)}")
            extra_str = f"  ({', '.join(extras)})" if extras and not strict else ""
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
        "--report",
        action="store_true",
        help="Print a full table of mutations and found codes; never fail",
    )
    args = parser.parse_args()

    results = run_mutations()

    if args.report:
        print_report(results)
        sys.exit(0)

    total, failures = print_summary(results, strict=args.strict)
    mode_str = "strict" if args.strict else "subset"
    print(f"\n{total - failures}/{total} passed ({mode_str} mode)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
