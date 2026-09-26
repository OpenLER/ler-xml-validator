"""
Oplyser om XML-kommentarer i dokumentet (G3).

LER-bogen, "Andre krav", G3 siger, at XML-kommentarer ikke er tilladt. LER har
tidligere haft problemer med kommentarer, men det er formentlig rettet.
Kommentarer er derfor ikke en fejl eller en advarsel, kun en oplysning, som kan
være relevant, hvis LER afviser dokumentet af uforklarlige grunde.
"""

from collections.abc import Iterator
from pathlib import Path

from lxml import etree
from lxml.etree import _ElementTree

from . import Violation


def validate(doc: _ElementTree) -> Iterator[Violation]:
    comments = doc.xpath("//comment()")
    if not comments:
        return
    first = comments[0]
    n = len(comments)
    yield Violation(
        code="G3",
        message=(
            f"dokumentet indeholder {n} XML-kommentar{'er' if n != 1 else ''} "
            "(LER har tidligere haft problemer med kommentarer)"
        ),
        severity="info",
        verbose_message="Se LER-bogen, 'Andre krav', G3.",
        xpath=doc.getpath(first) if first.getparent() is not None else None,
        line=first.sourceline,
    )


def validate_file(path: str | Path) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc)


def validate_string(xml: str) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
