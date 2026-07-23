#!/usr/bin/env python3
"""
btest.py — branch test runner for lerxml.

An alternative to mut.py: instead of a flat list of independent mutations,
each *.yml under btest/ (skipping archive/) describes a tree. The root
names one source XML file and may itself carry assertions (checked against
the unmodified source). Each branch adds one incremental XQuery Update
Facility modification on top of its parent, and may itself carry assertions
plus further nested branches.

A test case corresponds to a node in the tree (root or branch): its XML is
the source with every ancestor's xquery applied, in order, followed by its
own. Every node is checked, not just leaves — this lets you assert partway
through a chain of modifications, not only at the end of it.

Node fields:
  source       (root only) path to the XML file, relative to the yml file
  name         (branches only, optional) short id for this branch; used to
               build the test path (falls back to a positional index when
               omitted, e.g. for branches whose xquery is too composite to
               summarize in a short name)
  xquery       (branches only) XQuery Update Facility expression, applied
               on top of the parent's accumulated state
  assertions   expected codes at this node (default: [])
  branches     child branches (default: [])

Example:
  source: elledning_2022.xml
  assertions: []
  branches:
    - name: mangler_driftsstatus
      xquery: delete node $doc//ler:driftsstatus
      assertions: [E1]
    - name: driftsstatus_ukendt
      xquery: replace node $doc//ler:driftsstatus with <ler:driftsstatus xsi:nil="true"/>
      assertions: []
      branches:
        - name: efter_skaeringsdato
          xquery: replace value of node $doc//ler:etableringstidspunkt with "2024-01-01"
          assertions: [driftsstatusVoidrestriktion]

Output is grouped by yml file (outer loop), and within each file the tree
is printed depth-first with indentation reflecting the branch structure.

Modes:
  default   Fail if any expected code is missing from the found codes (subset check)
  --strict  Fail if found codes don't match expected codes exactly

Usage:
  python btest.py
  python btest.py --strict
  python btest.py -k elledning_2022
  python btest.py -k driftsstatus_ukendt

-k/--filter matches test paths (e.g. "restr/elledning_2022/driftsstatus_ukendt/
forkert_dybde_enhed") by substring, the same way pytest's -k does and the same
way mut.py's -k does.

Requires a basex server to be running first, e.g.:
  basexserver -p1984
"""

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from mut import (
    GREEN,
    RED,
    YELLOW,
    colorize,
    connect,
    generate_mutation,
)

BTEST_DIR = Path(__file__).parent / "btest"

# Feature type templates dir: where shared source XML files live, referenced
# from source: fields as "$FT/...". Defaults to btest/ft/ when $FT isn't set.
FT_DIR = Path(os.environ.get("FT", BTEST_DIR / "ft")).resolve()

BRANCH_MARKER = "└─"
ASSERTION_MARKER = "·"


def resolve_source(source: str, yml_dir: Path) -> Path:
    """Resolve a source: field. "$FT/..." resolves against FT_DIR; anything
    else resolves relative to the yml file's own directory."""
    if source.startswith("$FT/"):
        return (FT_DIR / source.removeprefix("$FT/")).resolve()
    return (yml_dir / source).resolve()


def shorten_path(path: Path) -> str:
    """Shorten path using FT_DIR (feature type templates dir), if the path is
    actually inside it; otherwise fall back to the resolved path."""
    try:
        rel = path.resolve().relative_to(FT_DIR)
        return f"$FT/{rel}"
    except ValueError:
        return str(path.resolve())


# ---------------------------------------------------------------------------
# Tree parsing
# ---------------------------------------------------------------------------

@dataclass
class BranchNode:
    name: str | None
    xquery: str | None  # None for the root
    assertions: list[str]
    branches: list["BranchNode"] = field(default_factory=list)


def parse_branch(data: dict) -> BranchNode:
    return BranchNode(
        name=data.get("name"),
        xquery=data["xquery"],
        assertions=data.get("assertions", []),
        branches=[parse_branch(b) for b in data.get("branches", [])],
    )


def parse_root(data: dict) -> BranchNode:
    return BranchNode(
        name=None,
        xquery=None,
        assertions=data.get("assertions", []),
        branches=[parse_branch(b) for b in data.get("branches", [])],
    )


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

@dataclass
class NodeCase:
    path: list[str]  # ancestor labels within the tree, e.g. [] for root, ["a", "b"] for a nested branch
    xqueries: list[str]
    expected_codes: list[str]

    @property
    def depth(self) -> int:
        return len(self.path)


@dataclass
class FileGroup:
    yml_rel_path: str  # e.g. "restr/elledning_2022.yml"
    xml_path: Path
    cases: list[NodeCase]


def walk(node: BranchNode, path: list[str], xqueries: list[str]) -> list[NodeCase]:
    cases = [NodeCase(path=list(path), xqueries=list(xqueries), expected_codes=node.assertions)]
    for i, child in enumerate(node.branches):
        label = child.name if child.name is not None else str(i)
        cases.extend(walk(child, path=path + [label], xqueries=xqueries + [child.xquery]))
    return cases


def collect_tests(filter_str: str | None = None) -> list[FileGroup]:
    groups = []
    for yml_path in sorted(BTEST_DIR.rglob("*.yml")):
        if "archive" in yml_path.parts:
            continue
        data = yaml.safe_load(yml_path.read_text()) or {}
        xml_path = resolve_source(data["source"], yml_path.parent)
        yml_rel_path = str(yml_path.relative_to(BTEST_DIR))
        filter_path = str(yml_path.relative_to(BTEST_DIR).with_suffix(""))
        root = parse_root(data)
        cases = walk(root, path=[], xqueries=[])
        if filter_str is not None:
            cases = [
                c for c in cases
                if filter_str in "/".join([filter_path, *c.path])
            ]
        if cases:
            groups.append(FileGroup(yml_rel_path=yml_rel_path, xml_path=xml_path, cases=cases))
    return groups


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def combined_xquery(xqueries: list[str]) -> str:
    return ",\n".join(xqueries) if xqueries else "()"


@dataclass
class NodeResult:
    case: NodeCase
    found_codes: set[str] = field(default_factory=set)
    error: str | None = None

    def check_subset(self) -> bool:
        return set(self.case.expected_codes).issubset(self.found_codes)

    def check_exact(self) -> bool:
        return set(self.case.expected_codes) == self.found_codes


@dataclass
class FileResult:
    yml_rel_path: str
    xml_path: Path
    node_results: list[NodeResult]


def run_tests(filter_str: str | None = None) -> list[FileResult]:
    from lerxml.geometri import validate_string as geometri_validate_string
    from lerxml.xsd import validate_string as xsd_validate_string
    from lerxml.xta import validate_string as xta_validate_string

    session = connect()
    try:
        file_results = []
        for group in collect_tests(filter_str):
            node_results = []
            for case in group.cases:
                try:
                    xml = generate_mutation(session, group.xml_path, combined_xquery(case.xqueries))
                    found = (
                        {e.code for e in xsd_validate_string(xml)}
                        | {e.code for e in xta_validate_string(xml)}
                        | {e.code for e in geometri_validate_string(xml)}
                    )
                    node_results.append(NodeResult(case=case, found_codes=found))
                except Exception as e:
                    node_results.append(NodeResult(case=case, error=str(e)))
            file_results.append(FileResult(
                yml_rel_path=group.yml_rel_path,
                xml_path=group.xml_path,
                node_results=node_results,
            ))
        return file_results
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def indent_for(depth: int) -> str:
    return "  " + "   " * depth


def node_label(fr: FileResult, case: NodeCase) -> str:
    return shorten_path(fr.xml_path) if not case.path else case.path[-1]


def print_results(file_results: list[FileResult], strict: bool) -> tuple[int, int]:
    total = 0
    failures = 0

    for fr in file_results:
        print(fr.yml_rel_path)
        for r in fr.node_results:
            total += 1
            branch_indent = indent_for(r.case.depth)
            label = node_label(fr, r.case)
            print(f"{branch_indent}{BRANCH_MARKER} {label}")

            if r.error:
                print(f"{indent_for(r.case.depth + 1)}{ASSERTION_MARKER} {colorize('ERROR: ' + r.error, RED)}")
                failures += 1
                continue

            ok = r.check_exact() if strict else r.check_subset()
            if not ok:
                failures += 1

            assertion_indent = indent_for(r.case.depth + 1)
            expected = set(r.case.expected_codes)
            codes = expected | r.found_codes
            if not codes:
                print(f"{assertion_indent}{ASSERTION_MARKER} {colorize('OK (no codes expected or found)', GREEN)}")
                continue
            for code in sorted(codes):
                if code in expected and code in r.found_codes:
                    color = GREEN
                elif code in expected:
                    color = RED
                else:
                    color = RED if strict else YELLOW
                print(f"{assertion_indent}{ASSERTION_MARKER} {colorize(code, color)}")
        print()

    return total, failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if found codes don't match expected codes exactly",
    )
    parser.add_argument(
        "-k", "--filter",
        dest="filter_str",
        default=None,
        help="Only run test cases whose test path contains this substring",
    )
    args = parser.parse_args()

    file_results = run_tests(args.filter_str)
    if not file_results:
        print(f"No test cases matched filter {args.filter_str!r}", file=sys.stderr)
        sys.exit(1)

    total, failures = print_results(file_results, strict=args.strict)
    mode_str = "strict" if args.strict else "subset"
    print(f"{total - failures}/{total} passed ({mode_str} mode)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
