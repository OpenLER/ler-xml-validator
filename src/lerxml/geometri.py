"""
Validerer den rå koordinat-geometri, uafhængigt af feature-type.
"""

from collections.abc import Iterator
from pathlib import Path

from lxml import etree
from lxml.etree import _Element, _ElementTree
from shapely.errors import ShapelyError
from shapely.geometry import LineString as ShapelyLineString

from . import ValidationError

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


def _parse_points(elem: _Element) -> list[tuple[float, ...]] | None:
    dim = _find_dimension(elem)
    values = [float(v) for v in (elem.text or "").split()]
    if dim <= 0 or len(values) % dim != 0:
        return None
    return [tuple(values[i:i + dim]) for i in range(0, len(values), dim)]


def _check_pos_list(doc: _ElementTree, elem: _Element) -> Iterator[ValidationError]:
    points = _parse_points(elem)
    if points is None:
        yield ValidationError(
            code="GEOM2",
            message="Antallet af tal i posList er ikke deleligt med srsDimension",
            location=doc.getpath(elem),
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
        yield ValidationError(
            code="GEOM1",
            message="Geometrien krydser/rører sig selv",
            location=doc.getpath(elem),
        )


def validate(doc: _ElementTree) -> Iterator[ValidationError]:
    for elem in doc.iter(POS_LIST_TAG):
        yield from _check_pos_list(doc, elem)


def validate_file(path: str | Path) -> Iterator[ValidationError]:
    doc = etree.parse(str(path))
    yield from validate(doc)


def validate_string(xml: str) -> Iterator[ValidationError]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
