"""
Tjekker at xmlns:xlink er deklareret i dokumentet, selvom prefixet ikke bruges.

Se LER-bogen, "Andre krav", G4 for baggrund, og
xlink_namespace_problem.md i dette repo for reproduktion.
"""

from collections.abc import Iterator
from pathlib import Path

from lxml import etree
from lxml.etree import _ElementTree

from . import Violation

XLINK_NS = "http://www.w3.org/1999/xlink"


def validate(doc: _ElementTree) -> Iterator[Violation]:
    if any(XLINK_NS in elem.nsmap.values() for elem in doc.iter()):
        return
    yield Violation(
        code="G4",
        message="xmlns:xlink er ikke deklareret i dokumentet",
        verbose_message="Se LER-bogen, 'Andre krav', G4.",
        location=doc.getpath(doc.getroot()),
    )


def validate_file(path: str | Path) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc)


def validate_string(xml: str) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
