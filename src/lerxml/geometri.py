"""
Validerer den rå koordinat-geometri, uafhængigt af feature-type.

G1 (LER-bogen, "Andre krav"): LER's Check3DGeometry kræver 3 tal pr. vertex (G1.1),
og at srsDimension er 3, hvis den er sat (G1.2). Et forkert srsDimension ét sted
afvises uanset hvad der står andre steder, så hvert element tjekkes for sig.
"""

from collections.abc import Iterator
from pathlib import Path

from lxml import etree
from lxml.etree import _Element, _ElementTree
from shapely.errors import ShapelyError
from shapely.geometry import LineString as ShapelyLineString

from . import Violation

GML_NS = "http://www.opengis.net/gml/3.2"
POS_LIST_TAG = f"{{{GML_NS}}}posList"
POS_TAG = f"{{{GML_NS}}}pos"


def _parse_numbers(elem: _Element) -> list[float] | None:
    try:
        return [float(v) for v in (elem.text or "").split()]
    except ValueError:
        return None  # indeholder noget, der ikke er et tal; det fanger XSD'en


def _g1(doc: _ElementTree, elem: _Element, sub_code: str, message: str) -> Violation:
    return Violation(
        code="G1",
        message=message,
        verbose_message="Se LER-bogen, 'Andre krav', G1.",
        xpath=doc.getpath(elem),
        line=elem.sourceline,
        sub_codes=[sub_code],
    )


def _check_srs_dimension(doc: _ElementTree) -> Iterator[Violation]:
    for elem in doc.xpath("//*[@srsDimension]"):
        dim = elem.get("srsDimension")
        if dim.strip() != "3":
            yield _g1(doc, elem, "G1.2", f"srsDimension er {dim!r}, men skal være 3 eller udeladt")


def _check_pos(doc: _ElementTree, elem: _Element) -> Iterator[Violation]:
    values = _parse_numbers(elem)
    if values is not None and len(values) != 3:
        yield _g1(doc, elem, "G1.1", f"pos har {len(values)} tal, men skal have 3")


def _check_pos_list(doc: _ElementTree, elem: _Element) -> Iterator[Violation]:
    values = _parse_numbers(elem)
    if values is None:
        return
    if len(values) % 3 != 0:
        yield _g1(doc, elem, "G1.1", f"posList har {len(values)} tal, som ikke går op i 3 tal pr. vertex")
        return

    points = [(values[i], values[i + 1]) for i in range(0, len(values), 3)]
    if len(points) < 2:
        return
    try:
        line = ShapelyLineString(points)
    except (ShapelyError, ValueError):
        return

    if not line.is_simple:
        yield Violation(
            code="GEOM1",
            message="Geometrien krydser/rører sig selv",
            xpath=doc.getpath(elem),
            line=elem.sourceline,
        )


def validate(doc: _ElementTree) -> Iterator[Violation]:
    yield from _check_srs_dimension(doc)
    for elem in doc.iter(POS_TAG):
        yield from _check_pos(doc, elem)
    for elem in doc.iter(POS_LIST_TAG):
        yield from _check_pos_list(doc, elem)


def validate_file(path: str | Path) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc)


def validate_string(xml: str) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
