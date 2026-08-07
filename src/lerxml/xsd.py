import warnings
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


# Backward-compat module-level singleton: xta.py's rule set is only written
# against 2.2.0's schema so far, and imports this directly.
schema = get_schema(DEFAULT_VERSION)


def resolve_schema_version(raw: str) -> str:
    """Expand a bare X.Y schemaVersion attribute value to the X.Y.Z we validate against.

    2.0 is a documented exception: 2.0.0 and 2.0.1 differ substantially, and
    schemaVersion="2.0" always means 2.0.1 (see adr/903)."""
    if raw == "2.0":
        return "2.0.1"
    if raw.count(".") == 1:
        return f"{raw}.0"
    return raw


def warn_if_schema_version_mismatch(doc: _ElementTree, version: str) -> None:
    """Warn when the root element's schemaVersion attribute (if present) disagrees
    with the version being validated against. Fragments (e.g. a single feature)
    have no schemaVersion attribute, so there is nothing to compare there."""
    raw = doc.getroot().get("schemaVersion")
    if raw is None:
        return
    doc_version = resolve_schema_version(raw)
    if doc_version != version:
        warnings.warn(
            f"validating against LER version {version!r}, but document's schemaVersion "
            f"attribute is {raw!r} (resolved: {doc_version!r})",
            stacklevel=3,
        )


def validate(doc: _ElementTree, version: str) -> Iterator[Violation]:
    warn_if_schema_version_mismatch(doc, version)
    for err in get_schema(version).iter_errors(doc):
        yield Violation(
            code="E1",
            message=err.reason,
            verbose_message=str(err),
            location=err.path,
            line=getattr(err, "position", (None, None))[0],
        )

def validate_file(path: str | Path, version: str) -> Iterator[Violation]:
    doc = etree.parse(str(path))
    yield from validate(doc, version)

def validate_string(xml: str, version: str) -> Iterator[Violation]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc, version)
