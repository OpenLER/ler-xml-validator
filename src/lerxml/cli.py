from argparse import ArgumentParser
from pathlib import Path
import sys

from lxml import etree

from . import geometri, xsd, xta
from . import Violation, validate as validate_report


def parse_xml(path: Path) -> etree._ElementTree:
    return etree.parse(str(path))


def print_violation(violation: Violation) -> None:
    xpath = f" at {violation.xpath}" if violation.xpath else ""
    line = f" line {violation.line}" if violation.line else ""

    marker = "[WRN]" if violation.severity == "warning" else "[ERR]"

    print(f"{marker} {violation.code}: {violation.message}{xpath}{line}")


def run_validate(path: Path, mode: str, version: str | None = None) -> int:
    doc = parse_xml(path)

    if mode == "xsd":
        violations = list(xsd.validate(doc, version))
    elif mode == "xta":
        violations = list(xta.validate(doc, version))
    elif mode == "geometri":
        violations = list(geometri.validate(doc))
    else:
        violations = validate_report(doc, version).violations

    for violation in violations:
        print_violation(violation)

    n_errors = sum(v.severity == "error" for v in violations)
    n_warnings = len(violations) - n_errors
    print(summary(n_errors, n_warnings, version))

    return 1 if n_errors else 0


def summary(n_errors: int, n_warnings: int, version: str | None) -> str:
    against = f" efter LER {version}" if version else ""
    warnings = f"{n_warnings} advarsel" if n_warnings == 1 else f"{n_warnings} advarsler"
    if n_errors:
        counts = f"{n_errors} fejl" + (f", {warnings}" if n_warnings else "")
        return f"Ugyldig{against}: {counts}"
    return f"Gyldig{against}" + (f" ({warnings})" if n_warnings else "")


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(prog="lerxml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ["validate", "xsd", "xta", "geometri"]:
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
