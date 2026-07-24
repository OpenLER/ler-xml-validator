from argparse import ArgumentParser
from itertools import chain
from pathlib import Path
import sys

from lxml import etree

from . import geometri, schematron, xsd, xta
from . import ValidationError


def parse_xml(path: Path) -> etree._ElementTree:
    return etree.parse(str(path))


def validate_all(path: Path, version: str = xsd.DEFAULT_VERSION):
    doc = parse_xml(path)

    yield from xsd.validate(doc, version)
    yield from xta.validate(doc, version)


def print_error(error: ValidationError) -> None:
    location = f" at {error.location}" if error.location else ""
    line = f" line {error.line}" if error.line else ""

    print(f"{error.code}: {error.message}{location}{line}")


def run_validate(path: Path, mode: str, version: str = xsd.DEFAULT_VERSION) -> int:
    doc = parse_xml(path)

    if mode == "xsd":
        errors = list(xsd.validate(doc, version))
    elif mode == "schematron":
        errors = list(schematron.validate(doc))
    elif mode == "xta":
        errors = list(xta.validate(doc, version))
    elif mode == "geometri":
        errors = list(geometri.validate(doc))
    else:
        errors = list(chain(
            xsd.validate(doc, version),
            xta.validate(doc, version),
        ))

    for error in errors:
        print_error(error)

    return 1 if errors else 0


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
                default=xsd.DEFAULT_VERSION,
                help=f"LER version to validate against (default: {xsd.DEFAULT_VERSION})",
            )

    args = parser.parse_args(argv)
    version = getattr(args, "ler_version", xsd.DEFAULT_VERSION)

    return run_validate(args.xml_file, args.command, version)


if __name__ == "__main__":
    raise SystemExit(main())
