"""
Tjekker etableringstidspunkt mod LER's EtableringstidspunktRule (G5).

Se LER-bogen, "Andre krav", G5. XSD'en fanger næsten intet her, fordi
gml:TimePositionType er en union, der indeholder anyURI.
"""

import re
from collections.abc import Iterator
from datetime import date
from pathlib import Path

from lxml import etree
from lxml.etree import _Element, _ElementTree

from . import Violation

CUTOFF = date(2023, 7, 1)
CUTOFF_YEAR = str(CUTOFF.year)
FORMAT_RE = re.compile(r"\d{4}(-\d{2}(-\d{2})?)?")


def _g5(doc: _ElementTree, elem: _Element, sub_code: str, message: str) -> Violation:
    return Violation(
        code="G5",
        message=message,
        verbose_message="Se LER-bogen, 'Andre krav', G5.",
        xpath=doc.getpath(elem),
        line=elem.sourceline,
        sub_codes=[sub_code],
    )


def _after_cutoff(value: str) -> bool:
    """Strengt efter skæringsdatoen. En dato, der ikke findes (fx 2024-02-30), regner
    LER som før skæringsdatoen, så den er heller ikke efter her."""
    parts = value.split("-")
    if len(parts) == 1:
        return value > CUTOFF_YEAR
    year, month = int(parts[0]), int(parts[1])
    if not 1 <= month <= 12:
        return False
    if len(parts) == 2:
        return (year, month) > (CUTOFF.year, CUTOFF.month)
    try:
        return date.fromisoformat(value) > CUTOFF
    except ValueError:
        return False


def _check(doc: _ElementTree, elem: _Element) -> Iterator[Violation]:
    if elem.get("calendarEraName") is not None:
        yield _g5(doc, elem, "G5.6", "calendarEraName må ikke være sat")

    position = elem.get("indeterminatePosition")
    if position is not None and position != "before":
        yield _g5(doc, elem, "G5.4", f"indeterminatePosition er {position!r}, men må kun være 'before'")

    value = (elem.text or "").strip()
    if not value:
        yield _g5(doc, elem, "G5.2", "værdien er tom")
        return
    if not FORMAT_RE.fullmatch(value):
        yield _g5(doc, elem, "G5.1", f"{value!r} er ikke ÅÅÅÅ-MM-DD, ÅÅÅÅ-MM eller ÅÅÅÅ")
        return

    if position is None and value == CUTOFF_YEAR:
        yield _g5(doc, elem, "G5.3", f"året {value} er skæringsåret, så det kan ikke afgøres, om det er før eller efter skæringsdatoen")
    if position == "before" and _after_cutoff(value):
        yield _g5(doc, elem, "G5.5", f"med indeterminatePosition='before' må {value} ikke være efter skæringsdatoen {CUTOFF}")


def validate(doc: _ElementTree) -> Iterator[Violation]:
    for elem in doc.xpath("//*[local-name()='etableringstidspunkt']"):
        yield from _check(doc, elem)


def validate_file(path: str | Path) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc)


def validate_string(xml: str) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
