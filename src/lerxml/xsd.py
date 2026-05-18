from collections.abc import Iterator

from importlib.resources import files
import xmlschema
from lxml import etree
from lxml.etree import _ElementTree
from pathlib import Path

from . import ValidationError

xsd_path = files("lerxml") / "xsd" / "2.2_ler.xsd"
schema = xmlschema.XMLSchema(xsd_path)


def validate(doc: _ElementTree) -> Iterator[ValidationError]:
    for err in schema.iter_errors(doc):
        yield ValidationError(
            code="E1",
            message=err.reason,
            verbose_message=str(err),
            location=err.path,
            line=getattr(err, "position", (None, None))[0],
        )

def validate_file(path: str | Path) -> Iterator[ValidationError]:
    doc = etree.parse(str(path))
    yield from validate(doc)

def validate_string(xml: str) -> Iterator[ValidationError]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
