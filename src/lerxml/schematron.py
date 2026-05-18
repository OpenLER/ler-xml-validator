from typing import Literal, Optional
from collections.abc import Iterator

from dataclasses import dataclass
from importlib.resources import files
from lxml import etree
from lxml.etree import _ElementTree
from pathlib import Path
from pyschematron import validate_document

from . import ValidationError

ns = {"svrl": "http://purl.oclc.org/dsdl/svrl"}
sch_path = files("lerxml") / "schematron" / "2.2_ler.sch"
sch_doc = etree.parse(sch_path)


def validate(doc: _ElementTree) -> Iterator[ValidationError]:
    result = validate_document(doc, sch_doc)
    svrl_doc = result.get_svrl()

    for failed in svrl_doc.findall(".//svrl:failed-assert", ns):
        yield ValidationError(
            code=failed.get("id"),
            message=failed.findtext("svrl:text", default="", namespaces=ns),
            location=failed.get("location"),
        )

def validate_file(path: str | Path) -> Iterator[ValidationError]:
    doc = etree.parse(str(path))
    yield from validate(doc)

def validate_string(xml: str) -> Iterator[ValidationError]:
    doc = etree.ElementTree(etree.fromstring(xml.encode()))
    yield from validate(doc)
