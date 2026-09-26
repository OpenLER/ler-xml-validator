"""
Validerer den rå koordinat-geometri, uafhængigt af feature-type.
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


def _find_dimension(elem: _Element) -> int:
    """srsDimension kan sidde direkte på elementet eller arves fra en forfader
    (samme opslagsmåde som andre_krav/srsdimension_pos.sch bruger for XYZ1)."""
    node = elem
    while node is not None:
        dim = node.get("srsDimension")
        if dim is not None:
            return int(dim)
        node = node.getparent()
    return 2


def _group_points(values: list[float], dim: int) -> list[tuple[float, ...]] | None:
    if dim <= 0 or len(values) % dim != 0:
        return None
    return [tuple(values[i:i + dim]) for i in range(0, len(values), dim)]


def _check_pos_list(doc: _ElementTree, elem: _Element) -> Iterator[Violation]:
    try:
        values = [float(v) for v in (elem.text or "").split()]
    except ValueError:
        yield Violation(
            code="GEOM3",
            message="posList indeholder noget, der ikke er et tal",
            xpath=doc.getpath(elem),
            line=elem.sourceline,
        )
        return
    try:
        dim = _find_dimension(elem)
    except ValueError:
        return  # srsDimension er ikke et heltal; det fanger XSD'en
    points = _group_points(values, dim)
    if points is None:
        yield Violation(
            code="GEOM2",
            message="Antallet af tal i posList er ikke deleligt med srsDimension",
            xpath=doc.getpath(elem),
            line=elem.sourceline,
        )
        return
    if len(points) < 2:
        return

    xy_points = [(p[0], p[1]) for p in points]
    try:
        line = ShapelyLineString(xy_points)
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
    for elem in doc.iter(POS_LIST_TAG):
        yield from _check_pos_list(doc, elem)


def validate_file(path: str | Path) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc)


def validate_string(xml: str) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
