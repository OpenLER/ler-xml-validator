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


def get_schema(version: str = DEFAULT_VERSION) -> xmlschema.XMLSchema:
    if version not in VERSIONS:
        raise ValueError(f"Unknown LER version {version!r}; known versions: {sorted(VERSIONS)}")
    if version not in _schemas:
        xsd_path = XSD_DIR / version / VERSIONS[version]
        _schemas[version] = xmlschema.XMLSchema(xsd_path, locations=EXTERNAL_LOCATIONS)
    return _schemas[version]


# Backward-compat module-level singleton: xta.py's rule set is only written
# against 2.2.0's schema so far, and imports this directly.
schema = get_schema(DEFAULT_VERSION)


def validate(doc: _ElementTree, version: str = DEFAULT_VERSION) -> Iterator[Violation]:
    for err in get_schema(version).iter_errors(doc):
        yield Violation(
            code="E1",
            message=err.reason,
            verbose_message=str(err),
            location=err.path,
            line=getattr(err, "position", (None, None))[0],
        )

def validate_file(path: str | Path, version: str = DEFAULT_VERSION) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc, version)

def validate_string(xml: str, version: str = DEFAULT_VERSION) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc, version)
