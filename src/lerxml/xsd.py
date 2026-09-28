from collections.abc import Iterator
from pathlib import Path

import xmlschema
from importlib.resources import files
from lxml import etree
from lxml.etree import _ElementTree

from . import Violation

XSD_DIR = files("lerxml") / "xsd"

# Newest first - used as the display order where relevant.
VERSIONS = {
    "2.2.0": "2.2_ler.xsd",
    "2.1.0": "2.1_ler.xsd",
    "2.0.1": "2.0_ler.xsd",
    "2.0.0": "2.0_ler.xsd",
}
LATEST_VERSION = "2.2.0"
DEFAULT_VERSION = LATEST_VERSION

# External standards (GML, ISO 19139/gmx, Dublin Core) are vendored once under
# xsd/http|https/, shared across every LER version. 2.2.0's own XSD already
# references them via relative paths into that vendored tree; 2.0.0/2.0.1/2.1.0's
# XSDs reference the same namespaces via absolute external URLs instead.
# Passing this uniformly for every version resolves both cases against the local
# vendored copies, so loading a schema never depends on a live network fetch.
EXTERNAL_LOCATIONS = [
    ("http://www.opengis.net/gml/3.2", str(XSD_DIR / "http/schemas.opengis.net/gml/3.2.1/gml.xsd")),
    ("http://www.isotc211.org/2005/gmx", str(XSD_DIR / "https/schemas.isotc211.org/19139/-/gmx/1.0/gmx.xsd")),
    ("http://purl.org/dc/terms/", str(XSD_DIR / "https/www.dublincore.org/schemas/xmls/qdc/2008/02/11/dcterms.xsd")),
]

_schemas: dict[str, xmlschema.XMLSchema] = {}


def get_schema(version: str) -> xmlschema.XMLSchema:
    if version not in VERSIONS:
        raise ValueError(f"Unknown LER version {version!r}; known versions: {sorted(VERSIONS)}")
    if version not in _schemas:
        xsd_path = XSD_DIR / version / VERSIONS[version]
        _schemas[version] = xmlschema.XMLSchema(xsd_path, locations=EXTERNAL_LOCATIONS)
    return _schemas[version]


def check_schema_version(doc: _ElementTree, version: str) -> Iterator[Violation]:
    """G8: warn unless the root element's schemaVersion attribute (if present) is
    exactly the X.Y.Z being validated against. X.Y is not enough, since e.g. 2.0.0
    and 2.0.1 share an XSD but differ in restrictions. Only Graveforespoergselssvar
    carries schemaVersion; fragments (e.g. a single feature) have none, so there is
    nothing to compare there."""
    root = doc.getroot()
    raw = root.get("schemaVersion")
    if raw is None or raw == version:
        return
    yield Violation(
        code="G8",
        message=f"der valideres efter LER {version}, men dokumentets schemaVersion er {raw!r}",
        severity="warning",
        verbose_message="Se LER-bogen, 'Andre krav', G8.",
        xpath=doc.getpath(root),
        line=root.sourceline,
    )


def validate(doc: _ElementTree, version: str) -> Iterator[Violation]:
    for err in get_schema(version).iter_errors(doc):
        yield Violation(
            code="XSD",
            message=err.reason,
            verbose_message=str(err),
            xpath=err.path,
            line=err.sourceline,
        )

def validate_file(path: str | Path, version: str) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc, version)

def validate_string(xml: str, version: str) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc, version)
