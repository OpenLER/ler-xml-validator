from argparse import ArgumentParser
from itertools import chain
from pathlib import Path
import sys

from lxml import etree

from . import schematron, xsd
from . import ValidationError


def parse_xml(path: Path) -> etree._ElementTree:
    return etree.parse(str(path))


def validate_all(path: Path):
    doc = parse_xml(path)

    yield from xsd.validate(doc)
    yield from schematron.validate(doc)


def print_error(error: ValidationError) -> None:
    location = f" at {error.location}" if error.location else ""
    line = f" line {error.line}" if error.line else ""

    print(f"{error.code}: {error.message}{location}{line}")


def run_validate(path: Path, mode: str) -> int:
    doc = parse_xml(path)

    if mode == "xsd":
        errors = list(xsd.validate(doc))
    elif mode == "schematron":
        errors = list(schematron.validate(doc))
    else:
        errors = list(chain(
            xsd.validate(doc),
            schematron.validate(doc),
        ))

    for error in errors:
        print_error(error)

    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(prog="lerxml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ["validate", "xsd", "schematron"]:
        subparser = subparsers.add_parser(command)
        subparser.add_argument("xml_file", type=Path)

    args = parser.parse_args(argv)

    return run_validate(args.xml_file, args.command)


if __name__ == "__main__":
    raise SystemExit(main())
