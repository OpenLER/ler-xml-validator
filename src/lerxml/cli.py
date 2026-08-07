from argparse import ArgumentParser
from pathlib import Path
import sys

from lxml import etree

from . import geometri, schematron, xsd, xta
from . import Violation, validate as validate_report


def parse_xml(path: Path) -> etree._ElementTree:
    return etree.parse(str(path))


def print_violation(violation: Violation) -> None:
    location = f" at {violation.location}" if violation.location else ""
    line = f" line {violation.line}" if violation.line else ""

    print(f"{violation.code}: {violation.message}{location}{line}")


def run_validate(path: Path, mode: str, version: str | None = None) -> int:
    doc = parse_xml(path)

    if mode == "xsd":
        violations = list(xsd.validate(doc, version))
    elif mode == "schematron":
        violations = list(schematron.validate(doc))
    elif mode == "xta":
        violations = list(xta.validate(doc, version))
    elif mode == "geometri":
        violations = list(geometri.validate(doc))
    else:
        violations = validate_report(doc, version).violations

    for violation in violations:
        print_violation(violation)

    return 1 if violations else 0


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(prog="lerxml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ["validate", "xsd", "schematron", "xta", "geometri"]:
        subparser = subparsers.add_parser(command)
        subparser.add_argument("xml_file", type=Path)
        if command in ("validate", "xsd", "xta"):
            subparser.add_argument(
                "--version", "-V",
                dest="ler_version",
                choices=sorted(xsd.VERSIONS),
                required=True,
                help="LER version to validate against",
            )

    args = parser.parse_args(argv)
    version = getattr(args, "ler_version", None)

    return run_validate(args.xml_file, args.command, version)


if __name__ == "__main__":
    raise SystemExit(main())
