#!/usr/bin/env python3
"""
run_mutation_tests.py — mutation test runner for lerxml.

For each foo.xml / foo.yml pair under tests/data/ (skipping archive/),
applies each XQuery mutation via BaseX and validates the result with
the lerxml schematron validator.

Modes:
  default   Fail if any expected code is missing from the found codes (subset check)
  --strict  Fail if found codes don't match expected codes exactly
  --report  Never fail; print a full table of mutations and their found codes

Usage:
  python run_mutation_tests.py --basex-jar .basex-jar/basex-11.7.jar
  python run_mutation_tests.py --basex-jar .basex-jar/basex-11.7.jar --strict
  python run_mutation_tests.py --basex-jar .basex-jar/basex-11.7.jar --report
"""

import argparse
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import yaml

from lerxml.schematron import validate_string

DATA_DIR = Path(__file__).parent / "tests" / "data"
BASEX_CLASS = "org.basex.BaseX"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class MutationResult:
    test_id: str
    xml_path: Path
    xquery: str
    expected_codes: list[str]
    found_codes: set[str]
    error: str | None = None

    @property
    def passed(self) -> bool:
        if self.error:
            return False
        return True

    def check_subset(self) -> bool:
        return set(self.expected_codes).issubset(self.found_codes)

    def check_exact(self) -> bool:
        return set(self.expected_codes) == self.found_codes


# ---------------------------------------------------------------------------
# BaseX
# ---------------------------------------------------------------------------

def apply_xquery_mutation(xml_path: Path, xquery: str, basex_jar: Path) -> str:
    wrapped = textwrap.dedent(f"""\
        declare namespace ler = "http://data.gov.dk/schemas/LER/2/gml";
        declare namespace gml = "http://www.opengis.net/gml/3.2";
        declare namespace xsi = "http://www.w3.org/2001/XMLSchema-instance";

        let $doc := doc('{xml_path.as_posix()}')
        return (
          copy $mutated := $doc
          modify ({xquery.strip().replace('$doc', '$mutated')})
          return $mutated
        )
    """)
    result = subprocess.run(
        ["java", "-cp", str(basex_jar), BASEX_CLASS, "-q", wrapped],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def collect_mutations() -> list[tuple[str, Path, str, list[str]]]:
    mutations = []
    for yml_path in sorted(DATA_DIR.rglob("*.yml")):
        if "archive" in yml_path.parts:
            continue
        xml_path = yml_path.with_suffix(".xml")
        if not xml_path.exists():
            continue
        entries = yaml.safe_load(yml_path.read_text()) or []
        for i, entry in enumerate(entries):
            codes = entry["codes"]
            test_id = f"{xml_path.stem}-{'-'.join(codes) if codes else i}"
            mutations.append((test_id, xml_path, entry["xquery"], codes))
    return mutations


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_mutations(basex_jar: Path) -> list[MutationResult]:
    results = []
    for test_id, xml_path, xquery, expected_codes in collect_mutations():
        try:
            mutated_xml = apply_xquery_mutation(xml_path, xquery, basex_jar)
            errors = list(validate_string(mutated_xml))
            found_codes = {e.code for e in errors}
            results.append(MutationResult(
                test_id=test_id,
                xml_path=xml_path,
                xquery=xquery,
                expected_codes=expected_codes,
                found_codes=found_codes,
            ))
        except RuntimeError as e:
            results.append(MutationResult(
                test_id=test_id,
                xml_path=xml_path,
                xquery=xquery,
                expected_codes=expected_codes,
                found_codes=set(),
                error=str(e),
            ))
    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(results: list[MutationResult]) -> None:
    col_id = max(len(r.test_id) for r in results)
    col_exp = max(len(str(r.expected_codes)) for r in results)

    header = f"{'TEST':<{col_id}}  {'EXPECTED':<{col_exp}}  FOUND"
    print(header)
    print("-" * len(header))

    for r in results:
        if r.error:
            found_str = f"ERROR: {r.error}"
        else:
            found_str = str(sorted(r.found_codes)) if r.found_codes else "(no errors)"
        print(f"{r.test_id:<{col_id}}  {str(r.expected_codes):<{col_exp}}  {found_str}")


def print_summary(results: list[MutationResult], strict: bool) -> tuple[int, int]:
    failures = 0
    for r in results:
        if r.error:
            print(f"  ERROR  {r.test_id}: {r.error}")
            failures += 1
            continue

        ok = r.check_exact() if strict else r.check_subset()
        if not ok:
            if strict:
                missing = set(r.expected_codes) - r.found_codes
                extra = r.found_codes - set(r.expected_codes)
                detail = []
                if missing:
                    detail.append(f"missing={sorted(missing)}")
                if extra:
                    detail.append(f"unexpected={sorted(extra)}")
                print(f"  FAIL   {r.test_id}: {', '.join(detail)}")
            else:
                missing = set(r.expected_codes) - r.found_codes
                print(f"  FAIL   {r.test_id}: missing={sorted(missing)}, got={sorted(r.found_codes)}")
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
    parser.add_argument(
        "--basex-jar",
        required=True,
        type=Path,
        help="Path to the BaseX JAR file",
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

    if not args.basex_jar.exists():
        print(f"Error: BaseX JAR not found: {args.basex_jar}", file=sys.stderr)
        sys.exit(1)

    results = run_mutations(args.basex_jar)

    if args.report:
        print_report(results)
        sys.exit(0)

    total, failures = print_summary(results, strict=args.strict)
    mode_str = "strict" if args.strict else "subset"
    print(f"\n{total - failures}/{total} passed ({mode_str} mode)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
