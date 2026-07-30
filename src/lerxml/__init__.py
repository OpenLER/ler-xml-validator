from dataclasses import asdict, dataclass, field
from importlib.metadata import PackageNotFoundError, version as _pkg_version
from itertools import chain
from pathlib import Path
from typing import Literal

from lxml import etree
from lxml.etree import _ElementTree


@dataclass
class Violation:
    code: str  # E1, EL1, TL1, TL2, etc.
    message: str
    severity: Literal["error", "warning"] = "error"
    verbose_message: str | None = None
    location: str | None = None  # XPath to node (if available)
    line: int | None = None   # line number (if available)
    sub_codes: list[str] = field(default_factory=list)  # names of failed sub_assertions, if any


try:
    LERXML_VERSION = _pkg_version("lerxml")
except PackageNotFoundError:
    LERXML_VERSION = "0.0.0+unknown"


@dataclass
class Report:
    ler_version: str
    lerxml_version: str
    violations: list[Violation]

    @property
    def valid(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)

    def to_dict(self) -> dict:
        return {
            "ler_version": self.ler_version,
            "lerxml_version": self.lerxml_version,
            "valid": self.valid,
            "violations": [asdict(v) for v in self.violations],
        }


# Imported after Violation/Report are defined: these submodules do `from . import
# Violation` at import time, which requires the class to already exist in this module.
from . import geometri, schematron, xsd, xta  # noqa: E402


def validate(doc: _ElementTree, version: str = xsd.DEFAULT_VERSION) -> Report:
    violations = list(chain(
        xsd.validate(doc, version),
        xta.validate(doc, version),
        geometri.validate(doc),
    ))
    return Report(ler_version=version, lerxml_version=LERXML_VERSION, violations=violations)


def validate_file(path: str | Path, version: str = xsd.DEFAULT_VERSION) -> Report:
    doc = etree.parse(str(path))
    return validate(doc, version)


def validate_string(xml: str, version: str = xsd.DEFAULT_VERSION) -> Report:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    return validate(doc, version)
